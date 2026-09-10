from __future__ import annotations

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from clinicops_os.site_quality import parse_metadata

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITEMAP = DOCS / "sitemap.xml"
EXCLUDED_HTML = {"404.html"}


def discover_urls() -> list[str]:
    urls: list[str] = []
    for page in sorted(DOCS.rglob("*.html")):
        relative = page.relative_to(DOCS).as_posix()
        if relative in EXCLUDED_HTML:
            continue
        parser = parse_metadata(page.read_text(encoding="utf-8"))
        canonical = parser.canonical
        if not canonical:
            raise SystemExit(f"{relative}: missing canonical URL")
        if not canonical.startswith("https://clinicops.dk/"):
            raise SystemExit(f"{relative}: unsupported canonical URL {canonical!r}")
        urls.append(canonical)

    if len(urls) != len(set(urls)):
        raise SystemExit("duplicate canonical URLs found across public HTML pages")
    return sorted(urls, key=lambda url: (url != "https://clinicops.dk/", url))


def render(urls: list[str]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    lines.extend(f"  <url><loc>{escape(url)}</loc></url>" for url in urls)
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = render(discover_urls())
    if args.check:
        existing = SITEMAP.read_text(encoding="utf-8") if SITEMAP.exists() else ""
        if existing != rendered:
            raise SystemExit(
                "docs/sitemap.xml is stale; run `python scripts/render_sitemap.py`"
            )
        print("sitemap contract: OK")
        return

    SITEMAP.write_text(rendered, encoding="utf-8")
    print(f"wrote {SITEMAP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
