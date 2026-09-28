from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
NAV_SCROLL_SCRIPT = (
    '<script>(function(){var n=document.querySelector("nav.primary"),a=n&&n.querySelector("[aria-current]");'
    "var r=a?a.offsetLeft+a.offsetWidth+16-n.clientWidth:0;if(r>0)n.scrollLeft=r})()</script>"
)
HEADER_RE = re.compile(
    r"<header\b[^>]*>.*?</header>(?:" + re.escape(NAV_SCROLL_SCRIPT) + ")?",
    re.IGNORECASE | re.DOTALL,
)
HEAD_CLOSE_RE = re.compile(r"</head>", re.IGNORECASE)
SITE_CSS_RE = re.compile(r"href=[\"'][^\"']*site\.css[\"']", re.IGNORECASE)
EXCLUDED = {"404.html", "clinical-operations.html"}

# Company-level scope/liability boundary. Every tool page already carries its
# own method-specific "what this tool is and isn't" callout (a different,
# already-good pattern, left untouched) — this is the narrower, page-agnostic
# statement of what ClinicOps itself is not, previously present verbatim on
# only one page (index.html) and paraphrased on one other. Centralizing it
# here means every page that ships a standard footer carries it, and any
# future page automatically inherits it rather than needing a human to
# remember to add it.
FOOTER_BOUNDARY_TEXT = (
    "ClinicOps is not a notified body or a competent authority, and does not "
    "replace your RA/QA team, RIM, QMS, PLM or ERP."
)
FOOTER_RE = re.compile(r"<footer\b[^>]*>.*?</footer>", re.IGNORECASE | re.DOTALL)
FOOTER_CLOSE_RE = re.compile(r"</footer>", re.IGNORECASE)

# A page's <title> and meta description are the single source of truth for
# its identity and summary. og:title, og:description and the WebPage
# JSON-LD name/description exist only to restate them for crawlers and link
# previews, but because each copy has historically been hand-edited
# independently, they drift: a retired claim (or any other wording fix) can
# be removed from one copy and survive untouched in the other three. This is
# the exact failure mode that let "500+ assignments / 100% on time" outlive
# its own removal from visible page copy. Syncing the derived copies here,
# on every harmonize run, makes that class of drift structurally impossible
# instead of relying on someone remembering to grep for it.
TITLE_TAG_RE = re.compile(r"(<title>)(.*?)(</title>)", re.DOTALL)
META_DESCRIPTION_RE = re.compile(r'(<meta name="description" content=")(.*?)(">)')
OG_TITLE_RE = re.compile(r'(<meta property="og:title" content=")(.*?)(">)')
OG_DESCRIPTION_RE = re.compile(r'(<meta property="og:description" content=")(.*?)(">)')
JSON_LD_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.DOTALL)


def _sync_json_ld_block(block: str, title: str, description: str) -> str:
    try:
        data = json.loads(block)
    except json.JSONDecodeError:
        return block
    graph = data.get("@graph") if isinstance(data, dict) else None
    candidates = graph if isinstance(graph, list) else [data]
    changed = False
    for obj in candidates:
        if not isinstance(obj, dict) or obj.get("@type") != "WebPage":
            continue
        if "name" in obj and obj["name"] != title:
            obj["name"] = title
            changed = True
        if "description" in obj and obj["description"] != description:
            obj["description"] = description
            changed = True
    if not changed:
        return block
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def sync_meta_consistency(text: str) -> str:
    """Only touches fields that already exist; never invents a new og:title,
    og:description or JSON-LD field. That keeps this additive-only, like
    _ensure_footer_boundary, and out of the business of deciding what a page
    should say -- only whether its existing restatements agree."""
    title_match = TITLE_TAG_RE.search(text)
    description_match = META_DESCRIPTION_RE.search(text)
    if not title_match or not description_match:
        return text
    title = title_match.group(2)
    description = description_match.group(2)

    def _sync_attr(pattern: re.Pattern[str], value: str) -> None:
        nonlocal text
        match = pattern.search(text)
        if match and match.group(2) != value:
            text = pattern.sub(
                lambda m: m.group(1) + value + m.group(3), text, count=1
            )

    _sync_attr(OG_TITLE_RE, title)
    _sync_attr(OG_DESCRIPTION_RE, description)

    def _replace_json_ld(match: re.Match[str]) -> str:
        return match.group(1) + _sync_json_ld_block(match.group(2), title, description) + match.group(3)

    text = JSON_LD_RE.sub(_replace_json_ld, text)
    return text


NAV_ITEMS = (
    ("Home", "index.html"),
    ("Solution", "services.html"),
    ("Use cases", "use-cases.html"),
    ("Research", "research.html"),
    ("Tools", "tools.html"),
    ("About", "about.html"),
    ("Contact", "contact.html"),
)

# Page -> highlighted nav label. Pages absent from this map (e.g. the privacy notice)
# carry no aria-current. Unknown new pages fail loudly so the map is kept current.
SECTION_BY_PAGE = {
    "index.html": "Home",
    "services.html": "Solution",
    "assessment-intake.html": "Solution",
    "evidence-change-control-pack.html": "Solution",
    "what-a-pilot-looks-like.html": "Solution",
    "evidence-pack-checklist.html": "Solution",
    "integrity-gate.html": "Solution",
    "use-cases.html": "Use cases",
    "authorised-representative-portfolio-intelligence.html": "Use cases",
    "class-iii-transition.html": "Use cases",
    "denmark-market-access.html": "Use cases",
    "eu-mdr-regulatory-integrity.html": "Use cases",
    "eudamed-transition.html": "Use cases",
    "medical-device-document-control.html": "Use cases",
    "regulatory-intelligence.html": "Use cases",
    "sscp-operations.html": "Use cases",
    "research.html": "Research",
    "primary-sources.html": "Research",
    "research/eudamed-watch/index.html": "Research",
    "research/sscp-public-record-scan/index.html": "Research",
    "tools.html": "Tools",
    "change-surface-mapper.html": "Tools",
    "identifier-check.html": "Tools",
    "integrity-check.html": "Tools",
    "integrity-economics.html": "Tools",
    "integrity-scanner.html": "Tools",
    "readiness-score.html": "Tools",
    "regulatory-change-impact.html": "Tools",
    "specimen-register/index.html": "Tools",
    "technical-file-consistency.html": "Tools",
    "danish-pv-literature-register.html": "Tools",
    "sdea-clause-checker.html": "Tools",
    "danish-dhpc-checker.html": "Tools",
    "transition-map-sample/index.html": "Tools",
    "about.html": "About",
    "expert-network.html": "About",
    "contact.html": "Contact",
    "privacy-notice/index.html": None,
}


