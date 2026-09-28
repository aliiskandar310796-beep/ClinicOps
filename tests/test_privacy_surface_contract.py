from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from clinicops_os.site_quality import url_to_docs_path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITEMAP = DOCS / "sitemap.xml"
PRIVACY = DOCS / "privacy-notice" / "index.html"
LIVE_CHECK = ROOT / "scripts" / "check_live_site.py"

TRACKING_RUNTIME_TOKENS = (
    "googletagmanager",
    "gtag(",
    "analytics.js",
    "plausible.io",
    "hotjar",
    "mixpanel",
    "segment.com",
)


def _sitemap_urls() -> list[str]:
    root = ElementTree.fromstring(SITEMAP.read_text(encoding="utf-8"))
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text or "" for loc in root.findall("sm:url/sm:loc", namespace)]


def _public_html_files() -> list[Path]:
    # Resolve through the same mapper the site validator uses, so the URL
    # form in the sitemap (.html, trailing slash, or extensionless since the
    # 2026-09-28 clean-URL change) can never silently shrink the set of pages
    # these contracts cover. The count assertion below is the guard against a
    # repeat: after the extensionless change this helper quietly dropped to
    # 6 of 38 pages and the no-tracking contract stopped checking the others.
    urls = _sitemap_urls()
    files = [url_to_docs_path(DOCS, url) for url in urls]
    assert len(files) == len(urls)
    assert all(path.is_file() for path in files), [str(p) for p in files if not p.is_file()]
    return files


def test_public_surface_helper_covers_every_sitemap_url() -> None:
    urls = _sitemap_urls()
    assert len(urls) >= 30
    assert len(_public_html_files()) == len(urls)


def test_privacy_notice_is_part_of_the_public_surface() -> None:
    html = PRIVACY.read_text(encoding="utf-8")
    sitemap = SITEMAP.read_text(encoding="utf-8")
    live_check = LIVE_CHECK.read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://clinicops.dk/privacy-notice/"' in html
    assert "Your right to object" in html
    assert "ClinicOps itself sets no cookies, runs no analytics" in html
    assert "https://clinicops.dk/privacy-notice/" in sitemap
    assert 'Target("/privacy-notice/", 200, "<title>Privacy Notice | ClinicOps</title>")' in live_check


def test_every_sitemap_html_page_links_to_privacy_notice() -> None:
    pages = _public_html_files()
    assert pages

    missing: list[str] = []
    for page in pages:
        html = page.read_text(encoding="utf-8")
        if "privacy-notice/" not in html:
            missing.append(str(page.relative_to(ROOT)))

    assert not missing, "privacy notice missing from public pages: " + ", ".join(missing)


def test_public_site_keeps_the_current_no_tracking_contract() -> None:
    violations: list[str] = []
    for page in _public_html_files():
        lower = page.read_text(encoding="utf-8").lower()
        for token in TRACKING_RUNTIME_TOKENS:
            if token in lower:
                violations.append(f"{page.relative_to(ROOT)}: {token}")

    assert not violations, "tracking runtime detected: " + ", ".join(violations)
