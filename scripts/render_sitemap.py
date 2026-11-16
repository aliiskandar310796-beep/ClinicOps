"""Render docs/sitemap.xml from the public HTML pages.

Per URL the sitemap carries:

* ``<loc>``: the page's own canonical URL (noindex pages are left out);
* ``<lastmod>``: the UTC date of the last git commit that touched the page
  file, or today's date when the working copy differs from HEAD;
* ``<xhtml:link rel="alternate" hreflang>`` alternates, only for page groups
  declared in ``data/hreflang_pairs.json`` (empty by default, so no hreflang
  is emitted for an English-only site).

lastmod and shallow clones
--------------------------
``git log`` on a shallow clone (the default ``actions/checkout``, depth 1)
reports the single boundary commit for every file, which would stamp every
page with the checkout date. The script therefore only trusts git history
when ``git rev-parse --is-shallow-repository`` is false (CI sets
``fetch-depth: 0``). Otherwise, or when git is not available at all:

* generation keeps the lastmod already recorded in ``docs/sitemap.xml`` for a
  page whose working copy is clean, and uses today's date for a page that is
  new to the sitemap or modified in the working tree;
* ``--check`` skips the exact lastmod comparison, still verifies the URL set
  and the hreflang block, and that every lastmod is a well-formed date that is
  not in the future, and says so on stdout.

With complete history the output is deterministic: same history, same bytes.
After a squash or rebase merge that lands on a different UTC day than the
commit the sitemap was generated at, rerun the script to realign the dates.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from xml.etree import ElementTree
from xml.sax.saxutils import escape

from clinicops_os.site_quality import parse_metadata

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITEMAP = DOCS / "sitemap.xml"
HREFLANG_PAIRS = ROOT / "data" / "hreflang_pairs.json"
EXCLUDED_HTML = {"404.html", "clinical-operations.html"}
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NS = "http://www.w3.org/1999/xhtml"
LANG_RE = re.compile(r"^[a-z]{2,3}(-[A-Z]{2})?$")
HTML_LANG_RE = re.compile(r"<html\b[^>]*\blang=[\"']([^\"']+)[\"']", re.IGNORECASE)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Page:
    url: str
    path: Path
    relative: str
    lang: str | None


def discover_pages() -> list[Page]:
    pages: list[Page] = []
    for page in sorted(DOCS.rglob("*.html")):
        relative = page.relative_to(DOCS).as_posix()
        if relative in EXCLUDED_HTML:
            continue
        text = page.read_text(encoding="utf-8")
        parser = parse_metadata(text)
        robots = parser.meta.get("robots", "").lower()
        if "noindex" in {token.strip() for token in robots.split(",")}:
            continue
        canonical = parser.canonical
        if not canonical:
            raise SystemExit(f"{relative}: missing canonical URL")
        if not canonical.startswith("https://clinicops.dk/"):
            raise SystemExit(f"{relative}: unsupported canonical URL {canonical!r}")
        lang_match = HTML_LANG_RE.search(text)
        pages.append(Page(canonical, page, relative, lang_match.group(1) if lang_match else None))

    urls = [page.url for page in pages]
    if len(urls) != len(set(urls)):
        raise SystemExit("duplicate canonical URLs found across public HTML pages")
    return sorted(pages, key=lambda page: (page.url != "https://clinicops.dk/", page.url))


def discover_urls() -> list[str]:
    return [page.url for page in discover_pages()]


# --- lastmod ---------------------------------------------------------------


def _git(*args: str) -> str | None:
    if shutil.which("git") is None:
        return None
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def history_is_complete() -> bool:
    """True only when git history can be trusted for per-file dates."""
    return _git("rev-parse", "--is-shallow-repository") == "false"


def _is_dirty(path: Path) -> bool:
    return bool(_git("status", "--porcelain", "--", str(path)))


def _today() -> str:
    return datetime.now(UTC).date().isoformat()


def git_lastmod(path: Path) -> str | None:
    """UTC date of the last commit touching ``path``; today when the working
    copy differs from HEAD (or is untracked); None when git cannot say."""
    if _is_dirty(path):
        return _today()
    stamp = _git("log", "-1", "--format=%ct", "--", str(path))
    if not stamp:
        return None
    return datetime.fromtimestamp(int(stamp), tz=UTC).date().isoformat()


def recorded_lastmods(sitemap: Path | None = None) -> dict[str, str]:
    sitemap = sitemap or SITEMAP
    if not sitemap.exists():
        return {}
    root = ElementTree.fromstring(sitemap.read_text(encoding="utf-8"))
    ns = {"sm": SITEMAP_NS}
    recorded: dict[str, str] = {}
    for node in root.findall("sm:url", ns):
        loc = node.find("sm:loc", ns)
        mod = node.find("sm:lastmod", ns)
        if loc is not None and loc.text and mod is not None and mod.text:
            recorded[loc.text.strip()] = mod.text.strip()
    return recorded


def compute_lastmods(pages: list[Page]) -> dict[str, str]:
    """lastmod per URL: git history when complete, else the documented fallback."""
    exact = history_is_complete()
    recorded = {} if exact else recorded_lastmods()
    result: dict[str, str] = {}
    for page in pages:
        if exact:
            result[page.url] = git_lastmod(page.path) or _today()
        elif page.url in recorded and not _is_dirty(page.path):
            result[page.url] = recorded[page.url]
        else:
            result[page.url] = _today()
    return result


# --- hreflang --------------------------------------------------------------


def load_hreflang_groups(path: Path | None = None) -> list[dict[str, str]]:
    """Each group maps a language code to the canonical URL of that
    language's page. See data/hreflang_pairs.json for the format."""
    path = path or HREFLANG_PAIRS
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    groups = data.get("pairs", [])
    if not isinstance(groups, list):
        raise SystemExit(f"{path.name}: 'pairs' must be a list")
    return active_groups(groups)


