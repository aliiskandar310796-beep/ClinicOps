from clinicops_os.human_review_gate import (
    NOT_APPROVED_STATUS,
    evaluate_human_review,
)


def _standard_record() -> dict[str, object]:
    return {
        "review_schema_version": "1.0",
        "reviewer": "Qualified Reviewer",
        "confirmed_evidence_population_and_as_of": True,
        "reviewed_derived_statements_against_evidence": True,
        "separated_machine_output_from_interpretation": True,
        "actor_role_distinctions_preserved": True,
        "unresolved_facts_left_unresolved": True,
        "internal_notes_removed": True,
        "approved_for_release": True,
    }


def test_full_checklist_approves_release() -> None:
    result = evaluate_human_review(_standard_record())

    assert result.approved is True
    assert result.reasons == ()
    assert result.as_dict()["status"] == "APPROVED"


def test_missing_reviewer_name_blocks_release() -> None:
    record = _standard_record()
    record["reviewer"] = ""

    result = evaluate_human_review(record)

    assert result.approved is False
    assert "a named human reviewer must be recorded" in result.reasons
    assert result.as_dict()["status"] == NOT_APPROVED_STATUS


def test_omitted_attestation_fails_closed_rather_than_defaulting_true() -> None:
    record = _standard_record()
    del record["internal_notes_removed"]

    result = evaluate_human_review(record)

    assert result.approved is False
    assert (
        "reviewer has not confirmed internal-only notes are removed from the "
        "client-facing bundle" in result.reasons
    )


def test_single_false_attestation_blocks_release_even_if_all_others_pass() -> None:
    record = _standard_record()
    record["unresolved_facts_left_unresolved"] = False

    result = evaluate_human_review(record)

    assert result.approved is False
    assert len(result.reasons) == 1
