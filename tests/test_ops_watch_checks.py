"""Offline tests for the weekly --full checks in scripts/check_live_site.py and
the Issue reporting in scripts/report_ops_issue.py. Fixtures only: no network,
and in particular no DoH lookup, TLS handshake or GitHub call is made."""

from __future__ import annotations

import json
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "ops_watch"
sys.path.insert(0, str(ROOT / "scripts"))

import check_live_site as cls
import report_ops_issue as roi

PAGES_IPS = sorted(cls.GITHUB_PAGES_IPS)


def fixture(name: str) -> str:
    return (FIX / name).read_text(encoding="utf-8")


def doh(name: str, rtype: str) -> list[str]:
    return cls.parse_doh_answers(json.loads(fixture(name)), rtype)


def make_lookup(table: dict[tuple[str, str], list[str]], calls: list | None = None):
    def lookup(name: str, rtype: str) -> list[str]:
        if calls is not None:
            calls.append((name, rtype))
        value = table.get((name, rtype), [])
        if isinstance(value, Exception):
            raise value
        return value

    return lookup


GOOD = {
    ("clinicops.dk", "A"): PAGES_IPS,
    ("www.clinicops.dk", "CNAME"): ["example-account.github.io"],
    ("clinicops.dk", "TXT"): ["v=spf1 include:spf.protection.outlook.com -all", "MS=ms1"],
    ("_dmarc.clinicops.dk", "TXT"): ["v=DMARC1; p=quarantine; rua=mailto:x@example.test"],
    ("selector1._domainkey.clinicops.dk", "CNAME"): ["selector1.example.test"],
    ("selector2._domainkey.clinicops.dk", "CNAME"): ["selector2.example.test"],
}


def by_check(findings):
    return {f.check: f for f in findings}


# --- DoH parsing -----------------------------------------------------------


def test_doh_a_records_parsed_and_trailing_dot_stripped():
    assert doh("doh_a_ok.json", "A") == PAGES_IPS


def test_doh_txt_chunks_are_joined_and_unquoted():
    txt = doh("doh_txt_spf_chunked.json", "TXT")
    assert "v=spf1 include:spf.protection.outlook.com -all" in txt
    assert "MS=ms00000000" in txt


def test_doh_nxdomain_is_empty_and_servfail_is_a_lookup_error():
    assert doh("doh_nxdomain.json", "CNAME") == []
    with pytest.raises(cls.DnsLookupError):
        doh("doh_servfail.json", "A")


# --- DNS checks ------------------------------------------------------------


def test_dns_all_good_has_no_failures_or_warnings():
    findings = cls.check_dns(make_lookup(GOOD), sleep=lambda _s: None)
    assert {f.severity for f in findings} == {cls.OK}
    assert {"dns-apex-a", "dns-www-cname", "dns-spf", "dns-dmarc", "dns-dkim-selector1"} <= set(
        by_check(findings)
    )


def test_apex_a_wrong_addresses_fail_after_all_attempts():
    calls: list = []
    table = {**GOOD, ("clinicops.dk", "A"): ["76.223.105.230", "13.248.243.5"]}
    findings = by_check(cls.check_dns(make_lookup(table, calls), attempts=3, sleep=lambda _s: None))
    assert findings["dns-apex-a"].severity == cls.FAIL
    assert sum(1 for c in calls if c == ("clinicops.dk", "A")) == 3


def test_apex_a_one_noisy_lookup_is_tolerated():
    answers = iter([["76.223.105.230"], PAGES_IPS])

    def lookup(name, rtype):
        if (name, rtype) == ("clinicops.dk", "A"):
            return next(answers)
        return GOOD.get((name, rtype), [])

    findings = by_check(cls.check_dns(lookup, sleep=lambda _s: None))
    assert findings["dns-apex-a"].severity == cls.OK


def test_apex_a_missing_one_pages_ip_is_only_a_warning():
    table = {**GOOD, ("clinicops.dk", "A"): PAGES_IPS[:3]}
    assert by_check(cls.check_dns(make_lookup(table), sleep=lambda _s: None))["dns-apex-a"].severity == cls.WARN


