from __future__ import annotations

from pathlib import Path

from clinicops_os.site_quality import (
    parse_json_ld,
    parse_metadata,
    schema_types,
    url_to_docs_path,
    validate_page_metadata,
)


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
{{"@context":"https://schema.org","@type":"WebPage","name":"Example", "url":"{url}"}}
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
