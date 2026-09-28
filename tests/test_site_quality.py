from __future__ import annotations

from pathlib import Path

from clinicops_os.site_quality import (
    parse_json_ld,
    parse_metadata,
    schema_types,
    url_to_docs_path,
    validate_page_metadata,
)

ROOT = Path(__file__).resolve().parents[1]


def _page(url: str, *, homepage: bool = False) -> str:
    extra = ""
    if homepage:
        extra = (
            '<script type="application/ld+json">'
            '{"@context":"https://schema.org","@type":"Organization",'
            '"name":"ClinicOps","url":"https://clinicops.dk/"}'
            "</script>"
            '<script type="application/ld+json">'
            '{"@context":"https://schema.org","@type":"WebSite",'
            '"name":"ClinicOps","url":"https://clinicops.dk/"}'
            "</script>"
        )
    return f"""<!doctype html>
<html><head>
<title>Example | ClinicOps</title>
<meta name="description" content="Example description">
<link rel="canonical" href="{url}">
<meta property="og:title" content="Example | ClinicOps">
<meta property="og:description" content="Example description">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="ClinicOps">
<meta name="twitter:card" content="summary">
{extra}
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"WebPage","name":"Example | ClinicOps","description":"Example description","url":"{url}"}}
</script>
</head><body><h1>Example</h1></body></html>"""


def test_parse_metadata_extracts_head_contract() -> None:
    parser = parse_metadata(_page("https://clinicops.dk/tools.html"))
    assert parser.title == "Example | ClinicOps"
    assert parser.canonical == "https://clinicops.dk/tools.html"
    assert parser.meta["og:site_name"] == "ClinicOps"
    assert len(parser.json_ld_blocks) == 1


def test_json_ld_types_are_detected() -> None:
    parser = parse_metadata(_page("https://clinicops.dk/", homepage=True))
    values, errors = parse_json_ld(parser.json_ld_blocks)
    assert not errors
    assert {"Organization", "WebSite", "WebPage"} <= schema_types(values)


def test_validate_page_metadata_accepts_complete_homepage() -> None:
    assert validate_page_metadata(
        _page("https://clinicops.dk/", homepage=True),
        "https://clinicops.dk/",
    ) == []


def test_validate_page_metadata_rejects_canonical_drift() -> None:
    errors = validate_page_metadata(
        _page("https://clinicops.dk/tools.html"),
        "https://clinicops.dk/research.html",
    )
    assert any("canonical" in error for error in errors)
    assert any("og:url" in error for error in errors)


def test_validate_page_metadata_rejects_og_title_drift() -> None:
    page = _page("https://clinicops.dk/tools.html").replace(
        '<meta property="og:title" content="Example | ClinicOps">',
        '<meta property="og:title" content="A Different Title | ClinicOps">',
    )
    errors = validate_page_metadata(page, "https://clinicops.dk/tools.html")
    assert any("og:title" in error for error in errors)


def test_validate_page_metadata_rejects_og_description_drift() -> None:
    page = _page("https://clinicops.dk/tools.html").replace(
        '<meta property="og:description" content="Example description">',
        '<meta property="og:description" content="A different description entirely">',
    )
    errors = validate_page_metadata(page, "https://clinicops.dk/tools.html")
    assert any("og:description" in error for error in errors)


def test_validate_page_metadata_rejects_json_ld_name_drift() -> None:
    page = _page("https://clinicops.dk/tools.html").replace(
        '"name":"Example | ClinicOps","description":"Example description"',
        '"name":"A Different Title | ClinicOps","description":"Example description"',
    )
    errors = validate_page_metadata(page, "https://clinicops.dk/tools.html")
    assert any("WebPage JSON-LD name" in error for error in errors)


def test_validate_page_metadata_rejects_json_ld_description_drift() -> None:
    # This is the exact failure mode that let a retired claim ("500+
    # assignments, 100% on time") survive in the JSON-LD copy after being
    # removed from the visible page and the meta description.
    page = _page("https://clinicops.dk/tools.html").replace(
        '"name":"Example | ClinicOps","description":"Example description"',
        '"name":"Example | ClinicOps","description":"A retired claim that should have been removed everywhere"',
    )
    errors = validate_page_metadata(page, "https://clinicops.dk/tools.html")
    assert any("WebPage JSON-LD description" in error for error in errors)


def test_homepage_social_metadata_reuses_search_metadata() -> None:
    parser = parse_metadata((ROOT / "docs" / "index.html").read_text(encoding="utf-8"))
    assert parser.meta["og:title"] == parser.title
    assert parser.meta["og:description"] == parser.meta["description"]


def test_url_to_docs_path_maps_directory_and_file_urls(tmp_path: Path) -> None:
    assert url_to_docs_path(tmp_path, "https://clinicops.dk/") == tmp_path / "index.html"
    assert (
        url_to_docs_path(tmp_path, "https://clinicops.dk/eudamed/")
        == tmp_path / "eudamed" / "index.html"
    )
    assert (
        url_to_docs_path(tmp_path, "https://clinicops.dk/tools.html")
        == tmp_path / "tools.html"
    )


def test_noindex_pages_are_not_in_sitemap() -> None:
    sitemap = (ROOT / "docs" / "sitemap.xml").read_text(encoding="utf-8")
    noindex_pages = (
        "assessment-intake.html",
        "change-surface-mapper.html",
        "danish-dhpc-checker.html",
        "danish-pv-literature-register.html",
        "evidence-change-control-pack.html",
        "evidence-pack-checklist.html",
        "expert-network.html",
        "identifier-check.html",
        "integrity-check.html",
        "integrity-economics.html",
        "integrity-gate.html",
        "readiness-score.html",
        "sdea-clause-checker.html",
        "specimen-register/",
        "transition-map-sample/",
        "what-a-pilot-looks-like.html",
    )
    for page in noindex_pages:
        assert f"https://clinicops.dk/{page}" not in sitemap
