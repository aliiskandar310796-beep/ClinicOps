"""Contract tests for the two QA/RA sanitized-prototype tools shipped 2026-09-17.

These pages are public demonstrations of method under the progression rule
(learn -> internal schema -> sanitized prototype -> design partner -> public
offer). The contract they must keep:

- they present themselves as sanitized prototypes, never as delivered work;
- they carry the compliance boundary explicitly;
- their intake handoffs use preset slugs the intake page actually knows;
- their fictional fixtures stay labeled fictional.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

IMPACT = DOCS / "regulatory-change-impact.html"
CONSISTENCY = DOCS / "technical-file-consistency.html"
INTAKE = DOCS / "assessment-intake.html"


def _intake_presets() -> dict[str, str]:
    match = re.search(r'presets=({"[^}]+})', INTAKE.read_text(encoding="utf-8"))
    assert match, "intake preset map not found"
    return json.loads(match.group(1))


def test_pages_exist_with_canonical_identity() -> None:
    impact = IMPACT.read_text(encoding="utf-8")
    consistency = CONSISTENCY.read_text(encoding="utf-8")

    assert '<link rel="canonical" href="https://clinicops.dk/regulatory-change-impact.html">' in impact
    assert "<title>Regulatory Change Impact Mapper | ClinicOps</title>" in impact
    assert '<link rel="canonical" href="https://clinicops.dk/technical-file-consistency.html">' in consistency
    assert "<title>Technical File Consistency Check | ClinicOps</title>" in consistency


def test_pages_keep_the_sanitized_prototype_boundary() -> None:
    for page in (IMPACT, CONSISTENCY):
        html = page.read_text(encoding="utf-8")
        lower = html.lower()
        assert "sanitized" in lower, page.name
        assert "not a compliance determination" in lower, page.name
        assert "privacy-notice/" in html, page.name
        # The progression rule: a prototype never claims delivered breadth.
        for banned in ("proven", "certified", "we manage", "track record"):
            assert banned not in lower, f"{page.name}: banned claim word {banned!r}"


def test_intake_presets_cover_both_tools() -> None:
    presets = _intake_presets()
    assert presets.get("regulatory-change-impact") == "Regulatory change impact mapping"
    assert presets.get("technical-file-consistency") == (
        "Technical documentation consistency"
    )

    impact = IMPACT.read_text(encoding="utf-8")
    consistency = CONSISTENCY.read_text(encoding="utf-8")
    assert "assessment-intake.html?workstream=regulatory-change-impact" in impact
    assert "assessment-intake.html?workstream=technical-file-consistency" in consistency


def test_impact_mapper_rule_table_is_complete() -> None:
    impact = IMPACT.read_text(encoding="utf-8")
    for ct in (f"ct-0{i}" for i in range(1, 9)):
        assert f'"{ct}"' in impact, f"change category {ct} missing from rule table"
    # deadline band must never be presented as a regulatory-risk score
    assert "not a regulatory-risk score" in impact


def test_consistency_check_keeps_fictional_fixture_and_mod10() -> None:
    consistency = CONSISTENCY.read_text(encoding="utf-8")
    assert "Nyrelia" in consistency
    assert "invented for demonstration" in consistency
    assert "mod10ok" in consistency
    # verbatim values are preserved; the tool never picks the correct value
    assert "never says which value is correct" in consistency


def test_tools_page_links_both_prototypes() -> None:
    tools = (DOCS / "tools.html").read_text(encoding="utf-8")
    assert 'href="regulatory-change-impact.html"' in tools
    assert 'href="technical-file-consistency.html"' in tools
