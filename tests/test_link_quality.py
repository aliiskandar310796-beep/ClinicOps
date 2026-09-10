from __future__ import annotations

from pathlib import Path

from clinicops_os.link_quality import extract_links, validate_internal_links


def test_extract_links_collects_anchor_hrefs() -> None:
    html = '<a href="a.html">A</a><a href="mailto:x@example.com">Mail</a>'
    assert extract_links(html) == ["a.html", "mailto:x@example.com"]


def test_validate_internal_links_accepts_relative_and_root_links(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(
        '<a href="about.html">About</a><a href="/">Home</a>', encoding="utf-8"
    )
    (tmp_path / "about.html").write_text(
        '<a href="index.html">Home</a>', encoding="utf-8"
    )
    assert validate_internal_links(tmp_path) == []


def test_validate_internal_links_reports_missing_target(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(
        '<a href="missing.html">Missing</a>', encoding="utf-8"
    )
    errors = validate_internal_links(tmp_path)
    assert len(errors) == 1
    assert "broken internal link" in errors[0]


def test_external_and_mailto_links_are_ignored(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(
        '<a href="https://example.com/x">External</a>'
        '<a href="mailto:info@clinicops.dk">Mail</a>',
        encoding="utf-8",
    )
    assert validate_internal_links(tmp_path) == []
