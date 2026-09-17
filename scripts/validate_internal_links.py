from __future__ import annotations

from pathlib import Path

from clinicops_os.link_quality import (
    validate_fragment_links,
    validate_internal_links,
    validate_workstream_routes,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    docs = ROOT / "docs"
    errors = (
        validate_internal_links(docs)
        + validate_fragment_links(docs)
        + validate_workstream_routes(docs)
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("internal link contract: OK")


if __name__ == "__main__":
    main()
