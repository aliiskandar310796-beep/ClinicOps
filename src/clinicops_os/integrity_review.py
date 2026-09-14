from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .integrity_gate import BUNDLE_SCHEMA_VERSION, sha256_path, verify_bundle_integrity

REVIEW_RECORD_SCHEMA_VERSION = "1.1"
REVIEW_GATE_SCHEMA_VERSION = "1.1"
REVIEW_APPROVED = "REVIEW APPROVED"
REVIEW_INCOMPLETE = "REVIEW INCOMPLETE"
DELIVERY_SCOPE = (
    "ClinicOps output bundle only; not device, controlled-document or submission release "
    "authorization"
)

REQUIRED_ATTESTATIONS = (
    "evidence_population_reviewed",
    "authority_conflicts_reviewed",
    "change_propagation_findings_reviewed",
    "false_positive_risk_reviewed",
    "regulatory_judgement_not_automated",
    "release_interpretation_approved",
)

ALLOWED_FINDING_DISPOSITIONS = (
    "CONFIRMED",
    "RESOLVED_BY_CONTEXT",
    "NOT_ACTIONABLE",
    "FALSE_POSITIVE",
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
    report = _read_json(report_path, label="integrity_report.json")
    findings = report.get("findings", [])
    if not isinstance(findings, list):
        raise TypeError("integrity_report findings must be a list")
    dispositions: dict[str, str] = {}
    for finding in findings:
        if not isinstance(finding, dict):
            raise TypeError("integrity_report finding must be a JSON object")
        finding_id = finding.get("finding_id")
        if not isinstance(finding_id, str) or not finding_id:
            raise ValueError("integrity_report finding has no finding_id")
        dispositions[finding_id] = ""

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
        "review_minutes": 0,
        "decision": "",
        "notes": "",
        "finding_dispositions": dispositions,
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
    try:
        report = _read_json(report_path, label="integrity_report.json")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        reasons.append(f"report: {exc}")
        report = {}

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
            completed = date.fromisoformat(completed_on)
            if completed > date.today():
                reasons.append("review_completed_on cannot be in the future")
        except ValueError:
            reasons.append("review_completed_on must be an ISO date (YYYY-MM-DD)")

    review_minutes = review_record.get("review_minutes")
    if (
        isinstance(review_minutes, bool)
        or not isinstance(review_minutes, int)
        or not 1 <= review_minutes <= 2880
    ):
        reasons.append("review_minutes must be an integer from 1 to 2880")

    findings = report.get("findings", [])
    expected_ids: set[str] = set()
    if isinstance(findings, list):
        for finding in findings:
            if isinstance(finding, dict) and isinstance(finding.get("finding_id"), str):
                expected_ids.add(str(finding["finding_id"]))
    else:
        reasons.append("integrity_report findings must be a list")

    dispositions = review_record.get("finding_dispositions")
    if not isinstance(dispositions, dict):
        reasons.append("finding_dispositions must be a JSON object")
        dispositions = {}
    supplied_ids = set(str(key) for key in dispositions)
    missing_ids = sorted(expected_ids - supplied_ids)
    unknown_ids = sorted(supplied_ids - expected_ids)
    if missing_ids:
        reasons.append(f"finding_dispositions missing current findings: {missing_ids}")
    if unknown_ids:
        reasons.append(f"finding_dispositions contains unknown findings: {unknown_ids}")
    for finding_id in sorted(expected_ids):
        disposition = dispositions.get(finding_id)
        if disposition not in ALLOWED_FINDING_DISPOSITIONS:
            reasons.append(
                f"{finding_id} disposition must be one of "
                + ", ".join(ALLOWED_FINDING_DISPOSITIONS)
            )

    notes = review_record.get("notes")
    if manifest.get("gate_status") != "PASS" and (
        not isinstance(notes, str) or not notes.strip()
    ):
        reasons.append("notes are required when the automated gate status is not PASS")

    if review_record.get("decision") != "APPROVE":
        reasons.append("decision must be APPROVE for external delivery of the ClinicOps output")
    for attestation in REQUIRED_ATTESTATIONS:
        if review_record.get(attestation) is not True:
            reasons.append(f"review attestation is not confirmed: {attestation}")

    if reasons:
        return IntegrityReviewResult(False, tuple(reasons), None)

    disposition_counts = Counter(str(dispositions[finding_id]) for finding_id in expected_ids)
    total_findings = len(expected_ids)
    false_positive_count = disposition_counts.get("FALSE_POSITIVE", 0)
    review_metrics = {
        "review_minutes": review_minutes,
        "findings_reviewed": total_findings,
        "confirmed": disposition_counts.get("CONFIRMED", 0),
        "resolved_by_context": disposition_counts.get("RESOLVED_BY_CONTEXT", 0),
        "not_actionable": disposition_counts.get("NOT_ACTIONABLE", 0),
        "false_positive": false_positive_count,
        "false_positive_rate": (
            false_positive_count / total_findings if total_findings else None
        ),
    }

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
        "clinicops_output_delivery_ready": True,
        "delivery_scope": DELIVERY_SCOPE,
        "review_metrics": review_metrics,
        "limitations": (
            "Approval records completion of the declared human review for this exact ClinicOps "
            "output bundle. It does not authorize release of a device, controlled document or "
            "regulatory submission, and it does not convert the automated screen into a legal "
            "or compliance determination."
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
    if gate.get("clinicops_output_delivery_ready") is not True:
        reasons.append("review gate clinicops_output_delivery_ready is not true")
    if gate.get("delivery_scope") != DELIVERY_SCOPE:
        reasons.append("review gate delivery_scope is missing or invalid")
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
    metrics = gate.get("review_metrics")
    if not isinstance(metrics, dict) or not isinstance(metrics.get("review_minutes"), int):
        reasons.append("review gate has no valid review_metrics")
    return not reasons, tuple(reasons)
