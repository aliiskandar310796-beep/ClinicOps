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
    verify_bundle_integrity,
)
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


def test_review_gate_is_fail_closed_and_hash_bound(tmp_path: Path) -> None:
    case_path = tmp_path / "case.json"
    case_path.write_text(json.dumps(_case(), indent=2), encoding="utf-8")
    bundle = tmp_path / "bundle"
    build_bundle(case_path, bundle)

    record = prepare_review_record(bundle)
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    result = write_review_gate(review_path, bundle)
    assert result.approved is False
    assert not (bundle / "review_gate.json").exists()

    record.update(
        {
            "human_reviewer": "Synthetic Reviewer",
            "reviewer_role": "RA/QA reviewer",
            "review_completed_on": "2026-09-14",
            "decision": "APPROVE",
        }
    )
    for key in REQUIRED_ATTESTATIONS:
        record[key] = True
    review_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    result = write_review_gate(review_path, bundle)
    assert result.approved is True
    ok, reasons = verify_review_gate(bundle)
    assert ok is True
    assert reasons == ()


def test_tamper_breaks_bundle_and_review_binding(tmp_path: Path) -> None:
    case_path = tmp_path / "case.json"
    case_path.write_text(json.dumps(_case(), indent=2), encoding="utf-8")
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
