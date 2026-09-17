from __future__ import annotations

import copy

from clinicops_os.risk_control import RiskRegister, evaluate_risk_register

BASE_REGISTER = {
    "schema_version": "1.0",
    "mission_id": "TEST-RISK",
    "risks": [
        {
            "risk_id": "R1",
            "category": "commercial",
            "description": "Friendly buyer interest may not convert to paid demand.",
            "likelihood": 3,
            "impact": 4,
            "owner_agent": "opportunity-architect",
            "status": "open",
            "mitigation": "Require a concrete commitment before claiming demand.",
            "trigger": "Three qualified conversations produce no commitment.",
            "evidence_refs": [],
            "review_point": "after each qualified conversation",
            "reserved_human_decision": False,
        }
    ],
}


def _register() -> dict[str, object]:
    return copy.deepcopy(BASE_REGISTER)


def test_open_high_but_noncritical_risk_can_remain_visible() -> None:
    evaluation = evaluate_risk_register(RiskRegister.from_dict(_register()))

    assert evaluation.control_pass is True
    assert evaluation.open_risks == 1
    assert evaluation.critical_open_risks == 0
    assert evaluation.highest_score == 12


def test_open_critical_risk_fails_closed() -> None:
    row = _register()
    row["risks"][0]["likelihood"] = 4

    evaluation = evaluate_risk_register(RiskRegister.from_dict(row))

    assert evaluation.control_pass is False
    assert evaluation.critical_open_risks == 1
    assert any("critical risk remains open" in item.message for item in evaluation.findings)


def test_mitigated_risk_requires_evidence() -> None:
    row = _register()
    row["risks"][0]["status"] = "mitigated"

    evaluation = evaluate_risk_register(RiskRegister.from_dict(row))

    assert evaluation.control_pass is False
    assert any("mitigated risk requires evidence" in item.message for item in evaluation.findings)


def test_accepted_high_risk_requires_decision_ref() -> None:
    row = _register()
    row["risks"][0]["status"] = "accepted"

    evaluation = evaluate_risk_register(RiskRegister.from_dict(row))

    assert evaluation.control_pass is False
    assert any("decision/evidence reference" in item.message for item in evaluation.findings)


def test_mitigated_risk_with_evidence_passes() -> None:
    row = _register()
    row["risks"][0]["status"] = "mitigated"
    row["risks"][0]["evidence_refs"] = ["artifact:mitigation"]

    evaluation = evaluate_risk_register(RiskRegister.from_dict(row))

    assert evaluation.control_pass is True
