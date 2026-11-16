"""Stale-twin check for translated public pages.

English is the authoritative source. A translated page (today: docs/da/) is
structured in the same units as its English source and stamps each unit with a
hash of the English text it was translated from. When the English page changes,
the hash no longer matches and the check fails until a person has re-read the
translated unit and re-stamped it.

Source units of an English page
-------------------------------
* ``head``  : <title> and the meta description.
* one unit per <section> inside <main>, keyed by aria-labelledby, else by the
  slug of its <h2> text without the leading number ("1. Who we are" ->
  "who-we-are"), else by its first CSS class (hero). Sections that carry their
  own lang attribute (the Danish section 9 of the English privacy notice) are
  already in another language and are not source units.
* ``loose`` : any main-level text outside all sections (for example the "Last
  updated" line), when there is any.

Markup on the translated page (all attributes are on existing elements)
-----------------------------------------------------------------------
<body data-source="privacy-notice/index.html"
      data-source-hash="<hash over every English unit hash>"
      data-source-head-hash="<hash of the English head unit>"
      data-source-skipped="how:<hash> ...">
<section data-source-unit="who-we-are" data-source-hash="<hash>">

``data-source-skipped`` lists English units deliberately not translated, each
with its hash, so a change in a skipped unit is also noticed.
"""

from __future__ import annotations

import hashlib
import html as htmllib
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

HASH_LEN = 16
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_SCRIPT_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.DOTALL | re.IGNORECASE)
_ANCHOR = re.compile(r"<a\b[^>]*?\bhref=[\"']([^\"']*)[\"'][^>]*>(.*?)</a>", re.DOTALL | re.IGNORECASE)
_TAG = re.compile(r"<[^>]+>")
_MAIN = re.compile(r"<main\b[^>]*>(.*?)</main>", re.DOTALL | re.IGNORECASE)
_SECTION = re.compile(r"<section\b([^>]*)>(.*?)</section>", re.DOTALL | re.IGNORECASE)
_H2 = re.compile(r"<h2\b[^>]*>(.*?)</h2>", re.DOTALL | re.IGNORECASE)
_TITLE = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.IGNORECASE)
_DESCRIPTION = re.compile(r'<meta name="description" content="(.*?)">', re.DOTALL)


def _normalise(fragment: str) -> str:
    """Visible text plus link targets, whitespace-collapsed; markup-only edits do not change it."""
    fragment = _COMMENT.sub("", fragment)
    fragment = _SCRIPT_STYLE.sub("", fragment)
    fragment = _ANCHOR.sub(lambda m: f"{m.group(2)} [{m.group(1)}]", fragment)
    fragment = _TAG.sub(" ", fragment)
    return " ".join(htmllib.unescape(fragment).split())


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:HASH_LEN]


def _attr(attrs: str, name: str) -> str | None:
    match = re.search(rf'\b{name}=["\']([^"\']*)["\']', attrs)
    return match.group(1) if match else None


def _slug(text: str) -> str:
    text = re.sub(r"^\s*\d+[.)]?\s*", "", text.lower())
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def english_units(source_html: str) -> dict[str, str]:
    """Ordered mapping of unit key -> normalised English text."""
    units: dict[str, str] = {}
    head_title = _TITLE.search(source_html)
    head_description = _DESCRIPTION.search(source_html)
    units["head"] = _normalise(
        (head_title.group(1) if head_title else "") + " | " + (head_description.group(1) if head_description else "")
    )
    main = _MAIN.search(source_html)
    if not main:
        return units
    body = _COMMENT.sub("", main.group(1))
    for match in _SECTION.finditer(body):
        attrs, inner = match.group(1), match.group(2)
        if _attr(attrs, "lang") not in (None, "en"):
            continue
        key = _attr(attrs, "aria-labelledby")
        if not key:
            h2 = _H2.search(inner)
            key = _slug(_normalise(h2.group(1))) if h2 else None
        if not key:
            classes = (_attr(attrs, "class") or "").split()
            key = classes[0] if classes else "section"
        base, n = key, 2
        while key in units:
            key, n = f"{base}-{n}", n + 1
        units[key] = _normalise(inner)
    loose = _normalise(_SECTION.sub(" ", body))
    if loose:
        units["loose"] = loose
    return units


