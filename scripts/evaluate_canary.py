from __future__ import annotations

import json
import os
from pathlib import Path

from clinicops_eudamed.canary_eval import evaluate_snapshot, has_errors

BASELINE = Path("research/canary/baseline.json")
LATEST = Path("research/canary/latest.json")


def main() -> int:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    latest = json.loads(LATEST.read_text(encoding="utf-8"))
    findings = evaluate_snapshot(baseline, latest)

    github_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    if not findings:
        print("EUDAMED canary: no reviewed-contract drift detected.")
        return 0

    for item in findings:
        page = f"page {item.page}" if item.page is not None else "canary"
        text = f"{page}: {item.message}"
        print(f"[{item.severity}] {text}")
        if github_actions and item.severity in {"warning", "error"}:
            print(f"::{item.severity} title=EUDAMED canary drift::{text}")

    return 2 if has_errors(findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
