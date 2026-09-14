from __future__ import annotations

import json
import sys

from .sales_swarm import evaluate_leads, load_leads, load_swarm, validate_swarm


def sales_swarm() -> None:
    if len(sys.argv) not in {2, 3}:
        raise SystemExit("usage: clinicops-sales-swarm <swarm.json> [lead-candidates.json]")

    try:
        swarm = load_swarm(sys.argv[1])
        errors = validate_swarm(swarm)
        if errors:
            raise ValueError("; ".join(errors))
        payload: dict[str, object] = {
            "schema_version": "1.0",
            "sales_cells": len(swarm.cells),
            "lead_target": sum(cell.lead_quota for cell in swarm.cells),
            "status": "SWARM READY",
        }
        if len(sys.argv) == 3:
            payload["lead_gate"] = evaluate_leads(load_leads(sys.argv[2]))
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc

    print(json.dumps(payload, indent=2, sort_keys=True))
