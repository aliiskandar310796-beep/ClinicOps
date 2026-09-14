from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "04_GROWTH" / "expansion_lanes.json"


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_live_portfolio_is_balanced_and_fail_closed_on_authority() -> None:
    data = load_registry()
    lanes = data["lanes"]
    policy = data["allocation_policy"]

    assert data["operating_rule"].startswith("RUN LIVE")
    assert data["status_model"]["operational_status"] == "LIVE_READY"
    assert {lane["id"] for lane in lanes} == {
        "regulatory-integrity",
        "trialops",
        "qualityops",
        "clinical-ai-ops",
        "labops",
        "clinic-ops",
        "medical-content-ops",
    }

    shares = [lane["capacity_share_pct"] for lane in lanes]
    assert sum(shares) == policy["total_capacity_pct"] == 100
    assert min(shares) >= policy["protected_floor_pct"]
    assert max(shares) <= policy["hard_ceiling_pct"]

    for lane in lanes:
        assert lane["operational_status"] == "LIVE_READY"
        assert lane["entry_offer"]
        assert lane["service_route"]
        assert lane["buyer_profiles"]
        assert lane["active_work"]
        assert lane["recurring_streams"]
        assert lane["low_touch_streams"]
        assert len(lane["distribution_channels"]) >= 3
        assert lane["automation_support_allowed"] is True
        assert lane["automated_authority_allowed"] is False
        assert lane["commercial_proof_public"] == "NOT_DISCLOSED"


def test_adjacent_lanes_do_not_overclaim_validation() -> None:
    data = load_registry()
    adjacent = [lane for lane in data["lanes"] if lane["id"] != "regulatory-integrity"]

    for lane in adjacent:
        assert lane["public_evidence_stage"] == "E1"
        assert lane["market_role"] in {
            "ACTIVE_ADJACENCY",
            "LIVE_EMERGING",
            "PARTNER_LED_LIVE",
        }


def test_registry_keeps_high_grade_buyer_evidence_private_and_outbound_global() -> None:
    data = load_registry()
    joined = "\n".join(data["guardrails"]).lower()
    controls = data["company_distribution_controls"]

    assert "e4+" in joined
    assert "private" in joined
    assert "compliance" in joined
    assert "human authority" in joined
    assert controls["cold_email_daily_ceiling"] == 15
    assert controls["cold_email_denmark_allowed"] is False
    assert controls["shared_outbound_ledger_required"] is True
