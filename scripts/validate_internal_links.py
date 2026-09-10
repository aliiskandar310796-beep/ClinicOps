from __future__ import annotations

from pathlib import Path

from clinicops_os.link_quality import validate_internal_links

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    errors = validate_internal_links(ROOT / "docs")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("internal link contract: OK")


if __name__ == "__main__":
    main()
