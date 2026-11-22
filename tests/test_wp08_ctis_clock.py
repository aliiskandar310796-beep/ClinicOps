"""WP-08: the CTIS initial-application clock page contract."""
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"


def test_page_is_local_and_governed() -> None:
    html = (DOCS / "ctis-clock.html").read_text(encoding="utf-8")
    assert "Content-Security-Policy" in html
    assert "<!-- claim-use: website -->" in html and "CO-CLM-0021" in html
    assert "not legal advice" in html.lower()
    assert "review due" in html.lower() or "Review due" in html


def test_linked_from_tools_and_hub_and_mapper_unlisted() -> None:
    assert 'href="ctis-clock"' in (DOCS / "tools.html").read_text(encoding="utf-8")
    assert 'href="ctis-clock"' in (DOCS / "ecoa.html").read_text(encoding="utf-8")
    assert 'href="regulatory-change-impact"' not in (DOCS / "tools.html").read_text(encoding="utf-8")
    assert "No longer listed" in (DOCS / "regulatory-change-impact.html").read_text(encoding="utf-8")
