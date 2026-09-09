from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from clinicops_os.claim_registry import audit_registry, load_registry


def main() -> int:
    path = Path("research/claims.jsonl")
    claims = load_registry(path)
    as_of = datetime.now(UTC).date()
    findings = audit_registry(claims, as_of=as_of)

    for item in findings:
        print(f"[{item.severity}] {item.claim_id}: {item.message}")

    errors = [item for item in findings if item.severity == "error"]
    print(
        f"Claim registry: {len(claims)} claims, "
        f"{len(errors)} errors, {len(findings) - len(errors)} warnings."
    )
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
