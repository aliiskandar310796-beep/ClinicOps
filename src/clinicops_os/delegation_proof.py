from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

PROOF_SCHEMA_VERSION = "1.1"
PAID_PILOT = "paid_pilot"
CONTROLLED_DRY_RUN = "controlled_dry_run"
VALID_RUN_KINDS = {PAID_PILOT, CONTROLLED_DRY_RUN}
PROVEN_STATUS = "FOUNDER-INDEPENDENT EXECUTION PROVEN"
NOT_PROVEN_STATUS = "FOUNDER-INDEPENDENT EXECUTION NOT PROVEN"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_SHA256_FIELDS = (
    "activation_record_sha256",
    "preflight_result_sha256",
    "review_record_sha256",
    "review_gate_result_sha256",
    "bundle_manifest_sha256",
    "bundle_verification_record_sha256",
    "source_sha256",
)


@dataclass(frozen=True)
class DelegationRunResult:
    run_id: str
    run_kind: str
    qualifies: bool
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "run_kind": self.run_kind,
            "qualifies": self.qualifies,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class DelegationProofResult:
    proven: bool
    qualifying_paid_pilot_ids: tuple[str, ...]
    qualifying_dry_run_ids: tuple[str, ...]
    run_results: tuple[DelegationRunResult, ...]
    evidence_errors: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "proof_schema_version": PROOF_SCHEMA_VERSION,
            "proven": self.proven,
            "status": PROVEN_STATUS if self.proven else NOT_PROVEN_STATUS,
            "qualifying_paid_pilot_ids": list(self.qualifying_paid_pilot_ids),
            "qualifying_dry_run_ids": list(self.qualifying_dry_run_ids),
            "evidence_errors": list(self.evidence_errors),
            "runs": [result.as_dict() for result in self.run_results],
        }


def _require_true(
    record: Mapping[str, object], key: str, message: str, reasons: list[str]
) -> None:
    if record.get(key) is not True:
        reasons.append(message)


def _require_false(
    record: Mapping[str, object], key: str, message: str, reasons: list[str]
) -> None:
    if record.get(key) is not False:
        reasons.append(message)


def _require_nonempty_string(
    record: Mapping[str, object], key: str, message: str, reasons: list[str]
) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        reasons.append(message)
        return ""
    return value.strip()


def _require_iso_date(
    record: Mapping[str, object], key: str, message: str, reasons: list[str]
) -> None:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        reasons.append(message)
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        reasons.append(message)


def _require_sha256(
    record: Mapping[str, object], key: str, message: str, reasons: list[str]
) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        reasons.append(message)
        return ""
    return value


def _artifact_fingerprint(record: Mapping[str, object]) -> tuple[str, ...]:
    return tuple(str(record.get(key, "")) for key in ARTIFACT_SHA256_FIELDS)


