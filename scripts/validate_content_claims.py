"""Claim gate for governed content.

Two surfaces are gated against research/claims.jsonl:

- website/*.md  (controlled sources; claim-use / claim-ids comments), and
- the served site: docs/**/*.html and docs/assets/*-data.js.

Every claim-use / claim-ids pair on a file is read, every CO-CLM id found in a
served file must be declared, and every declared id must pass the registry gate
(known, verified or qualified, allowed for the declared use, not superseded, and
review_after not past). With no arguments both surfaces are scanned; with
arguments only those files or directories are.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from clinicops_os.claim_registry import load_registry
from clinicops_os.page_claims import scan_text

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "research" / "claims.jsonl"
MARKDOWN_ROOT = ROOT / "website"
PUBLIC_ROOT = ROOT / "docs"
CLAIM_MARKERS = ("claim-use:", "claim-ids:", "CO-CLM-")


def _is_public(path: Path) -> bool:
    if PUBLIC_ROOT not in path.parents:
        return False
    return path.suffix == ".html" or (path.suffix == ".js" and path.name.endswith("-data.js"))


def iter_files(args: list[str]) -> list[Path]:
    roots = [ROOT / arg for arg in args] if args else [MARKDOWN_ROOT, PUBLIC_ROOT]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            candidates = [root]
        elif root.is_dir():
            candidates = sorted(item for item in root.rglob("*") if item.is_file())
        else:
            candidates = []
        for item in candidates:
            if item.suffix.lower() == ".md" or _is_public(item):
                files.append(item)
    return files


def main() -> int:
    registry = load_registry(REGISTRY)
    today = date.today()  # noqa: DTZ011 — content expiry is intentionally calendar-date based.
    problems: list[str] = []
    markdown = 0
    public = 0
    for path in iter_files(sys.argv[1:]):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() == ".md":
            if any(marker in text for marker in CLAIM_MARKERS[:2]):
                markdown += 1
                problems.extend(
                    scan_text(rel, text, registry, today, uses=None, research_prefix="")
                )
        else:
            public += 1
            problems.extend(scan_text(rel, text, registry, today))

    if problems:
        print("Content claim validation failed:")
        for problem in problems:
            print(f"- {problem}")
        return 2

    print(
        f"content claim validation: {markdown} governed markdown file(s), "
        f"{public} served html/js file(s) scanned, 0 errors"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
