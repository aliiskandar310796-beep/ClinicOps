from __future__ import annotations

import json
import sys

from .delegation_proof import (
    evaluate_delegation_proof,
    load_delegation_records,
    render_delegation_proof,
)


def delegation_proof() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: clinicops-delegation-proof <proof-runs.json>")
    try:
        records = load_delegation_records(sys.argv[1])
        result = evaluate_delegation_proof(records)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print(render_delegation_proof(result), end="")
    if not result.proven:
        raise SystemExit(2)
