from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .pilot_gate import evaluate_standard_pilot

REVIEW_RECORD_SCHEMA_VERSION = "1.0"
EXPECTED_BUNDLE_SCHEMA_VERSION = "1.1"
REVIEW_APPROVED_STATUS = "REVIEW APPROVED"
REVIEW_INCOMPLETE_STATUS = "REVIEW INCOMPLETE"

REQUIRED_REVIEW_ATTESTATIONS = (
    "evidence_population_confirmed",
    "warnings_and_information_gaps_reviewed",
    "material_derived_statements_reviewed",
    "structural_signals_separated_from_regulatory_judgement",
    "actor_role_distinctions_reviewed",
    "unsupported_facts_left_unresolved",
    "internal_only_notes_removed",
    "client_facing_interpretation_approved",
)


@dataclass(frozen=True)
class PilotReviewResult:
    approved: bool
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "review_record_schema_version": REVIEW_RECORD_SCHEMA_VERSION,
            "bundle_schema_version": EXPECTED_BUNDLE_SCHEMA_VERSION,
            "approved": self.approved,
            "status": REVIEW_APPROVED_STATUS if self.approved else REVIEW_INCOMPLETE_STATUS,
            "reasons": list(self.reasons),
        }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json_object(path: str | Path, *, label: str) -> dict[str, object]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError(f"{label} must be a JSON object")
    return raw


def _load_manifest(output_dir: str | Path) -> tuple[Path, dict[str, object]]:
    manifest_path = Path(output_dir) / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("manifest.json is missing")
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("manifest.json must contain a JSON object")
    if raw.get("bundle_schema_version") != EXPECTED_BUNDLE_SCHEMA_VERSION:
        raise ValueError(
            f"bundle_schema_version must be {EXPECTED_BUNDLE_SCHEMA_VERSION}"
        )
    return manifest_path, raw


def prepare_review_record(
    activation_record: Mapping[str, object],
    output_dir: str | Path,
) -> dict[str, object]:
    """Prepare a fail-closed human-review attestation bound to the final bundle manifest.

    All substantive review attestations start false. A reviewer must change them only
    after completing the corresponding review step. Preparing this record is not review.
    """

    preflight = evaluate_standard_pilot(activation_record)
    if not preflight.activated:
        detail = "; ".join(preflight.reasons)
        raise ValueError(f"pilot activation is not valid: {detail}")

    manifest_path, manifest = _load_manifest(output_dir)
    reviewer = activation_record.get("human_reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("activation record has no named human reviewer")

    record: dict[str, object] = {
        "record_schema_version": REVIEW_RECORD_SCHEMA_VERSION,
        "bundle_schema_version": EXPECTED_BUNDLE_SCHEMA_VERSION,
        "human_reviewer": reviewer.strip(),
        "reviewed_as_of": manifest.get("as_of"),
        "bundle_manifest_sha256": _sha256(manifest_path),
        "source_sha256": manifest.get("source_sha256"),
        "review_completed_on": "",
        "founder_transaction_decision_required": False,
        "unplanned_exception": False,
    }
    for key in REQUIRED_REVIEW_ATTESTATIONS:
        record[key] = False
    return record


def evaluate_review_gate(
    activation_record: Mapping[str, object],
    review_record: Mapping[str, object],
    output_dir: str | Path,
) -> PilotReviewResult:
    """Validate recorded human-review completion for the exact final bundle.

    This gate validates the review record and its binding to the bundle. It cannot
    establish whether the reviewer performed the work truthfully, and it does not
    replace professional regulatory judgement.
    """

    reasons: list[str] = []
    preflight = evaluate_standard_pilot(activation_record)
    if not preflight.activated:
        reasons.append("activation record is not ACTIVATED")
        reasons.extend(f"activation: {reason}" for reason in preflight.reasons)

    try:
        manifest_path, manifest = _load_manifest(output_dir)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return PilotReviewResult(False, (str(exc),))

    if review_record.get("record_schema_version") != REVIEW_RECORD_SCHEMA_VERSION:
        reasons.append(
            f"record_schema_version must be {REVIEW_RECORD_SCHEMA_VERSION}"
        )
    if review_record.get("bundle_schema_version") != EXPECTED_BUNDLE_SCHEMA_VERSION:
        reasons.append(
            f"bundle_schema_version must be {EXPECTED_BUNDLE_SCHEMA_VERSION}"
        )

    assigned_reviewer = activation_record.get("human_reviewer")
    recorded_reviewer = review_record.get("human_reviewer")
    if (
        not isinstance(assigned_reviewer, str)
        or not isinstance(recorded_reviewer, str)
        or recorded_reviewer.strip() != assigned_reviewer.strip()
    ):
        reasons.append("human_reviewer must match the activated pilot reviewer")

    if review_record.get("reviewed_as_of") != manifest.get("as_of"):
        reasons.append("reviewed_as_of does not match the final bundle as_of date")
    if review_record.get("source_sha256") != manifest.get("source_sha256"):
        reasons.append("source_sha256 does not match the final bundle manifest")
    if review_record.get("bundle_manifest_sha256") != _sha256(manifest_path):
        reasons.append("bundle_manifest_sha256 does not match the final manifest")

    completed_on = review_record.get("review_completed_on")
    if not isinstance(completed_on, str) or not completed_on.strip():
        reasons.append("review_completed_on must be recorded")
    else:
        try:
            date.fromisoformat(completed_on)
        except ValueError:
            reasons.append("review_completed_on must be an ISO date (YYYY-MM-DD)")

    for key in REQUIRED_REVIEW_ATTESTATIONS:
        if review_record.get(key) is not True:
            reasons.append(f"review attestation is not confirmed: {key}")

    if review_record.get("founder_transaction_decision_required") is not False:
        reasons.append(
            "founder_transaction_decision_required must be explicitly false for the standard path"
        )
    if review_record.get("unplanned_exception") is not False:
        reasons.append("unplanned_exception must be explicitly false for the standard path")

    return PilotReviewResult(approved=not reasons, reasons=tuple(reasons))


def load_review_record(path: str | Path) -> dict[str, object]:
    return _read_json_object(path, label="review record")


def render_review_record(record: Mapping[str, object]) -> str:
    return json.dumps(dict(record), indent=2, ensure_ascii=False) + "\n"


def render_review_result(result: PilotReviewResult) -> str:
    return json.dumps(result.as_dict(), indent=2, ensure_ascii=False) + "\n"
