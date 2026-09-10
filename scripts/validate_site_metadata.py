from __future__ import annotations

from pathlib import Path

from clinicops_os.site_quality import validate_site

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    page_count, errors = validate_site(ROOT / "docs")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"site metadata contract: OK ({page_count} sitemap pages)")


if __name__ == "__main__":
    main()
