"""WP-09: planner exports and DHPC save/load stay browser-local."""
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"


def test_planner_page_has_all_exports() -> None:
    html = (DOCS / "ecoa-lead-time-planner.html").read_text(encoding="utf-8")
    for ident in ("export-csv", "export-scenarios", "export-ics", "export-json"):
        assert f'id="{ident}"' in html


def test_dhpc_checker_saves_to_file_not_storage() -> None:
    html = (DOCS / "danish-dhpc-checker.html").read_text(encoding="utf-8")
    assert 'id="save"' in html and 'id="load"' in html and 'id="example"' in html
    assert 'aria-live="polite"' in html
    assert "localStorage" not in html and "sessionStorage" not in html
    assert "beforeunload" in html
