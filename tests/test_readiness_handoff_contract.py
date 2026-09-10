"""Contract for the browser-local Readiness Score → assessment-brief handoff.

The handoff must stay strictly browser-local: an explicit user click writes a
small sessionStorage payload (score, band, gap list) on the readiness page,
and the assessment-intake page consumes it one-shot. Neither side may gain a
network submission path, and the two pages must agree on the storage key so
the handoff cannot silently break when one side is edited.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "docs" / "readiness-score.html"
INTAKE = ROOT / "docs" / "assessment-intake.html"

HANDOFF_KEY = "clinicops.readiness.handoff"
FORBIDDEN_NETWORK = ("fetch(", "xmlhttprequest", "sendbeacon", "websocket")


def test_readiness_page_offers_explicit_continue_to_brief() -> None:
    html = READINESS.read_text(encoding="utf-8")

    assert 'id="continue-brief"' in html
    assert 'href="assessment-intake.html"' in html
    # The write happens on the explicit continue click, not automatically.
    assert "addEventListener('click'" in html
    assert HANDOFF_KEY in html
    # The carried payload is disclosed to the user in plain copy.
    assert "Nothing is sent to ClinicOps" in html


def test_both_pages_agree_on_handoff_key() -> None:
    assert HANDOFF_KEY in READINESS.read_text(encoding="utf-8")
    assert HANDOFF_KEY in INTAKE.read_text(encoding="utf-8")


def test_intake_consumes_handoff_one_shot() -> None:
    html = INTAKE.read_text(encoding="utf-8")
    assert "sessionStorage.getItem" in html
    assert "sessionStorage.removeItem" in html


def test_handoff_adds_no_network_path_to_either_page() -> None:
    for page in (READINESS, INTAKE):
        lower = page.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN_NETWORK:
            assert token not in lower, f"{page.name} must stay local-only: {token}"