def test_www_cname_missing_fails_and_non_github_target_warns():
    table = {**GOOD, ("www.clinicops.dk", "CNAME"): []}
    assert by_check(cls.check_dns(make_lookup(table), sleep=lambda _s: None))["dns-www-cname"].severity == cls.FAIL
    table = {**GOOD, ("www.clinicops.dk", "CNAME"): ["parking.example.test"]}
    assert by_check(cls.check_dns(make_lookup(table), sleep=lambda _s: None))["dns-www-cname"].severity == cls.WARN


def test_spf_missing_or_duplicated_fails():
    for records in ([], ["MS=x"], ["v=spf1 -all", "v=spf1 include:a.test -all"]):
        table = {**GOOD, ("clinicops.dk", "TXT"): records}
        f = by_check(cls.check_dns(make_lookup(table), sleep=lambda _s: None))["dns-spf"]
        assert f.severity == cls.FAIL, records


def test_dmarc_missing_fails():
    table = {**GOOD, ("_dmarc.clinicops.dk", "TXT"): ["something else"]}
    assert by_check(cls.check_dns(make_lookup(table), sleep=lambda _s: None))["dns-dmarc"].severity == cls.FAIL


def test_dkim_absent_is_a_warning_by_default_and_a_failure_when_promoted():
    table = {k: v for k, v in GOOD.items() if "_domainkey" not in k[0]}
    findings = by_check(cls.check_dns(make_lookup(table), sleep=lambda _s: None))
    assert findings["dns-dkim-selector1"].severity == cls.WARN
    assert findings["dns-dkim-selector2"].severity == cls.WARN
    assert "founder" in findings["dns-dkim-selector1"].message
    promoted = by_check(cls.check_dns(make_lookup(table), dkim_severity=cls.FAIL, sleep=lambda _s: None))
    assert promoted["dns-dkim-selector1"].severity == cls.FAIL


def test_dkim_txt_fallback_counts_as_present():
    table = {k: v for k, v in GOOD.items() if "selector1._domainkey" not in k[0]}
    table[("selector1._domainkey.clinicops.dk", "TXT")] = ["v=DKIM1; k=rsa; p=AAAA"]
    assert by_check(cls.check_dns(make_lookup(table), sleep=lambda _s: None))["dns-dkim-selector1"].severity == cls.OK


def test_lookup_service_outage_is_a_warning_not_a_site_failure():
    err = cls.DnsLookupError("dns.google unreachable")
    table = {key: err for key in GOOD}
    findings = cls.check_dns(make_lookup(table), sleep=lambda _s: None)
    assert findings and all(f.severity == cls.WARN for f in findings)
    assert {f.check for f in findings} == {"dns-lookup"}


# --- TLS expiry ------------------------------------------------------------

NOW = datetime(2026, 11, 16, tzinfo=UTC)


def test_tls_expiry_thresholds():
    assert cls.check_tls_expiry(NOW + timedelta(days=60), NOW).severity == cls.OK
    assert cls.check_tls_expiry(NOW + timedelta(days=15, hours=1), NOW).severity == cls.OK
    assert cls.check_tls_expiry(NOW + timedelta(days=14, hours=1), NOW).severity == cls.FAIL
    assert cls.check_tls_expiry(NOW - timedelta(days=1), NOW).severity == cls.FAIL


def test_tls_unreadable_certificate_fails():
    f = cls.check_tls_expiry(None, NOW, error="timed out")
    assert f.severity == cls.FAIL and "timed out" in f.message


# --- Sitemap ---------------------------------------------------------------


def test_sitemap_matching_counts_pass():
    assert cls.check_sitemap(fixture("sitemap_two.xml"), fixture("sitemap_two.xml")).severity == cls.OK


