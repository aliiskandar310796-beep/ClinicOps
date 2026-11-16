from __future__ import annotations

import argparse
from datetime import UTC, date, datetime
from pathlib import Path

from clinicops_os.claim_registry import RegistryClaim
from clinicops_os.public_feeds import (
    CORRECTIONS_PAGE,
    build_entries,
    check_correction_ids,
    eligible_claims,
    load_rows,
    page_index,
    parse_corrections,
    render_atom,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CLAIMS = ROOT / "research" / "claims.jsonl"
FEED = DOCS / "feed.xml"


def render(as_of: date) -> tuple[str, list[tuple[str, str]]]:
    rows = load_rows(CLAIMS)
    by_id = {claim.claim_id: claim for claim in map(RegistryClaim.from_dict, rows)}
    published, skipped = eligible_claims(rows, page_index(DOCS), as_of)
    corrections = parse_corrections(
        (DOCS / CORRECTIONS_PAGE).read_text(encoding="utf-8")
    )
    check_correction_ids(corrections, by_id)
    return render_atom(build_entries(published, corrections, by_id)), skipped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--as-of",
        type=date.fromisoformat,
        default=datetime.now(UTC).date(),
        help="date used for the registry review-expiry gate (default: today, UTC)",
    )
    parser.add_argument("--report", action="store_true", help="list claims left out")
    args = parser.parse_args()

    try:
        rendered, skipped = render(args.as_of)
    except ValueError as exc:
        raise SystemExit(f"feed: {exc}") from exc
    if args.report:
        for claim_id, reason in skipped:
            print(f"left out {claim_id}: {reason}")
    if args.check:
        existing = FEED.read_text(encoding="utf-8") if FEED.exists() else ""
        if existing != rendered:
            raise SystemExit("docs/feed.xml is stale; run `python scripts/render_feed.py`")
        print("feed contract: OK")
        return

    FEED.write_text(rendered, encoding="utf-8")
    print(f"wrote {FEED.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
