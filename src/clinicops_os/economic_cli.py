from __future__ import annotations

import json
import sys

from .economic_validation import (
    evaluate_economic_ledger,
    load_economic_ledger,
    render_evaluation,
)


def economic_validation() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: clinicops-economic-validation <economic-validation.json>")

    try:
        ledger = load_economic_ledger(sys.argv[1])
        evaluation = evaluate_economic_ledger(ledger)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc

    print(render_evaluation(evaluation), end="")
    if not evaluation.control_pass:
        raise SystemExit(2)
