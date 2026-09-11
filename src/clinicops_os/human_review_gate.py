from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

REVIEW_SCHEMA_VERSION = "1.0"
APPROVED_STATUS = "APPROVED"
NOT_APPROVED_STATUS = "NOT APPROVED — RELEASE BLOCKED"


@dataclass(frozen=True)
class HumanReviewResult:
    approved: bool
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "review_schema_version": REVIEW_SCHEMA_VERSION,
            "status": APPROVED_STATUS if self.approved else NOT_APPROVED_STATUS,
            "approved": self.approved,
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


def evaluate_human_review(record: Mapping[str, object]) -> HumanReviewResult:
    """Evaluate the mandatory human regulatory-review checklist before bundle release.

    This is the executable projection of the "Human regulatory review" gate in
    `sales/commercial-activation-gate.md` and the ClinicOps Execution Handoff review
    checklist. It converts a previously implicit, prose-only step into a fail-closed
    control: every condition below must be explicitly attested `true`, and omission is
    never treated as satisfied. This is a release gate, not a regulatory or legal
    determination, and it does not replace the reviewer's own judgement.
    """

    reasons: list[str] = []

    if record.get("review_schema_version") != REVIEW_SCHEMA_VERSION:
        reasons.append(f"review_schema_version must be {REVIEW_SCHEMA_VERSION}")

    reviewer = record.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        reasons.append("a named human reviewer must be recorded")

    _require_true(
        record,
        "confirmed_evidence_population_and_as_of",
        "reviewer has not confirmed the supplied evidence population and as_of date",
        reasons,
    )
    _require_true(
        record,
        "reviewed_derived_statements_against_evidence",
        "reviewer has not reviewed material derived statements against actual evidence",
        reasons,
    )
    _require_true(
        record,
        "separated_machine_output_from_interpretation",
        "reviewer has not separated machine-detected structure from human regulatory interpretation",
        reasons,
    )
    _require_true(
        record,
        "actor_role_distinctions_preserved",
        "reviewer has not confirmed MF/AR/IM/PR actor-role distinctions are preserved",
        reasons,
    )
    _require_true(
        record,
        "unresolved_facts_left_unresolved",
        "reviewer has not confirmed unresolved facts were left unresolved rather than guessed",
        reasons,
    )
    _require_true(
        record,
        "internal_notes_removed",
        "reviewer has not confirmed internal-only notes are removed from the client-facing bundle",
        reasons,
    )
    _require_true(
        record,
        "approved_for_release",
        "reviewer has not explicitly approved the client-facing interpretation for release",
        reasons,
    )

    return HumanReviewResult(approved=not reasons, reasons=tuple(reasons))


def load_review_record(path: str | Path) -> dict[str, object]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("human review record must be a JSON object")
    return raw


def render_review_result(result: HumanReviewResult) -> str:
    return json.dumps(result.as_dict(), indent=2, ensure_ascii=False) + "\n"
