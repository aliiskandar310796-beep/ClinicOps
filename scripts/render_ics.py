from __future__ import annotations

import argparse
from datetime import UTC, date, datetime
from pathlib import Path

from clinicops_os.public_feeds import (
    build_events,
    eligible_claims,
    load_rows,
    page_index,
    render_ics,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CLAIMS = ROOT / "research" / "claims.jsonl"
ICS = DOCS / "regulatory-dates.ics"


def render(as_of: date) -> tuple[bytes, list[tuple[str, str]], int]:
    published, skipped = eligible_claims(load_rows(CLAIMS), page_index(DOCS), as_of)
    events = build_events(published)
    return render_ics(events), skipped, len(events)


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
        rendered, skipped, count = render(args.as_of)
    except ValueError as exc:
        raise SystemExit(f"ics: {exc}") from exc
    if args.report:
        for claim_id, reason in skipped:
            print(f"left out {claim_id}: {reason}")
    if args.check:
        existing = ICS.read_bytes() if ICS.exists() else b""
        if existing != rendered:
            raise SystemExit(
                "docs/regulatory-dates.ics is stale; run `python scripts/render_ics.py`"
            )
        print(f"calendar contract: OK ({count} events)")
        return

    ICS.write_bytes(rendered)
    print(f"wrote {ICS.relative_to(ROOT)} ({count} events)")


if __name__ == "__main__":
    main()