def _prefix(page: Path) -> str:
    relative = Path(os.path.relpath(DOCS, page.parent)).as_posix()
    return "" if relative == "." else f"{relative}/"


def _nav_href(prefix: str, href: str) -> str:
    """Extensionless visitor-facing href for a NAV_ITEMS target.

    The site root (index.html) is special-cased: GitHub Pages already serves
    a directory path's index.html implicitly, so the prefix itself (e.g.
    "../", or "/" when the page lives at the docs root) already resolves to
    it. Every other target is a flat file, so dropping ".html" is enough —
    GitHub Pages serves the extensionless path and the .html file identically.
    """
    if href == "index.html":
        return prefix or "/"
    return f"{prefix}{href[: -len('.html')]}"


def _current_section(relative: str) -> str | None:
    if relative not in SECTION_BY_PAGE:
        raise ValueError(f"{relative}: add page to SECTION_BY_PAGE in harmonize_public_shell.py")
    return SECTION_BY_PAGE[relative]


def _header(page: Path) -> str:
    relative = page.relative_to(DOCS).as_posix()
    prefix = _prefix(page)
    current = _current_section(relative)
    links: list[str] = []
    assert current is None or current in {label for label, _ in NAV_ITEMS}
    for label, href in NAV_ITEMS:
        active = ' aria-current="page"' if label == current else ""
        links.append(f'<a href="{_nav_href(prefix, href)}"{active}>{label}</a>')
    nav = "".join(links)
    return (
        f'<header class="site"><div class="site-inner">'
        f'<a class="brand" href="{_nav_href(prefix, "index.html")}">Clinic<span>Ops</span></a>'
        f'<nav class="primary" aria-label="Primary">{nav}</nav>'
        f"</div></header>"
        f"{NAV_SCROLL_SCRIPT}"
    )


def _ensure_footer_boundary(text: str) -> str:
    """Insert the shared boundary line into a standard <footer class="site">
    block if the page has one and doesn't already carry that exact line.
    Idempotent (safe to run repeatedly) and additive only: it never touches
    a page's existing tagline or link set, so the deliberate per-page footer
    copy already in place (e.g. tool pages read "Browser-local evidence
    tools.") is preserved exactly."""
    match = FOOTER_RE.search(text)
    if not match or FOOTER_BOUNDARY_TEXT in match.group(0):
        return text
    addition = f'<div class="footer-inner"><span>{FOOTER_BOUNDARY_TEXT}</span></div>'
    start, end = match.span()
    footer_block = text[start:end]
    footer_block = FOOTER_CLOSE_RE.sub(f"{addition}</footer>", footer_block, count=1)
    return text[:start] + footer_block + text[end:]


def transform(page: Path, text: str) -> str:
    relative = page.relative_to(DOCS).as_posix()
    text = sync_meta_consistency(text)
    if relative in EXCLUDED:
        return _ensure_footer_boundary(text)
    if not HEADER_RE.search(text):
        raise ValueError(f"{relative}: public page has no replaceable <header>")
    transformed = HEADER_RE.sub(_header(page), text, count=1)
    transformed = _ensure_footer_boundary(transformed)
    if "skip-link" not in transformed:
        transformed = transformed.replace(
            '<header class="site"',
            '<a class="skip-link" href="#main">Skip to content</a><header class="site"',
            1,
        )
    transformed = re.sub(r"<main(?![^>]*\bid=)([^>]*)>", r'<main id="main" tabindex="-1"\1>', transformed, count=1)
    if not SITE_CSS_RE.search(transformed):
        prefix = _prefix(page)
        stylesheet = f'<link rel="stylesheet" href="{prefix}site.css">'
        transformed, count = HEAD_CLOSE_RE.subn(
            f"{stylesheet}</head>", transformed, count=1
        )
        if count != 1:
            raise ValueError(f"{relative}: public page has no </head>")
    return transformed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    pages = sorted(DOCS.rglob("*.html"))
    changed = 0
    for page in pages:
        relative = page.relative_to(DOCS).as_posix()
        text = page.read_text(encoding="utf-8")
        try:
            transformed = transform(page, text)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        if transformed != text:
            changed += 1
            if not args.check:
                page.write_text(transformed, encoding="utf-8")
        if relative not in EXCLUDED:
            for _, href in NAV_ITEMS:
                expected = f'href="{_nav_href(_prefix(page), href)}"'
                if expected not in transformed:
                    raise SystemExit(f"{relative}: missing harmonized nav target {href}")

    if args.check and changed:
        raise SystemExit(
            f"public shell drift: {changed} page(s) differ; run `python scripts/harmonize_public_shell.py`"
        )
    mode = "validated" if args.check else "harmonized"
    print(f"public shell {mode}: {len(pages) - len(EXCLUDED)} pages; {changed} changed")


if __name__ == "__main__":
    main()
