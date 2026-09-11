import csv
import json
from datetime import date
from pathlib import Path

from clinicops_os.dry_run import (
    STEP_BUNDLE,
    STEP_HUMAN_REVIEW,
    STEP_PREFLIGHT,
    STEP_VERIFY,
    run_pilot_dry_run,
)

FIELDNAMES = [
    "company",
    "device",
    "actor_role",
    "registration_type",
    "basic_udi_di",
    "certificate_expiry",
    "danish_market",
    "linked_sscp",
    "source_url",
    "notes",
]


def _write_portfolio(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow(
            {
                "company": "Example Co",
                "device": "Example device",
                "actor_role": "MF",
                "registration_type": "legacy",
                "basic_udi_di": "B-123",
                "certificate_expiry": "2026-12-01",
                "danish_market": "confirmed",
                "linked_sscp": "null",
                "source_url": "https://example.test",
                "notes": "fictional",
            }
        )


def _standard_preflight_record() -> dict[str, object]:
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


def _standard_review_record() -> dict[str, object]:
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


def _write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_clean_dry_run_completes_every_step_with_no_escalation(tmp_path: Path) -> None:
    portfolio = tmp_path / "portfolio.csv"
    _write_portfolio(portfolio)
    preflight_path = tmp_path / "preflight.json"
    _write_json(preflight_path, _standard_preflight_record())
    review_path = tmp_path / "review.json"
    _write_json(review_path, _standard_review_record())
    output_dir = tmp_path / "bundle"

    result = run_pilot_dry_run(
        preflight_record_path=preflight_path,
        review_record_path=review_path,
        portfolio_path=portfolio,
        output_dir=output_dir,
        as_of=date(2026, 9, 11),
    )

    assert result.completed is True
    assert result.escalated is False
    assert [step.name for step in result.steps] == [
        STEP_PREFLIGHT,
        STEP_BUNDLE,
        STEP_HUMAN_REVIEW,
        STEP_VERIFY,
    ]
    assert all(step.passed for step in result.steps)
    assert result.manifest is not None
    assert result.manifest["bundle_schema_version"] == "1.1"
    assert (output_dir / "manifest.json").is_file()


def test_non_standard_preflight_halts_before_any_bundle_is_generated(
    tmp_path: Path,
) -> None:
    portfolio = tmp_path / "portfolio.csv"
    _write_portfolio(portfolio)
    record = _standard_preflight_record()
    record["patient_identifiable_data"] = True
    preflight_path = tmp_path / "preflight.json"
    _write_json(preflight_path, record)
    review_path = tmp_path / "review.json"
    _write_json(review_path, _standard_review_record())
    output_dir = tmp_path / "bundle"

    result = run_pilot_dry_run(
        preflight_record_path=preflight_path,
        review_record_path=review_path,
        portfolio_path=portfolio,
        output_dir=output_dir,
        as_of=date(2026, 9, 11),
    )

    assert result.completed is False
    assert result.escalated is True
    assert [step.name for step in result.steps] == [STEP_PREFLIGHT]
    assert result.steps[0].passed is False
    assert result.manifest is None
    assert not output_dir.exists()


def test_missing_human_review_approval_blocks_verification_and_release(
    tmp_path: Path,
) -> None:
    portfolio = tmp_path / "portfolio.csv"
    _write_portfolio(portfolio)
    preflight_path = tmp_path / "preflight.json"
    _write_json(preflight_path, _standard_preflight_record())
    review_record = _standard_review_record()
    review_record["approved_for_release"] = False
    review_path = tmp_path / "review.json"
    _write_json(review_path, review_record)
    output_dir = tmp_path / "bundle"

    result = run_pilot_dry_run(
        preflight_record_path=preflight_path,
        review_record_path=review_path,
        portfolio_path=portfolio,
        output_dir=output_dir,
        as_of=date(2026, 9, 11),
    )

    assert result.completed is False
    assert result.escalated is True
    assert [step.name for step in result.steps] == [
        STEP_PREFLIGHT,
        STEP_BUNDLE,
        STEP_HUMAN_REVIEW,
    ]
    assert result.steps[-1].passed is False
    # The bundle was generated (evidence processing doesn't require review), but the
    # dry run must not proceed to verification/release without an approved review.
    assert result.manifest is not None
