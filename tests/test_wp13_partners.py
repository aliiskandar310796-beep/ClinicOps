"""WP-13: partner page rules and the paused specialist form."""
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"


def test_partner_page_states_the_rules() -> None:
    html = (DOCS / "expert-network.html").read_text(encoding="utf-8")
    assert "<title>Working with partners | ClinicOps</title>" in html
    for phrase in ("No silent subcontracting", "NDA first", "One accountable owner", "Inbound only", "Sample scope (fictional)"):
        assert phrase in html, phrase
    # A price would read "EUR 500", "500 EUR", a euro sign or an entity. The registry stamp
    # legitimately names "EUR-Lex" as a source, so the bare token is not the test.
    assert not re.search(r"\bEUR\s?\d|\d\s?EUR\b|&euro;|\u20ac", html), "no price before cover or a signed cap"


def test_interest_form_is_paused_and_noindex() -> None:
    html = (DOCS / "expert-network-interest.html").read_text(encoding="utf-8")
    assert 'name="robots" content="noindex,follow"' in html
    assert 'id="interest"' not in html and 'id="draft"' not in html
    assert "paused" in html.lower()
