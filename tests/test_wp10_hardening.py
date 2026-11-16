from __future__ import annotations

from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"
TOOLS = (
    "change-surface-mapper", "identifier-check", "integrity-check", "integrity-scanner",
    "regulatory-change-impact", "technical-file-consistency", "ecoa-delivery-workbench",
    "coa-type-finder", "ecoa-lead-time-planner", "ecoa-visit-burden", "danish-dhpc-checker",
    "danish-pv-literature-register", "sdea-clause-checker", "readiness-score", "integrity-economics",
)


def test_every_tool_page_blocks_network_calls_with_a_meta_csp() -> None:
    for slug in TOOLS:
        html = (DOCS / f"{slug}.html").read_text(encoding="utf-8")
        head = html.split("</head>", 1)[0]
        assert 'http-equiv="Content-Security-Policy"' in head, slug
        assert "connect-src 'none'" in head, slug
        assert "object-src 'none'" in head and "frame-src 'none'" in head, slug
        assert "https://" not in head.split('http-equiv="Content-Security-Policy" content="', 1)[1].split('"', 1)[0], slug


def test_every_tool_page_warns_against_personal_data() -> None:
    for slug in TOOLS:
        text = (DOCS / f"{slug}.html").read_text(encoding="utf-8").lower()
        assert "patient-identifiable" in text or "patient identifiable" in text or "personal data" in text, slug


def test_scanner_states_where_mapping_profiles_are_kept() -> None:
    html = (DOCS / "integrity-scanner.html").read_text(encoding="utf-8")
    assert "Profiles hold column names only" in html
