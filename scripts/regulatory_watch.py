"""Regulatory change watch: official feeds in, GitHub Issues out. Nothing else.

What it does, weekly (see .github/workflows/regulatory-watch.yml):
  1. Fetches three official public feeds, one request each, with an identifying
     User-Agent and only if robots.txt allows it.
  2. Compares the items with research/regulatory-watch-state.json and with the
     items already reported in earlier regulatory-watch Issues.
  3. Opens ONE Issue listing new or changed items (title, link, date), with a
     paste-ready state update. A human reads the primary source and decides.
  4. Opens the "Monthly verification YYYY-MM" Issue once per month from
     .github/ISSUE_TEMPLATE/monthly-verification.md.

What it must never do (lens 29, section 6, and AGENTS.md rules 11 and 12):
  * edit a claim, stamp, page or the registry; commit anything; publish anything;
  * retry after a 403 or 429, or poll a source that has refused us: the refusal
    opens an Issue and that feed stays paused until the Issue is closed by a human;
  * poll the EUDAMED public API (only the Commission's news RSS is read here);
  * store regulator text: state keeps only item ids and hashes, Issues quote a
    title, a link and a date, with the source named.

A feed item is a prompt to read the primary source, never evidence by itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.robotparser import RobotFileParser

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ops_common import (
    USER_AGENT,
    GitHubIssues,
    UnsafeXMLError,
    ensure_label,
    list_issues,
    safe_parse_xml,
    strip_ns,
)

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "research" / "regulatory-watch-state.json"
TEMPLATE_PATH = ROOT / ".github" / "ISSUE_TEMPLATE" / "monthly-verification.md"

LABEL = "regulatory-watch"
MONTHLY_LABEL = "monthly-verification"
FETCH_TIMEOUT = 20
MAX_BODY_BYTES = 2_000_000
MAX_LISTED = 25
MAX_STATE_ITEMS = 200

FEEDS: tuple[dict[str, str], ...] = (
    {
        "id": "commission-eudamed",
        "label": "European Commission, EUDAMED news (RSS)",
        "url": "https://health.ec.europa.eu/node/12988/rss_en",
    },
    {
        "id": "ema-whats-new",
        "label": "EMA, What's new (RSS)",
        "url": "https://www.ema.europa.eu/en/whats-new.xml",
    },
    {
        "id": "dkma-news",
        "label": "Danish Medicines Agency, news (RSS)",
        "url": "https://laegemiddelstyrelsen.dk/en/news/rss-feed/",
    },
)


@dataclass(frozen=True)
class Item:
    id: str
    title: str
    link: str
    published: str
    digest: str  # hash of title|link|published, so an edited item is "changed"


@dataclass(frozen=True)
class FetchResult:
    status: int | None  # HTTP status, None when no response (network error, robots)
    body: bytes = b""
    error: str = ""
    robots_blocked: bool = False


# ---------------------------------------------------------------------------
# Parsing and diffing (pure functions, unit-tested with fixture feeds)
# ---------------------------------------------------------------------------


def _text(el: Any, *names: str) -> str:
    for child in el:
        if strip_ns(child.tag) in names and (child.text or "").strip():
            return " ".join(child.text.split())
    return ""


def parse_feed(payload: bytes) -> list[Item]:
    """RSS 2.0 or Atom. Raises UnsafeXMLError on a DTD, oversize input or bad XML."""
    root = safe_parse_xml(payload)
    items: list[Item] = []
    for el in root.iter():
        kind = strip_ns(el.tag)
        if kind not in ("item", "entry"):
            continue
        title = _text(el, "title")
        published = _text(el, "pubDate", "published", "updated", "date")
        link = _text(el, "link")
        if not link:  # Atom: <link href="..."/>
            for child in el:
                if strip_ns(child.tag) == "link" and child.get("href"):
                    link = child.get("href", "")
                    break
        guid = _text(el, "guid", "id") or link or f"{title}|{published}"
        if not (title or link):
            continue
        digest = hashlib.sha256(f"{title}|{link}|{published}".encode()).hexdigest()[:16]
        items.append(Item(guid, title, link, published, digest))
    return items


def item_key(feed_id: str, item: Item) -> str:
    return hashlib.sha256(f"{feed_id}|{item.id}|{item.digest}".encode()).hexdigest()[:16]


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema": 1, "feeds": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def diff_feed(
    feed_id: str, items: list[Item], state: dict[str, Any], reported_keys: set[str]
) -> tuple[list[Item], list[Item]]:
    """Return (new, changed) items not yet accepted in state nor reported in an Issue."""
    seen: dict[str, str] = state.get("feeds", {}).get(feed_id, {}).get("seen", {})
    new: list[Item] = []
    changed: list[Item] = []
    for item in items:
        if item_key(feed_id, item) in reported_keys:
            continue
        if item.id not in seen:
            new.append(item)
        elif seen[item.id] != item.digest:
            changed.append(item)
    return new, changed


def state_update(findings: dict[str, tuple[list[Item], list[Item]]]) -> dict[str, dict[str, str]]:
    """The paste-ready {feed_id: {item id: digest}} for items an Issue reports."""
    return {
        feed_id: {i.id: i.digest for i in new + changed}
        for feed_id, (new, changed) in findings.items()
        if new or changed
    }


def merge_state(state: dict[str, Any], update: dict[str, dict[str, str]]) -> dict[str, Any]:
    feeds = state.setdefault("feeds", {})
    for feed in FEEDS:
        entry = feeds.setdefault(feed["id"], {"url": feed["url"], "seen": {}})
        entry["seen"].update(update.get(feed["id"], {}))
        entry["seen"] = dict(list(entry["seen"].items())[-MAX_STATE_ITEMS:])
    return state


# ---------------------------------------------------------------------------
# Fetching: one polite request per source, no retry, robots.txt first
# ---------------------------------------------------------------------------


def _open(url: str, timeout: int = FETCH_TIMEOUT) -> tuple[int, bytes]:
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.1")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(MAX_BODY_BYTES + 1)
    except urllib.error.HTTPError as exc:
        return exc.code, b""


Opener = Any  # callable(url) -> (status, body); injected in tests


def robots_allows(url: str, opener: Opener = _open) -> tuple[bool, str]:
    parts = urllib.parse.urlsplit(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    try:
        status, body = opener(robots_url)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, f"robots.txt unreachable ({exc}); not fetching"
    parser = RobotFileParser()
    if status in (401, 403):
        return False, f"robots.txt returned {status}; treating as disallowed"
    if status >= 500:
        return False, f"robots.txt returned {status}; not fetching"
    parser.parse(body.decode("utf-8", "replace").splitlines() if status == 200 else [])
    if parser.can_fetch(USER_AGENT, url):
        return True, ""
    return False, "robots.txt disallows this path for our user agent"


def fetch_feed(url: str, opener: Opener = _open) -> FetchResult:
    allowed, reason = robots_allows(url, opener)
    if not allowed:
        return FetchResult(None, error=reason, robots_blocked=True)
    try:
        status, body = opener(url)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return FetchResult(None, error=f"network error: {exc}")
    if len(body) > MAX_BODY_BYTES:
        return FetchResult(status, error="response larger than the 2 MB cap")
    return FetchResult(status, body)


# ---------------------------------------------------------------------------
# Issue building and publishing (Issues only)
# ---------------------------------------------------------------------------

_KEYS_RE = re.compile(r"<!-- rw-keys: ([0-9a-f ]*)-->")


def reported_keys(api: Any) -> set[str]:
    keys: set[str] = set()
    for issue in list_issues(api, LABEL, "all"):
        for match in _KEYS_RE.finditer(issue.get("body") or ""):
            keys.update(match.group(1).split())
    return keys


def _bullet(item: Item) -> str:
    link = f" ({item.link})" if item.link else ""
    date = f" [{item.published}]" if item.published else ""
    return f"- {item.title or '(untitled)'}{date}{link}"


def build_watch_issue(
    findings: dict[str, tuple[list[Item], list[Item]]], labels: dict[str, str], today: str
) -> tuple[str, str]:
    all_keys: list[str] = []
    lines = [
        (
            f"Weekly feed check, {today}. A feed item is a prompt to read the primary source; it is not "
            "evidence and nothing on the site has been changed. Titles, links and dates below are quoted "
            "from each publisher's feed (credit: the publisher named in each heading)."
        ),
        "",
    ]
    for feed_id, (new, changed) in findings.items():
        if not (new or changed):
            continue
        lines.append(f"### {labels[feed_id]}")
        for heading, items in (("New", new), ("Changed", changed)):
            if items:
                lines.append(f"{heading} ({len(items)}):")
                lines += [_bullet(i) for i in items[:MAX_LISTED]]
                if len(items) > MAX_LISTED:
                    lines.append(f"- ... and {len(items) - MAX_LISTED} more (all are recorded below)")
        lines.append("")
        all_keys += [item_key(feed_id, i) for i in new + changed]
    lines += [
        "### What to do",
        "1. Read the primary source for anything that touches a class A or B claim in `research/claims.jsonl`.",
        "2. Change a claim, date or stamp only after reading at source, in a normal PR (never from this Issue).",
        (
            "3. Optional housekeeping: paste the block below into a file and run "
            "`python scripts/regulatory_watch.py apply-update FILE` to accept these items into "
            "`research/regulatory-watch-state.json`. Not needed to stop repeats: reported items are "
            "not re-listed."
        ),
        "",
        "<details><summary>State update</summary>",
        "",
        "```json",
        json.dumps(state_update(findings), indent=1, sort_keys=True),
        "```",
        "",
        "</details>",
        "",
        f"<!-- rw-keys: {' '.join(all_keys)} -->",
    ]
    return f"Regulatory watch: new items {today}", "\n".join(lines)


def build_blocked_issue(feed: dict[str, str], result: FetchResult) -> tuple[str, str]:
    why = result.error or f"HTTP {result.status}"
    title = f"Regulatory watch: {feed['label']} not readable ({why[:60]})"
    body = (
        f"The weekly watch could not read `{feed['url']}`: {why}.\n\n"
        "Per the reuse rules in lens 29 and `research/eudamed-public-api-reuse-review.md`, the watch made no "
        "retry and will not request this feed again while this Issue is open. A 403 or 429 means the "
        "publisher is refusing automated reads: check the publisher's terms and the feed address, then "
        "close this Issue to resume (or change the feed in `scripts/regulatory_watch.py`). Until then read "
        "this source by hand in the monthly routine.\n\n"
        f"<!-- rw-blocked: {feed['id']} -->"
    )
    return title, body


def blocked_feed_ids(api: Any) -> set[str]:
    out: set[str] = set()
    for issue in list_issues(api, LABEL, "open"):
        out.update(re.findall(r"<!-- rw-blocked: ([a-z0-9-]+) -->", issue.get("body") or ""))
    return out


def strip_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    _, front, body = text.split("---", 2)
    meta = {}
    for line in front.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip("'\"")
    return meta, body.lstrip("\n")


def ensure_monthly_issue(api: Any, template: str, now: datetime) -> str:
    _, body = strip_front_matter(template)
    title = f"Monthly verification {now:%Y-%m}"
    if any(i["title"] == title for i in list_issues(api, MONTHLY_LABEL, "all")):
        return "exists"
    ensure_label(api, MONTHLY_LABEL, "0e8a16", "Monthly regulatory verification routine")
    api.request("POST", "/issues", {"title": title, "body": body, "labels": [MONTHLY_LABEL]})
    return "created"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run(api: Any, state: dict[str, Any], opener: Opener, now: datetime, template: str) -> dict[str, Any]:
    labels = {f["id"]: f["label"] for f in FEEDS}
    paused = blocked_feed_ids(api)
    known = reported_keys(api)
    findings: dict[str, tuple[list[Item], list[Item]]] = {}
    summary: dict[str, Any] = {"feeds": {}, "errors": []}

    for feed in FEEDS:
        fid = feed["id"]
        if fid in paused:
            summary["feeds"][fid] = "paused (open 'not readable' Issue)"
            continue
        result = fetch_feed(feed["url"], opener)
        refused = result.status in (403, 429) or result.robots_blocked
        if refused:
            title, body = build_blocked_issue(feed, result)
            ensure_label(api, LABEL, "1d76db", "Official-feed change watch")
            api.request("POST", "/issues", {"title": title, "body": body, "labels": [LABEL]})
            summary["feeds"][fid] = f"refused ({result.error or result.status}); Issue opened, polling paused"
            continue
        if result.status != 200 or result.error:
            msg = result.error or f"HTTP {result.status}"
            summary["feeds"][fid] = f"error: {msg}"
            summary["errors"].append(f"{fid}: {msg}")
            continue
        try:
            items = parse_feed(result.body)
        except UnsafeXMLError as exc:
            summary["feeds"][fid] = f"error: {exc}"
            summary["errors"].append(f"{fid}: {exc}")
            continue
        if not items:
            summary["feeds"][fid] = "error: feed parsed but contained no items"
            summary["errors"].append(f"{fid}: no items")
            continue
        new, changed = diff_feed(fid, items, state, known)
        findings[fid] = (new, changed)
        summary["feeds"][fid] = f"{len(items)} items, {len(new)} new, {len(changed)} changed"

    if any(new or changed for new, changed in findings.values()):
        title, body = build_watch_issue(findings, labels, f"{now:%Y-%m-%d}")
        ensure_label(api, LABEL, "1d76db", "Official-feed change watch")
        api.request("POST", "/issues", {"title": title, "body": body, "labels": [LABEL]})
        summary["issue"] = title
    summary["monthly"] = ensure_monthly_issue(api, template, now)
    return summary


def apply_update(state_path: Path, text: str) -> dict[str, Any]:
    """Merge a '```json' state-update block (or bare JSON) from an Issue body into the state file."""
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    update = json.loads(match.group(1) if match else text)
    unknown = set(update) - {f["id"] for f in FEEDS}
    if unknown:
        raise SystemExit(f"unknown feed ids in update: {sorted(unknown)}")
    state = merge_state(load_state(state_path), update)
    state["schema"] = 1
    state_path.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return state


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    run_p = sub.add_parser("run", help="fetch feeds and open Issues (needs GITHUB_TOKEN)")
    run_p.add_argument("--state", default=str(STATE_PATH))
    run_p.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    up_p = sub.add_parser("apply-update", help="merge an Issue's state-update block into the state file")
    up_p.add_argument("file")
    up_p.add_argument("--state", default=str(STATE_PATH))
    args = parser.parse_args(argv)

    if args.cmd == "apply-update":
        apply_update(Path(args.state), Path(args.file).read_text(encoding="utf-8"))
        print(f"state updated: {args.state}")
        return

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    if not token or not args.repo:
        raise SystemExit("GITHUB_TOKEN and --repo (or GITHUB_REPOSITORY) are required")
    summary = run(
        GitHubIssues(args.repo, token),
        load_state(Path(args.state)),
        _open,
        datetime.now(UTC),
        TEMPLATE_PATH.read_text(encoding="utf-8"),
    )
    print(json.dumps(summary, indent=2))
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as fh:
            fh.write("## Regulatory watch\n\n```json\n" + json.dumps(summary, indent=2) + "\n```\n")
    if summary["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
