from __future__ import annotations

from datetime import date

from clinicops_os.expert_network import validate_assignment, validate_expert


def _expert(**overrides):
    row = {
        "expert_id": "EXP-1",
        "preferred_name": "Example Expert",
        "contact_route": "expert@example.invalid",
        "country": "DK",
        "jurisdictions": ["DK", "EU"],
        "professional_role": "Regulatory consultant",
        "competency_domains": ["MDR", "UDI"],
        "permitted_work_types": ["REGULATORY_DATA_REVIEW"],
        "languages": ["da", "en"],
        "network_status": "AVAILABLE",
        "credentials_verified_on": "2026-09-01",
        "conflict_checked_on": "2026-09-01",
        "last_reviewed_on": "2026-09-01",
        "nda_status": "SIGNED",
        "contract_status": "READY",
        "insurance_status": "VERIFIED",
        "public_profile_consent": False,
        "public_wording": "",
    }
    row.update(overrides)
    return row


def _assignment(**overrides):
    row = {
        "assignment_id": "ASN-1",
        "expert_id": "EXP-1",
        "engagement_id": "ENG-1",
        "scoped_question": "Review the declared data relationship.",
        "work_type": "REGULATORY_DATA_REVIEW",
        "markets": ["DK"],
        "languages": ["da"],
        "accountable_owner": "ClinicOps engagement lead",
        "role_type": "REVIEWER",
        "credentials_checked_on": "2026-09-20",
        "conflict_checked_on": "2026-09-25",
        "insurance_checked_on": "2026-09-20",
        "confidentiality_confirmed": True,
        "contract_confirmed": True,
        "compensation_confirmed": True,
        "sensitive_data_access": "NONE",
        "data_terms_confirmed": False,
        "data_minimisation_note": "",
        "authority_basis": "",
        "governance_approval_id": "",
    }
    row.update(overrides)
    return row


def test_available_expert_passes_roster_gate():
    findings = validate_expert(_expert(), as_of=date(2026, 9, 28))
    assert not [f for f in findings if f.severity == "error"]


def test_available_expert_requires_contract_and_confidentiality():
    findings = validate_expert(
        _expert(nda_status="PENDING", contract_status="PENDING"),
        as_of=date(2026, 9, 28),
    )
    fields = {f.field for f in findings if f.severity == "error"}
    assert {"nda_status", "contract_status"} <= fields


def test_public_wording_requires_consent():
    findings = validate_expert(
        _expert(public_profile_consent=False, public_wording="Dr Example, ClinicOps"),
        as_of=date(2026, 9, 28),
    )
    assert any(f.field == "public_wording" and f.severity == "error" for f in findings)


def test_assignment_gate_passes_for_verified_scope():
    expert = _expert()
    findings = validate_assignment(_assignment(), expert, as_of=date(2026, 9, 28))
    assert not [f for f in findings if f.severity == "error"]


def test_assignment_rejects_out_of_scope_market_and_work_type():
    expert = _expert(jurisdictions=["DK"], permitted_work_types=["REGULATORY_DATA_REVIEW"])
    findings = validate_assignment(
        _assignment(markets=["SE"], work_type="CLINICAL_REVIEW"),
        expert,
        as_of=date(2026, 9, 28),
    )
    fields = {f.field for f in findings if f.severity == "error"}
    assert {"markets", "work_type"} <= fields


def test_sensitive_data_requires_terms_and_minimisation():
    findings = validate_assignment(
        _assignment(sensitive_data_access="SPECIAL_CATEGORY"),
        _expert(),
        as_of=date(2026, 9, 28),
    )
    fields = {f.field for f in findings if f.severity == "error"}
    assert {"data_terms_confirmed", "data_minimisation_note"} <= fields


def test_decision_owner_requires_separate_authority_basis():
    findings = validate_assignment(
        _assignment(role_type="DECISION_OWNER"),
        _expert(),
        as_of=date(2026, 9, 28),
    )
    fields = {f.field for f in findings if f.severity == "error"}
    assert {"authority_basis", "governance_approval_id"} <= fields


def test_public_example_roster_is_synthetic() -> None:
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    raw = json.loads(
        (root / "03_OPERATIONS" / "expert_network" / "roster.example.json").read_text(
            encoding="utf-8"
        )
    )
    assert raw["experts"]
    for expert in raw["experts"]:
        assert str(expert["expert_id"]).startswith("EXP-SYN-")
        assert str(expert["contact_route"]).endswith(".invalid")
