from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .bundle import build_pilot_bundle
from .bundle_verify import verify_pilot_bundle
from .human_review_gate import evaluate_human_review, load_review_record
from .pilot_gate import evaluate_standard_pilot, load_preflight_record

DRY_RUN_SCHEMA_VERSION = "1.0"

STEP_PREFLIGHT = "preflight"
STEP_BUNDLE = "bundle"
STEP_HUMAN_REVIEW = "human_review"
STEP_VERIFY = "verify"
ORDERED_STEPS = (STEP_PREFLIGHT, STEP_BUNDLE, STEP_HUMAN_REVIEW, STEP_VERIFY)


@dataclass(frozen=True)
class DryRunStep:
    name: str
    passed: bool
    reasons: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {"step": self.name, "passed": self.passed, "reasons": list(self.reasons)}


@dataclass(frozen=True)
class DryRunResult:
    """Record of one controlled dry run of the standard paid-pilot execution path.

    This exercises the *actual* operator workflow end to end — preflight, bundle
    generation, the mandatory human-review checklist, and final bundle-integrity
    verification — against a synthetic, non-confidential fixture. It proves the
    tooling is founder-independent to run; it does NOT by itself prove
    founder-independent execution. Per `sales/commercial-activation-gate.md`'s
    delegation proof test, that requires either one eligible real paid pilot or two
    complete controlled dry runs — ideally with a genuine qualified human reviewer
    completing the review checkpoint, not a synthetic attestation — each with zero
    ad hoc founder decisions. A single passing run here is at most one data point
    toward that standard, and ANY step below that halts (escalated=True) is exactly
    the kind of undocumented decision that must be captured and resolved in the
    standard operating envelope rather than waved through.
    """

    steps: tuple[DryRunStep, ...]
    manifest: dict[str, object] | None

    @property
    def completed(self) -> bool:
        return all(step.passed for step in self.steps) and len(self.steps) == len(ORDERED_STEPS)

    @property
    def escalated(self) -> bool:
        """True if any step failed and the dry run halted before completion.

        A real escalation in this harness means a documented gate stopped the
        pipeline — never that the pipeline pushed through anyway. Zero escalations
        across two dry runs is part of what the delegation proof test requires.
        """
        return not self.completed

    def as_dict(self) -> dict[str, object]:
        return {
            "dry_run_schema_version": DRY_RUN_SCHEMA_VERSION,
            "completed": self.completed,
            "escalated": self.escalated,
            "steps": [step.as_dict() for step in self.steps],
            "manifest": self.manifest,
            "note": (
                "A completed, non-escalated dry run is at most one of the two runs "
                "(or one eligible real paid pilot) required before founder-independent "
                "execution is considered proven. See "
                "sales/commercial-activation-gate.md's delegation proof test."
            ),
        }


def run_pilot_dry_run(
    *,
    preflight_record_path: str | Path,
    review_record_path: str | Path,
    portfolio_path: str | Path,
    output_dir: str | Path,
    as_of: date,
) -> DryRunResult:
    """Run the standard paid-pilot path end to end against a synthetic fixture.

    Sequence: preflight -> bundle generation -> human-review checkpoint -> integrity
    verification. Each step is the same code a real pilot uses (`pilot_gate`,
    `bundle`, `human_review_gate`, `bundle_verify`) — nothing here is stubbed or
    mocked. The human-review step is a real fail-closed gate: it requires an
    explicit, fully-attested review record and blocks verification without one,
    exactly as a real pilot must never skip review before release.
    """

    steps: list[DryRunStep] = []
    manifest: dict[str, object] | None = None

    preflight_record = load_preflight_record(preflight_record_path)
    preflight_result = evaluate_standard_pilot(preflight_record)
    steps.append(
        DryRunStep(STEP_PREFLIGHT, preflight_result.activated, preflight_result.reasons)
    )
    if not preflight_result.activated:
        return DryRunResult(tuple(steps), manifest)

    try:
        bundle_result = build_pilot_bundle(portfolio_path, output_dir, as_of=as_of)
    except ValueError as exc:
        steps.append(DryRunStep(STEP_BUNDLE, False, (str(exc),)))
        return DryRunResult(tuple(steps), manifest)
    manifest = bundle_result.manifest
    steps.append(DryRunStep(STEP_BUNDLE, True))

    review_record = load_review_record(review_record_path)
    review_result = evaluate_human_review(review_record)
    steps.append(DryRunStep(STEP_HUMAN_REVIEW, review_result.approved, review_result.reasons))
    if not review_result.approved:
        return DryRunResult(tuple(steps), manifest)

    verify_result = verify_pilot_bundle(output_dir, portfolio_path)
    steps.append(DryRunStep(STEP_VERIFY, verify_result.valid, verify_result.errors))

    return DryRunResult(tuple(steps), manifest)


def render_dry_run_result(result: DryRunResult) -> str:
    return json.dumps(result.as_dict(), indent=2, ensure_ascii=False) + "\n"
