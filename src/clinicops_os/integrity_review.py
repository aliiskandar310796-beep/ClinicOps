from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .integrity_gate import BUNDLE_SCHEMA_VERSION, sha256_path, verify_bundle_integrity

REVIEW_RECORD_SCHEMA_VERSION = "1.0"
REVIEW_GATE_SCHEMA_VERSION = "1.0"
REVIEW_APPROVED = "REVIEW APPROVED"
REVIEW_INCOMPLETE = "REVIEW INCOMPLETE"

REQUIRED_ATTESTATIONS = (
    "evidence_population_reviewed",
    "authority_conflicts_reviewed",
    "change_propagation_findings_reviewed",
    "false_positive_risk_reviewed",
    "regulatory_judgement_not_automated",
    "release_interpretation_approved",
)


@dataclass(frozen=True)
class IntegrityReviewResult:
    approved: bool
    reasons: tuple[str, ...]
    review_gate: dict[str, object] | None

    def as_dict(self) -> dict[str, object]:
        return {
            "review_gate_schema_version": REVIEW_GATE_SCHEMA_VERSION,
            "approved": self.approved,
            "status": REVIEW_APPROVED if self.approved else REVIEW_INCOMPLETE,
            "reasons": list(self.reasons),
            "review_gate": self.review_gate,
        }


def _read_json(path: str | Path, *, label: str) -> dict[str, object]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError(f"{label} must be a JSON object")
    return raw


def prepare_review_record(output_dir: str | Path) -> dict[str, object]:
    verified, reasons, manifest = verify_bundle_integrity(output_dir)
    if not verified:
        raise ValueError("bundle integrity failed: " + "; ".join(reasons))
    report_path = Path(output_dir) / "integrity_report.json"
    manifest_path = Path(output_dir) / "manifest.json"
    record: dict[str, object] = {
        "record_schema_version": REVIEW_RECORD_SCHEMA_VERSION,
        "bundle_schema_version": BUNDLE_SCHEMA_VERSION,
        "case_id": manifest.get("case_id"),
        "source_sha256": manifest.get("source_sha256"),
        "bundle_manifest_sha256": sha256_path(manifest_path),
        "integrity_report_sha256": sha256_path(report_path),
        "human_reviewer": "",
        "reviewer_role": "",
        "review_completed_on": "",
        "decision": "",
        "notes": "",
    }
    for attestation in REQUIRED_ATTESTATIONS:
        record[attestation] = False
    return record


def load_review_record(path: str | Path) -> dict[str, object]:
    return _read_json(path, label="integrity review record")


