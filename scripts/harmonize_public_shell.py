from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
HEADER_RE = re.compile(r"<header\b[^>]*>.*?</header>", re.IGNORECASE | re.DOTALL)
HEAD_CLOSE_RE = re.compile(r"</head>", re.IGNORECASE)
SITE_CSS_RE = re.compile(r"href=[\"'][^\"']*site\.css[\"']", re.IGNORECASE)
EXCLUDED = {"404.html", "clinical-operations.html"}

NAV_ITEMS = (
    ("Home", "index.html"),
    ("Services", "services.html"),
    ("Denmark Market Access", "denmark-market-access.html"),
    ("Integrity Review", "integrity-gate.html"),
    ("Sources", "primary-sources.html"),
    ("Tools", "tools.html"),
    ("About", "about.html"),
    ("Contact", "contact.html"),
)

TOOLS_PAGES = {
    "identifier-check.html",
    "integrity-check.html",
    "integrity-economics.html",
    "readiness-score.html",
    "tools.html",
    "transition-map-sample/index.html",
    "specimen-register/index.html",
}


def _prefix(page: Path) -> str:
    relative = Path(os.path.relpath(DOCS, page.parent)).as_posix()
    return "" if relative == "." else f"{relative}/"


def _current_section(relative: str) -> str:
    if relative == "index.html":
        return "Home"
    if relative == "denmark-market-access.html":
        return "Denmark Market Access"
    if relative in {"integrity-gate.html", "eu-mdr-regulatory-integrity.html", "evidence-change-control-pack.html", "medical-device-document-control.html"}:
        return "Integrity Review"
    if relative == "primary-sources.html" or relative.startswith("research/"):
        return "Sources"
    if relative in TOOLS_PAGES:
        return "Tools"
    if relative in {"about.html", "expert-network.html"}:
        return "About"
    if relative == "contact.html":
        return "Contact"
    return "Services"


def _header(page: Path) -> str:
    relative = page.relative_to(DOCS).as_posix()
    prefix = _prefix(page)
    current = _current_section(relative)
    links: list[str] = []
    for label, href in NAV_ITEMS:
        active = ' aria-current="page"' if label == current else ""
        links.append(f'<a href="{prefix}{href}"{active}>{label}</a>')
    nav = "".join(links)
    return (
        f'<header class="site"><div class="site-inner">'
        f'<a class="brand" href="{prefix}index.html">Clinic<span>Ops</span></a>'
        f'<nav class="primary" aria-label="Primary">{nav}</nav>'
        f"</div></header>"
        '<script>(function(){var n=document.querySelector("nav.primary"),a=n&&n.querySelector("[aria-current]");if(a&&n.scrollWidth>n.clientWidth)n.scrollLeft=Math.max(0,a.offsetLeft-32)})()</script>'
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

    mode = "validated" if args.check else "harmonized"
    print(f"public shell {mode}: {len(pages) - len(EXCLUDED)} pages; {changed} changed")


if __name__ == "__main__":
    main()
