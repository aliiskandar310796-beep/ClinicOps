from clinicops_os.company_run import CompanyRun, evaluate_company_run


def _event(
    event_id: str,
    *,
    department: str = "revenue-opportunity",
    status: str = "completed",
    ai_led: bool = True,
    founder_intervention: bool = False,
    reserved_human_decision: bool = False,
    commercial_stage: str = "E2",
    evidence_refs: list[str] | None = None,
    artifact_refs: list[str] | None = None,
    handoff_to: str | None = None,
    handoff_completed: bool = False,
    safety_violation: bool = False,
) -> dict[str, object]:
    return {
        "event_id": event_id,
        "department": department,
        "objective": f"Objective {event_id}",
        "status": status,
        "ai_led": ai_led,
        "founder_intervention": founder_intervention,
        "reserved_human_decision": reserved_human_decision,
        "commercial_stage": commercial_stage,
        "evidence_refs": evidence_refs or [],
        "artifact_refs": artifact_refs or [f"artifact://{event_id}"],
        "handoff_to": handoff_to,
        "handoff_completed": handoff_completed,
        "safety_violation": safety_violation,
        "notes": None,
    }


def _run(events: list[dict[str, object]]) -> CompanyRun:
    return CompanyRun.from_dict(
        {
            "run_id": "RUN-001",
            "period_start": "2026-09-01",
            "period_end": "2026-09-30",
            "events": events,
        }
    )


def test_clean_run_separates_operational_and_commercial_pass() -> None:
    run = _run(
        [
            _event(
                "EVT-1",
                handoff_to="customer-discovery-partnerships",
                handoff_completed=True,
            ),
            _event(
                "EVT-2",
                department="customer-discovery-partnerships",
                commercial_stage="E6",
                evidence_refs=["private://priced-scope-request"],
            ),
        ]
    )

    result = evaluate_company_run(run)

    assert result.operational_pass is True
    assert result.commercial_signal is True
    assert result.activated_commercial_loop is False
    assert result.autonomy_rate == 1.0
    assert result.handoff_closure_rate == 1.0


def test_reserved_human_decision_is_excluded_from_autonomy_denominator() -> None:
    run = _run(
        [
            _event("EVT-1"),
            _event(
                "EVT-2",
                department="human-governance",
                ai_led=False,
                founder_intervention=True,
                reserved_human_decision=True,
                commercial_stage="E7",
                evidence_refs=["private://review"],
            ),
        ]
    )

    result = evaluate_company_run(run)

    assert result.eligible_completed_events == 1
    assert result.autonomous_completed_events == 1
    assert result.autonomy_rate == 1.0
    assert result.reserved_human_decisions == 1
    assert result.non_reserved_founder_interventions == 0


def test_non_reserved_founder_intervention_reduces_autonomy() -> None:
    run = _run(
        [
            _event("EVT-1"),
            _event("EVT-2", founder_intervention=True),
        ]
    )

    result = evaluate_company_run(run)

    assert result.autonomy_rate == 0.5
    assert result.non_reserved_founder_interventions == 1
    assert result.operational_pass is False


def test_e4_plus_requires_external_or_private_evidence_reference() -> None:
    run = _run([_event("EVT-1", commercial_stage="E5")])

    result = evaluate_company_run(run)

    assert result.operational_pass is False
    assert any(
        finding.severity == "error" and "requires at least one" in finding.message
        for finding in result.findings
    )


def test_safety_violation_invalidates_operational_pass() -> None:
    run = _run([_event("EVT-1", safety_violation=True)])

    result = evaluate_company_run(run)

    assert result.operational_pass is False
    assert any(finding.severity == "error" for finding in result.findings)


def test_open_handoff_reduces_handoff_closure_rate() -> None:
    run = _run(
        [
            _event(
                "EVT-1",
                handoff_to="customer-discovery-partnerships",
                handoff_completed=False,
            )
        ]
    )

    result = evaluate_company_run(run)

    assert result.handoff_closure_rate == 0.0
    assert result.operational_pass is False


def test_duplicate_event_ids_are_rejected() -> None:
    try:
        _run([_event("EVT-1"), _event("EVT-1")])
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("duplicate event IDs should be rejected")
