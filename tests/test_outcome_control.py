from __future__ import annotations

import copy

import pytest

from clinicops_os.outcome_control import OutcomeMission, evaluate_outcome_mission


BASE_MISSION = {
    "schema_version": "1.0",
    "mission_id": "TEST-MISSION",
    "owner_agent": "opportunity-architect",
    "outcome_class": "commercial-evidence",
    "objective": "Move a bounded test toward stronger external evidence.",
    "status": "active",
    "metric_name": "commercial_evidence_stage_number",
    "metric_direction": "increase",
    "baseline": 1,
    "target": 6,
    "current": 3,
    "unit": "E-stage number",
    "commercial_stage": "E3",
    "evidence_refs": [],
    "artifact_refs": ["artifact:test"],
    "review_point": "after the next high-information test",
    "stop_condition": "stop if the test cannot create new external evidence",
    "workers": [
        {
            "worker_id": "W1",
            "specialty": "market-scout",
            "parent_agent": "opportunity-architect",
            "objective": "Prepare the bounded market hypothesis.",
            "status": "completed",
            "success_criteria": ["bounded hypothesis"],
            "stop_condition": "stop after the hypothesis is ready",
            "evidence_refs": [],
            "artifact_refs": ["artifact:w1"],
            "handoff_to": "customer-discovery",
            "handoff_completed": True,
            "reserved_human_action": False,
            "control_violation": False,
            "violation_resolved": False,
            "notes": None,
        }
    ],
}


def _mission() -> dict[str, object]:
    return copy.deepcopy(BASE_MISSION)


def test_valid_active_mission_passes_control_without_claiming_outcome() -> None:
    evaluation = evaluate_outcome_mission(OutcomeMission.from_dict(_mission()))

    assert evaluation.control_pass is True
    assert evaluation.outcome_achieved is False
    assert evaluation.progress_ratio == pytest.approx(0.4)
    assert evaluation.handoff_closure_rate == 1.0


def test_e4_plus_requires_external_evidence_ref() -> None:
    row = _mission()
    row["commercial_stage"] = "E4"
    row["current"] = 4

    evaluation = evaluate_outcome_mission(OutcomeMission.from_dict(row))

    assert evaluation.control_pass is False
    assert any("E4 requires private external evidence refs" in item.message for item in evaluation.findings)


def test_metric_movement_requires_evidence_or_artifact() -> None:
    row = _mission()
    row["artifact_refs"] = []
    row["evidence_refs"] = []

    evaluation = evaluate_outcome_mission(OutcomeMission.from_dict(row))

    assert evaluation.control_pass is False
    assert any("metric movement requires" in item.message for item in evaluation.findings)


def test_completed_worker_requires_reference() -> None:
    row = _mission()
    worker = row["workers"][0]
    worker["artifact_refs"] = []
    worker["evidence_refs"] = []

    evaluation = evaluate_outcome_mission(OutcomeMission.from_dict(row))

    assert evaluation.control_pass is False
    assert any("completed worker requires" in item.message for item in evaluation.findings)


def test_active_worker_cap_is_enforced() -> None:
    row = _mission()
    row["workers"] = []
    for index in range(6):
        row["workers"].append(
            {
                "worker_id": f"W{index}",
                "specialty": "market-scout",
                "parent_agent": "opportunity-architect",
                "objective": "Run one bounded independent research slice.",
                "status": "working",
                "success_criteria": ["one verified slice"],
                "stop_condition": "stop after one slice",
                "evidence_refs": [],
                "artifact_refs": [],
                "handoff_to": None,
                "handoff_completed": False,
                "reserved_human_action": False,
                "control_violation": False,
                "violation_resolved": False,
                "notes": None,
            }
        )

    evaluation = evaluate_outcome_mission(OutcomeMission.from_dict(row))

    assert evaluation.active_workers == 6
    assert evaluation.control_pass is False
    assert any("active worker cap exceeded" in item.message for item in evaluation.findings)


def test_completed_mission_must_reach_target() -> None:
    row = _mission()
    row["status"] = "completed"

    evaluation = evaluate_outcome_mission(OutcomeMission.from_dict(row))

    assert evaluation.control_pass is False
    assert any("cannot be completed before" in item.message for item in evaluation.findings)


def test_decrease_metric_progress_and_completion() -> None:
    row = _mission()
    row.update(
        {
            "outcome_class": "cycle-time",
            "metric_name": "hours_to_controlled_bundle",
            "metric_direction": "decrease",
            "baseline": 10,
            "target": 4,
            "current": 4,
            "unit": "hours",
            "status": "completed",
        }
    )

    evaluation = evaluate_outcome_mission(OutcomeMission.from_dict(row))

    assert evaluation.control_pass is True
    assert evaluation.outcome_achieved is True
    assert evaluation.progress_ratio == 1.0


def test_resolved_control_incident_is_visible_but_not_failure() -> None:
    row = _mission()
    worker = row["workers"][0]
    worker["control_violation"] = True
    worker["violation_resolved"] = True

    evaluation = evaluate_outcome_mission(OutcomeMission.from_dict(row))

    assert evaluation.control_pass is True
    assert any(item.severity == "info" for item in evaluation.findings)


def test_unresolved_control_incident_fails() -> None:
    row = _mission()
    worker = row["workers"][0]
    worker["control_violation"] = True

    evaluation = evaluate_outcome_mission(OutcomeMission.from_dict(row))

    assert evaluation.control_pass is False
    assert any("unresolved control violation" in item.message for item in evaluation.findings)


def test_completed_mission_cannot_leave_open_worker_handoff() -> None:
    row = _mission()
    row["status"] = "completed"
    row["current"] = 6
    row["commercial_stage"] = "E6"
    row["evidence_refs"] = ["private-evidence:test"]
    worker = row["workers"][0]
    worker["handoff_completed"] = False

    evaluation = evaluate_outcome_mission(OutcomeMission.from_dict(row))

    assert evaluation.outcome_achieved is True
    assert evaluation.control_pass is False
    assert any("handoff" in item.message for item in evaluation.findings)


def test_schema_rejects_unknown_worker_specialty() -> None:
    row = _mission()
    row["workers"][0]["specialty"] = "generic-ai-helper"

    with pytest.raises(ValueError, match="unknown specialty"):
        OutcomeMission.from_dict(row)
