from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

PREFLIGHT_SCHEMA_VERSION = "1.0"
STANDARD_ENVELOPE_VERSION = "standard-paid-pilot-1.0"
ACTIVATED_STATUS = "ACTIVATED"
NOT_ACTIVATED_STATUS = "NON-STANDARD — NOT ACTIVATED"
APPROVED_ACTIVATION_CONDITIONS = {
    "upfront_payment",
    "deposit_or_first_milestone",
    "accepted_po_or_signed_commitment",
}


@dataclass(frozen=True)
class PilotPreflightResult:
    activated: bool
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "envelope_version": STANDARD_ENVELOPE_VERSION,
            "status": ACTIVATED_STATUS if self.activated else NOT_ACTIVATED_STATUS,
            "activated": self.activated,
            "reasons": list(self.reasons),
        }


def _require_true(
    record: Mapping[str, object],
    key: str,
    message: str,
    reasons: list[str],
) -> None:
    if record.get(key) is not True:
        reasons.append(message)


def _require_false(
    record: Mapping[str, object],
    key: str,
    message: str,
    reasons: list[str],
) -> None:
    if record.get(key) is not False:
        reasons.append(message)


def evaluate_standard_pilot(record: Mapping[str, object]) -> PilotPreflightResult:
    """Evaluate the founder-independent Class III Transition Map pilot envelope.

    The record belongs in approved private storage for real buyers. This evaluator is a
    fail-closed operational control, not a legal or regulatory determination.
    """

    reasons: list[str] = []

    if record.get("record_schema_version") != PREFLIGHT_SCHEMA_VERSION:
        reasons.append(f"record_schema_version must be {PREFLIGHT_SCHEMA_VERSION}")
    if record.get("experiment_id") != "EXP-001":
        reasons.append("pilot must be governed by EXP-001")
    if record.get("commercial_form") != "paid_pilot":
        reasons.append("commercial_form must be paid_pilot")

    _require_true(record, "exp_001_eligible", "buyer is not confirmed EXP-001 eligible", reasons)
    _require_true(
        record,
        "scope_accepted_in_writing",
        "written scope acceptance is not confirmed",
        reasons,
    )
    _require_true(
        record,
        "commercial_owner_identified",
        "commercial/procurement owner is not identified",
        reasons,
    )
    _require_true(record, "population_bounded", "evidence population is not bounded", reasons)
    _require_true(
        record,
        "standard_deliverables",
        "deliverables are outside the standard pilot template",
        reasons,
    )
    _require_true(
        record,
        "standard_commercial_terms",
        "commercial terms are outside the approved standard",
        reasons,
    )

    activation_condition = record.get("activation_condition")
    if (
        not isinstance(activation_condition, str)
        or activation_condition not in APPROVED_ACTIVATION_CONDITIONS
    ):
        reasons.append("activation_condition is not an approved paid-pilot condition")
    _require_true(
        record,
        "activation_condition_satisfied",
        "commercial activation condition is not satisfied",
        reasons,
    )

    _require_true(
        record,
        "private_storage_approved",
        "approved private storage route is not confirmed",
        reasons,
    )
    _require_true(
        record,
        "buyer_authorised_to_share",
        "buyer authority to share the evidence is not confirmed",
        reasons,
    )
    _require_false(
        record,
        "patient_identifiable_data",
        "patient-identifiable data is present, requested, or not explicitly excluded",
        reasons,
    )

    if record.get("bundle_schema_version") != "1.1":
        reasons.append("bundle_schema_version must be 1.1")

    reviewer = record.get("human_reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        reasons.append("a named human reviewer must be assigned before kickoff")
    _require_true(
        record,
        "human_reviewer_qualified",
        "assigned human reviewer is not confirmed qualified",
        reasons,
    )

    _require_false(
        record,
        "novel_public_claim",
        "scope introduces a novel public claim",
        reasons,
    )
    _require_false(
        record,
        "custom_regulatory_conclusion",
        "scope requests a custom regulatory conclusion",
        reasons,
    )
    _require_false(
        record,
        "nonstandard_liability",
        "scope contains non-standard liability or legal terms",
        reasons,
    )
    _require_false(
        record,
        "unsupported_interpretation",
        "scope requires unsupported interpretation",
        reasons,
    )

    return PilotPreflightResult(activated=not reasons, reasons=tuple(reasons))


def load_preflight_record(path: str | Path) -> dict[str, object]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("preflight record must be a JSON object")
    return raw


def render_preflight_result(result: PilotPreflightResult) -> str:
    return json.dumps(result.as_dict(), indent=2, ensure_ascii=False) + "\n"
