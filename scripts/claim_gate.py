#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
from clinicops_eudamed.claim_guard import check_claim

TEXT_SUFFIXES = {".md", ".txt", ".html", ".csv", ".json"}


def iter_files(args):
    for arg in args:
        path = Path(arg)
        if path.is_dir():
            yield from (x for x in path.rglob("*") if x.is_file() and x.suffix.lower() in TEXT_SUFFIXES)
        elif path.is_file():
            yield path


def main() -> int:
    failures = []
    for path in iter_files(sys.argv[1:]):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for flag in check_claim(text):
            if flag.severity == "high":
                failures.append((path, flag))
            print(f"{path}: [{flag.severity}] {flag.pattern} — {flag.guidance}")
    if failures:
        print(f"\nBlocked: {len(failures)} high-severity ClinicOps claim-rule violation(s).")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
