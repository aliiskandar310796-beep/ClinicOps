"""Render the registry-backed stamps into the pages (style of render_sitemap.py).

    python scripts/render_page_stamps.py          # rewrite pages in place
    python scripts/render_page_stamps.py --check  # CI: fail if any page is stale

Config: research/page_stamps.json. Claims: research/claims.jsonl. The step only
writes what a person already recorded in the registry; it never sets a date.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from clinicops_os.claim_registry import load_registry
from clinicops_os.page_stamps import StampConfig, managed_pages, render_page

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "research" / "page_stamps.json"
REGISTRY = ROOT / "research" / "claims.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    registry = {claim.claim_id: claim for claim in load_registry(REGISTRY)}
    config = StampConfig.load(CONFIG)
    stale: list[str] = []
    changed = 0
    pages = managed_pages(ROOT, config)
    for rel in pages:
        path = ROOT / rel
        current = path.read_text(encoding="utf-8")
        rendered = render_page(rel, current, registry, config)
        if rendered != current:
            stale.append(rel)
            if not args.check:
                path.write_text(rendered, encoding="utf-8")
                changed += 1

    if args.check:
        if stale:
            raise SystemExit(
                "page stamps are stale in: "
                + ", ".join(stale)
                + "; run `python scripts/render_page_stamps.py`"
            )
        print(f"page stamps contract: OK ({len(pages)} pages)")
        return
    print(f"page stamps: {len(pages)} pages, {changed} rewritten")


if __name__ == "__main__":
    main()
