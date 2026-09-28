"""Strategic regression guards (2026-09-28).

Technical CI can stay green while the business architecture regresses: a
merge can quietly re-broaden the category, swap the canonical LinkedIn
identity, bring back retired severity/"risk score" language, let the sitemap
balloon with utilities, or drop the Organization/Person schema that makes
ClinicOps one entity across search, LinkedIn and the site. These tests pin
the strategic invariants so that kind of change fails the merge instead of
being noticed weeks later in search results.

Only strategic invariants are pinned here. Generated artifacts (sitemap,
llms.txt, og/JSON-LD mirrors) are covered by their own --check scripts, and
commercial assumptions are deliberately NOT encoded as tests.

Positioning source of truth:
01_STRATEGY/POSITIONING_2026-09-18_REGULATORY_DATA_INTEGRITY.md.
"""

from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree

from clinicops_os.site_quality import parse_json_ld, parse_metadata, url_to_docs_path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITEMAP = DOCS / "sitemap.xml"
LEGACY_STUB = DOCS / "clinical-operations.html"

# --- one canonical identity -------------------------------------------------
CANONICAL_COMPANY_LINKEDIN = "https://www.linkedin.com/company/clinicops-dk/"
DEPRECATED_COMPANY_LINKEDIN_SLUG = "clinicops-danish-regulatory"
FOUNDER_LINKEDIN = "https://www.linkedin.com/in/ali-iskandar"
CANONICAL_CATEGORY = "EU MedTech regulatory data integrity"
CONTACT_EMAIL = "info@clinicops.dk"

# --- the homepage's single story -------------------------------------------
HOMEPAGE_H1 = (
    "Keep EUDAMED, UDI, certificates, SS(C)P and controlled records aligned "
    "when products change."
)
PRIMARY_CTAS = (">Check a change free</a>", ">Scope a review</a>")

# --- page identity ----------------------------------------------------------
PINNED_TITLES = {
    "index.html": "ClinicOps | EU MedTech Regulatory Data Integrity",
    "services.html": "Solution: Regulatory Change Integrity Review | ClinicOps",
    "use-cases.html": "Use Cases: EUDAMED, SS(C)P, AR Portfolios, Denmark | ClinicOps",
    "tools.html": "Tools: Integrity Scanner and Evidence Utilities | ClinicOps",
    "evidence-change-control-pack.html": "Regulatory Change Integrity Review | ClinicOps",
    "integrity-scanner.html": "Regulatory Integrity Scanner | ClinicOps",
    "about.html": "About ClinicOps | EU MedTech Regulatory Data Integrity",
}
FLAGSHIP_URL = "https://clinicops.dk/evidence-change-control-pack"

# --- index architecture -----------------------------------------------------
SITEMAP_URL_CEILING = 40
REQUIRED_SITEMAP_URLS = {
    "https://clinicops.dk/",
    "https://clinicops.dk/services",
    "https://clinicops.dk/use-cases",
    "https://clinicops.dk/about",
    "https://clinicops.dk/contact",
    FLAGSHIP_URL,
    "https://clinicops.dk/integrity-scanner",
    "https://clinicops.dk/research",
    "https://clinicops.dk/privacy-notice/",
}

# --- retired language -------------------------------------------------------
# Old two-product / severity-scale architecture and the Danish-led tagline.
# "severity bands" (tool triage vocabulary) and negated boundary statements
# ("not a ... compliance score") are deliberately allowed; the retired items
# are the *scale/score* framing itself and the old company tagline.
RETIRED_PUBLIC_STRINGS = (
    "severity scale",
    "four-level severity",
    "four-level",
    "risk scoring",
    "Danish-led, EU-wide medical device regulatory intelligence",
    DEPRECATED_COMPANY_LINKEDIN_SLUG,
)


def _sitemap_urls() -> list[str]:
    root = ElementTree.fromstring(SITEMAP.read_text(encoding="utf-8"))
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text or "" for loc in root.findall("sm:url/sm:loc", ns)]


def _public_pages() -> list[Path]:
    return [url_to_docs_path(DOCS, url) for url in _sitemap_urls()]


def _all_html() -> list[Path]:
    return sorted(p for p in DOCS.rglob("*.html") if "vendor" not in p.parts)


def _schema_objects(html: str, schema_type: str) -> list[dict]:
    values, errors = parse_json_ld(parse_metadata(html).json_ld_blocks)
    assert not errors, errors
    return [v for v in values if isinstance(v, dict) and v.get("@type") == schema_type]


# ---------------------------------------------------------------------------
# One canonical identity