def test_sitemap_count_mismatch_fails_and_names_the_difference():
    f = cls.check_sitemap(fixture("sitemap_two.xml"), fixture("sitemap_three.xml"))
    assert f.severity == cls.FAIL and "https://example.test/extra" in f.message


def test_sitemap_over_ceiling_fails_even_if_it_matches_the_repo():
    f = cls.check_sitemap(fixture("sitemap_three.xml"), fixture("sitemap_three.xml"), ceiling=2)
    assert f.severity == cls.FAIL and "ceiling" in f.message


def test_sitemap_rejects_dtd_and_malformed_xml():
    assert cls.check_sitemap(fixture("rss_entity_bomb.xml"), fixture("sitemap_two.xml")).severity == cls.FAIL
    assert cls.check_sitemap("<urlset><url>", fixture("sitemap_two.xml")).severity == cls.FAIL


def test_committed_sitemap_is_within_the_ceiling():
    count = len(cls.sitemap_locs(cls.LOCAL_SITEMAP.read_text(encoding="utf-8")))
    assert count <= cls.SITEMAP_CEILING


# --- security.txt ----------------------------------------------------------

TODAY = date(2026, 11, 16)


def test_security_txt_ok():
    assert cls.check_security_txt(200, fixture("security_ok.txt"), TODAY).severity == cls.OK


def test_security_txt_missing_is_a_warning_expired_is_a_failure():
    assert cls.check_security_txt(404, "", TODAY).severity == cls.WARN
    assert cls.check_security_txt(200, fixture("security_expired.txt"), TODAY).severity == cls.FAIL
    assert cls.check_security_txt(200, "Expires: 2027-01-01T00:00:00Z", TODAY).severity == cls.WARN
    assert cls.check_security_txt(200, "Contact: mailto:a@b.test", TODAY).severity == cls.WARN


# --- Report ----------------------------------------------------------------


def test_build_report_groups_by_severity_and_keeps_http_failures():
    findings = [cls.Finding(cls.OK, "a", "fine"), cls.Finding(cls.WARN, "b", "meh")]
    report = cls.build_report(["/x: HTTP 500, expected 200"], findings, "2026-11-16T06:13Z")
    assert [f["check"] for f in report["failures"]] == ["http"]
    assert [f["check"] for f in report["warnings"]] == ["b"]
    assert [f["check"] for f in report["ok"]] == ["a"]


# --- Issue reporting -------------------------------------------------------


class FakeApi:
    def __init__(self, issues=None, comments=None):
        self.issues = issues or []
        self.comments = comments or []
        self.calls: list[tuple[str, str, dict | None]] = []

    def request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        if method == "GET" and path.startswith("/issues?"):
            return self.issues
        if method == "GET" and "/comments" in path:
            return self.comments
        return {}

    def writes(self):
        return [c for c in self.calls if c[0] != "GET"]


def report_with(failures=(), warnings=()):
    return {
        "generated": "2026-11-16T06:13Z",
        "failures": [{"severity": "fail", "check": c, "message": "m"} for c in failures],
        "warnings": [{"severity": "warn", "check": c, "message": "m"} for c in warnings],
        "ok": [{"severity": "ok", "check": "x", "message": "m"}],
    }


def test_clean_report_with_no_open_issue_does_nothing():
    api = FakeApi()
    assert roi.sync_findings_issue(api, report_with(), None) == "none"
    assert api.writes() == []


def test_findings_open_one_labelled_issue():
    api = FakeApi()
    assert roi.sync_findings_issue(api, report_with(failures=["dns-spf"]), "https://run") == "created"
    created = next(c for c in api.writes() if c[1] == "/issues")[2]
    assert created["title"] == roi.FINDINGS_TITLE and created["labels"] == ["ops-watch"]
    assert "dns-spf" in created["body"] and "https://run" in created["body"]


def test_same_findings_next_week_update_the_body_without_commenting():
    report = report_with(warnings=["dns-dkim-selector1"])
    existing = {"number": 7, "title": roi.FINDINGS_TITLE, "body": roi.render_body(report, None)}
    api = FakeApi(issues=[existing])
    assert roi.sync_findings_issue(api, report, None) == "updated"
    methods = [(m, p) for m, p, _ in api.writes()]
    assert methods == [("PATCH", "/issues/7")]


