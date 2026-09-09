from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

from clinicops_os.claim_registry import load_registry
from clinicops_os.publication import build_publication_pack

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "research" / "claims.jsonl"
USE_RE = re.compile(r"<!--\s*claim-use:\s*([a-z-]+)\s*-->", re.IGNORECASE)
IDS_RE = re.compile(r"<!--\s*claim-ids:\s*([^>]+?)\s*-->", re.IGNORECASE)
REF_RE = re.compile(r"CO-CLM-\d{4}")


def validate_file(path: Path, *, as_of: date) -> list[str]:
    text = path.read_text(encoding="utf-8")
    use_match = USE_RE.search(text)
    ids_match = IDS_RE.search(text)

    if not use_match and not ids_match:
        return []
    if not use_match or not ids_match:
        return [f"{path}: claim-use and claim-ids metadata must appear together"]

    use = use_match.group(1).lower()
    declared = [item.strip() for item in ids_match.group(1).split(",") if item.strip()]
    declared_set = set(declared)
    referenced = set(REF_RE.findall(text))
    problems: list[str] = []

    undeclared = referenced - declared_set
    if undeclared:
        problems.append(
            f"{path}: referenced but undeclared claim IDs: {', '.join(sorted(undeclared))}"
        )

    try:
        build_publication_pack(
            load_registry(REGISTRY),
            declared,
            title=str(path.relative_to(ROOT)),
            use=use,
            as_of=as_of,
        )
    except ValueError as exc:
        problems.append(f"{path}: {exc}")
    return problems


def iter_markdown(args: list[str]) -> list[Path]:
    roots = [ROOT / arg for arg in args] if args else [ROOT / "website"]
    files: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix.lower() == ".md":
            files.append(root)
        elif root.is_dir():
            files.extend(sorted(root.rglob("*.md")))
    return files


def main() -> int:
    problems: list[str] = []
    checked = 0
    today = date.today()  # noqa: DTZ011 — content expiry is intentionally calendar-date based.
    for path in iter_markdown(sys.argv[1:]):
        text = path.read_text(encoding="utf-8")
        if USE_RE.search(text) or IDS_RE.search(text):
            checked += 1
            problems.extend(validate_file(path, as_of=today))

    if problems:
        print("Content claim validation failed:")
        for problem in problems:
            print(f"- {problem}")
        return 2

    print(f"content claim validation: {checked} governed file(s), 0 errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
