"""WP-13: partner page rules and the paused specialist form."""
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"


def test_partner_page_states_the_rules() -> None:
    html = (DOCS / "expert-network.html").read_text(encoding="utf-8")
    assert "<title>Working with partners | ClinicOps</title>" in html
    for phrase in ("No silent subcontracting", "NDA first", "One accountable owner", "Inbound only", "Sample scope (fictional)"):
        assert phrase in html, phrase
    assert "EUR" not in html and "&euro;" not in html, "no price before cover or a signed cap"


def test_interest_form_is_paused_and_noindex() -> None:
    html = (DOCS / "expert-network-interest.html").read_text(encoding="utf-8")
    assert 'name="robots" content="noindex,follow"' in html
    assert 'id="interest"' not in html and 'id="draft"' not in html
    assert "paused" in html.lower()
