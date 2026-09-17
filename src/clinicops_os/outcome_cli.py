from __future__ import annotations

import json
import sys

from .outcome_control import (
    evaluate_outcome_mission,
    load_outcome_mission,
    render_evaluation,
)


def outcome_control() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: clinicops-outcome-control <mission.json>")

    try:
        mission = load_outcome_mission(sys.argv[1])
        evaluation = evaluate_outcome_mission(mission)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc

    print(render_evaluation(evaluation), end="")
    if not evaluation.control_pass:
        raise SystemExit(2)