PAIR_STATUSES = ("draft_pending_review", "reviewed")


def active_groups(groups: list[dict[str, str]]) -> list[dict[str, str]]:
    """Pairs that may be emitted as hreflang: status "reviewed" (or no status).

    A "draft_pending_review" pair points at a noindex Danish draft. Google ignores
    hreflang to a noindex page and the draft is not in the sitemap, so the pair is
    skipped here and its URLs are not validated as sitemap pages. The "status" key
    is stripped; the remaining keys are language codes."""
    active: list[dict[str, str]] = []
    for index, group in enumerate(groups, start=1):
        if not isinstance(group, dict):
            raise SystemExit(f"hreflang_pairs.json pair {index}: must be an object")
        status = group.get("status", "reviewed")
        if status not in PAIR_STATUSES:
            raise SystemExit(
                f"hreflang_pairs.json pair {index}: status {status!r} must be one of {', '.join(PAIR_STATUSES)}"
            )
        if status == "reviewed":
            active.append({lang: url for lang, url in group.items() if lang != "status"})
    return active


def validate_hreflang_groups(groups: list[dict[str, str]], pages: list[Page]) -> None:
    by_url = {page.url: page for page in pages}
    seen: dict[str, int] = {}
    for index, group in enumerate(groups, start=1):
        label = f"hreflang_pairs.json pair {index}"
        if not isinstance(group, dict) or len(group) < 2:
            raise SystemExit(f"{label}: needs at least two languages")
        if "en" not in group:
            raise SystemExit(f"{label}: must include 'en' (x-default points to the English page)")
        if len(set(group.values())) != len(group):
            raise SystemExit(f"{label}: the same URL is listed for two languages")
        for lang, url in group.items():
            if not LANG_RE.match(lang):
                raise SystemExit(
                    f"{label}: invalid language code {lang!r} (use 'en' or 'da', not region-only codes)"
                )
            if url not in by_url:
                raise SystemExit(
                    f"{label}: {url} is not an indexable sitemap page "
                    "(alternates must be self-canonical, indexable and listed)"
                )
            if url in seen:
                raise SystemExit(f"{label}: {url} already belongs to pair {seen[url]}")
            seen[url] = index
            page_lang = (by_url[url].lang or "").split("-")[0].lower()
            if page_lang != lang.split("-")[0].lower():
                raise SystemExit(
                    f"{label}: {by_url[url].relative} has <html lang={page_lang!r}>, expected {lang!r}"
                )


def alternates_for(groups: list[dict[str, str]]) -> dict[str, list[tuple[str, str]]]:
    """url -> [(hreflang, href)], identical for every member of a group
    (self-referencing and reciprocal), plus x-default -> the English URL."""
    result: dict[str, list[tuple[str, str]]] = {}
    for group in groups:
        links = sorted(group.items(), key=lambda item: (item[0] != "en", item[0]))
        links.append(("x-default", group["en"]))
        for url in group.values():
            result[url] = list(links)
    return result


# --- render ----------------------------------------------------------------


def render(
    urls: list[str],
    lastmods: dict[str, str] | None = None,
    alternates: dict[str, list[tuple[str, str]]] | None = None,
) -> str:
    lastmods = lastmods or {}
    alternates = alternates or {}
    namespaces = f'xmlns="{SITEMAP_NS}"'
    if alternates:
        namespaces += f' xmlns:xhtml="{XHTML_NS}"'
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', f"<urlset {namespaces}>"]
    for url in urls:
        parts = [f"<loc>{escape(url)}</loc>"]
        if url in lastmods:
            parts.append(f"<lastmod>{lastmods[url]}</lastmod>")
        for lang, href in alternates.get(url, []):
            parts.append(f'<xhtml:link rel="alternate" hreflang="{escape(lang)}" href="{escape(href)}"/>')
        lines.append("  <url>" + "".join(parts) + "</url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def _check_recorded_lastmods(urls: list[str]) -> dict[str, str]:
    """Shape validation used when exact recomputation is impossible."""
    recorded = recorded_lastmods()
    today = datetime.now(UTC).date()
    for url in urls:
        value = recorded.get(url)
        if not value or not DATE_RE.match(value):
            raise SystemExit(
                f"docs/sitemap.xml: {url} has no valid <lastmod>; run `python scripts/render_sitemap.py`"
            )
        if date.fromisoformat(value) > today:
            raise SystemExit(f"docs/sitemap.xml: {url} has a future <lastmod> {value}")
    return recorded


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    pages = discover_pages()
    groups = load_hreflang_groups()
    validate_hreflang_groups(groups, pages)
    alternates = alternates_for(groups)
    urls = [page.url for page in pages]

    if args.check:
        existing = SITEMAP.read_text(encoding="utf-8") if SITEMAP.exists() else ""
        stale = "docs/sitemap.xml is stale; run `python scripts/render_sitemap.py`"
        if history_is_complete():
            if existing != render(urls, compute_lastmods(pages), alternates):
                raise SystemExit(stale)
            print("sitemap contract: OK")
            return
        recorded = _check_recorded_lastmods(urls)
        if existing != render(urls, recorded, alternates):
            raise SystemExit(stale)
        print("sitemap contract: OK (shallow or git-less checkout: lastmod values checked for shape only)")
        return

    SITEMAP.write_text(render(urls, compute_lastmods(pages), alternates), encoding="utf-8")
    print(f"wrote {SITEMAP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
