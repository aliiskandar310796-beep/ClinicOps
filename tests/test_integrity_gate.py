from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinicops_os.integrity_gate import (
    HOLD_FOR_HUMAN_DECISION,
    PASS,
    UNRESOLVED_AUTHORITY,
    build_bundle,
    evaluate_case,
    sha256_path,
    verify_bundle_integrity,
)
from clinicops_os.integrity_guard import preflight_case_safety
from clinicops_os.integrity_review import (
    REQUIRED_ATTESTATIONS,
    prepare_review_record,
    verify_review_gate,
    write_review_gate,
)


def _case() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "case_id": "TEST-IG-001",
        "as_of": "2026-09-14",
        "data_governance": {
            "contains_patient_identifiable_data": False,
            "processing_authorized": True,
            "source_population_approved": True,
        },
        "scope": {"description": "synthetic"},
        "controlled_sources": [
            {
                "source_id": "master",
                "source_type": "client_approved_controlled_source",
                "evidence_ref": "synthetic://master",
                "fields": {"device_name": "A", "ifu_revision": "2"},
            }
        ],
        "surfaces": [
            {
                "surface_id": "eudamed",
                "surface_type": "dataset",
                "evidence_ref": "synthetic://eudamed",
                "fields": {"device_name": "A", "ifu_revision": "1"},
            },
            {
                "surface_id": "ifu",
                "surface_type": "ifu",
                "evidence_ref": "synthetic://ifu",
                "fields": {"device_name": "A", "ifu_revision": "2"},
            },
        ],
        "rules": [
            {
                "rule_id": "R1",
                "field": "device_name",
                "mode": "match_authority",
                "targets": ["eudamed", "ifu"],
            },
            {
                "rule_id": "R2",
                "field": "ifu_revision",
                "mode": "match_authority",
                "targets": ["eudamed", "ifu"],
            },
        ],
        "changes": [
            {
                "change_id": "C1",
                "field": "ifu_revision",
                "old_value": "1",
                "new_value": "2",
                "approved_source_id": "master",
                "expected_surfaces": ["eudamed", "ifu"],
            }
        ],
    }


def _write_case(tmp_path: Path, case: dict[str, object]) -> Path:
    path = tmp_path / "case.json"
    path.write_text(json.dumps(case, indent=2), encoding="utf-8")
    return path


def _complete_review(bundle: Path) -> dict[str, object]:
    record = prepare_review_record(bundle)
    record.update(
        {
            "human_reviewer": "Synthetic Reviewer",
            "reviewer_role": "RA/QA reviewer",
            "review_completed_on": "2026-09-14",
            "review_minutes": 12,
            "decision": "APPROVE",
            "notes": "Synthetic smoke review; finding disposition completed.",
        }
    )
    for key in REQUIRED_ATTESTATIONS:
        record[key] = True
    dispositions = record["finding_dispositions"]
    assert isinstance(dispositions, dict)
    for finding_id in dispositions:
        dispositions[finding_id] = "CONFIRMED"
    return record


def _write_approved_review(tmp_path: Path, bundle: Path) -> Path:
    review_path = tmp_path / "review.json"
    review_path.write_text(
        json.dumps(_complete_review(bundle), indent=2), encoding="utf-8"
    )
    result = write_review_gate(review_path, bundle)
    assert result.approved is True
    return review_path


def test_detects_incomplete_change_without_duplicate_lower_severity() -> None:
    result = evaluate_case(_case())
    assert result["gate_status"] == HOLD_FOR_HUMAN_DECISION
    findings = result["findings"]
    assert len(findings) == 1
    assert findings[0]["code"] == "CHANGE_NOT_PROPAGATED"


def test_pass_still_requires_human_review() -> None:
    case = _case()
    case["surfaces"][0]["fields"]["ifu_revision"] = "2"
    result = evaluate_case(case)
    assert result["gate_status"] == PASS
    assert result["human_review_required"] is True
    assert result["release_ready"] is False


def test_conflicting_controlled_sources_never_infers_authority() -> None:
    case = _case()
    case["controlled_sources"].append(
        {
            "source_id": "rim",
            "source_type": "client_approved_controlled_source",
            "evidence_ref": "synthetic://rim",
            "fields": {"device_name": "B", "ifu_revision": "2"},
        }
    )
    case["changes"] = []
    result = evaluate_case(case)
    assert result["gate_status"] == UNRESOLVED_AUTHORITY
    assert any(f["code"] == "AUTHORITY_CONFLICT" for f in result["findings"])


