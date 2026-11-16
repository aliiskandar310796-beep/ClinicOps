"""Check (or re-stamp) the source hashes on translated pages under docs/da/.

    python scripts/check_translation_sync.py            # fail if any English source changed
    python scripts/check_translation_sync.py --report   # also print the current English text of stale units
    python scripts/check_translation_sync.py --stamp docs/da/privacy-notice/index.html
        # record that a person re-read the Danish page against the current English source

Each Danish page names its English source in <body data-source="...">; see
src/clinicops_os/translation_sync.py for the markup contract.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from clinicops_os.translation_sync import (
    check_translation,
    english_units,
    read_stamp,
    restamp,
    translated_pages,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true", help="print the current English text of every stale unit")
    parser.add_argument("--stamp", metavar="PAGE", help="rewrite the hashes of one translated page (after human re-check)")
    args = parser.parse_args()

    if args.stamp:
        page = (ROOT / args.stamp).resolve()
        stamp = read_stamp(page.read_text(encoding="utf-8"))
        if not stamp.source:
            raise SystemExit(f"{args.stamp}: no data-source on <body>")
        source = (DOCS / stamp.source).read_text(encoding="utf-8")
        page.write_text(restamp(page.read_text(encoding="utf-8"), source), encoding="utf-8")
        print(f"re-stamped {args.stamp} against {stamp.source}")
        return 0

    problems: list[str] = []
    pages = translated_pages(DOCS)
    for page in pages:
        relative = page.relative_to(DOCS).as_posix()
        text = page.read_text(encoding="utf-8")
        stamp = read_stamp(text)
        if not stamp.source:
            problems.append(f"{relative}: <body> has no data-source attribute")
            continue
        source_html = (DOCS / stamp.source).read_text(encoding="utf-8")
        errors = check_translation(text, source_html, relative)
        problems.extend(errors)
        if errors and args.report:
            units = english_units(source_html)
            for error in errors:
                if "unit '" in error:
                    key = error.split("unit '", 1)[1].split("'", 1)[0]
                    if key in units:
                        print(f"--- English source, unit '{key}' ({stamp.source}):\n{units[key]}\n")
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        print("Danish page(s) are out of sync with the English source: re-translate the listed units, then "
              "`python scripts/check_translation_sync.py --stamp <page>`.")
        return 1
    print(f"translation sync contract: OK ({len(pages)} Danish page(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
