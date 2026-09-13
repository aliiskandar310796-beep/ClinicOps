from __future__ import annotations

import json
import sys

from .company_run import evaluate_company_run, load_company_run, render_evaluation


def company_run() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: clinicops-company-run <company-run.json>")
    try:
        run = load_company_run(sys.argv[1])
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc

    evaluation = evaluate_company_run(run)
    print(render_evaluation(evaluation), end="")
    if not evaluation.operational_pass:
        raise SystemExit(2)