def test_review_gate_is_fail_closed_hash_bound_and_measured(tmp_path: Path) -> None:
    case_path = _write_case(tmp_path, _case())
    bundle = tmp_path / "bundle"
    build_bundle(case_path, bundle)

    record = prepare_review_record(bundle)
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    result = write_review_gate(review_path, bundle)
    assert result.approved is False
    assert not (bundle / "review_gate.json").exists()
    assert not (bundle / "review_record.json").exists()

    record = _complete_review(bundle)
    review_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    result = write_review_gate(review_path, bundle)
    assert result.approved is True
    assert result.review_gate is not None
    assert result.review_gate["clinicops_output_delivery_ready"] is True
    metrics = result.review_gate["review_metrics"]
    assert metrics["review_minutes"] == 12
    assert metrics["confirmed"] == 1
    assert metrics["false_positive_rate"] == 0
    bundled_review = bundle / "review_record.json"
    assert bundled_review.is_file()
    assert result.review_gate["review_record_sha256"] == sha256_path(bundled_review)
    ok, reasons = verify_review_gate(bundle)
    assert ok is True
    assert reasons == ()


def test_review_requires_disposition_for_every_current_finding(tmp_path: Path) -> None:
    case_path = _write_case(tmp_path, _case())
    bundle = tmp_path / "bundle"
    build_bundle(case_path, bundle)
    record = prepare_review_record(bundle)
    record.update(
        {
            "human_reviewer": "Synthetic Reviewer",
            "reviewer_role": "RA/QA reviewer",
            "review_completed_on": "2026-09-14",
            "review_minutes": 10,
            "decision": "APPROVE",
            "notes": "Reviewed.",
        }
    )
    for key in REQUIRED_ATTESTATIONS:
        record[key] = True
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    result = write_review_gate(review_path, bundle)
    assert result.approved is False
    assert any("disposition must be one of" in reason for reason in result.reasons)


def test_tampered_bundled_review_record_breaks_review_gate(tmp_path: Path) -> None:
    case_path = _write_case(tmp_path, _case())
    bundle = tmp_path / "bundle"
    build_bundle(case_path, bundle)
    _write_approved_review(tmp_path, bundle)

    bundled_review = bundle / "review_record.json"
    record = json.loads(bundled_review.read_text(encoding="utf-8"))
    record["review_minutes"] = 99
    bundled_review.write_text(json.dumps(record, indent=2), encoding="utf-8")

    ok, reasons = verify_review_gate(bundle)
    assert ok is False
    assert any("review_record_sha256" in reason for reason in reasons)


def test_tampered_review_gate_metrics_break_reconstruction(tmp_path: Path) -> None:
    case_path = _write_case(tmp_path, _case())
    bundle = tmp_path / "bundle"
    build_bundle(case_path, bundle)
    _write_approved_review(tmp_path, bundle)

    gate_path = bundle / "review_gate.json"
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    gate["review_metrics"]["review_minutes"] = 99
    gate_path.write_text(json.dumps(gate, indent=2), encoding="utf-8")

    ok, reasons = verify_review_gate(bundle)
    assert ok is False
    assert any("does not match bundled approved review record" in reason for reason in reasons)


def test_tamper_breaks_bundle_and_review_binding(tmp_path: Path) -> None:
    case_path = _write_case(tmp_path, _case())
    bundle = tmp_path / "bundle"
    build_bundle(case_path, bundle)
    (bundle / "integrity_report.md").write_text("tampered\n", encoding="utf-8")
    ok, reasons, _ = verify_bundle_integrity(bundle, case_path)
    assert ok is False
    assert any("hash does not match" in reason for reason in reasons)


def test_invalid_target_is_rejected() -> None:
    case = _case()
    case["rules"][0]["targets"] = ["missing"]
    with pytest.raises(ValueError, match="unknown surfaces"):
        evaluate_case(case)


def test_preflight_rejects_patient_identifiable_data(tmp_path: Path) -> None:
    case = _case()
    case["data_governance"]["contains_patient_identifiable_data"] = True
    path = _write_case(tmp_path, case)
    with pytest.raises(ValueError, match="must be explicitly false"):
        preflight_case_safety(path)


def test_preflight_rejects_noop_change(tmp_path: Path) -> None:
    case = _case()
    case["changes"][0]["new_value"] = "1"
    path = _write_case(tmp_path, case)
    with pytest.raises(ValueError, match="old_value and new_value must differ"):
        preflight_case_safety(path)


def test_preflight_rejects_unapproved_processing(tmp_path: Path) -> None:
    case = _case()
    case["data_governance"]["processing_authorized"] = False
    path = _write_case(tmp_path, case)
    with pytest.raises(ValueError, match="processing_authorized must be explicitly true"):
        preflight_case_safety(path)
