from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "04_GROWTH" / "expansion_lanes.json"


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_tier1_lanes_fail_closed_before_real_validation() -> None:
    data = load_registry()
    lanes = data["lanes"]

    assert data["promotion_rule"] == (
        "DISCOVER -> TEST -> SELL MANUALLY -> PROVE REPEATABILITY -> AUTOMATE"
    )
    assert data["public_state_ceiling"] == "E1"
    assert {lane["id"] for lane in lanes} == {
        "trialops",
        "qualityops",
        "clinical-ai-ops",
    }

    for lane in lanes:
        assert lane["public_evidence_stage"] == "E1"
        assert lane["commercial_status"] == "TEST_NOW"
        assert lane["automation_allowed"] is False
        assert lane["entry_offer"]
        assert lane["buyer_profiles"]
        assert lane["active_work"]
        assert lane["primary_sources"]
        threshold = lane["validation_threshold"]
        assert threshold["qualified_conversations"] >= 3
        assert threshold["independent_repeated_pain_confirmations"] >= 2
        assert threshold["concrete_commercial_signals"] >= 1
        assert threshold["paid_or_activated_pilot_before_productization"] >= 1


def test_registry_keeps_high_grade_buyer_evidence_private() -> None:
    data = load_registry()
    joined = "\n".join(data["guardrails"]).lower()
    assert "e4+" in joined
    assert "private" in joined
    assert "compliance" in joined
    assert "automation remains blocked" in joined
