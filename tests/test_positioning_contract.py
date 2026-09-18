"""Positioning contract (2026-09-18 repositioning).

The public site presents ONE company: EU MedTech Regulatory Data Integrity.
These tests pin the repositioning so a later edit cannot quietly re-broaden
the public architecture or reintroduce banned claim language. Source of
truth: 01_STRATEGY/POSITIONING_2026-09-18_REGULATORY_DATA_INTEGRITY.md.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

# Broad Ops categories archived from the public architecture. They may keep
# living inside the intake form's option list (form granularity, not
# positioning), but must not reappear as named categories in page copy.
ARCHIVED_CATEGORIES = ("TrialOps", "QualityOps", "Clinical AI Ops", "LabOps")

# Words the validation gates reserve until external evidence exists.
BANNED_VALIDATION_WORDS = ("production-proven", "market-tested", "battle-tested")


def _pages() -> list[Path]:
    return [p for p in DOCS.glob("*.html") if p.name not in {"404.html", "clinical-operations.html"}]


def test_homepage_states_the_category_and_flagship() -> None:
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    assert "EU MedTech Regulatory Data Integrity" in html
    assert "Regulatory Change Integrity Review" in html
    assert 'href="integrity-scanner.html"' in html
    # no black-box score on the primary journey
    assert "readiness-score" not in html


def test_primary_navigation_is_simplified() -> None:
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    nav = re.search(r'<nav class="primary".*?</nav>', html, re.DOTALL)
    assert nav
    links = re.findall(r"<a ", nav.group(0))
    assert len(links) <= 7, "primary navigation grew beyond 7 items"
    for label in ("Solution", "Use cases", "Research", "Tools"):
        assert f">{label}</a>" in nav.group(0)


def test_broad_ops_categories_stay_archived() -> None:
    offenders: list[str] = []
    for page in _pages():
        html = page.read_text(encoding="utf-8")
        for cat in ARCHIVED_CATEGORIES:
            if cat in html:
                offenders.append(f"{page.name}: {cat}")
    assert not offenders, "archived Ops category on public page: " + ", ".join(offenders)


LEGACY_IDENTITY_PHRASES = (
    "Danish-Led, EU-Wide Clinical Operations",
    "clinical operations practice",
    "clinic operations",
    "Clinical Ops",
)


def test_head_metadata_carries_no_legacy_identity() -> None:
    """Titles, descriptions, OG and JSON-LD must never resurrect the old
    multi-lane identity — a smoke marker once protected the OLD About/Contact
    titles, so this pins the head of every canonical page (QA Cycle 3 P0A)."""
    offenders: list[str] = []
    for page in _pages():
        html = page.read_text(encoding="utf-8")
        head = html.split("</head>", 1)[0]
        for phrase in LEGACY_IDENTITY_PHRASES:
            if phrase.lower() in head.lower():
                offenders.append(f"{page.name}: {phrase}")
    assert not offenders, "legacy identity in page head: " + ", ".join(offenders)


def test_live_smoke_markers_carry_no_legacy_identity() -> None:
    checker = (ROOT / "scripts" / "check_live_site.py").read_text(encoding="utf-8")
    assert "Clinical Operations" not in checker


def test_no_reserved_validation_language() -> None:
    offenders: list[str] = []
    for page in _pages():
        lower = page.read_text(encoding="utf-8").lower()
        for word in BANNED_VALIDATION_WORDS:
            if word in lower:
                offenders.append(f"{page.name}: {word}")
    assert not offenders, ", ".join(offenders)


def test_scanner_exists_with_both_modes_and_boundary() -> None:
    html = (DOCS / "integrity-scanner.html").read_text(encoding="utf-8")
    assert "<title>Regulatory Integrity Scanner | ClinicOps</title>" in html
    assert 'id="modeA"' in html and 'id="modeB"' in html
    for status in ("mismatch signal", "missing evidence", "requires qualified review"):
        assert status in html
    for banned in ("non-compliant", "compliance score"):
        assert banned not in html.lower()
    assert "privacy-notice/" in html


def test_flagship_page_is_reframed() -> None:
    html = (DOCS / "evidence-change-control-pack.html").read_text(encoding="utf-8")
    assert "<title>Regulatory Change Integrity Review | ClinicOps</title>" in html


def test_solution_page_is_flagship_first() -> None:
    html = (DOCS / "services.html").read_text(encoding="utf-8")
    for anchor in ('id="change-review"', 'id="portfolio-scan"', 'id="monitoring"'):
        assert anchor in html
    # one flagship, not three equal products
    assert "not a separate product" in html
    # PV is isolated from the flagship identity (lives on the Denmark page)
    assert 'id="danish-pv"' not in html
    denmark = (DOCS / "denmark-market-access.html").read_text(encoding="utf-8")
    assert 'id="danish-pv"' in denmark  # demand-evidenced lane stays discoverable


def test_use_cases_hub_routes_to_products() -> None:
    html = (DOCS / "use-cases.html").read_text(encoding="utf-8")
    assert "services.html#change-review" in html or "services.html#portfolio-scan" in html
    for page in ("eudamed-transition.html", "sscp-operations.html", "class-iii-transition.html", "denmark-market-access.html"):
        assert page in html
