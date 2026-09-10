from pathlib import Path

from clinicops_os.conversion_quality import validate_conversion_paths

ROOT = Path(__file__).resolve().parents[1]


def test_production_conversion_paths_are_connected() -> None:
    assert validate_conversion_paths(ROOT / "docs") == []


def test_missing_required_conversion_link_is_reported(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "transition-map-sample").mkdir()
    (docs / "index.html").write_text(
        '<a href="assessment-intake.html">Assessment</a>', encoding="utf-8"
    )
    (docs / "tools.html").write_text(
        '<a href="transition-map-sample/">Sample</a>', encoding="utf-8"
    )
    (docs / "assessment-intake.html").write_text(
        '<a href="readiness-score.html">Readiness</a>', encoding="utf-8"
    )
    (docs / "readiness-score.html").write_text(
        '<a href="assessment-intake.html">Assessment</a>', encoding="utf-8"
    )
    (docs / "transition-map-sample" / "index.html").write_text(
        '<a href="/readiness-score.html">Readiness</a>', encoding="utf-8"
    )

    errors = validate_conversion_paths(docs)
    assert "index.html: missing high-intent path to transition-map-sample/" in errors
    assert (
        "assessment-intake.html: missing high-intent path to transition-map-sample/"
        in errors
    )
    assert (
        "transition-map-sample/index.html: missing high-intent path to "
        "/assessment-intake.html"
        in errors
    )
