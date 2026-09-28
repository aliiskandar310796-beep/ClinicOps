from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "assessment-intake.html"


class FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "form":
            self.forms.append({key.lower(): value or "" for key, value in attrs})


def test_assessment_intake_is_browser_local_and_user_controlled() -> None:
    html = PAGE.read_text(encoding="utf-8")
    lower = html.lower()

    assert 'rel="canonical" href="https://clinicops.dk/assessment-intake"' in html
    assert "No form data is transmitted by this page." in html
    assert "patient-identifiable data" in lower
    assert 'maxlength="1200"' in html
    assert "transition-map-sample/" in html
    assert "readiness-score" in html
    assert "info@clinicops.dk" in html
    assert "mailto:info@clinicops.dk" in html
    assert "ClinicOps Regulatory Data Integrity Scope Brief" in html
    assert "Acquisition context (from the link you opened):" in html
    assert 'safeCampaignParam("src")' in html
    assert 'safeCampaignParam("campaign")' in html
    assert 'safeCampaignParam("segment")' in html

    forbidden = ("fetch(", "xmlhttprequest", "sendbeacon", "websocket")
    assert not any(token in lower for token in forbidden)

    parser = FormParser()
    parser.feed(html)
    assert len(parser.forms) == 1
    assert "action" not in parser.forms[0]
    assert "method" not in parser.forms[0]
