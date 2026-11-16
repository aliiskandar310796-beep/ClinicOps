from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "assessment-intake.html"


class FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, str]] = []
        self.required: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "form":
            self.forms.append(values)
        if tag.lower() in {"select", "input", "textarea"} and "required" in values and values.get("type") != "checkbox":
            self.required.append(values.get("id", ""))


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
    # Title renamed from "ClinicOps Regulatory Data Integrity Scope Brief" on 2026-11-16: the
    # brief now has a door for eCOA and Denmark as well as device records, so a
    # device-only title would mislabel two of the four doors (lens 19, section 6).
    assert "ClinicOps Scope Brief" in html
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


def test_intake_asks_four_required_fields_and_no_qualification_questions() -> None:
    """Lens 19 section 6: budget, buying posture and evidence start are
    qualification fields for ClinicOps, so they move to the reply."""
    html = PAGE.read_text(encoding="utf-8")
    parser = FormParser()
    parser.feed(html)
    assert parser.required == ["door", "org", "timing", "notes"]
    assert 'id="door"' in html
    for door in ("devices", "ecoa", "denmark", "unsure"):
        assert f'<option value="{door}">' in html, door
    for removed in ('id="budget"', 'id="buying"', 'id="evidence"', "Budget range:", "Buying posture:"):
        assert removed not in html, removed
    assert 'maxlength="800"' in html
    # no fixed-scope quote option while no priced page is published
    assert "fixed-scope quote" not in html.lower()


def test_intake_presets_map_every_legacy_workstream_to_a_real_option() -> None:
    """The flat preset map stays machine-checkable (scripts/validate_internal_links.py
    reads it); the door is derived from the optgroup that holds the option."""
    html = PAGE.read_text(encoding="utf-8")
    presets = json.loads(re.search(r'presets=(\{"[^}]+\})', html).group(1))
    for preset in ("trial-change", "clinic-ops", "ctis", "coa", "translation", "sdea", "integrity-review", "danish-pv"):
        assert preset in presets, preset
    select = re.search(r'<select id="workstream"[^>]*>(.*?)</select>', html, re.DOTALL).group(1)
    door_of: dict[str, str] = {}
    for door, body in re.findall(r'<optgroup label="[^"]*" data-door="([a-z]+)">(.*?)</optgroup>', select, re.DOTALL):
        for option in re.findall(r"<option>([^<]*)</option>", body):
            door_of[option] = door
    assert all(label in door_of for label in presets.values()), sorted(set(presets.values()) - set(door_of))
    # eCOA presets land on the eCOA door, not on "Other / mixed"
    for slug in ("trial-change", "clinic-ops", "ctis", "coa"):
        assert door_of[presets[slug]] == "ecoa", slug
    for slug in ("translation", "sdea", "danish-pv", "denmark-market-access"):
        assert door_of[presets[slug]] == "denmark", slug
    assert presets["trial-change"] == "eCOA delivery planning"
    assert 'params.get("door")' in html


def test_intake_mailto_is_length_capped_and_the_address_is_visible() -> None:
    html = PAGE.read_text(encoding="utf-8")
    assert "MAILTO_URL_CAP=2000" in html
    assert "url.length>MAILTO_URL_CAP" in html
    assert 'id="target"' in html and "Send to <strong>info@clinicops.dk</strong>" in html
    assert "If your email app does not open, copy the brief and send it to info@clinicops.dk." in html
    assert "This opens an email in your own mail app. Nothing is sent to ClinicOps until you send it." in html
    assert "personally" not in html.lower()
    # Danish letters survive: the cap is measured on the encoded URL, not on characters
    assert "encodeURIComponent(brief)" in html


def test_intake_reads_the_generalised_handoff_one_shot() -> None:
    html = PAGE.read_text(encoding="utf-8")
    assert 'HANDOFF_KEY="clinicops.handoff"' in html
    assert "removeItem(HANDOFF_KEY)" in html
    for field in ("tool", "summary", "at"):
        assert f"data.{field}" in html, field
    assert "3600000" in html  # same one-hour freshness window as before
