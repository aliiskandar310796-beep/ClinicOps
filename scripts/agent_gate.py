from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from clinicops_os.agents import gate_payload, load_agent_tasks


def main() -> None:
    if len(sys.argv) not in {2, 3}:
        raise SystemExit("usage: python scripts/agent_gate.py <tasks.json> [YYYY-MM-DD]")

    root = Path(__file__).resolve().parents[1]
    as_of = date.fromisoformat(sys.argv[2]) if len(sys.argv) == 3 else date.today()
    try:
        tasks = load_agent_tasks(sys.argv[1])
        payload = gate_payload(
            tasks,
            registry_path=root / "research" / "claims.jsonl",
            as_of=as_of,
        )
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    summary = payload["summary"]
    if isinstance(summary, dict) and summary.get("failed"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
