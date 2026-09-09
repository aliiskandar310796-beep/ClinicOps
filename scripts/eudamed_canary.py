from __future__ import annotations

import json
from pathlib import Path

from clinicops_eudamed.canary import build_snapshot, probe


def main() -> None:
    output = build_snapshot([probe(0), probe(30_000), probe(32_000)])
    path = Path("research/canary/latest.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
