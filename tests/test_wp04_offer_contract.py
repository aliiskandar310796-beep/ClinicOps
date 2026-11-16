from __future__ import annotations

from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"


def _read(name: str) -> str:
    return (DOCS / name).read_text(encoding="utf-8")


def test_pilot_page_states_acceptance_changes_stop_and_handover() -> None:
    html = _read("what-a-pilot-looks-like.html")
    for needle in ("How each deliverable is accepted", "Changes, stops and hand-over", "Change requests", "One stage gate", "Hand-over"):
        assert needle in html, needle
    for deliverable in ("Source register", "Exception queue", "Closure packet", "Machine-readable export"):
        assert deliverable in html, deliverable


def test_intake_collects_buying_signals_without_publishing_a_price() -> None:
    html = _read("assessment-intake.html")
    for field_id in ("budget", "sample", "owner", "driver", "constraints"):
        assert f'id="{field_id}"' in html, field_id
    for label in ("Budget range:", "Sample first:", "Decision owner (role):", "Deadline driver:", "Constraints and tolerance:"):
        assert label in html, label
    # the budget select is an intake signal; no price is published on offer pages
    for page in ("services.html", "what-a-pilot-looks-like.html"):
        assert "EUR 2,400" not in _read(page)


def test_intake_optional_fields_are_not_required() -> None:
    html = _read("assessment-intake.html")
    for field_id in ("budget", "sample", "owner", "driver", "constraints"):
        tag = html.split(f'id="{field_id}"', 1)[1].split(">", 1)[0]
        assert "required" not in tag, field_id
