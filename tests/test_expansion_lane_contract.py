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


def test_opportunity_pipeline_topology_reflects_parallel_convergence() -> None:
    data = load_registry()
    pipeline = data["opportunity_pipeline"]
    stages = pipeline["stages"]
    stage_ids = {stage["stage_id"] for stage in stages}

    assert pipeline["model"] == "parallel_discovery_converge"
    assert pipeline["changed_from"] == "fixed_serial"
    assert len(stage_ids) == len(stages)

    prerequisite = [s for s in stages if s["parallel_group"] == "prerequisite"]
    discovery_scoring = [s for s in stages if s["parallel_group"] == "discovery-scoring"]
    convergence = [s for s in stages if s["parallel_group"] == "convergence"]
    gate = [s for s in stages if s["parallel_group"] == "gate"]

    # Regulatory Evidence Steward: the one genuine upstream prerequisite, no dependencies.
    assert len(prerequisite) == 1
    assert prerequisite[0]["stage_id"] == "regulatory-evidence-steward"
    assert prerequisite[0]["depends_on"] == []

    # Visibility Architect, Customer Discovery Agent and Portfolio Operator: mutually
    # independent, each depending only on the prerequisite stage (never on each other).
    assert {s["stage_id"] for s in discovery_scoring} == {
        "visibility-architect",
        "customer-discovery",
        "portfolio-operator",
    }
    for stage in discovery_scoring:
        assert stage["depends_on"] == [prerequisite[0]["stage_id"]]

    # Opportunity Architect: the convergence point, depending on the full parallel group.
    assert len(convergence) == 1
    assert convergence[0]["stage_id"] == "opportunity-architect"
    assert set(convergence[0]["depends_on"]) == {s["stage_id"] for s in discovery_scoring}

    # Release Sentinel: unchanged final serial gate over the converged output.
    assert len(gate) == 1
    assert gate[0]["stage_id"] == "release-sentinel"
    assert gate[0]["depends_on"] == [convergence[0]["stage_id"]]

    # Every declared dependency must reference a real stage in this pipeline.
    for stage in stages:
        assert set(stage["depends_on"]) <= stage_ids
