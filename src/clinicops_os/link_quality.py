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
            if target.suffix.lower() not in {".html", ""} and target.exists():
                continue
            if not target.exists():
                errors.append(
                    f"{page.relative_to(docs_root)}: broken internal link {href!r}"
                )
    return errors


class IdParser(HTMLParser):
    """Collects id attributes so local fragment links can be validated."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name.lower() == "id" and value:
                self.ids.add(value)


def extract_ids(html: str) -> set[str]:
    parser = IdParser()
    parser.feed(html)
    return parser.ids


def _intake_contract(intake_html: str) -> tuple[dict[str, str], set[str]]:
    """Return (preset slug -> option text, set of option texts) from the intake page."""
    import json
    import re

    preset_match = re.search(r'presets=({"[^}]+})', intake_html)
    presets: dict[str, str] = json.loads(preset_match.group(1)) if preset_match else {}
    select_match = re.search(
        r'<select id="workstream"[^>]*>(.*?)</select>', intake_html, re.DOTALL
    )
    options: set[str] = set()
    if select_match:
        options = {
            m.group(1).strip()
            for m in re.finditer(r"<option[^>]*>([^<]*)</option>", select_match.group(1))
            if m.group(1).strip()
        }
    return presets, options


def validate_workstream_routes(docs_root: Path) -> list[str]:
    """Every public ?workstream=<slug> deep-link must preselect a real intake option.

    This exists because pages shipped links like ?workstream=danish-pv while the
    intake preset map did not know the slug: the page loaded fine but silently
    failed to preselect, which is exactly the kind of quiet contract drift a
    validator has to catch.
    """
    import re

    errors: list[str] = []
    intake = docs_root / "assessment-intake.html"
    if not intake.exists():
        return ["assessment-intake.html missing; workstream contract unverifiable"]
    presets, options = _intake_contract(intake.read_text(encoding="utf-8"))
    if not presets:
        errors.append("assessment-intake.html: preset map not found")
    for slug, option_text in presets.items():
        if option_text not in options:
            errors.append(
                f"assessment-intake.html: preset {slug!r} maps to missing option "
                f"{option_text!r}"
            )
    pattern = re.compile(r'assessment-intake\.html\?workstream=([a-z0-9-]+)')
    for page in sorted(docs_root.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        for href in extract_links(html):
            match = pattern.search(href)
            if match and match.group(1) not in presets:
                errors.append(
                    f"{page.relative_to(docs_root)}: unknown workstream slug "
                    f"{match.group(1)!r} in {href!r}"
                )
    return errors


def validate_fragment_links(docs_root: Path) -> list[str]:
    """Local fragment links must point at an id that exists in the target page."""
    errors: list[str] = []
    id_cache: dict[Path, set[str]] = {}

    def ids_for(path: Path) -> set[str]:
        if path not in id_cache:
            id_cache[path] = extract_ids(path.read_text(encoding="utf-8"))
        return id_cache[path]

    for page in sorted(docs_root.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        for href in extract_links(html):
            parsed = urlparse(href)
            if not parsed.fragment:
                continue
            if href.startswith("#"):
                target = page
            else:
                try:
                    resolved = _local_target(page, docs_root, href)
                except ValueError:
                    continue
                if resolved is None or not resolved.exists():
                    continue  # broken files already reported by the link validator
                target = resolved
            if parsed.fragment not in ids_for(target):
                errors.append(
                    f"{page.relative_to(docs_root)}: fragment {href!r} has no "
                    f"id={parsed.fragment!r} in target"
                )
    return errors