def test_homepage_organization_schema_pins_the_canonical_identity() -> None:
    orgs = _schema_objects((DOCS / "index.html").read_text(encoding="utf-8"), "Organization")
    assert len(orgs) == 1
    org = orgs[0]
    assert org["name"] == "ClinicOps"
    assert org["url"] == "https://clinicops.dk/"
    assert org["email"] == CONTACT_EMAIL
    assert org["logo"].startswith("https://clinicops.dk/assets/")
    assert CANONICAL_CATEGORY in org["description"]
    assert org["sameAs"] == [CANONICAL_COMPANY_LINKEDIN]
    assert org["founder"]["name"] == "Ali Iskandar"
    assert FOUNDER_LINKEDIN in org["founder"]["sameAs"]


def test_about_person_schema_pins_the_founder_identity() -> None:
    people = _schema_objects((DOCS / "about.html").read_text(encoding="utf-8"), "Person")
    assert len(people) == 1
    person = people[0]
    assert person["name"] == "Ali Iskandar"
    assert person["worksFor"]["name"] == "ClinicOps"
    assert person["worksFor"]["url"] == "https://clinicops.dk/"
    assert person["sameAs"] == [FOUNDER_LINKEDIN]
    assert person["url"] == "https://clinicops.dk/about"


def test_only_the_canonical_company_linkedin_slug_appears_anywhere() -> None:
    offenders = []
    linked = []
    for page in _all_html():
        text = page.read_text(encoding="utf-8")
        if DEPRECATED_COMPANY_LINKEDIN_SLUG in text:
            offenders.append(str(page.relative_to(ROOT)))
        for url in re.findall(r"https://www\.linkedin\.com/company/[^\"'\s<]+", text):
            if url.rstrip("/") != CANONICAL_COMPANY_LINKEDIN.rstrip("/"):
                offenders.append(f"{page.relative_to(ROOT)}: {url}")
            linked.append(page)
    assert not offenders, offenders
    assert linked, "no page links the canonical company LinkedIn page"


def test_llms_txt_opens_with_the_canonical_category() -> None:
    llms = (DOCS / "llms.txt").read_text(encoding="utf-8")
    first_paragraph = llms.split("\n\n")[1]
    assert first_paragraph.startswith("ClinicOps is an EU MedTech regulatory data integrity practice.")
    assert "secondary specialist capabilities" in first_paragraph


# ---------------------------------------------------------------------------
# The homepage's single story


def test_homepage_h1_and_primary_ctas_are_pinned() -> None:
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    h1s = re.findall(r"<h1>(.*?)</h1>", html, re.DOTALL)
    assert h1s == [HOMEPAGE_H1]
    for cta in PRIMARY_CTAS:
        assert cta in html, cta


def test_pinned_page_titles() -> None:
    for name, expected in PINNED_TITLES.items():
        title = parse_metadata((DOCS / name).read_text(encoding="utf-8")).title
        assert title == expected, f"{name}: {title!r} != {expected!r}"


# ---------------------------------------------------------------------------
# Index architecture


def test_sitemap_stays_bounded_and_carries_the_core_urls() -> None:
    urls = _sitemap_urls()
    assert len(urls) == len(set(urls))
    assert len(urls) <= SITEMAP_URL_CEILING, (
        f"sitemap has {len(urls)} URLs (ceiling {SITEMAP_URL_CEILING}); "
        "add a page to the index architecture deliberately, not by default"
    )
    missing = REQUIRED_SITEMAP_URLS - set(urls)
    assert not missing, missing
    assert FLAGSHIP_URL in urls


def test_every_sitemap_page_is_indexable_and_self_canonical() -> None:
    for url, page in zip(_sitemap_urls(), _public_pages(), strict=True):
        parser = parse_metadata(page.read_text(encoding="utf-8"))
        assert parser.meta.get("robots", "").lower().find("noindex") == -1, page
        assert parser.canonical == url, (page, parser.canonical, url)


def test_legacy_clinical_operations_url_is_a_noindex_redirect_stub() -> None:
    html = LEGACY_STUB.read_text(encoding="utf-8")
    parser = parse_metadata(html)
    assert "noindex" in parser.meta.get("robots", "")
    assert parser.canonical == "https://clinicops.dk/services"
    assert re.search(r'http-equiv="refresh"\s+content="0;\s*url=services"', html)
    assert "https://clinicops.dk/clinical-operations" not in SITEMAP.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Retired language


def test_retired_positioning_strings_are_absent_from_every_public_page() -> None:
    offenders = []
    for page in _all_html():
        if page == LEGACY_STUB:
            continue
        lower = page.read_text(encoding="utf-8").lower()
        for needle in RETIRED_PUBLIC_STRINGS:
            if needle.lower() in lower:
                offenders.append(f"{page.relative_to(ROOT)}: {needle}")
    assert not offenders, offenders


def test_flagship_and_scanner_carry_the_human_decision_boundary() -> None:
    boundary = "ClinicOps is not a notified body or a competent authority"
    for name in ("index.html", "integrity-scanner.html", "evidence-change-control-pack.html"):
        assert boundary in (DOCS / name).read_text(encoding="utf-8"), name
