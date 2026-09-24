from __future__ import annotations

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "pipeline_report", Path(__file__).resolve().parent.parent / "scripts" / "pipeline_report.py"
)
pr = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(pr)

HEADER = "deal_id,evidence_level,evidence_ref,human_interaction,simulated\n"


def _write(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path


def test_missing_files_report_no_evidence(tmp_path):
    out = pr.build_report(tmp_path / "a.csv", tmp_path / "b.csv")
    assert out.count("NO EVIDENCE YET") == 2


def test_header_only_files_report_no_evidence(tmp_path):
    a = _write(tmp_path / "a.csv", HEADER)
    b = _write(tmp_path / "b.csv", HEADER)
    assert pr.build_report(a, b).count("NO EVIDENCE YET") == 2


def test_real_pipeline_header_is_only_header():
    assert len(pr.read_rows(pr.PIPELINE)) == 0


def test_counts_by_level(tmp_path):
    body = HEADER + "D1,E2,,false,false\nD2,E3,,false,false\nD3,E4,ref1,true,false\n"
    counts, refused = pr.classify(pr.read_rows(_write(tmp_path / "p.csv", body)))
    assert counts["E2"] == 1 and counts["E3"] == 1 and counts["E4"] == 1
    assert refused == []


def test_simulated_row_rejected(tmp_path):
    body = HEADER + "D1,E5,ref,true,true\nD2,E1,,false,false\n"
    counts, refused = pr.classify(pr.read_rows(_write(tmp_path / "p.csv", body)))
    assert counts["E5"] == 0 and counts["E1"] == 1
    assert any("simulated" in m for m in refused)


def test_only_simulated_rows_still_no_evidence(tmp_path):
    p = _write(tmp_path / "p.csv", HEADER + "D1,E6,ref,true,true\n")
    out = pr.build_report(tmp_path / "none.csv", p)
    assert out.count("NO EVIDENCE YET") == 2
    assert "REFUSED" in out


def test_e4_requires_human_and_ref(tmp_path):
    body = HEADER + "D1,E4,ref,false,false\nD2,E4,,true,false\n"
    counts, refused = pr.classify(pr.read_rows(_write(tmp_path / "p.csv", body)))
    assert counts["E4"] == 0 and len(refused) == 2


def test_invalid_level_refused(tmp_path):
    counts, refused = pr.classify(pr.read_rows(_write(tmp_path / "p.csv", HEADER + "D1,banana,,,\n")))
    assert not counts and refused
