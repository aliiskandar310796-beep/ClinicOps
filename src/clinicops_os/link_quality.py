from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        values = {name.lower(): value or "" for name, value in attrs}
        href = values.get("href", "").strip()
        if href:
            self.links.append(href)


def extract_links(html: str) -> list[str]:
    parser = LinkParser()
    parser.feed(html)
    return parser.links


def _local_target(page: Path, docs_root: Path, href: str) -> Path | None:
    parsed = urlparse(href)
    if parsed.scheme in {"mailto", "tel"}:
        return None
    if parsed.scheme in {"http", "https"}:
        if parsed.hostname not in {"clinicops.dk", "www.clinicops.dk"}:
            return None
        raw_path = parsed.path or "/"
        base = docs_root
    elif parsed.scheme or parsed.netloc:
        return None
    else:
        raw_path = parsed.path
        if not raw_path:
            return None
        base = docs_root if raw_path.startswith("/") else page.parent

    path = unquote(raw_path)
    if path == "/":
        candidate = docs_root / "index.html"
    else:
        relative = path.lstrip("/") if path.startswith("/") else path
        candidate = base / relative
        if path.endswith("/"):
            candidate = candidate / "index.html"

    root = docs_root.resolve()
    resolved = candidate.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"link escapes docs root: {href}")
    return resolved


def validate_internal_links(docs_root: Path) -> list[str]:
    errors: list[str] = []
    for page in sorted(docs_root.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        for href in extract_links(html):
            if href.startswith("#"):
                continue
            try:
                target = _local_target(page, docs_root, href)
            except ValueError as exc:
                errors.append(f"{page.relative_to(docs_root)}: {exc}")
                continue
            if target is None:
                continue
            if target.suffix.lower() not in {".html", ""}:
                if target.exists():
                    continue
            if not target.exists():
                errors.append(
                    f"{page.relative_to(docs_root)}: broken internal link {href!r}"
                )
    return errors
