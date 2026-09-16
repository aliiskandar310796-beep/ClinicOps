from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "product_opportunity_gate.example.json"

REQUIRED_STATES = {"REJECTED", "OBSERVED_PAIN", "PAID_PATTERN", "CORE_MVP_CANDIDATE"}

CORE_THRESHOLDS = {
    "completed_real_cases": 10,
    "independent_organizations_or_workflows": 3,
    "buyers_willing_to_pay": 5,
    "repeat_purchases_or_commitments": 2,
    "common_io_contract_case_share_pct": 80,
}

CORE_BOOLEANS = {
    "buyer_problem_spontaneously_reported",
    "competitor_gap_documented",
    "measurable_value_documented",
    "standardized_delivery_reduces_marginal_effort",
    "credible_repeat_use_path",
    "human_authority_boundaries_explicit",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def validate_opportunity(item: dict) -> None:
    for key in ("id", "title", "promotion_state", "problem_statement", "evidence"):
        if key not in item:
            fail(f"opportunity missing required field: {key}")

    state = item["promotion_state"]
    if state not in REQUIRED_STATES:
        fail(f"{item['id']}: unsupported promotion_state {state!r}")

    evidence = item["evidence"]
    if not isinstance(evidence, dict):
        fail(f"{item['id']}: evidence must be an object")

    required_evidence_keys = set(CORE_THRESHOLDS) | CORE_BOOLEANS
    missing = required_evidence_keys - set(evidence)
    if missing:
        fail(f"{item['id']}: missing evidence fields: {', '.join(sorted(missing))}")

    for key in CORE_THRESHOLDS:
        value = evidence[key]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            fail(f"{item['id']}: {key} must be a non-negative integer")

    if evidence["common_io_contract_case_share_pct"] > 100:
        fail(f"{item['id']}: common_io_contract_case_share_pct cannot exceed 100")

    for key in CORE_BOOLEANS:
        if not isinstance(evidence[key], bool):
            fail(f"{item['id']}: {key} must be boolean")

    if state == "REJECTED" and not item.get("kill_reason"):
        fail(f"{item['id']}: REJECTED opportunities require kill_reason")

    if state == "CORE_MVP_CANDIDATE":
        for key, minimum in CORE_THRESHOLDS.items():
            if evidence[key] < minimum:
                fail(
                    f"{item['id']}: CORE_MVP_CANDIDATE blocked; "
                    f"{key}={evidence[key]} < {minimum}"
                )
        failed_booleans = sorted(key for key in CORE_BOOLEANS if not evidence[key])
        if failed_booleans:
            fail(
                f"{item['id']}: CORE_MVP_CANDIDATE blocked; false gates: "
                + ", ".join(failed_booleans)
            )


def main() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        fail("unsupported schema_version")

    opportunities = data.get("opportunities")
    if not isinstance(opportunities, list) or not opportunities:
        fail("opportunities must be a non-empty list")

    seen: set[str] = set()
    for item in opportunities:
        if not isinstance(item, dict):
            fail("each opportunity must be an object")
        opportunity_id = item.get("id")
        if opportunity_id in seen:
            fail(f"duplicate opportunity id: {opportunity_id}")
        seen.add(opportunity_id)
        validate_opportunity(item)

    print(
        json.dumps(
            {
                "status": "VALID",
                "schema_version": data["schema_version"],
                "opportunities": len(opportunities),
                "core_candidate_gate": CORE_THRESHOLDS,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
