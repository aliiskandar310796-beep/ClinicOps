from __future__ import annotations

import json
import sys

from .pilot_gate import load_preflight_record
from .review_gate import (
    evaluate_review_gate,
    load_review_record,
    prepare_review_record,
    render_review_record,
    render_review_result,
)


def pilot_review_prepare() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: clinicops-pilot-review-prepare <activation-record.json> <output-dir>"
        )
    try:
        activation = load_preflight_record(sys.argv[1])
        record = prepare_review_record(activation, sys.argv[2])
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print(render_review_record(record), end="")


def pilot_review_gate() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: clinicops-pilot-review-gate "
            "<activation-record.json> <review-record.json> <output-dir>"
        )
    try:
        activation = load_preflight_record(sys.argv[1])
        review = load_review_record(sys.argv[2])
        result = evaluate_review_gate(activation, review, sys.argv[3])
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print(render_review_result(result), end="")
    if not result.approved:
        raise SystemExit(2)
