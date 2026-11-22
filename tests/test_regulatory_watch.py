"""Offline tests for scripts/regulatory_watch.py using fixture feeds only.

No feed is fetched and no GitHub call is made: the opener and the Issues API
are fakes. The behaviours pinned here are the safety rules: Issues only, no
retry after 403/429, a refused feed stays paused, nothing is committed, and an
item is never reported twice.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "ops_watch"
sys.path.insert(0, str(ROOT / "scripts"))

import regulatory_watch as rw
from ops_common import UnsafeXMLError

NOW = datetime(2026, 11, 16, 6, 23, tzinfo=UTC)
TEMPLATE = (ROOT / ".github" / "ISSUE_TEMPLATE" / "monthly-verification.md").read_text(encoding="utf-8")


def fx(name: str) -> bytes:
    return (FIX / name).read_bytes()


# --- parsing ---------------------------------------------------------------


def test_parse_rss_items_with_guid_and_link_fallback():
    items = rw.parse_feed(fx("rss_commission.xml"))
    assert [i.title for i in items] == ["Fixture item one", "Fixture item two", "Fixture item three"]
    assert items[0].id == "a-1"
    assert items[2].id == "https://example.test/a/3"  # no guid: falls back to the link


def test_parse_atom_entries_use_href_and_id():
    items = rw.parse_feed(fx("atom_ema.xml"))
    assert [i.id for i in items] == ["urn:fixture:b-1", "urn:fixture:b-2"]
    assert items[0].link == "https://example.test/b/1"
    assert items[0].published == "2026-11-12T08:00:00Z"


def test_parse_refuses_entity_declarations():
    with pytest.raises(UnsafeXMLError):
        rw.parse_feed(fx("rss_entity_bomb.xml"))


def test_parse_refuses_oversized_and_malformed_input():
    with pytest.raises(UnsafeXMLError):
        rw.parse_feed(b"<rss>" + b"x" * 2_100_000 + b"</rss>")
    with pytest.raises(UnsafeXMLError):
        rw.parse_feed(b"<rss><item>")


# --- diff logic ------------------------------------------------------------


def state_with(feed_id: str, items):
    return {"feeds": {feed_id: {"seen": {i.id: i.digest for i in items}}}}


def test_diff_everything_is_new_against_empty_state():
    items = rw.parse_feed(fx("rss_commission.xml"))
    new, changed = rw.diff_feed("commission-eudamed", items, {"feeds": {}}, set())
    assert len(new) == 3 and changed == []


def test_diff_known_items_are_silent_and_only_the_new_one_is_reported():
    items = rw.parse_feed(fx("rss_commission.xml"))
    state = state_with("commission-eudamed", items[:2])
    new, changed = rw.diff_feed("commission-eudamed", items, state, set())
    assert [i.id for i in new] == [items[2].id] and changed == []


def test_diff_detects_an_edited_item_as_changed():
    items = rw.parse_feed(fx("rss_commission.xml"))
    state = state_with("commission-eudamed", items)
    edited = rw.parse_feed(fx("rss_commission.xml").replace(b"Fixture item two", b"Fixture item two (revised)"))
    new, changed = rw.diff_feed("commission-eudamed", edited, state, set())
    assert new == [] and [i.id for i in changed] == ["a-2"]


def test_diff_skips_items_already_reported_in_an_issue():
    items = rw.parse_feed(fx("rss_commission.xml"))
    reported = {rw.item_key("commission-eudamed", i) for i in items}
    new, changed = rw.diff_feed("commission-eudamed", items, {"feeds": {}}, reported)
    assert new == [] and changed == []


def test_item_key_depends_on_the_feed_and_the_content():
    a = rw.parse_feed(fx("rss_commission.xml"))[0]
    assert rw.item_key("f1", a) != rw.item_key("f2", a)


def test_state_update_and_merge_round_trip_without_regulator_text():
    items = rw.parse_feed(fx("rss_commission.xml"))
    update = rw.state_update({"commission-eudamed": (items, []), "dkma-news": ([], [])})
    assert set(update) == {"commission-eudamed"}
    merged = rw.merge_state({"schema": 1, "feeds": {}}, update)
    seen = merged["feeds"]["commission-eudamed"]["seen"]
    assert set(seen) == {i.id for i in items}
    assert "Fixture item one" not in json.dumps(merged)  # ids and hashes only, no titles


def test_apply_update_reads_the_block_from_an_issue_body(tmp_path):
    items = rw.parse_feed(fx("atom_ema.xml"))
    _, body = rw.build_watch_issue(
        {"ema-whats-new": (items, [])}, {"ema-whats-new": "EMA fixture"}, "2026-11-16"
    )
    state_file = tmp_path / "state.json"
    state_file.write_text(json.dumps({"schema": 1, "feeds": {}}), encoding="utf-8")
    state = rw.apply_update(state_file, body)
    assert set(state["feeds"]["ema-whats-new"]["seen"]) == {i.id for i in items}
    assert json.loads(state_file.read_text(encoding="utf-8"))["schema"] == 1
    with pytest.raises(SystemExit):
        rw.apply_update(state_file, json.dumps({"not-a-feed": {"x": "y"}}))


def test_committed_state_file_is_valid_and_covers_every_feed():
    state = json.loads(rw.STATE_PATH.read_text(encoding="utf-8"))
    assert state["schema"] == 1
    assert set(state["feeds"]) == {f["id"] for f in rw.FEEDS}
    for feed in rw.FEEDS:
        assert state["feeds"][feed["id"]]["url"] == feed["url"]


def test_the_three_named_feeds_are_configured_and_no_eudamed_api():
    urls = {f["url"] for f in rw.FEEDS}
    assert "https://health.ec.europa.eu/node/12988/rss_en" in urls
    assert "https://laegemiddelstyrelsen.dk/en/news/rss-feed/" in urls
    assert any("ema.europa.eu" in u for u in urls)
    assert not any("api" in u.lower() or "eudamed/api" in u for u in urls)


# --- fetching: robots.txt, no retry ---------------------------------------


class FakeOpener:
    """Exact-URL fake; any robots.txt not listed answers 404 (allowed)."""

    def __init__(self, responses):
        self.responses = responses  # full URL or "/robots.txt" suffix -> (status, body) or Exception
        self.requests: list[str] = []

    def __call__(self, url):
        self.requests.append(url)
        value = self.responses.get(url)
        if value is None:
            value = next((v for k, v in self.responses.items() if k.startswith("/") and url.endswith(k)), (404, b""))
        if isinstance(value, Exception):
            raise value
        return value


def test_robots_404_allows_and_disallow_blocks():
    allow = FakeOpener({"/robots.txt": (404, b"")})
    assert rw.robots_allows("https://example.test/feed", allow)[0] is True
    block = FakeOpener({"/robots.txt": (200, b"User-agent: *\nDisallow: /feed\n")})
    ok, why = rw.robots_allows("https://example.test/feed", block)
    assert ok is False and "disallows" in why
    forbidden = FakeOpener({"/robots.txt": (403, b"")})
    assert rw.robots_allows("https://example.test/feed", forbidden)[0] is False


def test_fetch_makes_exactly_one_feed_request_and_never_retries_a_403():
    opener = FakeOpener({"https://example.test/feed": (403, b"")})
    result = rw.fetch_feed("https://example.test/feed", opener)
    assert result.status == 403
    assert opener.requests.count("https://example.test/feed") == 1


def test_fetch_does_not_request_the_feed_when_robots_blocks():
    opener = FakeOpener({"/robots.txt": (200, b"User-agent: *\nDisallow: /\n"), "https://example.test/feed": (200, b"<rss/>")})
    result = rw.fetch_feed("https://example.test/feed", opener)
    assert result.robots_blocked and "https://example.test/feed" not in opener.requests


def test_network_errors_are_reported_not_raised():
    opener = FakeOpener({"https://example.test/feed": TimeoutError("slow")})
    result = rw.fetch_feed("https://example.test/feed", opener)
    assert result.status is None and "network error" in result.error


# --- orchestration ---------------------------------------------------------


class FakeApi:
    def __init__(self, issues=None):
        self.issues = issues or []
        self.calls: list[tuple[str, str, dict | None]] = []

    def request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        if method == "GET" and path.startswith("/issues?"):
            label = path.split("labels=")[1].split("&")[0]
            return [i for i in self.issues if label in i.get("labels", [])]
        return {}

    def created(self):
        return [c[2] for c in self.calls if c[0] == "POST" and c[1] == "/issues"]


def opener_for(feeds: dict[str, tuple[int, bytes]]):
    return FakeOpener({f["url"]: feeds[f["id"]] for f in rw.FEEDS})


GOOD_FEEDS = {
    "commission-eudamed": (200, fx("rss_commission.xml")),
    "ema-whats-new": (200, fx("atom_ema.xml")),
    "dkma-news": (200, fx("rss_dkma.xml")),
}


def test_first_run_opens_one_watch_issue_and_the_monthly_issue():
    api = FakeApi()
    summary = rw.run(api, {"feeds": {}}, opener_for(GOOD_FEEDS), NOW, TEMPLATE)
    titles = [c["title"] for c in api.created()]
    assert titles == ["Regulatory watch: new items 2026-11-16", "Monthly verification 2026-11"]
    watch = api.created()[0]
    assert watch["labels"] == ["regulatory-watch"]
    for needle in ("Fixture item one", "Fixture guideline update", "Fixture Danish news"):
        assert needle in watch["body"]
    assert "nothing on the site has been changed" in watch["body"]
    assert summary["errors"] == []


def test_only_issues_are_written_never_contents_or_pulls():
    api = FakeApi()
    rw.run(api, {"feeds": {}}, opener_for(GOOD_FEEDS), NOW, TEMPLATE)
    for method, path, _ in api.calls:
        assert path.startswith(("/issues", "/labels")), path
        assert "/contents" not in path and "/pulls" not in path and "/git/" not in path


def test_second_run_with_the_same_items_opens_no_second_watch_issue():
    first = FakeApi()
    rw.run(first, {"feeds": {}}, opener_for(GOOD_FEEDS), NOW, TEMPLATE)
    watch = first.created()[0]
    monthly = first.created()[1]
    existing = [
        {"title": watch["title"], "body": watch["body"], "labels": ["regulatory-watch"]},
        {"title": monthly["title"], "body": monthly["body"], "labels": ["monthly-verification"]},
    ]
    second = FakeApi(issues=existing)
    summary = rw.run(second, {"feeds": {}}, opener_for(GOOD_FEEDS), NOW, TEMPLATE)
    assert second.created() == []
    assert "issue" not in summary and summary["monthly"] == "exists"


def test_state_file_items_suppress_reporting():
    state = {"feeds": {}}
    for feed_id, xml in (("commission-eudamed", "rss_commission.xml"), ("ema-whats-new", "atom_ema.xml"), ("dkma-news", "rss_dkma.xml")):
        state["feeds"][feed_id] = {"seen": {i.id: i.digest for i in rw.parse_feed(fx(xml))}}
    api = FakeApi()
    summary = rw.run(api, state, opener_for(GOOD_FEEDS), NOW, TEMPLATE)
    assert [c["title"] for c in api.created()] == ["Monthly verification 2026-11"]
    assert "issue" not in summary


def test_403_opens_a_blocked_issue_once_and_does_not_retry():
    feeds = {**GOOD_FEEDS, "ema-whats-new": (403, b"")}
    opener = opener_for(feeds)
    api = FakeApi()
    summary = rw.run(api, {"feeds": {}}, opener, NOW, TEMPLATE)
    ema_url = next(f["url"] for f in rw.FEEDS if f["id"] == "ema-whats-new")
    assert opener.requests.count(ema_url) == 1
    blocked = [c for c in api.created() if "rw-blocked: ema-whats-new" in c["body"]]
    assert len(blocked) == 1 and "no retry" in blocked[0]["body"]
    assert "refused" in summary["feeds"]["ema-whats-new"]
    assert summary["errors"] == []  # a refusal is an Issue for a human, not a retry loop


def test_429_is_treated_like_403():
    feeds = {**GOOD_FEEDS, "dkma-news": (429, b"")}
    api = FakeApi()
    rw.run(api, {"feeds": {}}, opener_for(feeds), NOW, TEMPLATE)
    assert any("rw-blocked: dkma-news" in c["body"] for c in api.created())


def test_a_feed_with_an_open_blocked_issue_is_not_requested_at_all():
    blocked_issue = {"title": "x", "body": "<!-- rw-blocked: ema-whats-new -->", "labels": ["regulatory-watch"]}
    opener = opener_for(GOOD_FEEDS)
    api = FakeApi(issues=[blocked_issue])
    summary = rw.run(api, {"feeds": {}}, opener, NOW, TEMPLATE)
    ema_url = next(f["url"] for f in rw.FEEDS if f["id"] == "ema-whats-new")
    assert ema_url not in opener.requests
    assert summary["feeds"]["ema-whats-new"].startswith("paused")


def test_unsafe_or_empty_feed_is_an_error_not_an_issue():
    feeds = {**GOOD_FEEDS, "commission-eudamed": (200, fx("rss_entity_bomb.xml")), "dkma-news": (200, b"<rss><channel/></rss>")}
    api = FakeApi()
    summary = rw.run(api, {"feeds": {}}, opener_for(feeds), NOW, TEMPLATE)
    assert len(summary["errors"]) == 2
    assert not any("rw-blocked" in c["body"] for c in api.created())


def test_server_error_is_an_error_without_an_issue():
    feeds = {**GOOD_FEEDS, "commission-eudamed": (503, b"")}
    summary = rw.run(FakeApi(), {"feeds": {}}, opener_for(feeds), NOW, TEMPLATE)
    assert any(e.startswith("commission-eudamed") for e in summary["errors"])


# --- monthly routine template ---------------------------------------------


def test_monthly_template_checklist_is_the_105_minute_routine():
    meta, body = rw.strip_front_matter(TEMPLATE)
    assert meta["labels"] == "monthly-verification"
    minutes = [int(m) for m in re.findall(r"^- \[ \] \d\. \((\d+) min\)", body, flags=re.MULTILINE)]
    assert len(minutes) == 8 and sum(minutes) == 105
    assert "hard cap 2 hours" in body


def test_monthly_issue_created_once_per_month():
    api = FakeApi()
    assert rw.ensure_monthly_issue(api, TEMPLATE, NOW) == "created"
    created = api.created()[0]
    assert created["title"] == "Monthly verification 2026-11" and "---" not in created["body"].splitlines()[0]
    again = FakeApi(issues=[{"title": created["title"], "body": "", "labels": ["monthly-verification"]}])
    assert rw.ensure_monthly_issue(again, TEMPLATE, NOW) == "exists"
    assert rw.ensure_monthly_issue(again, TEMPLATE, datetime(2026, 12, 7, tzinfo=UTC)) == "created"


# --- workflow contract -----------------------------------------------------


def test_workflow_triggers_permissions_and_no_write_path():
    import yaml

    path = ROOT / ".github" / "workflows" / "regulatory-watch.yml"
    wf = yaml.safe_load(path.read_text(encoding="utf-8"))
    triggers = wf.get("on", wf.get(True))
    assert set(triggers) == {"workflow_dispatch", "schedule"}
    assert triggers["schedule"] == [{"cron": "23 6 * * 1"}]
    job = wf["jobs"]["regulatory-watch"]
    assert job["permissions"] == {"contents": "read", "issues": "write"}
    text = path.read_text(encoding="utf-8")
    for forbidden in ("git push", "git commit", "contents: write", "pull-requests: write"):
        assert forbidden not in text
