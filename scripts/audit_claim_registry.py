from __future__ import annotations

import argparse
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path

from clinicops_os.claim_registry import audit_registry, load_registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit research/claims.jsonl")
    parser.add_argument("--registry", default="research/claims.jsonl")
    parser.add_argument("--as-of", help="ISO date to audit against (default: today, UTC)")
    args = parser.parse_args()

    claims = load_registry(Path(args.registry))
    as_of = date.fromisoformat(args.as_of) if args.as_of else datetime.now(UTC).date()
    findings = audit_registry(claims, as_of=as_of)

    for item in findings:
        print(f"[{item.severity}] {item.claim_id}: {item.message}")

    live = [c for c in claims if not c.superseded_by and c.status.value in {"verified", "qualified"}]
    by_class = Counter(c.risk_class or "?" for c in live)
    print(
        "Live claims by risk class: "
        + ", ".join(f"{cls}={by_class[cls]}" for cls in sorted(by_class))
    )
    errors = [item for item in findings if item.severity == "error"]
    print(
        f"Claim registry: {len(claims)} claims, "
        f"{len(errors)} errors, {len(findings) - len(errors)} warnings."
    )
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
