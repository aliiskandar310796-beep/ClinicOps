from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _read(rel: str) -> str:
    return (DOCS / rel).read_text(encoding="utf-8")


def test_ar_page_states_no_ar_service_and_no_registry_identity() -> None:
    html = _read("eu-authorised-representative.html")
    assert "not an authorised representative" in html
    assert "PRRC" in html
    for token in ("ES-AR", "Iskandar", "EU AR scoping request", "in Spain"):
        assert token not in html, token


def test_ar_page_is_not_offered_as_a_service_elsewhere() -> None:
    for rel in ("contact.html", "llms.txt"):
        text = _read(rel)
        assert "ES-AR-000060462" not in text, rel
        assert "authorised representation by the registered Spanish operator" not in text, rel
        assert "Registered in Spain" not in text, rel


def test_privacy_notice_matches_current_practice() -> None:
    html = _read("privacy-notice/index.html")
    assert "Gumroad" not in html
    assert "Spain (self-employed, serving Denmark and the EU)" in html
    assert "AEPD" in html and "Datatilsynet" in html
    assert "Egedalsv" not in html and "Kokkedal" not in html
    assert "do not send unsolicited email or direct messages to organisations established in Denmark" in html
    assert "sender ikke uopfordret e-mail" in html


def test_eudamed_page_carries_the_dated_why_now_with_registry_entry() -> None:
    html = _read("eudamed-transition.html")
    assert "27 November 2026" in html
    assert "CO-CLM-0020" in html
    claims = [json.loads(line) for line in (ROOT / "research" / "claims.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    entry = next(c for c in claims if c["id"] == "CO-CLM-0020")
    assert entry["status"] == "qualified"
    assert "website" in entry["allowed_uses"]
    assert entry["limitations"]