def english_hashes(source_html: str) -> dict[str, str]:
    return {key: digest(text) for key, text in english_units(source_html).items()}


def page_hash(hashes: dict[str, str]) -> str:
    return digest("\n".join(f"{key}:{value}" for key, value in hashes.items()))


@dataclass
class Stamp:
    source: str | None = None
    page_hash: str | None = None
    head_hash: str | None = None
    skipped: dict[str, str] = field(default_factory=dict)
    units: dict[str, str] = field(default_factory=dict)


class _StampParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stamp = Stamp()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if tag == "body":
            self.stamp.source = values.get("data-source") or None
            self.stamp.page_hash = values.get("data-source-hash") or None
            self.stamp.head_hash = values.get("data-source-head-hash") or None
            for item in values.get("data-source-skipped", "").split():
                key, _, value = item.partition(":")
                self.stamp.skipped[key] = value
        elif "data-source-unit" in values:
            self.stamp.units[values["data-source-unit"]] = values.get("data-source-hash", "")


def read_stamp(translated_html: str) -> Stamp:
    parser = _StampParser()
    parser.feed(translated_html)
    return parser.stamp


def check_translation(translated_html: str, source_html: str, label: str = "page") -> list[str]:
    """Return human-readable problems; empty list means the translation is in sync."""
    stamp = read_stamp(translated_html)
    if not stamp.source:
        return [f"{label}: <body> has no data-source attribute"]
    current = english_hashes(source_html)
    errors: list[str] = []
    if stamp.head_hash != current["head"]:
        errors.append(f"{label}: stale head (title/description): stamped {stamp.head_hash}, English is {current['head']}")
    translated_or_skipped = set(stamp.units) | set(stamp.skipped)
    for key, value in current.items():
        if key == "head":
            continue
        if key not in translated_or_skipped:
            errors.append(f"{label}: English unit '{key}' is neither translated nor listed in data-source-skipped")
        elif key in stamp.units and stamp.units[key] != value:
            errors.append(f"{label}: stale unit '{key}': stamped {stamp.units[key]}, English is now {value}")
        elif key in stamp.skipped and stamp.skipped[key] != value:
            errors.append(f"{label}: skipped unit '{key}' changed in English: stamped {stamp.skipped[key]}, now {value}")
    for key in sorted(translated_or_skipped - set(current)):
        errors.append(f"{label}: translated unit '{key}' no longer exists in the English source")
    if stamp.page_hash != page_hash(current):
        errors.append(f"{label}: stale page hash: stamped {stamp.page_hash}, English is {page_hash(current)}")
    return errors


def restamp(translated_html: str, source_html: str) -> str:
    """Rewrite every hash attribute to match the current English source.

    Only run this after a person has re-read the translated units against the
    current English text; it records that confirmation, it does not perform it.
    """
    current = english_hashes(source_html)
    stamp = read_stamp(translated_html)

    def tag_sub(match: re.Match[str]) -> str:
        tag = match.group(0)
        unit = re.search(r'data-source-unit="([^"]+)"', tag)
        if unit and unit.group(1) in current:
            return re.sub(r'data-source-hash="[^"]*"', f'data-source-hash="{current[unit.group(1)]}"', tag)
        return tag

    out = re.sub(r"<(?!body\b)[a-z][^>]*\bdata-source-unit=[^>]*>", tag_sub, translated_html)

    def body_sub(match: re.Match[str]) -> str:
        tag = match.group(0)
        tag = re.sub(r'data-source-hash="[^"]*"', f'data-source-hash="{page_hash(current)}"', tag)
        tag = re.sub(r'data-source-head-hash="[^"]*"', f'data-source-head-hash="{current["head"]}"', tag)
        skipped = " ".join(f"{key}:{current[key]}" for key in stamp.skipped if key in current)
        return re.sub(r'data-source-skipped="[^"]*"', f'data-source-skipped="{skipped}"', tag)

    return re.sub(r"<body\b[^>]*>", body_sub, out, count=1)


def source_path(docs_root: Path, relative: str) -> Path:
    return docs_root / relative


def translated_pages(docs_root: Path) -> list[Path]:
    return sorted((docs_root / "da").rglob("*.html")) if (docs_root / "da").is_dir() else []
