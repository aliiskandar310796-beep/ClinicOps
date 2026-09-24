from __future__ import annotations

import argparse
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
        links.append(f'<a href="{prefix}{href}"{active}>{label}</a>')
    nav = "".join(links)
    return (
        f'<header class="site"><div class="site-inner">'
        f'<a class="brand" href="{prefix}index.html">Clinic<span>Ops</span></a>'
        f'<nav class="primary" aria-label="Primary">{nav}</nav>'
        f"</div></header>"
        f"{NAV_SCROLL_SCRIPT}"
    )


def transform(page: Path, text: str) -> str:
    relative = page.relative_to(DOCS).as_posix()
    if relative in EXCLUDED:
        return text
    if not HEADER_RE.search(text):
        raise ValueError(f"{relative}: public page has no replaceable <header>")
    transformed = HEADER_RE.sub(_header(page), text, count=1)
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
                expected = f'href="{_prefix(page)}{href}"'
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
