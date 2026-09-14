from __future__ import annotations

import json
import sys

from .risk_control import evaluate_risk_register, load_risk_register, render_evaluation


def risk_control() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: clinicops-risk-control <risks.json>")

    try:
        register = load_risk_register(sys.argv[1])
        evaluation = evaluate_risk_register(register)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc

    print(render_evaluation(evaluation), end="")
    if not evaluation.control_pass:
        raise SystemExit(2)
