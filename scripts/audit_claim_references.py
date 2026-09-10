from __future__ import annotations

import re
import sys
from pathlib import Path

from clinicops_os.claim_registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "research" / "claims.jsonl"
DEFAULT_TARGETS = (
    ROOT / "offers",
    ROOT / "sales",
    ROOT / "research",
    ROOT / "content",
    ROOT / "website",
    ROOT / "README.md",
)
CLAIM_REF_RE = re.compile(r"\bCO-CLM-\d{4}\b")


def iter_markdown(targets: list[Path]):
    for target in targets:
        if target.is_dir():
            yield from sorted(target.rglob("*.md"))
        elif target.is_file() and target.suffix.lower() == ".md":
            yield target


def main() -> int:
    known = {claim.claim_id for claim in load_registry(REGISTRY)}
    targets = [Path(arg) for arg in sys.argv[1:]] or list(DEFAULT_TARGETS)
    unknown: list[tuple[Path, str]] = []
    refs = 0

    for path in iter_markdown(targets):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for claim_id in sorted(set(CLAIM_REF_RE.findall(text))):
            refs += 1
            if claim_id not in known:
                unknown.append((path, claim_id))

    if unknown:
        for path, claim_id in unknown:
            try:
                display = path.relative_to(ROOT)
            except ValueError:
                display = path
            print(f"unknown claim reference: {display}: {claim_id}")
        return 2

    print(f"claim references: {refs} references checked; all resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
