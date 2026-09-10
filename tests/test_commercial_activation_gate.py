from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "sales" / "commercial-activation-gate.md"


def _gate_text() -> str:
    return GATE.read_text(encoding="utf-8")


def test_standard_pilot_has_founder_independent_delegation_envelope() -> None:
    text = _gate_text()

    assert "## Standard paid-pilot delegation envelope" in text
    assert "zero Ali transaction-level decisions" in text
    assert "qualified, named human reviewer" in text
    assert "current controlled bundle schema" in text
    assert "`EXP-001`" in text


def test_non_standard_work_abstains_instead_of_seeking_ad_hoc_approval() -> None:
    text = _gate_text()

    assert "## Automatic abstention boundary" in text
    assert "NON-STANDARD — NOT ACTIVATED" in text
    assert "does not route them to Ali for ad hoc approval" in text
    assert "### Abstain / flag" in text
    assert "### Escalate" not in text
    assert "Ali must deliberately approve" not in text


def test_delegation_does_not_remove_human_regulatory_review() -> None:
    text = _gate_text()

    assert "Human regulatory review remains mandatory" in text
    assert "qualified review cannot be secured safely and economically" in text
