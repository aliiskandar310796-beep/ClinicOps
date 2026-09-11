"""Offline tests for scripts/eudamed_watch.py.

All responses come from tests/fixtures/eudamed_fixture.json (fictional data).
No network access is used or permitted by these tests.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "eudamed_watch.py"
FIXTURE = ROOT / "tests" / "fixtures" / "eudamed_fixture.json"
SEED_WATCHLIST = ROOT / "data" / "eudamed" / "watchlist.json"

_spec = importlib.util.spec_from_file_location("eudamed_watch", SCRIPT)
watch = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(watch)

STYLET = "Fixture — Stylet"
SNARE = "Fixture — ONE Snare"
OPRA = "Fixture — OPRA"
PALACOS = "Heraeus — PALACOS"
CERAMENT = "Fixture — CERAMENT"
VARIANT = "Fixture — Variants"

TEST_WATCHLIST = {
    "entries": [
        {"label": STYLET, "trade_name_query": "Stylet", "manufacturer_contains": "Brainlab", "expected_srn": "DE-MF-000000001"},
        {"label": SNARE, "trade_name_query": "ONE Snare", "manufacturer_contains": "Merit"},
        {"label": OPRA, "trade_name_query": "OPRA", "manufacturer_contains": "Integrum"},
        {"label": PALACOS, "trade_name_query": "PALACOS", "manufacturer_contains": "Heraeus"},
        {"label": CERAMENT, "trade_name_query": "CERAMENT", "manufacturer_contains": "BONESUPPORT"},
        {"label": VARIANT, "trade_name_query": "Variant", "manufacturer_contains": "Fixture Variant"},
    ]
}


@pytest.fixture
def workspace(tmp_path: Path) -> dict[str, Path]:
    watchlist = tmp_path / "watchlist.json"
    watchlist.write_text(json.dumps(TEST_WATCHLIST), encoding="utf-8")
    out = tmp_path / "eudamed"
    return {"watchlist": watchlist, "out": out, "tmp": tmp_path}


def _run(workspace: dict[str, Path], fixture: Path, date: str, strict: bool = False) -> int:
    argv = [
        "run",
        "--watchlist",
        str(workspace["watchlist"]),
        "--out",
        str(workspace["out"]),
        "--fetch-fixture",
        str(fixture),
        "--date",
        date,
        "--sleep",
        "0",
    ]
    if strict:
        argv.append("--strict")
    return watch.main(argv)


def _snapshot(workspace: dict[str, Path], date: str) -> dict:
    return json.loads((workspace["out"] / "snapshots" / f"{date}.json").read_text(encoding="utf-8"))


def _entry(snapshot: dict, label: str) -> dict:
    return next(e for e in snapshot["entries"] if e["label"] == label)


def _revised_fixture(tmp: Path, revision: str, issue_date: str) -> Path:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    detail_url = watch.detail_url("fixture-uuid-0001")
    data["responses"][detail_url]["linkedSscp"]["revisionNumber"] = revision
    data["responses"][detail_url]["linkedSscp"]["issueDate"] = issue_date
    path = tmp / "fixture_v2.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_url_builders_match_measured_api_shape():
    url = watch.search_url("ONE Snare", 2)
    assert url == (
        "https://ec.europa.eu/tools/eudamed/api/devices/udiDiData"
        "?page=2&pageSize=50&size=50&iso2Code=en&languageIso2Code=en&tradeName=ONE%20Snare"
    )
    assert watch.detail_url("abc") == (
        "https://ec.europa.eu/tools/eudamed/api/devices/basicUdiData/udiDiData/abc?languageIso2Code=en"
    )
    assert watch.PAGE_SIZE == 50
    assert watch.USER_AGENT == "ClinicOps-eudamed-watch/1.0 (+https://clinicops.dk)"


def test_first_run_dedupes_filters_and_classifies(workspace):
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    snap = _snapshot(workspace, "2026-09-01")
    assert snap["tool"] == "eudamed_watch"
    assert snap["mode"] == "fixture"
    assert snap["sha256"] == watch.canonical_sha256(snap)

    stylet = _entry(snap, STYLET)
    # 6 rows returned, 1 filtered out by manufacturer_contains.
    assert stylet["rows_seen"] == 6
    assert stylet["rows_filtered_out_by_manufacturer"] == 1
    assert "FIXTURE-BUDI-STYLET-OTHER" not in stylet["devices"]
    assert stylet["total_elements_approximate"] == 6
    assert stylet["truncated_by_max_pages"] is False

    # 3 rows of one family collapse into one distinct device with a detail lookup.
    assert stylet["distinct_devices"] == 3
    family = stylet["devices"]["FIXTURE-BUDI-STYLET-MDR"]
    assert family["rows_collapsed"] == 3
    assert family["risk_class"] == "class-iii"
    assert family["risk_class_raw"] == "refdata.risk-class.class-iii"
    assert family["status"] == "on-the-market"
    assert family["classification"] == watch.CLS_LINKED
    assert family["detail_lookup_done"] is True
    assert family["linked_sscp"] == {
        "referenceNumber": "FIXTURE-SSCP-001",
        "revisionNumber": "1",
        "issueDate": "2026-01-15",
        "validated": True,
        "inactive": False,
    }
    assert family["legislation"] == "mdr"
    assert family["legacy_directive"] is False
    assert family["implantable"] is True
    assert family["sscp_expected"] is True
    assert family["nb_decision_reason"] == "approved"
    assert family["nb_decision_date"] == "2026-08-19"
    assert family["first_certificate_type"] == "technical-documentation"
    assert family["first_certificate_number"] is None
    assert family["certificates_count"] == 1
    assert family["srn_matches_expected"] is True

    legacy = stylet["devices"]["B-000000000000FIXTURE"]
    assert legacy["classification"] == watch.CLS_LEGACY
    assert legacy["detail_lookup_done"] is False
    assert legacy["linked_sscp"] is None
    assert legacy["sscp_expected"] is False

    pack = stylet["devices"]["FIXTURE-BUDI-STYLET-PACK"]
    assert pack["classification"] == watch.CLS_PR
    assert pack["srn_role"] == "PR"
    assert pack["detail_lookup_done"] is False
    assert pack["sscp_expected"] is False

    assert stylet["classification_counts"] == {
        watch.CLS_LEGACY: 1,
        watch.CLS_LINKED: 1,
        watch.CLS_PR: 1,
    }


def test_no_detail_lookup_for_legacy_or_pr_rows_and_only_one_per_family(workspace):
    fetcher = watch.FixtureFetcher(FIXTURE)
    entries = watch.load_watchlist(workspace["watchlist"])
    watch.build_snapshot(fetcher, entries, max_pages=5, snapshot_date="2026-09-01", watchlist_path="x")
    detail_calls = [u for u in fetcher.requested if "/basicUdiData/udiDiData/" in u]
    assert detail_calls[:2] == [
        watch.detail_url("fixture-uuid-0001"),  # one lookup for the 3-row family
        watch.detail_url("fixture-uuid-0101"),  # snare (fails: absent from fixture)
    ]
    assert detail_calls.count(watch.detail_url("fixture-uuid-0001")) == 1
    assert watch.detail_url("fixture-uuid-0004") not in fetcher.requested  # legacy B-
    assert watch.detail_url("fixture-uuid-0005") not in fetcher.requested  # PR role
    assert watch.detail_url("fixture-uuid-0006") not in fetcher.requested  # filtered out


def test_failures_are_recorded_not_swallowed(workspace):
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    snap = _snapshot(workspace, "2026-09-01")
    kinds = {(f["entry_label"], f["kind"]) for f in snap["failures"]}
    assert (OPRA, "search_page") in kinds
    assert (SNARE, "detail_lookup") in kinds
    opra = _entry(snap, OPRA)
    assert opra["pages_failed"] == 1
    assert opra["pages_fetched"] == 0
    assert opra["devices"] == {}
    snare = _entry(snap, SNARE)
    assert snare["devices"]["FIXTURE-BUDI-SNARE-MDR"]["classification"] == watch.CLS_LOOKUP_FAILED
    latest = (workspace["out"] / "LATEST.md").read_text(encoding="utf-8")
    assert "HTTP 503" in latest
    assert "fixture has no response" in latest
    # strict mode surfaces failures through the exit code.
    assert _run(workspace, FIXTURE, "2026-09-01", strict=True) == 1


def test_second_snapshot_diff_detects_revision_change(workspace):
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    assert not (workspace["out"] / "diffs" / "2026-09-01.md").exists()
    v2 = _revised_fixture(workspace["tmp"], revision="2", issue_date="2026-09-20")
    assert _run(workspace, v2, "2026-10-01") == 0

    diff_md = (workspace["out"] / "diffs" / "2026-10-01.md").read_text(encoding="utf-8")
    assert "## SS(C)P link changes (1)" in diff_md
    assert "FIXTURE-BUDI-STYLET-MDR" in diff_md
    assert "revisionNumber, issueDate" in diff_md
    assert "revisionNumber=1" in diff_md and "revisionNumber=2" in diff_md
    assert "## New devices seen (0)" in diff_md
    assert "## Entered 'SS(C)P expected but absent'" in diff_md
    assert "## Left 'SS(C)P expected but absent' (0)" in diff_md
    assert "## Devices no longer seen (0)" in diff_md
    assert "## Status changes (0)" in diff_md

    old, new = _snapshot(workspace, "2026-09-01"), _snapshot(workspace, "2026-10-01")
    diff = watch.compute_diff(old, new)
    assert diff["sscp_changes"][0]["fields"] == ["revisionNumber", "issueDate"]
    assert old["sha256"] != new["sha256"]


def test_diff_command_and_gone_device_artefact_flag(workspace, capsys):
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    old_path = workspace["out"] / "snapshots" / "2026-09-01.json"
    old = json.loads(old_path.read_text(encoding="utf-8"))
    new = json.loads(json.dumps(old))
    new["snapshot_date"] = "2026-10-01"
    # Simulate the family vanishing after a failed page on the same entry.
    del _entry(new, STYLET)["devices"]["FIXTURE-BUDI-STYLET-MDR"]
    _entry(new, STYLET)["devices"]["B-000000000000FIXTURE"]["status"] = "no-longer-placed-on-the-market"
    new["failures"].append({"entry_label": STYLET, "kind": "search_page", "page": 1, "url": "x", "error": "HTTP 500"})
    new_path = workspace["tmp"] / "new.json"
    new_path.write_text(json.dumps(new), encoding="utf-8")

    assert watch.main(["diff", str(old_path), str(new_path)]) == 0
    out = capsys.readouterr().out
    assert "## Devices no longer seen (1)" in out
    assert "POSSIBLE EXTRACTION ARTEFACT" in out
    assert "## Status changes (1)" in out
    assert "on-the-market -> no-longer-placed-on-the-market" in out


def test_markdown_carries_limits_block(workspace):
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    v2 = _revised_fixture(workspace["tmp"], revision="2", issue_date="2026-09-20")
    assert _run(workspace, v2, "2026-10-01") == 0
    for path in (workspace["out"] / "LATEST.md", workspace["out"] / "diffs" / "2026-10-01.md"):
        text = path.read_text(encoding="utf-8")
        assert "## Standing limits" in text
        assert "Extraction date: 2026-10-01" in text
        assert "not a compliance, conformity or diligence statement" in text
        assert "unanchored substring" in text
        assert "not 'not registered'" in text
        assert "approximate" in text
        assert "not a finding that any obligation is unmet" in text
    snap = _snapshot(workspace, "2026-10-01")
    assert snap["limits"] == watch.STANDING_LIMITS


def test_refdata_prefix_normalisation():
    assert watch.normalise_code({"code": "refdata.risk-class.class-iii"}) == "class-iii"
    assert watch.raw_code({"code": "refdata.risk-class.class-iii"}) == "refdata.risk-class.class-iii"
    assert watch.normalise_code({"code": "refdata.device-model-status.on-the-market"}) == "on-the-market"
    assert watch.normalise_code({"code": "refdata.applicable-legislation.mdr"}) == "mdr"
    assert watch.normalise_code("CLASS_III") == "class_iii"  # bare strings tolerated
    assert watch.normalise_code(None) is None
    assert watch.normalise_code({"code": None}) is None
    assert watch.normalise_code({}) is None


def test_basic_udi_as_object_or_string():
    assert watch.basic_udi_code({"uuid": "x", "code": "4260102130101010001AJ", "type": "BASIC_UDI"}) == "4260102130101010001AJ"
    assert watch.basic_udi_code("4260102130101010001AJ") == "4260102130101010001AJ"
    assert watch.basic_udi_code(None) == ""
    assert watch.basic_udi_code({"code": None}) == ""


def test_real_palacos_shapes_parse(workspace):
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    snap = _snapshot(workspace, "2026-09-01")
    palacos = _entry(snap, PALACOS)
    device = palacos["devices"]["4260102130101010001AJ"]
    assert device["detail_basic_udi"] == "4260102130101010001AJ"
    assert "detail_basic_udi_mismatch" not in device
    assert device["detail_uuid"] != device["uuid"]  # detail carries its own uuid
    assert device["risk_class"] == "class-iii"
    assert device["status"] == "not-intended-for-eu-market"
    assert device["status_raw"] == "refdata.device-model-status.not-intended-for-eu-market"
    assert device["manufacturer_status"] == "active"
    assert device["linked_sscp"] == {
        "referenceNumber": "61339",
        "revisionNumber": "10",
        "issueDate": "2025-12-01",
        "validated": True,
        "inactive": False,
    }
    assert device["legislation"] == "mdr" and device["legacy_directive"] is False
    assert device["implantable"] is True
    assert device["sscp_expected"] is True
    assert device["classification"] == watch.CLS_LINKED
    # Zero-result query is recorded as 'not findable', not as a failure.
    cerament = _entry(snap, CERAMENT)
    assert cerament["rows_seen"] == 0 and cerament["devices"] == {}
    assert cerament["total_elements_approximate"] == 0
    assert cerament["pages_failed"] == 0
    assert not [f for f in snap["failures"] if f["entry_label"] == CERAMENT]


def test_sscp_expected_logic_and_legacy_directive(workspace):
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    snap = _snapshot(workspace, "2026-09-01")
    devices = _entry(snap, VARIANT)["devices"]

    class_i = devices["FIXTURE-BUDI-VARIANT-CLASS-I"]
    assert class_i["risk_class"] == "class-i" and class_i["implantable"] is False
    assert class_i["sscp_expected"] is False
    assert class_i["classification"] == watch.CLS_ABSENT
    assert class_i["certificates_count"] == 0 and class_i["first_certificate_type"] is None

    mdd = devices["FIXTURE-BUDI-VARIANT-MDD-III"]
    assert mdd["risk_class"] == "class-iii" and mdd["implantable"] is True
    assert mdd["legislation"] == "mdd" and mdd["legacy_directive"] is True
    assert mdd["sscp_expected"] is False
    assert mdd["classification"] == watch.CLS_ABSENT

    implantable = devices["FIXTURE-BUDI-VARIANT-IIB-IMPL"]
    assert implantable["risk_class"] == "class-iib" and implantable["implantable"] is True
    assert implantable["sscp_expected"] is True
    assert implantable["classification"] == watch.CLS_EXPECTED_ABSENT

    class_iii = devices["FIXTURE-BUDI-VARIANT-III-NOSSCP"]
    assert class_iii["sscp_expected"] is True
    assert class_iii["classification"] == watch.CLS_EXPECTED_ABSENT

    assert _entry(snap, VARIANT)["classification_counts"] == {watch.CLS_ABSENT: 2, watch.CLS_EXPECTED_ABSENT: 2}
    latest = (workspace["out"] / "LATEST.md").read_text(encoding="utf-8")
    assert "## SS(C)P expected but absent in the public record" in latest
    assert "FIXTURE-BUDI-VARIANT-IIB-IMPL" in latest and "FIXTURE-BUDI-VARIANT-III-NOSSCP" in latest
    assert "FIXTURE-BUDI-VARIANT-CLASS-I" not in latest.split("## SS(C)P expected but absent")[1].split("## Recorded failures")[0]


def test_sscp_expected_pure_function():
    base = {"basic_udi": "X", "srn_role": "MF", "risk_class": "class-iii", "implantable": False, "legislation": "mdr", "legacy_directive": False}
    assert watch.sscp_expected(base) is True
    assert watch.sscp_expected({**base, "risk_class": "class-i"}) is False
    assert watch.sscp_expected({**base, "risk_class": "class-iib", "implantable": True}) is True
    assert watch.sscp_expected({**base, "basic_udi": "B-1"}) is False
    assert watch.sscp_expected({**base, "srn_role": "PR"}) is False
    assert watch.sscp_expected({**base, "legislation": "mdd", "legacy_directive": True}) is False
    assert watch.sscp_expected({**base, "legislation": "ivdr"}) is False
    assert watch.sscp_expected({**base, "legislation": None}) is False


def test_diff_reports_entering_expected_but_absent(workspace):
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["responses"][watch.detail_url("fixture-uuid-0001")]["linkedSscp"] = None
    v2 = workspace["tmp"] / "fixture_nolink.json"
    v2.write_text(json.dumps(data), encoding="utf-8")
    assert _run(workspace, v2, "2026-10-01") == 0
    diff_md = (workspace["out"] / "diffs" / "2026-10-01.md").read_text(encoding="utf-8")
    assert "## Entered 'SS(C)P expected but absent' (public record shows no link; not a compliance finding) (1)" in diff_md
    assert "`FIXTURE-BUDI-STYLET-MDR`" in diff_md
    assert "sscp_linked -> sscp_expected_but_absent" in diff_md


def test_seed_watchlist_is_valid_and_filtered():
    entries = watch.load_watchlist(SEED_WATCHLIST)
    assert len(entries) == 14
    assert all(e["manufacturer_contains"] for e in entries)
    assert {e["trade_name_query"] for e in entries} >= {"Stylet", "ONE Snare", "OPRA", "t:slim"}


def test_watchlist_validation_errors(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"entries": [{"label": "x"}]}), encoding="utf-8")
    with pytest.raises(ValueError):
        watch.load_watchlist(bad)
    dup = tmp_path / "dup.json"
    dup.write_text(
        json.dumps({"entries": [{"label": "a", "trade_name_query": "q"}, {"label": "a", "trade_name_query": "r"}]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        watch.load_watchlist(dup)


def test_pagination_honours_max_pages_and_marks_truncation(tmp_path):
    rows = [
        {"uuid": f"u{i}", "basicUdi": f"BUDI-{i}", "manufacturerName": "Fixture Co", "manufacturerSrn": "DK-MF-000000009", "riskClass": {"code": "refdata.risk-class.class-i"}}
        for i in range(50)
    ]
    responses = {watch.search_url("Foo", p): {"content": rows, "totalElements": 999, "totalPages": 20} for p in range(3)}
    for i in range(50):
        responses[watch.detail_url(f"u{i}")] = {"linkedSscp": None}
    fixture = tmp_path / "pages.json"
    fixture.write_text(json.dumps({"responses": responses}), encoding="utf-8")
    fetcher = watch.FixtureFetcher(fixture)
    failures: list = []
    rows_out, meta = watch.fetch_search_rows(fetcher, {"label": "Foo", "trade_name_query": "Foo"}, 2, failures)
    assert len(rows_out) == 100
    assert meta["pages_fetched"] == 2
    assert meta["truncated_by_max_pages"] is True
    assert meta["total_elements_approximate"] == 999
    assert failures == []
