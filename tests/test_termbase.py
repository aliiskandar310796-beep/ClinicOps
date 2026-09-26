from __future__ import annotations

from pathlib import Path

import pytest

from clinicops_os.autonomy import termbase
from clinicops_os.autonomy.termbase import (
    HEADER,
    TermbaseError,
    merge,
    qa_report,
    read_rows,
    validate,
    validate_rows,
    write_rows,
)

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data" / "termbase" / "termbase_public.csv"


def row(**overrides: str) -> dict[str, str]:
    base = {
        "id": "TB-0001",
        "en_term": "medical device",
        "da_term": "medicinsk udstyr",
        "domain": "regulatory",
        "subdomain": "MDR definitions",
        "source_ref": "MDR 2017/745 Art. 2(1)",
        "source_url": "https://eur-lex.europa.eu/legal-content/DA/TXT/?uri=CELEX:32017R0745",
        "context_en": "'medical device' means any instrument",
        "context_da": "»medicinsk udstyr«: ethvert instrument",
        "status": "verified",
        "confidence": "0.95",
        "added_utc": "2026-09-25T00:00:00Z",
        "job_run": "test",
    }
    base.update(overrides)
    return base


def test_public_seed_file_is_valid_and_all_unverified() -> None:
    assert validate(PUBLIC) == []
    rows = read_rows(PUBLIC)
    assert len(rows) == 22
    assert {r["status"] for r in rows} == {"unverified-seed"}
    assert {r["confidence"] for r in rows} == {"0.4"}
    assert {r["job_run"] for r in rows} == {"seed-2026-09-25"}
    assert all(r["context_en"] == "" and r["context_da"] == "" for r in rows)
    assert PUBLIC.read_text(encoding="utf-8").splitlines()[0] == ",".join(HEADER)


def test_header_must_match_exactly(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    bad.write_text("id,en_term,da_term\nTB-0001,a,b\n", encoding="utf-8")
    errors = validate(bad)
    assert len(errors) == 1 and "header mismatch" in errors[0]
    with pytest.raises(TermbaseError, match="header mismatch"):
        read_rows(bad)
    with pytest.raises(TermbaseError, match="not found"):
        read_rows(tmp_path / "missing.csv")


def test_valid_row_passes() -> None:
    assert validate_rows([row()]) == []


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"id": "TB-001"}, "id must match"),
        ({"id": "XX-0001"}, "id must match"),
        ({"status": "approved"}, "status 'approved' not in"),
        ({"confidence": "1.5"}, "between 0 and 1"),
        ({"confidence": "abc"}, "between 0 and 1"),
        ({"confidence": "nan"}, "between 0 and 1"),
        ({"en_term": " "}, "en_term must not be empty"),
        ({"da_term": ""}, "da_term must not be empty"),
        ({"source_ref": ""}, "source_ref must not be empty"),
        ({"context_da": ""}, "both context_en and context_da"),
        ({"source_url": ""}, "verified rows need a source_url"),
        ({"source_url": "eur-lex.europa.eu"}, "must start with http"),
        ({"status": "unverified-seed", "confidence": "0.6", "context_en": "", "context_da": ""}, "<= 0.5"),
        ({"added_utc": "2026-09-25"}, "ISO 8601 UTC"),
    ],
)
def test_validation_edge_cases(overrides: dict[str, str], fragment: str) -> None:
    errors = validate_rows([row(**overrides)])
    assert any(fragment in error for error in errors), errors


def test_unverified_seed_without_contexts_is_fine_at_low_confidence() -> None:
    seed = row(status="unverified-seed", confidence="0.4", context_en="", context_da="")
    assert validate_rows([seed]) == []


def test_duplicate_ids_are_rejected() -> None:
    errors = validate_rows([row(), row(en_term="importer", da_term="importør")])
    assert any("duplicate id" in error for error in errors)


def test_wrong_column_count_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "cols.csv"
    path.write_text(",".join(HEADER) + "\nTB-0001,a,b\n", encoding="utf-8")
    errors = validate(path)
    assert errors and "expected 13 columns" in errors[0]


