"""WP-14: the non-EU manufacturer section is sourced and does not offer AR."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_section_is_sourced_and_does_not_offer_mandates() -> None:
    html = (ROOT / "docs" / "eu-mdr-regulatory-integrity.html").read_text(encoding="utf-8")
    assert 'id="outside-the-eu"' in html
    assert "CO-CLM-0023" in html and "not an authorised representative and does not offer mandates" in html
    assert "Article 11(1)" in html and "Article 31(1)" in html
    assert 'href="eu-authorised-representative"' in html and 'href="eudamed-transition"' in html
    claims = {json.loads(x)["id"]: json.loads(x) for x in (ROOT / "research" / "claims.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()}
    assert claims["CO-CLM-0023"]["status"] == "qualified" and "website" in claims["CO-CLM-0023"]["allowed_uses"]
