"""Turn an Ops Watch findings report into a GitHub Issue, and keep the schedule alive.

Run by .github/workflows/ops-watch.yml after scripts/check_live_site.py. It only
ever creates, edits, comments on or closes Issues (label ``ops-watch``). It
never commits and never edits a page, claim or stamp.

Behaviour:
* findings present  -> open one issue "Ops Watch: live-site findings", or update
  its body in place (edits do not notify). A comment is added only when the set
  of failing/warning checks changes, so a standing DKIM warning is one issue,
  not one email per week.
* all clear         -> if that issue is open, comment "clear" and close it.
* heartbeat         -> at most one comment per ~28 days on the open
  "Ops Watch heartbeat" issue. See docs in 07_RESILIENCE/OPS_WATCH_KEEPALIVE.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ops_common import GitHubIssues, ensure_label, list_issues

LABEL = "ops-watch"
FINDINGS_TITLE = "Ops Watch: live-site findings"
HEARTBEAT_TITLE = "Ops Watch heartbeat"
HEARTBEAT_EVERY = timedelta(days=28)
MARKER_PREFIX = "<!-- ops-watch-fingerprint: "


def fingerprint(report: dict[str, Any]) -> str:
    """Stable id of WHICH checks are failing or warning (not of their changing detail)."""
    keys = sorted(
        f"{item['severity']}:{item['check']}"
        for item in report.get("failures", []) + report.get("warnings", [])
    )
    return hashlib.sha256("|".join(keys).encode()).hexdigest()[:12]


def missing_report(reason: str) -> dict[str, Any]:
    return {
        "generated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ"),
        "failures": [{"severity": "fail", "check": "ops-watch-run", "message": reason}],
        "warnings": [],
        "ok": [],
    }


def render_body(report: dict[str, Any], run_url: str | None) -> str:
    lines = [
        f"Weekly live-site check, {report.get('generated', 'unknown time')}.",
        "",
    ]
    for heading, key in (("Failures", "failures"), ("Warnings", "warnings")):
        items = report.get(key, [])
        if items:
            lines.append(f"### {heading}")
            lines += [f"- `{i['check']}`: {i['message']}" for i in items]
            lines.append("")
    lines += [
        f"Passing checks this run: {len(report.get('ok', []))}.",
    ]
    if run_url:
        lines.append(f"Run: {run_url}")
    lines += [
        "",
        (
            "Warnings that need a founder action (for example DKIM) stay here until the record is "
            "published; this issue closes itself when a run is clean. Failures mean the live site or "
            "its DNS differs from what the repo expects: check before relying on the site."
        ),
        "",
        f"{MARKER_PREFIX}{fingerprint(report)} -->",
    ]
    return "\n".join(lines)


def _find(issues: list[dict[str, Any]], title: str) -> dict[str, Any] | None:
    return next((i for i in issues if i["title"] == title), None)


def sync_findings_issue(api: Any, report: dict[str, Any], run_url: str | None) -> str:
    """Returns one of: created, updated, commented, closed, none."""
    issues = list_issues(api, LABEL, "open")
    existing = _find(issues, FINDINGS_TITLE)
    has_findings = bool(report.get("failures") or report.get("warnings"))

    if not has_findings:
        if existing:
            api.request("POST", f"/issues/{existing['number']}/comments", {"body": "Latest run is clean. Closing."})
            api.request("PATCH", f"/issues/{existing['number']}", {"state": "closed"})
            return "closed"
        return "none"

    body = render_body(report, run_url)
    if not existing:
        ensure_label(api, LABEL, "5319e7", "Automated live-site and schedule monitoring")
        api.request("POST", "/issues", {"title": FINDINGS_TITLE, "body": body, "labels": [LABEL]})
        return "created"

    previous = existing.get("body") or ""
    changed = f"{MARKER_PREFIX}{fingerprint(report)} -->" not in previous
    api.request("PATCH", f"/issues/{existing['number']}", {"body": body})
    if changed:
        api.request(
            "POST",
            f"/issues/{existing['number']}/comments",
            {"body": "The set of failing or warning checks changed; see the updated description."},
        )
        return "commented"
    return "updated"


def heartbeat(api: Any, now: datetime) -> str:
    """One comment every ~28 days so the repo shows regular activity. Returns the action taken."""
    issues = list_issues(api, LABEL, "open")
    issue = _find(issues, HEARTBEAT_TITLE)
    stamp = now.strftime("%Y-%m-%d")
    if not issue:
        ensure_label(api, LABEL, "5319e7", "Automated live-site and schedule monitoring")
        api.request(
            "POST",
            "/issues",
            {
                "title": HEARTBEAT_TITLE,
                "body": (
                    "Keep-alive for the scheduled Ops Watch and Regulatory Watch workflows. GitHub disables "
                    "scheduled workflows in a public repository after 60 days without repository activity; "
                    "this issue gets one comment about every four weeks. Leave it open. If the last comment "
                    "is older than 35 days, open the Actions tab and re-enable both workflows."
                ),
                "labels": [LABEL],
            },
        )
        return "created"
    comments = api.request("GET", f"/issues/{issue['number']}/comments?per_page=100") or []
    last = issue["created_at"]
    if comments:
        last = comments[-1]["created_at"]
    last_dt = datetime.fromisoformat(last)
    if now - last_dt >= HEARTBEAT_EVERY:
        api.request("POST", f"/issues/{issue['number']}/comments", {"body": f"Ops Watch ran on {stamp}."})
        return "commented"
    return "none"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--run-url", default=None)
    args = parser.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    if not token or not args.repo:
        raise SystemExit("GITHUB_TOKEN and --repo (or GITHUB_REPOSITORY) are required")

    path = Path(args.report)
    if path.exists():
        report = json.loads(path.read_text(encoding="utf-8"))
    else:
        report = missing_report("the check did not produce a report (the job crashed or timed out)")

    api = GitHubIssues(args.repo, token)
    print("findings issue:", sync_findings_issue(api, report, args.run_url))
    print("heartbeat:", heartbeat(api, datetime.now(UTC)))


if __name__ == "__main__":
    main()
