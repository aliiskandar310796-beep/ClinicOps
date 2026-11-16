"""One positioning source across the human and machine-readable layers.

The home page's own <title> and meta description are the source of truth.
og tags, the Organization/WebPage JSON-LD and llms.txt are derived from them
(scripts/harmonize_public_shell.py, scripts/render_llms_txt.py). This test
fails when any copy diverges, when JSON-LD entities stop linking through
@id, when a social image is missing, when a retired tool page is indexable
again, or when robots.txt starts blocking a search or AI crawler.
"""

from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree

from clinicops_os.site_quality import (
    CANONICAL_ORG_SAMEAS,
    ORGANIZATION_ID,
    WEBSITE_ID,
    home_positioning,
    iter_schema_objects,
    parse_json_ld,
    parse_metadata,
    url_to_docs_path,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RETIRED_TOOLS = ("identifier-check", "integrity-economics", "readiness-score", "regulatory-change-impact")
OG_IMAGE = "https://clinicops.dk/assets/og-image.png"
STALE_LLMS_PHRASES = (
    "regulatory data integrity practice",
    "secondary specialist capabilities",
    "Archived tools",
)
REQUIRED_CRAWLERS = (
    "Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
    "Claude-User", "PerplexityBot", "Google-Extended", "CCBot",
)


def _sitemap_urls() -> list[str]:
    root = ElementTree.fromstring((DOCS / "sitemap.xml").read_text(encoding="utf-8"))
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [node.text or "" for node in root.findall("sm:url/sm:loc", ns)]


def _json_ld(html: str) -> list[dict]:
    values, errors = parse_json_ld(parse_metadata(html).json_ld_blocks)
    assert not errors, errors
    return [obj for value in values for obj in iter_schema_objects(value) if isinstance(obj, dict)]


def _home_objects() -> list[dict]:
    return _json_ld((DOCS / "index.html").read_text(encoding="utf-8"))


# --- title / description / JSON-LD / llms.txt agree -------------------------


def test_home_title_description_json_ld_and_llms_txt_share_one_source() -> None:
    positioning = home_positioning(DOCS)
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    meta = parse_metadata(html).meta
    objects = _home_objects()

    assert meta["og:title"] == positioning.title
    assert meta["og:description"] == positioning.description

    web_page = next(o for o in objects if o.get("@type") == "WebPage")
    assert web_page["name"] == positioning.title
    assert web_page["description"] == positioning.description

    organization = next(o for o in objects if o.get("@type") == "Organization" and "sameAs" in o)
    assert organization["description"] == positioning.description
    assert positioning.tagline in organization["description"]

    llms = (DOCS / "llms.txt").read_text(encoding="utf-8")
    headline, summary = llms.split("\n\n")[:2]
    assert headline == "# ClinicOps"
    assert summary == f"> {positioning.description}"
    for stale in STALE_LLMS_PHRASES:
        assert stale not in llms, stale


def test_llms_txt_lists_only_sitemap_pages() -> None:
    llms = (DOCS / "llms.txt").read_text(encoding="utf-8")
    listed = set(re.findall(r"https://clinicops\.dk/[^\s]*", llms))
    allowed = set(_sitemap_urls()) | {"https://clinicops.dk/"}
    assert listed <= allowed, sorted(listed - allowed)
    for slug in RETIRED_TOOLS:
        assert f"https://clinicops.dk/{slug}" not in llms


# --- JSON-LD identity linking ------------------------------------------------


def test_home_json_ld_defines_linked_organization_website_and_webpage() -> None:
    objects = _home_objects()
    organization = next(o for o in objects if o.get("@type") == "Organization" and "sameAs" in o)
    website = next(o for o in objects if o.get("@type") == "WebSite")
    web_page = next(o for o in objects if o.get("@type") == "WebPage")
    assert organization["@id"] == ORGANIZATION_ID
    assert website["@id"] == WEBSITE_ID
    assert website["publisher"] == {"@id": ORGANIZATION_ID}
    assert web_page["@id"] == "https://clinicops.dk/#webpage"
    assert web_page["isPartOf"]["@id"] == WEBSITE_ID
    assert web_page["publisher"]["@id"] == ORGANIZATION_ID
    assert organization["sameAs"] == CANONICAL_ORG_SAMEAS


def test_every_page_links_organization_and_website_by_id() -> None:
    for url in _sitemap_urls():
        page = url_to_docs_path(DOCS, url)
        objects = _json_ld(page.read_text(encoding="utf-8"))
        web_pages = [o for o in objects if o.get("@type") == "WebPage"]
        assert web_pages, url
        for web_page in web_pages:
            assert web_page.get("@id"), url
            assert web_page["isPartOf"]["@id"] == WEBSITE_ID, url
            assert web_page["publisher"]["@id"] == ORGANIZATION_ID, url
        for obj in objects:
            for key in ("publisher", "provider", "author"):
                ref = obj.get(key)
                if isinstance(ref, dict) and ref.get("@type") == "Organization":
                    assert ref.get("@id") == ORGANIZATION_ID, (url, obj.get("@type"), key)


def test_json_ld_has_one_linkedin_identity_and_no_person_or_author_name() -> None:
    for url in _sitemap_urls():
        page = url_to_docs_path(DOCS, url)
        for obj in _json_ld(page.read_text(encoding="utf-8")):
            assert obj.get("@type") != "Person", url
            if "sameAs" in obj:
                assert obj["sameAs"] == CANONICAL_ORG_SAMEAS, url
            author = obj.get("author")
            if author is not None:
                assert isinstance(author, dict) and author.get("@type") == "Organization", url
                assert author.get("name") == "ClinicOps", url


# --- social image ------------------------------------------------------------


def test_every_indexable_page_carries_the_social_image() -> None:
    for url in _sitemap_urls():
        page = url_to_docs_path(DOCS, url)
        meta = parse_metadata(page.read_text(encoding="utf-8")).meta
        assert meta.get("og:image") == OG_IMAGE, url
        assert meta.get("twitter:image") == OG_IMAGE, url
        assert meta.get("twitter:card") == "summary_large_image", url
        assert (meta.get("og:image:width"), meta.get("og:image:height")) == ("1200", "630"), url
    assert (DOCS / "assets" / "og-image.png").is_file()


# --- retired tool pages ------------------------------------------------------


def test_retired_tool_pages_are_noindex_unlisted_and_not_linked_from_listed_pages() -> None:
    sitemap = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    slugs = "|".join(RETIRED_TOOLS)
    link_re = re.compile(rf'href="/?(?:\.\./)*({slugs})(?:\.html)?[#"?]')
    for slug in RETIRED_TOOLS:
        html = (DOCS / f"{slug}.html").read_text(encoding="utf-8")
        robots = parse_metadata(html).meta.get("robots", "")
        assert robots == "noindex,follow", slug
        assert f"https://clinicops.dk/{slug}</loc>" not in sitemap, slug
        assert "No longer listed." in html, slug
    for url in _sitemap_urls():
        text = url_to_docs_path(DOCS, url).read_text(encoding="utf-8")
        found = link_re.search(text)
        assert not found, (url, found.group(0) if found else "")


# --- robots.txt --------------------------------------------------------------


def test_robots_txt_allows_search_and_ai_crawlers_and_keeps_the_sitemap() -> None:
    robots = (DOCS / "robots.txt").read_text(encoding="utf-8")
    lines = [line.strip() for line in robots.splitlines() if line.strip() and not line.startswith("#")]
    assert not [line for line in lines if line.lower().startswith("disallow") and line.split(":", 1)[1].strip()]
    agents = {line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("user-agent")}
    assert "*" in agents
    for crawler in REQUIRED_CRAWLERS:
        assert crawler in agents, crawler
    assert "Sitemap: https://clinicops.dk/sitemap.xml" in lines