def evaluate_review_gate(
    review_record: Mapping[str, object],
    output_dir: str | Path,
    *,
    review_record_sha256: str | None = None,
) -> IntegrityReviewResult:
    reasons: list[str] = []
    verified, bundle_reasons, manifest = verify_bundle_integrity(output_dir)
    if not verified:
        reasons.extend(f"bundle: {reason}" for reason in bundle_reasons)

    out = Path(output_dir)
    manifest_path = out / "manifest.json"
    report_path = out / "integrity_report.json"

    if review_record.get("record_schema_version") != REVIEW_RECORD_SCHEMA_VERSION:
        reasons.append(f"record_schema_version must be {REVIEW_RECORD_SCHEMA_VERSION}")
    if review_record.get("bundle_schema_version") != BUNDLE_SCHEMA_VERSION:
        reasons.append(f"bundle_schema_version must be {BUNDLE_SCHEMA_VERSION}")
    if review_record.get("case_id") != manifest.get("case_id"):
        reasons.append("case_id does not match bundle manifest")
    if review_record.get("source_sha256") != manifest.get("source_sha256"):
        reasons.append("source_sha256 does not match bundle manifest")
    if manifest_path.is_file() and review_record.get(
        "bundle_manifest_sha256"
    ) != sha256_path(manifest_path):
        reasons.append("bundle_manifest_sha256 does not match current manifest")
    if report_path.is_file() and review_record.get(
        "integrity_report_sha256"
    ) != sha256_path(report_path):
        reasons.append("integrity_report_sha256 does not match current report")

    reviewer = review_record.get("human_reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        reasons.append("human_reviewer must be recorded")
    role = review_record.get("reviewer_role")
    if not isinstance(role, str) or not role.strip():
        reasons.append("reviewer_role must be recorded")

    completed_on = review_record.get("review_completed_on")
    if not isinstance(completed_on, str) or not completed_on.strip():
        reasons.append("review_completed_on must be recorded")
    else:
        try:
            date.fromisoformat(completed_on)
        except ValueError:
            reasons.append("review_completed_on must be an ISO date (YYYY-MM-DD)")

    if review_record.get("decision") != "APPROVE":
        reasons.append("decision must be APPROVE for external release")
    for attestation in REQUIRED_ATTESTATIONS:
        if review_record.get(attestation) is not True:
            reasons.append(f"review attestation is not confirmed: {attestation}")

    if reasons:
        return IntegrityReviewResult(False, tuple(reasons), None)

    gate = {
        "review_gate_schema_version": REVIEW_GATE_SCHEMA_VERSION,
        "status": REVIEW_APPROVED,
        "case_id": manifest.get("case_id"),
        "source_sha256": manifest.get("source_sha256"),
        "bundle_manifest_sha256": sha256_path(manifest_path),
        "integrity_report_sha256": sha256_path(report_path),
        "review_record_sha256": review_record_sha256,
        "human_reviewer": str(reviewer).strip(),
        "reviewer_role": str(role).strip(),
        "review_completed_on": completed_on,
        "automated_gate_status": manifest.get("gate_status"),
        "release_ready": True,
        "limitations": (
            "Approval records completion of the declared human review for this exact bundle. "
            "It does not convert the automated screen into a legal or compliance determination."
        ),
    }
    return IntegrityReviewResult(True, (), gate)


def write_review_gate(
    review_record_path: str | Path, output_dir: str | Path
) -> IntegrityReviewResult:
    review = load_review_record(review_record_path)
    result = evaluate_review_gate(
        review,
        output_dir,
        review_record_sha256=sha256_path(review_record_path),
    )
    if result.approved and result.review_gate is not None:
        gate_path = Path(output_dir) / "review_gate.json"
        gate_path.write_text(
            json.dumps(result.review_gate, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return result


def verify_review_gate(output_dir: str | Path) -> tuple[bool, tuple[str, ...]]:
    out = Path(output_dir)
    gate_path = out / "review_gate.json"
    if not gate_path.is_file():
        return False, ("review_gate.json is missing",)
    try:
        gate = _read_json(gate_path, label="review_gate.json")
        manifest = _read_json(out / "manifest.json", label="manifest.json")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return False, (str(exc),)

    reasons: list[str] = []
    if gate.get("review_gate_schema_version") != REVIEW_GATE_SCHEMA_VERSION:
        reasons.append(
            f"review_gate_schema_version must be {REVIEW_GATE_SCHEMA_VERSION}"
        )
    if gate.get("status") != REVIEW_APPROVED:
        reasons.append("review gate status is not REVIEW APPROVED")
    if gate.get("release_ready") is not True:
        reasons.append("review gate release_ready is not true")
    if gate.get("case_id") != manifest.get("case_id"):
        reasons.append("review gate case_id does not match manifest")
    if gate.get("source_sha256") != manifest.get("source_sha256"):
        reasons.append("review gate source_sha256 does not match manifest")
    if gate.get("bundle_manifest_sha256") != sha256_path(out / "manifest.json"):
        reasons.append("review gate manifest binding does not match")
    if gate.get("integrity_report_sha256") != sha256_path(
        out / "integrity_report.json"
    ):
        reasons.append("review gate report binding does not match")
    if not isinstance(gate.get("review_record_sha256"), str) or not gate.get(
        "review_record_sha256"
    ):
        reasons.append("review gate has no review_record_sha256")
    return not reasons, tuple(reasons)
