from clinicops_os.delegation_proof import (
    CONTROLLED_DRY_RUN,
    PAID_PILOT,
    evaluate_delegation_proof,
    evaluate_delegation_run,
)


def _run(run_id: str, run_kind: str) -> dict[str, object]:
    record: dict[str, object] = {
        "record_schema_version": "1.0",
        "run_id": run_id,
        "run_kind": run_kind,
        "execution_completed_on": "2026-09-11",
        "operator": "Trained Operator",
        "human_reviewer": "Qualified Reviewer",
        "private_operational_record": True,
        "proof_use_allowed": True,
        "ci_or_automated_smoke": False,
        "execution_completed": True,
        "qualification_stage_completed": True,
        "written_scope_stage_completed": True,
        "preflight_status": "ACTIVATED",
        "intake_validated": True,
        "bundle_generated": True,
        "human_review_status": "REVIEW APPROVED",
        "bundle_integrity_status": "VERIFIED",
        "delivery_stage_completed": True,
        "evidence_gate_satisfied": True,
        "claim_gate_satisfied": True,
        "commercial_gate_satisfied": True,
        "data_handling_gate_satisfied": True,
        "qualified_human_review_completed": True,
        "founder_transaction_decision_required": False,
        "unplanned_exception": False,
        "nonstandard_scope_claim_or_commercial_exception": False,
        "closeout_completed": True,
        "commercial_learning_captured_privately": True,
        "real_paid_pilot": run_kind == PAID_PILOT,
        "payment_or_procurement_path_followed": run_kind == PAID_PILOT,
        "full_operator_dry_run": run_kind == CONTROLLED_DRY_RUN,
    }
    return record


def test_one_eligible_paid_pilot_proves_delegation() -> None:
    result = evaluate_delegation_proof([_run("PAID-001", PAID_PILOT)])

    assert result.proven is True
    assert result.qualifying_paid_pilot_ids == ("PAID-001",)
    assert result.qualifying_dry_run_ids == ()


def test_one_controlled_dry_run_is_not_enough() -> None:
    result = evaluate_delegation_proof([_run("DRY-001", CONTROLLED_DRY_RUN)])

    assert result.proven is False
    assert result.qualifying_dry_run_ids == ("DRY-001",)


def test_two_complete_unique_controlled_dry_runs_prove_delegation() -> None:
    result = evaluate_delegation_proof(
        [
            _run("DRY-001", CONTROLLED_DRY_RUN),
            _run("DRY-002", CONTROLLED_DRY_RUN),
        ]
    )

    assert result.proven is True
    assert result.qualifying_dry_run_ids == ("DRY-001", "DRY-002")


def test_ci_or_automated_smoke_can_never_qualify() -> None:
    record = _run("DRY-CI", CONTROLLED_DRY_RUN)
    record["ci_or_automated_smoke"] = True

    run = evaluate_delegation_run(record)
    proof = evaluate_delegation_proof([record, _run("DRY-002", CONTROLLED_DRY_RUN)])

    assert run.qualifies is False
    assert any("CI or automated smoke" in reason for reason in run.reasons)
    assert proof.proven is False


def test_public_or_unapproved_record_cannot_qualify() -> None:
    record = _run("DRY-PUBLIC", CONTROLLED_DRY_RUN)
    record["private_operational_record"] = False
    record["proof_use_allowed"] = False

    result = evaluate_delegation_run(record)

    assert result.qualifies is False
    assert any("private operational record" in reason for reason in result.reasons)
    assert any("not explicitly authorised" in reason for reason in result.reasons)


def test_founder_decision_or_exception_disqualifies_run() -> None:
    record = _run("DRY-EXCEPTION", CONTROLLED_DRY_RUN)
    record["founder_transaction_decision_required"] = True
    record["unplanned_exception"] = True

    result = evaluate_delegation_run(record)

    assert result.qualifies is False
    assert any("founder transaction-level decision" in reason for reason in result.reasons)
    assert any("unplanned exception" in reason for reason in result.reasons)


def test_negative_attestations_are_fail_closed_when_omitted() -> None:
    record = _run("DRY-OMITTED", CONTROLLED_DRY_RUN)
    del record["founder_transaction_decision_required"]
    del record["unplanned_exception"]
    del record["nonstandard_scope_claim_or_commercial_exception"]

    result = evaluate_delegation_run(record)

    assert result.qualifies is False
    assert len(result.reasons) >= 3


def test_duplicate_run_ids_invalidate_evidence_set() -> None:
    result = evaluate_delegation_proof(
        [
            _run("DRY-SAME", CONTROLLED_DRY_RUN),
            _run("DRY-SAME", CONTROLLED_DRY_RUN),
        ]
    )

    assert result.proven is False
    assert result.qualifying_dry_run_ids == ()
    assert any("run_id values must be unique" in error for error in result.evidence_errors)


def test_paid_pilot_requires_real_payment_or_procurement_path() -> None:
    record = _run("PAID-NOT-REAL", PAID_PILOT)
    record["real_paid_pilot"] = False
    record["payment_or_procurement_path_followed"] = False

    result = evaluate_delegation_run(record)

    assert result.qualifies is False
    assert any("real eligible paid pilot" in reason for reason in result.reasons)
    assert any("payment/procurement" in reason for reason in result.reasons)


def test_missing_existing_gate_disqualifies_run() -> None:
    record = _run("DRY-MISSING-GATE", CONTROLLED_DRY_RUN)
    record["claim_gate_satisfied"] = False

    result = evaluate_delegation_run(record)

    assert result.qualifies is False
    assert "claim-safety gate is not recorded as satisfied" in result.reasons


def test_incomplete_lifecycle_stage_disqualifies_run() -> None:
    record = _run("DRY-INCOMPLETE", CONTROLLED_DRY_RUN)
    record["qualification_stage_completed"] = False
    record["delivery_stage_completed"] = False

    result = evaluate_delegation_run(record)

    assert result.qualifies is False
    assert any("qualification stage" in reason for reason in result.reasons)
    assert any("delivery/release stage" in reason for reason in result.reasons)
