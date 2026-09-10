from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

SITEMAP_NAMESPACE = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
REQUIRED_META = (
    "description",
    "og:title",
    "og:description",
    "og:type",
    "og:url",
    "og:site_name",
    "twitter:card",
)


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.meta: dict[str, str] = {}
        self.canonical: str | None = None
        self.json_ld_blocks: list[str] = []
        self._in_title = False
        self._in_json_ld = False
        self._script_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.lower(): value or "" for name, value in attrs}
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = values.get("name") or values.get("property")
            if key:
                self.meta[key.lower()] = values.get("content", "").strip()
        elif tag == "link":
            rel = values.get("rel", "").lower().split()
            if "canonical" in rel:
                self.canonical = values.get("href", "").strip()
        elif tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._script_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_json_ld:
            self.json_ld_blocks.append("".join(self._script_parts).strip())
            self._in_json_ld = False
            self._script_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_json_ld:
            self._script_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


def parse_metadata(html: str) -> MetadataParser:
    parser = MetadataParser()
    parser.feed(html)
    return parser


def parse_json_ld(blocks: list[str]) -> tuple[list[object], list[str]]:
    values: list[object] = []
    errors: list[str] = []
    for index, block in enumerate(blocks, start=1):
        try:
            values.append(json.loads(block))
        except json.JSONDecodeError as exc:
            errors.append(f"JSON-LD block {index} is invalid: {exc.msg}")
    return values, errors


def iter_schema_objects(value: object):
    if isinstance(value, dict):
        yield value
        graph = value.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                yield from iter_schema_objects(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_schema_objects(item)


def schema_types(values: list[object]) -> set[str]:
    types: set[str] = set()
    for value in values:
        for item in iter_schema_objects(value):
            schema_type = item.get("@type")
            if isinstance(schema_type, str):
                types.add(schema_type)
            elif isinstance(schema_type, list):
                types.update(str(entry) for entry in schema_type)
    return types


def validate_page_metadata(html: str, expected_url: str) -> list[str]:
    parser = parse_metadata(html)
    errors: list[str] = []

    if not parser.title:
        errors.append("missing <title>")
    for key in REQUIRED_META:
        if not parser.meta.get(key):
            errors.append(f"missing {key}")

    if parser.canonical != expected_url:
        errors.append(f"canonical is {parser.canonical!r}, expected {expected_url!r}")
    if parser.meta.get("og:url") != expected_url:
        errors.append(f"og:url must equal canonical {expected_url!r}")
    if parser.meta.get("og:type") != "website":
        errors.append("og:type must be 'website'")
    if parser.meta.get("og:site_name") != "ClinicOps":
        errors.append("og:site_name must be 'ClinicOps'")
    if parser.meta.get("twitter:card") != "summary":
        errors.append("twitter:card must be 'summary'")

    if not parser.json_ld_blocks:
        errors.append("missing application/ld+json structured data")
        return errors

    json_values, json_errors = parse_json_ld(parser.json_ld_blocks)
    errors.extend(json_errors)
    if json_errors:
        return errors

    types = schema_types(json_values)
    if "WebPage" not in types:
        errors.append("structured data must include WebPage")

    web_pages = [
        item
        for value in json_values
        for item in iter_schema_objects(value)
        if item.get("@type") == "WebPage"
    ]
    if not any(item.get("url") == expected_url for item in web_pages):
        errors.append("WebPage structured data URL must match canonical")

    if expected_url == "https://clinicops.dk/":
        if "Organization" not in types:
            errors.append("homepage structured data must include Organization")
        if "WebSite" not in types:
            errors.append("homepage structured data must include WebSite")

    return errors


def sitemap_urls(sitemap_path: Path) -> list[str]:
    root = ElementTree.fromstring(sitemap_path.read_text(encoding="utf-8"))
    urls: list[str] = []
    for node in root.findall("sm:url/sm:loc", SITEMAP_NAMESPACE):
        if node.text and node.text.strip():
            urls.append(node.text.strip())
    return urls


def url_to_docs_path(docs_root: Path, url: str) -> Path:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "clinicops.dk":
        raise ValueError(f"unsupported sitemap URL: {url}")
    if parsed.query or parsed.fragment:
        raise ValueError(f"sitemap URL must not contain query/fragment: {url}")

    path = parsed.path
    if path == "/":
        relative = Path("index.html")
    elif path.endswith("/"):
        relative = Path(path.lstrip("/")) / "index.html"
    else:
        relative = Path(path.lstrip("/"))

    resolved_root = docs_root.resolve()
    target = (docs_root / relative).resolve()
    if target != resolved_root and resolved_root not in target.parents:
        raise ValueError(f"sitemap URL escapes docs root: {url}")
    return target


def validate_site(docs_root: Path) -> tuple[int, list[str]]:
    sitemap_path = docs_root / "sitemap.xml"
    robots_path = docs_root / "robots.txt"
    errors: list[str] = []

    if not sitemap_path.exists():
        return 0, ["docs/sitemap.xml is missing"]
    if not robots_path.exists():
        return 0, ["docs/robots.txt is missing"]

    urls = sitemap_urls(sitemap_path)
    if not urls:
        errors.append("sitemap contains no URLs")
    if len(urls) != len(set(urls)):
        errors.append("sitemap contains duplicate URLs")

    robots = robots_path.read_text(encoding="utf-8")
    if "Sitemap: https://clinicops.dk/sitemap.xml" not in robots:
        errors.append("robots.txt must advertise the canonical sitemap URL")

    for url in urls:
        try:
            page_path = url_to_docs_path(docs_root, url)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not page_path.exists():
            errors.append(f"{url}: mapped file is missing ({page_path.name})")
            continue
        page_errors = validate_page_metadata(
            page_path.read_text(encoding="utf-8"),
            expected_url=url,
        )
        errors.extend(f"{url}: {error}" for error in page_errors)

    return len(urls), errors