def test_merge_dedups_case_insensitively_and_reassigns_colliding_ids() -> None:
    master = [row(), row(id="TB-0002", en_term="importer", da_term="importør")]
    delta = [
        row(id="TB-0009", en_term="Medical Device", da_term="MEDICINSK UDSTYR"),  # duplicate
        row(id="TB-0002", en_term="distributor", da_term="distributør"),  # id collision
        row(id="TB-0010", en_term="notified body", da_term="bemyndiget organ"),
        row(id="", en_term="label", da_term="mærkning"),  # missing id
    ]
    result = merge(master, delta)
    assert result.added == 3
    assert result.skipped == 1
    ids = [r["id"] for r in result.rows]
    assert ids == ["TB-0001", "TB-0002", "TB-0003", "TB-0010", "TB-0011"]
    assert result.reassigned_ids["TB-0002"] == "TB-0003"
    assert validate_rows(result.rows) == []
    assert master[0]["id"] == "TB-0001", "merge must not mutate its inputs"


def test_merge_source_ref_is_part_of_the_key() -> None:
    master = [row()]
    delta = [row(id="TB-0002", source_ref="MDR 2017/745 Art. 2(1) ")]
    assert merge(master, delta).skipped == 1
    delta = [row(id="TB-0002", source_ref="IVDR 2017/746 Art. 2(2)")]
    assert merge(master, delta).added == 1


def test_qa_report_counts_and_flags_suspicious_rows(tmp_path: Path) -> None:
    rows = [
        row(),
        row(id="TB-0002", en_term="importer", da_term="importør", domain="actors"),
        row(id="TB-0003", en_term="CE", da_term="ce", status="candidate", confidence="0.5"),
        row(id="TB-0004", en_term="2017", da_term="2017", status="candidate", confidence="0.5"),
        row(id="TB-0005", en_term="x" * 81, da_term="y", status="candidate", confidence="0.5"),
        row(id="TB-0006", en_term="Medical device", da_term="Medicinsk udstyr"),
    ]
    path = tmp_path / "qa.csv"
    write_rows(path, rows)
    report = qa_report(path)
    assert report["rows"] == 6
    assert report["by_status"] == {"candidate": 3, "verified": 3}
    assert report["by_domain"] == {"actors": 1, "regulatory": 5}
    assert report["counts"]["duplicates"] == 1
    assert report["duplicates"][0]["ids"] == ["TB-0001", "TB-0006"]
    reasons = {(item["id"], item["reason"]) for item in report["suspicious"]}
    assert ("TB-0003", "identical en_term and da_term") in reasons
    assert ("TB-0004", "identical en_term and da_term") in reasons
    assert ("TB-0004", "term consists of digits only") in reasons
    assert ("TB-0005", "term longer than 80 characters") in reasons
    rendered = termbase.render_qa_report(report)
    assert "duplicates: 1" in rendered and "TB-0005" in rendered


def test_qa_flags_verified_without_url_after_validation_bypass(tmp_path: Path) -> None:
    path = tmp_path / "v.csv"
    write_rows(path, [row(source_url="")])
    report = qa_report(path)
    assert report["suspicious"] == [{"id": "TB-0001", "reason": "verified row without source_url"}]


def test_write_and_read_round_trip_with_commas_and_quotes(tmp_path: Path) -> None:
    tricky = row(
        da_term='overvågning, efter at "udstyret" er bragt i omsætning',
        context_en='"medical device" means, inter alia, any instrument',
    )
    path = tmp_path / "rt.csv"
    write_rows(path, [tricky])
    assert read_rows(path) == [tricky]


def test_cli_validate_merge_and_qa(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    master = tmp_path / "master.csv"
    delta = tmp_path / "delta.csv"
    merged = tmp_path / "merged.csv"
    write_rows(master, [row()])
    write_rows(
        delta,
        [row(id="TB-0001", en_term="importer", da_term="importør"), row(id="TB-0002")],
    )

    assert termbase.main(["validate", str(master)]) == 0
    assert termbase.main(["merge", str(master), str(delta), "--out", str(merged)]) == 0
    assert termbase.main(["validate", str(merged)]) == 0
    merged_rows = read_rows(merged)
    assert [r["id"] for r in merged_rows] == ["TB-0001", "TB-0002"]
    assert merged_rows[1]["en_term"] == "importer", "colliding id reassigned, duplicate skipped"
    assert termbase.main(["qa", str(merged)]) == 0
    assert termbase.main(["qa", str(merged), "--json"]) == 0

    bad = tmp_path / "bad.csv"
    write_rows(bad, [row(status="nonsense")])
    assert termbase.main(["validate", str(bad)]) == 2
    assert termbase.main(["qa", str(bad)]) == 2
    assert termbase.main(["merge", str(master), str(bad)]) == 2
    assert termbase.main([]) == 2
    out = capsys.readouterr().out
    assert "termbase valid" in out and "INVALID" in out and '"by_status"' in out
