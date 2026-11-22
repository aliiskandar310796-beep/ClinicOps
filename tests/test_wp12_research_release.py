"""WP-12: research pages carry cite-as, data policy, corrections and the reuse note."""
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"


def test_research_page_has_cite_data_and_corrections() -> None:
    html = (DOCS / "research.html").read_text(encoding="utf-8")
    assert 'id="cite-and-correct"' in html
    for phrase in ("Cite as", "fewer than 10", "records differ", "info@clinicops.dk", "8 September 2026", "14 November 2026"):
        assert phrase in html, phrase
    assert "non-compliant" in html  # only in the sentence that says the note never says it


def test_primary_sources_has_bounded_reuse_note() -> None:
    html = (DOCS / "primary-sources.html").read_text(encoding="utf-8")
    assert 'id="data-licence"' in html
    assert "not legal advice" in html and "only aggregates are published" in html
