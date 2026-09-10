from clinicops_os.pilot_gate import (
    NOT_ACTIVATED_STATUS,
    evaluate_standard_pilot,
)


def _standard_record() -> dict[str, object]:
    return {
        "record_schema_version": "1.0",
        "experiment_id": "EXP-001",
        "commercial_form": "paid_pilot",
        "exp_001_eligible": True,
        "scope_accepted_in_writing": True,
        "commercial_owner_identified": True,
        "population_bounded": True,
        "standard_deliverables": True,
        "standard_commercial_terms": True,
        "activation_condition": "accepted_po_or_signed_commitment",
        "activation_condition_satisfied": True,
        "private_storage_approved": True,
        "buyer_authorised_to_share": True,
        "patient_identifiable_data": False,
        "bundle_schema_version": "1.1",
        "human_reviewer": "Qualified Reviewer",
        "human_reviewer_qualified": True,
        "novel_public_claim": False,
        "custom_regulatory_conclusion": False,
        "nonstandard_liability": False,
        "unsupported_interpretation": False,
    }


def test_standard_paid_pilot_activates_only_when_every_gate_passes() -> None:
    result = evaluate_standard_pilot(_standard_record())

    assert result.activated is True
    assert result.reasons == ()
    assert result.as_dict()["status"] == "ACTIVATED"


def test_design_partner_cannot_enter_standard_delegated_envelope() -> None:
    record = _standard_record()
    record["commercial_form"] = "design_partner"

    result = evaluate_standard_pilot(record)

    assert result.activated is False
    assert "commercial_form must be paid_pilot" in result.reasons
    assert result.as_dict()["status"] == NOT_ACTIVATED_STATUS


def test_missing_reviewer_and_nonstandard_terms_fail_closed() -> None:
    record = _standard_record()
    record["human_reviewer"] = ""
    record["human_reviewer_qualified"] = False
    record["nonstandard_liability"] = True

    result = evaluate_standard_pilot(record)

    assert result.activated is False
    assert "a named human reviewer must be assigned before kickoff" in result.reasons
    assert "assigned human reviewer is not confirmed qualified" in result.reasons
    assert "scope contains non-standard liability or legal terms" in result.reasons


def test_patient_data_and_unsatisfied_payment_condition_block_activation() -> None:
    record = _standard_record()
    record["patient_identifiable_data"] = True
    record["activation_condition_satisfied"] = False

    result = evaluate_standard_pilot(record)

    assert result.activated is False
    assert "commercial activation condition is not satisfied" in result.reasons
    assert any("patient-identifiable data" in reason for reason in result.reasons)


def test_missing_negative_attestation_fails_closed() -> None:
    record = _standard_record()
    del record["unsupported_interpretation"]

    result = evaluate_standard_pilot(record)

    assert result.activated is False
    assert "scope requires unsupported interpretation" in result.reasons


def test_malformed_activation_condition_fails_closed_without_crashing() -> None:
    record = _standard_record()
    record["activation_condition"] = ["upfront_payment"]

    result = evaluate_standard_pilot(record)

    assert result.activated is False
    assert "activation_condition is not an approved paid-pilot condition" in result.reasons