def test_changed_findings_add_one_comment():
    old = report_with(warnings=["dns-dkim-selector1"])
    existing = {"number": 7, "title": roi.FINDINGS_TITLE, "body": roi.render_body(old, None)}
    api = FakeApi(issues=[existing])
    new = report_with(failures=["tls-expiry"], warnings=["dns-dkim-selector1"])
    assert roi.sync_findings_issue(api, new, None) == "commented"
    assert [(m, p) for m, p, _ in api.writes()] == [("PATCH", "/issues/7"), ("POST", "/issues/7/comments")]


def test_clean_run_closes_the_open_issue():
    existing = {"number": 7, "title": roi.FINDINGS_TITLE, "body": ""}
    api = FakeApi(issues=[existing])
    assert roi.sync_findings_issue(api, report_with(), None) == "closed"
    assert ("PATCH", "/issues/7", {"state": "closed"}) in api.writes()


def test_pull_requests_are_never_mistaken_for_the_issue():
    pr = {"number": 3, "title": roi.FINDINGS_TITLE, "pull_request": {}}
    api = FakeApi(issues=[pr])
    assert roi.sync_findings_issue(api, report_with(failures=["tls-expiry"]), None) == "created"


def test_fingerprint_ignores_message_detail_but_not_the_set_of_checks():
    a = report_with(failures=["tls-expiry"])
    a["failures"][0]["message"] = "expires in 9 days"
    b = report_with(failures=["tls-expiry"])
    b["failures"][0]["message"] = "expires in 2 days"
    assert roi.fingerprint(a) == roi.fingerprint(b)
    assert roi.fingerprint(a) != roi.fingerprint(report_with(failures=["tls-expiry", "dns-spf"]))


def test_missing_report_becomes_a_failure():
    r = roi.missing_report("crashed")
    assert r["failures"][0]["check"] == "ops-watch-run"


def test_heartbeat_creates_then_comments_only_when_stale():
    now = datetime(2026, 11, 16, 6, 13, tzinfo=UTC)
    api = FakeApi()
    assert roi.heartbeat(api, now) == "created"

    issue = {"number": 9, "title": roi.HEARTBEAT_TITLE, "created_at": "2026-09-01T00:00:00+00:00"}
    fresh = FakeApi(issues=[issue], comments=[{"created_at": "2026-11-10T00:00:00+00:00"}])
    assert roi.heartbeat(fresh, now) == "none"
    assert fresh.writes() == []

    stale = FakeApi(issues=[issue], comments=[{"created_at": "2026-10-01T00:00:00+00:00"}])
    assert roi.heartbeat(stale, now) == "commented"
    assert stale.writes()[0][1] == "/issues/9/comments"


def test_heartbeat_with_no_comments_uses_issue_creation_date():
    now = datetime(2026, 11, 16, tzinfo=UTC)
    issue = {"number": 9, "title": roi.HEARTBEAT_TITLE, "created_at": "2026-11-01T00:00:00+00:00"}
    assert roi.heartbeat(FakeApi(issues=[issue]), now) == "none"


# --- Workflow contract -----------------------------------------------------


def test_workflow_keeps_only_dispatch_and_weekly_cron_and_no_content_write():
    import yaml

    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "ops-watch.yml").read_text(encoding="utf-8"))
    triggers = wf.get("on", wf.get(True))
    assert set(triggers) == {"workflow_dispatch", "schedule"}
    assert wf["permissions"] == {"contents": "read"}
    job_perms = wf["jobs"]["live-site-health"]["permissions"]
    assert job_perms["contents"] == "read"
    assert set(job_perms) == {"contents", "issues", "actions"}
    text = (ROOT / ".github" / "workflows" / "ops-watch.yml").read_text(encoding="utf-8")
    assert "git push" not in text and "git commit" not in text
