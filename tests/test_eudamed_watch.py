"""Offline tests for scripts/eudamed_watch.py.

All responses come from tests/fixtures/eudamed_fixture.json (fictional data
plus one real public-registry PALACOS row used as a realistic shape case).
No network access is used or permitted by these tests.

The committed outputs are anonymised: a core concern of this suite is that no
string identifying a manufacturer, device, trade name, identifier or SS(C)P
reference reaches the public snapshot, diff, LATEST.md or stdout/stderr.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "eudamed_watch.py"
FIXTURE = ROOT / "tests" / "fixtures" / "eudamed_fixture.json"
EXAMPLE_WATCHLIST = ROOT / "data" / "eudamed" / "watchlist.example.json"

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


def _identifying_strings() -> set[str]:
    """Every string from the test watchlist and fixture that identifies a
    manufacturer, device, trade name, identifier or SS(C)P reference."""
    out: set[str] = set()
    for entry in TEST_WATCHLIST["entries"]:
        out.add(entry["label"])
        out.add(entry["trade_name_query"])
        if entry.get("manufacturer_contains"):
            out.add(entry["manufacturer_contains"])
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for body in fixture["responses"].values():
        if not isinstance(body, dict):
            continue
        for row in body.get("content", []) if isinstance(body.get("content"), list) else []:
            for field in ("basicUdi", "tradeName", "manufacturerName", "primaryDi", "uuid"):
                if row.get(field):
                    out.add(str(row[field]))
        code = body.get("basicUdi")
        if isinstance(code, dict) and code.get("code"):
            out.add(str(code["code"]))
        sscp = body.get("linkedSscp")
        if isinstance(sscp, dict) and sscp.get("referenceNumber"):
            out.add(str(sscp["referenceNumber"]))
        if body.get("manufacturerName"):
            out.add(str(body["manufacturerName"]))
    return {s for s in out if len(s) >= 4}


@pytest.fixture
def workspace(tmp_path: Path) -> dict[str, Path]:
    watchlist = tmp_path / "watchlist.json"
    watchlist.write_text(json.dumps(TEST_WATCHLIST), encoding="utf-8")
    out = tmp_path / "eudamed"
    return {"watchlist": watchlist, "out": out, "tmp": tmp_path}


def _run(workspace, fixture: Path, date: str, strict: bool = False, full_out: Path | None = None) -> int:
    argv = [
        "run",
        "--watchlist", str(workspace["watchlist"]),
        "--out", str(workspace["out"]),
        "--fetch-fixture", str(fixture),
        "--date", date,
        "--sleep", "0",
    ]
    if strict:
        argv.append("--strict")
    if full_out is not None:
        argv += ["--full-out", str(full_out)]
    return watch.main(argv)


def _snapshot(workspace, date: str) -> dict:
    return json.loads((workspace["out"] / "snapshots" / f"{date}.json").read_text(encoding="utf-8"))


def _collect(fixture: Path = FIXTURE) -> dict:
    fetcher = watch.FixtureFetcher(fixture)
    entries = watch.load_watchlist_from(TEST_WATCHLIST)
    return watch.collect_full(fetcher, entries, max_pages=5, snapshot_date="2026-09-01"), fetcher


def _entry(full: dict, label: str) -> dict:
    return next(e for e in full["entries"] if e["label"] == label)


def _revised_fixture(tmp: Path, *, drop_link: bool = False, revision: str | None = None) -> Path:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    detail = data["responses"][watch.detail_url("fixture-uuid-0001")]
    if drop_link:
        detail["linkedSscp"] = None
    if revision is not None:
        detail["linkedSscp"]["revisionNumber"] = revision
    path = tmp / "fixture_v2.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# ------------------------------------------------------------ URL / parsing


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


def test_refdata_prefix_normalisation():
    assert watch.normalise_code({"code": "refdata.risk-class.class-iii"}) == "class-iii"
    assert watch.raw_code({"code": "refdata.risk-class.class-iii"}) == "refdata.risk-class.class-iii"
    assert watch.normalise_code({"code": "refdata.device-model-status.on-the-market"}) == "on-the-market"
    assert watch.normalise_code({"code": "refdata.applicable-legislation.mdr"}) == "mdr"
    assert watch.normalise_code("CLASS_III") == "class_iii"
    assert watch.normalise_code(None) is None
    assert watch.normalise_code({}) is None


def test_basic_udi_as_object_or_string():
    assert watch.basic_udi_code({"uuid": "x", "code": "4260102130101010001AJ"}) == "4260102130101010001AJ"
    assert watch.basic_udi_code("4260102130101010001AJ") == "4260102130101010001AJ"
    assert watch.basic_udi_code(None) == ""
    assert watch.basic_udi_code({"code": None}) == ""


# --------------------------------------------------- Extraction (full, local)


def test_collect_full_dedupes_filters_and_classifies():
    full, fetcher = _collect()
    stylet = _entry(full, STYLET)
    assert stylet["rows_seen"] == 6
    assert stylet["rows_filtered_out_by_manufacturer"] == 1
    assert "FIXTURE-BUDI-STYLET-OTHER" not in stylet["devices"]
    assert stylet["distinct_devices"] == 3

    family = stylet["devices"]["FIXTURE-BUDI-STYLET-MDR"]
    assert family["rows_collapsed"] == 3
    assert family["risk_class"] == "class-iii"
    assert family["classification"] == watch.CLS_LINKED
    assert family["linked_sscp"]["revisionNumber"] == "1"
    assert family["sscp_expected"] is True
    assert family["srn_matches_expected"] is True

    legacy = stylet["devices"]["B-000000000000FIXTURE"]
    assert legacy["classification"] == watch.CLS_LEGACY
    assert legacy["detail_lookup_done"] is False
    pack = stylet["devices"]["FIXTURE-BUDI-STYLET-PACK"]
    assert pack["classification"] == watch.CLS_PR
    assert pack["detail_lookup_done"] is False

    # exactly one detail lookup per distinct non-legacy, non-PR family
    detail_calls = [u for u in fetcher.requested if "/basicUdiData/udiDiData/" in u]
    assert detail_calls.count(watch.detail_url("fixture-uuid-0001")) == 1
    assert watch.detail_url("fixture-uuid-0004") not in fetcher.requested
    assert watch.detail_url("fixture-uuid-0005") not in fetcher.requested
    assert watch.detail_url("fixture-uuid-0006") not in fetcher.requested

    # real PALACOS shapes parse
    palacos = _entry(full, PALACOS)["devices"]["4260102130101010001AJ"]
    assert palacos["risk_class"] == "class-iii"
    assert palacos["linked_sscp"]["referenceNumber"] == "61339"
    assert palacos["legislation"] == "mdr" and palacos["implantable"] is True
    assert palacos["classification"] == watch.CLS_LINKED

    # sscp_expected variants incl. legacyDirective
    devices = _entry(full, VARIANT)["devices"]
    assert devices["FIXTURE-BUDI-VARIANT-CLASS-I"]["classification"] == watch.CLS_ABSENT
    mdd = devices["FIXTURE-BUDI-VARIANT-MDD-III"]
    assert mdd["legacy_directive"] is True and mdd["classification"] == watch.CLS_ABSENT
    assert devices["FIXTURE-BUDI-VARIANT-IIB-IMPL"]["classification"] == watch.CLS_EXPECTED_ABSENT
    assert devices["FIXTURE-BUDI-VARIANT-III-NOSSCP"]["classification"] == watch.CLS_EXPECTED_ABSENT

    # failures recorded, never swallowed
    kinds = {(f["entry_label"], f["kind"]) for f in full["failures"]}
    assert (OPRA, "search_page") in kinds
    assert (SNARE, "detail_lookup") in kinds


def test_sscp_expected_pure_function():
    base = {"basic_udi": "X", "srn_role": "MF", "risk_class": "class-iii", "implantable": False, "legislation": "mdr", "legacy_directive": False}
    assert watch.sscp_expected(base) is True
    assert watch.sscp_expected({**base, "risk_class": "class-i"}) is False
    assert watch.sscp_expected({**base, "risk_class": "class-iib", "implantable": True}) is True
    assert watch.sscp_expected({**base, "basic_udi": "B-1"}) is False
    assert watch.sscp_expected({**base, "srn_role": "PR"}) is False
    assert watch.sscp_expected({**base, "legislation": "mdd", "legacy_directive": True}) is False
    assert watch.sscp_expected({**base, "legislation": None}) is False


def test_pagination_honours_max_pages_and_marks_truncation(tmp_path):
    rows = [
        {"uuid": f"u{i}", "basicUdi": f"BUDI-{i}", "manufacturerName": "Fixture Co", "manufacturerSrn": "DK-MF-000000009", "riskClass": {"code": "refdata.risk-class.class-i"}}
        for i in range(50)
    ]
    responses = {watch.search_url("Foo", p): {"content": rows, "totalElements": 999, "totalPages": 20} for p in range(3)}
    fixture = tmp_path / "pages.json"
    fixture.write_text(json.dumps({"responses": responses}), encoding="utf-8")
    fetcher = watch.FixtureFetcher(fixture)
    failures: list = []
    rows_out, meta = watch.fetch_search_rows(fetcher, {"label": "Foo", "trade_name_query": "Foo"}, 2, failures)
    assert len(rows_out) == 100
    assert meta["pages_fetched"] == 2
    assert meta["truncated_by_max_pages"] is True
    assert failures == []


# ----------------------------------------------------- Anonymised public run


def test_public_outputs_contain_no_identifying_strings(workspace, capsys, monkeypatch):
    monkeypatch.setenv(watch.HMAC_KEY_ENV, "test-secret-key")
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    v2 = _revised_fixture(workspace["tmp"], drop_link=True)
    assert _run(workspace, v2, "2026-10-01") == 0
    captured = capsys.readouterr()

    texts = {
        "stdout": captured.out,
        "stderr": captured.err,
        "snapshot1": (workspace["out"] / "snapshots" / "2026-09-01.json").read_text(encoding="utf-8"),
        "snapshot2": (workspace["out"] / "snapshots" / "2026-10-01.json").read_text(encoding="utf-8"),
        "diff": (workspace["out"] / "diffs" / "2026-10-01.md").read_text(encoding="utf-8"),
        "latest": (workspace["out"] / "LATEST.md").read_text(encoding="utf-8"),
    }
    identifying = _identifying_strings()
    assert identifying  # sanity: the guard list is non-empty
    for where, text in texts.items():
        lower = text.lower()
        hits = [s for s in identifying if s.lower() in lower]
        assert not hits, f"identifying strings leaked into {where}: {hits}"


def test_snapshot_totals_and_failure_counts(workspace):
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    snap = _snapshot(workspace, "2026-09-01")
    assert snap["anonymisation"] == "aggregate"
    assert "devices" not in snap
    totals = snap["totals"]
    assert totals["entries_queried"] == 6
    assert totals["rows_seen"] == 6 + 1 + 0 + 1 + 0 + 4
    assert totals["rows_filtered_out_by_manufacturer"] == 1
    assert totals["distinct_devices"] == 3 + 1 + 1 + 4
    assert totals["entries_with_zero_rows"] == 2  # OPRA (failed page), CERAMENT (empty)
    assert totals["classification_counts"] == {
        watch.CLS_LEGACY: 1,
        watch.CLS_PR: 1,
        watch.CLS_LINKED: 2,
        watch.CLS_EXPECTED_ABSENT: 2,
        watch.CLS_ABSENT: 2,
        watch.CLS_LOOKUP_FAILED: 1,
    }
    assert snap["failures_recorded"] == 2
    assert snap["failure_counts"] == {"detail_lookup": 1, "search_page": 1}
    assert snap["sha256"] == watch.canonical_sha256(snap)
    # strict mode surfaces failures through the exit code
    assert _run(workspace, FIXTURE, "2026-09-01", strict=True) == 1


def test_hmac_keying_is_stable_and_opt_in(workspace, monkeypatch):
    assert watch.device_key("k", "BUDI-1") == watch.device_key("k", "BUDI-1")
    assert watch.device_key("k", "BUDI-1") != watch.device_key("k", "BUDI-2")
    assert watch.device_key("k", "BUDI-1") != watch.device_key("other", "BUDI-1")
    assert len(watch.device_key("k", "BUDI-1")) == 16

    monkeypatch.setenv(watch.HMAC_KEY_ENV, "stable-key")
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    snap1 = _snapshot(workspace, "2026-09-01")
    assert snap1["anonymisation"] == "aggregate+keyed"
    assert snap1["devices"]
    for key, record in snap1["devices"].items():
        assert len(key) == 16 and int(key, 16) >= 0
        assert set(record) == {"classification", "risk_class", "sscp_expected", "linked", "validated", "issue_year"}
    expected_key = watch.device_key("stable-key", "FIXTURE-BUDI-STYLET-MDR")
    assert snap1["devices"][expected_key]["classification"] == watch.CLS_LINKED
    assert snap1["devices"][expected_key]["issue_year"] == 2026

    # same key, second run: identical device keys
    assert _run(workspace, FIXTURE, "2026-10-01") == 0
    snap2 = _snapshot(workspace, "2026-10-01")
    assert set(snap1["devices"]) == set(snap2["devices"])


def test_keyed_diff_detects_device_change(workspace, monkeypatch):
    monkeypatch.setenv(watch.HMAC_KEY_ENV, "stable-key")
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    v2 = _revised_fixture(workspace["tmp"], drop_link=True)
    assert _run(workspace, v2, "2026-10-01") == 0
    diff_md = (workspace["out"] / "diffs" / "2026-10-01.md").read_text(encoding="utf-8")
    key = watch.device_key("stable-key", "FIXTURE-BUDI-STYLET-MDR")
    assert f"`{key}`" in diff_md
    assert "classification: sscp_linked -> sscp_expected_but_absent" in diff_md
    assert "sscp_linked: 2 -> 1" in diff_md
    assert "sscp_expected_but_absent: 2 -> 3" in diff_md


def test_aggregate_diff_without_hmac_reports_count_deltas_only(workspace, monkeypatch):
    monkeypatch.delenv(watch.HMAC_KEY_ENV, raising=False)
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    v2 = _revised_fixture(workspace["tmp"], drop_link=True)
    assert _run(workspace, v2, "2026-10-01") == 0
    diff_md = (workspace["out"] / "diffs" / "2026-10-01.md").read_text(encoding="utf-8")
    assert "aggregate-only" in diff_md
    assert "sscp_linked: 2 -> 1" in diff_md
    assert "sscp_expected_but_absent: 2 -> 3" in diff_md
    snap = _snapshot(workspace, "2026-10-01")
    assert "devices" not in snap


def test_v1_named_snapshot_never_feeds_keys_into_a_diff():
    v1 = {
        "snapshot_date": "2026-09-11",
        "entries": [
            {"pages_fetched": 1, "pages_failed": 0, "rows_seen": 5, "rows_filtered_out_by_manufacturer": 0,
             "distinct_devices": 2, "truncated_by_max_pages": False,
             "classification_counts": {"sscp_linked": 2}},
        ],
        "devices": {"REAL-BASIC-UDI-01": {"classification": "sscp_linked"}},
        "failures": [],
    }
    v2 = {"snapshot_date": "2026-10-01", "totals": watch.snapshot_totals(v1), "failures_recorded": 0, "devices": {}}
    diff = watch.compute_diff(v1, v2)
    assert diff["keyed_comparison"] is False  # non-HMAC keys are refused
    md = watch.render_diff_markdown(diff)
    assert "REAL-BASIC-UDI-01" not in md
    assert watch.snapshot_totals(v1)["classification_counts"] == {"sscp_linked": 2}


def test_full_out_writes_named_report_and_is_local_only(workspace):
    full_dir = workspace["tmp"] / "full"
    assert _run(workspace, FIXTURE, "2026-09-01", full_out=full_dir) == 0
    named = (full_dir / "2026-09-01_full.md").read_text(encoding="utf-8")
    assert "DO NOT PUBLISH" in named
    assert STYLET in named and PALACOS in named
    assert "FIXTURE-BUDI-STYLET-MDR" in named
    assert "4260102130101010001AJ" in named and "61339" in named
    assert "## SS(C)P expected but absent" in named
    assert "## Recorded failures" in named and "HTTP 503" in named
    assert (full_dir / "LATEST.md").exists()
    # the named report never lands in the committed output tree
    committed = [p.name for p in workspace["out"].rglob("*") if p.is_file()]
    assert "2026-09-01_full.md" not in committed
    # and data/eudamed/full/ is gitignored
    assert "data/eudamed/full/" in (ROOT / ".gitignore").read_text(encoding="utf-8")


def test_markdown_carries_limits_block(workspace):
    assert _run(workspace, FIXTURE, "2026-09-01") == 0
    v2 = _revised_fixture(workspace["tmp"], revision="2")
    assert _run(workspace, v2, "2026-10-01") == 0
    for path in (workspace["out"] / "LATEST.md", workspace["out"] / "diffs" / "2026-10-01.md"):
        text = path.read_text(encoding="utf-8")
        assert "## Standing limits" in text
        assert "Extraction date: 2026-10-01" in text
        assert "not a compliance, conformity or diligence statement" in text
        assert "unanchored substring" in text
        assert "not 'not registered'" in text
        assert "approximate" in text
        assert "name no manufacturer" in text


# ------------------------------------------------------------------ Watchlist


def test_example_watchlist_is_valid_and_fictional():
    entries = watch.load_watchlist(EXAMPLE_WATCHLIST)
    assert len(entries) == 2
    assert all(e["manufacturer_contains"] for e in entries)
    raw = EXAMPLE_WATCHLIST.read_text(encoding="utf-8")
    assert "FICTIONAL" in raw
    assert "not committed" in raw.lower() or "NOT committed" in raw


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
