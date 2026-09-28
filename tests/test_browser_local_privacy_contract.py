"""Browser-local privacy/storage contract for public utilities.

These checks complement the real-browser Scanner network audit. They fail CI if
a browser-local utility gains a network primitive, external script/form target,
or unexpected persistent storage without an explicit architecture change.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

BROWSER_LOCAL = (
    "identifier-check.html",
    "integrity-check.html",
    "change-surface-mapper.html",
    "regulatory-change-impact.html",
    "technical-file-consistency.html",
    "readiness-score.html",
    "integrity-economics.html",
    "danish-pv-literature-register.html",
    "sdea-clause-checker.html",
    "danish-dhpc-checker.html",
    "assessment-intake.html",
    "integrity-scanner.html",
)

NETWORK_PRIMITIVES = ("fetch(", "xmlhttprequest", "sendbeacon", "websocket")


def _page_source(name: str) -> str:
    """The page plus every same-origin script it loads.

    Page logic may live in <script src="assets/..."> files (the Scanner's was
    moved out of an inline block on 2026-09-28 to get it off the mobile
    critical path), and those files are part of the same privacy boundary.
    Scanning only the HTML would silently stop covering them.
    """
    html = (DOCS / name).read_text(encoding="utf-8")
    parts = [html]
    for src in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE):
        if src.startswith(("http://", "https://", "//")):
            continue
        parts.append((DOCS / name).parent.joinpath(src).read_text(encoding="utf-8"))
    return "\n".join(parts)


def test_browser_local_utilities_have_no_submission_or_network_primitive() -> None:
    offenders: list[str] = []
    for name in BROWSER_LOCAL:
        html = _page_source(name)
        lower = html.lower()
        for token in NETWORK_PRIMITIVES:
            if token in lower:
                offenders.append(f"{name}: {token}")
        if re.search(r'<script[^>]+src=["\']https?://', html, re.IGNORECASE):
            offenders.append(f"{name}: external script")
        if re.search(r'<form[^>]+action=["\']https?://', html, re.IGNORECASE):
            offenders.append(f"{name}: external form action")
    assert not offenders, "browser-local privacy boundary changed: " + ", ".join(offenders)


def test_persistent_storage_is_mapping_profiles_only() -> None:
    scanner = _page_source("integrity-scanner.html")
    assert 'const PROF_KEY="clinicops.scanner.mappingProfiles"' in scanner
    assert "localStorage.setItem(PROF_KEY" in scanner
    scrubbed = scanner.replace("localStorage.getItem(PROF_KEY)", "").replace(
        "localStorage.setItem(PROF_KEY", ""
    )
    assert "localStorage" not in scrubbed

    for name in BROWSER_LOCAL:
        if name == "integrity-scanner.html":
            continue
        html = _page_source(name)
        assert "localStorage" not in html, f"{name}: unexpected persistent storage"


def test_ephemeral_handoffs_are_session_storage_only() -> None:
    mapper = (DOCS / "change-surface-mapper.html").read_text(encoding="utf-8")
    readiness = (DOCS / "readiness-score.html").read_text(encoding="utf-8")
    intake = (DOCS / "assessment-intake.html").read_text(encoding="utf-8")
    assert "sessionStorage" in mapper
    assert "sessionStorage" in readiness
    assert "sessionStorage" in intake
    assert "removeItem(HANDOFF_KEY)" in intake