def evaluate_delegation_run(record: Mapping[str, object]) -> DelegationRunResult:
    """Evaluate one private proof run against the standard delegation proof policy.

    This evaluator checks recorded evidence, explicit attestations and immutable artifact
    bindings. It cannot prove that a human performed a review truthfully or that a private
    record is genuine. Real proof records must therefore remain controlled operational
    records, not CI output.
    """

    reasons: list[str] = []
    if record.get("record_schema_version") != PROOF_SCHEMA_VERSION:
        reasons.append(f"record_schema_version must be {PROOF_SCHEMA_VERSION}")

    run_id = _require_nonempty_string(
        record, "run_id", "run_id must be recorded", reasons
    )
    run_kind = _require_nonempty_string(
        record, "run_kind", "run_kind must be recorded", reasons
    )
    if run_kind and run_kind not in VALID_RUN_KINDS:
        reasons.append("run_kind must be paid_pilot or controlled_dry_run")

    _require_iso_date(
        record,
        "execution_completed_on",
        "execution_completed_on must be an ISO date (YYYY-MM-DD)",
        reasons,
    )
    _require_nonempty_string(
        record, "operator", "operator must be identified", reasons
    )
    _require_nonempty_string(
        record, "human_reviewer", "human_reviewer must be identified", reasons
    )

    for key in ARTIFACT_SHA256_FIELDS:
        _require_sha256(
            record,
            key,
            f"{key} must be a lowercase 64-character SHA-256 binding",
            reasons,
        )

    _require_true(
        record,
        "private_operational_record",
        "delegation proof must come from an approved private operational record",
        reasons,
    )
    _require_true(
        record,
        "proof_use_allowed",
        "record is not explicitly authorised for delegation-proof use",
        reasons,
    )
    _require_false(
        record,
        "ci_or_automated_smoke",
        "CI or automated smoke executions cannot count as delegation proof",
        reasons,
    )
    _require_true(
        record,
        "execution_completed",
        "run did not complete the full controlled execution path",
        reasons,
    )

    _require_true(
        record,
        "qualification_stage_completed",
        "run did not complete the qualified-conversation/qualification stage",
        reasons,
    )
    _require_true(
        record,
        "written_scope_stage_completed",
        "run did not complete the written-scope stage",
        reasons,
    )
    if record.get("preflight_status") != "ACTIVATED":
        reasons.append("preflight_status must be ACTIVATED")
    _require_true(
        record,
        "intake_validated",
        "portfolio intake validation was not completed successfully",
        reasons,
    )
    _require_true(
        record,
        "bundle_generated",
        "controlled schema-1.1 bundle was not generated",
        reasons,
    )
    if record.get("human_review_status") != "REVIEW APPROVED":
        reasons.append("human_review_status must be REVIEW APPROVED")
    if record.get("bundle_integrity_status") != "VERIFIED":
        reasons.append("bundle_integrity_status must be VERIFIED")
    _require_true(
        record,
        "delivery_stage_completed",
        "run did not complete the controlled delivery/release stage",
        reasons,
    )

    _require_true(
        record,
        "evidence_gate_satisfied",
        "evidence gate is not recorded as satisfied",
        reasons,
    )
    _require_true(
        record,
        "claim_gate_satisfied",
        "claim-safety gate is not recorded as satisfied",
        reasons,
    )
    _require_true(
        record,
        "commercial_gate_satisfied",
        "commercial activation gate is not recorded as satisfied",
        reasons,
    )
    _require_true(
        record,
        "data_handling_gate_satisfied",
        "data-handling gate is not recorded as satisfied",
        reasons,
    )
    _require_true(
        record,
        "qualified_human_review_completed",
        "qualified human review is not recorded as completed",
        reasons,
    )

    _require_false(
        record,
        "founder_transaction_decision_required",
        "a founder transaction-level decision was required",
        reasons,
    )
    _require_false(
        record,
        "unplanned_exception",
        "an unplanned exception occurred",
        reasons,
    )
    _require_false(
        record,
        "nonstandard_scope_claim_or_commercial_exception",
        "a non-standard scope, claim, or commercial exception occurred",
        reasons,
    )

    _require_true(
        record,
        "closeout_completed",
        "run did not complete controlled closeout",
        reasons,
    )
    _require_true(
        record,
        "commercial_learning_captured_privately",
        "commercial learning was not captured privately against EXP-001",
        reasons,
    )

    if run_kind == PAID_PILOT:
        _require_true(
            record,
            "real_paid_pilot",
            "paid-pilot proof must represent a real eligible paid pilot",
            reasons,
        )
        _require_true(
            record,
            "payment_or_procurement_path_followed",
            "paid-pilot payment/procurement path was not followed through closeout",
            reasons,
        )
    elif run_kind == CONTROLLED_DRY_RUN:
        _require_false(
            record,
            "real_paid_pilot",
            "controlled dry run must not be represented as a real paid pilot",
            reasons,
        )
        _require_true(
            record,
            "full_operator_dry_run",
            "dry-run proof must be a complete operator dry run, not a unit/CI smoke",
            reasons,
        )

    return DelegationRunResult(
        run_id=run_id,
        run_kind=run_kind,
        qualifies=not reasons,
        reasons=tuple(reasons),
    )


def evaluate_delegation_proof(
    records: Sequence[Mapping[str, object]],
) -> DelegationProofResult:
    """Apply the one-paid-pilot-or-two-dry-runs proof threshold fail-closed."""

    results = tuple(evaluate_delegation_run(record) for record in records)
    evidence_errors: list[str] = []

    ids = [result.run_id for result in results if result.run_id]
    duplicate_ids = sorted({run_id for run_id in ids if ids.count(run_id) > 1})
    if duplicate_ids:
        evidence_errors.append(
            "run_id values must be unique: " + ", ".join(duplicate_ids)
        )

    qualifying_records = [
        record
        for record, result in zip(records, results, strict=True)
        if result.qualifies
    ]
    fingerprints = [_artifact_fingerprint(record) for record in qualifying_records]
    if len(fingerprints) != len(set(fingerprints)):
        evidence_errors.append(
            "qualifying runs must have distinct controlled-artifact SHA-256 bindings; "
            "copying one execution under a new run_id is not independent proof"
        )

    if evidence_errors:
        paid_ids: tuple[str, ...] = ()
        dry_ids: tuple[str, ...] = ()
    else:
        paid_ids = tuple(
            result.run_id
            for result in results
            if result.qualifies and result.run_kind == PAID_PILOT
        )
        dry_ids = tuple(
            result.run_id
            for result in results
            if result.qualifies and result.run_kind == CONTROLLED_DRY_RUN
        )

    proven = not evidence_errors and (len(paid_ids) >= 1 or len(dry_ids) >= 2)
    return DelegationProofResult(
        proven=proven,
        qualifying_paid_pilot_ids=paid_ids,
        qualifying_dry_run_ids=dry_ids,
        run_results=results,
        evidence_errors=tuple(evidence_errors),
    )


def load_delegation_records(path: str | Path) -> list[dict[str, object]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = raw.get("runs") if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        raise TypeError(
            "delegation proof input must be a JSON list or an object with a 'runs' list"
        )
    if not all(isinstance(item, dict) for item in rows):
        raise TypeError("every delegation proof run must be a JSON object")
    return rows


def render_delegation_proof(result: DelegationProofResult) -> str:
    return json.dumps(result.as_dict(), indent=2, ensure_ascii=False) + "\n"
