from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

from clinicops_os.site_quality import (
    CANONICAL_ORG_SAMEAS,
    ORGANIZATION_ID,
    SITE_ORIGIN,
    WEBSITE_ID,
)

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


ORG_REF_KEYS = ("publisher", "provider", "author")


def _put_id(obj: dict, identifier: str) -> bool:
    """Set "@id" right after "@type" (stable, readable key order)."""
    if obj.get("@id") == identifier:
        return False
    rest = {k: v for k, v in obj.items() if k != "@id"}
    obj.clear()
    for key, value in rest.items():
        obj[key] = value
        if key == "@type":
            obj["@id"] = identifier
    obj.setdefault("@id", identifier)
    return True


def _organization_stub() -> dict:
    return {"@type": "Organization", "@id": ORGANIZATION_ID, "name": "ClinicOps", "url": SITE_ORIGIN}


def _website_stub() -> dict:
    return {"@type": "WebSite", "@id": WEBSITE_ID, "name": "ClinicOps", "url": SITE_ORIGIN}


def _link_entities(obj: dict, description: str, is_home: bool) -> bool:
    """Give the Organization / WebSite / WebPage nodes stable @id values and
    make every cross-reference point at them, so crawlers see one entity
    instead of a new anonymous "ClinicOps" per page. Deliberately carries no
    author or person node (impersonal brand)."""
    changed = False
    node_type = obj.get("@type")
    if node_type == "Organization":
        changed |= _put_id(obj, ORGANIZATION_ID)
        if "sameAs" in obj and obj["sameAs"] != CANONICAL_ORG_SAMEAS:
            obj["sameAs"] = list(CANONICAL_ORG_SAMEAS)
            changed = True
        if is_home and "description" in obj and obj["description"] != description:
            obj["description"] = description
            changed = True
    elif node_type == "WebSite":
        changed |= _put_id(obj, WEBSITE_ID)
        if is_home and obj.get("publisher") != {"@id": ORGANIZATION_ID}:
            obj["publisher"] = {"@id": ORGANIZATION_ID}
            changed = True
    elif node_type == "WebPage":
        url = obj.get("url")
        if "@id" not in obj and isinstance(url, str) and url:
            # An existing @id is kept: the research pages already use their URL
            # as @id and point Article.mainEntityOfPage at it.
            changed |= _put_id(obj, url + "#webpage")
        if obj.get("isPartOf") != _website_stub():
            obj["isPartOf"] = _website_stub()
            changed = True
        if obj.get("publisher") != _organization_stub():
            obj["publisher"] = _organization_stub()
            changed = True
    # Organization references nested inside WebPage / WebApplication / Service /
    # Article nodes: same @id, existing fields untouched.
    for key in ORG_REF_KEYS:
        ref = obj.get(key)
        if isinstance(ref, dict) and ref.get("@type") == "Organization":
            changed |= _put_id(ref, ORGANIZATION_ID)
    return changed


def _sync_json_ld_block(block: str, title: str, description: str, is_home: bool = False) -> str:
    try:
        data = json.loads(block)
    except json.JSONDecodeError:
        return block
    graph = data.get("@graph") if isinstance(data, dict) else None
    candidates = graph if isinstance(graph, list) else [data]
    changed = False
    for obj in candidates:
        if not isinstance(obj, dict):
            continue
        if obj.get("@type") == "WebPage":
            if "name" in obj and obj["name"] != title:
                obj["name"] = title
                changed = True
            if "description" in obj and obj["description"] != description:
                obj["description"] = description
                changed = True
        changed |= _link_entities(obj, description, is_home)
    if not changed:
        return block
    if "\n" in block:
        return "\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def sync_meta_consistency(text: str, is_home: bool = False) -> str:
    """Only touches fields that already exist; never invents a new og:title,
    og:description or JSON-LD field. That keeps this additive-only, like
    _ensure_footer_boundary, and out of the business of deciding what a page
    should say -- only whether its existing restatements agree.

    The single exception is the @id / cross-reference linking of the
    Organization, WebSite and WebPage JSON-LD nodes, which is structural
    identity (not copy). On the home page the page's own title and meta
    description are the positioning source of truth, so the Organization
    description is mirrored from them here too (llms.txt is derived from the
    same source by render_llms_txt.py)."""
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
        return (
            match.group(1)
            + _sync_json_ld_block(match.group(2), title, description, is_home)
            + match.group(3)
        )

    text = JSON_LD_RE.sub(_replace_json_ld, text)
    return text


# ---------------------------------------------------------------------------
# Security meta (plenum lenses 28 and 30, PR tool-privacy)
#
# GitHub Pages cannot send response headers, so the page itself carries the
# policy. Every public page gets a meta Content-Security-Policy and a
# no-referrer policy. The policy is generated here, not hand-written, because
# script-src lists a SHA-256 hash for every executable inline script on the
# page instead of 'unsafe-inline': a hash only matches the exact script text
# that was reviewed, so injected script cannot run. Any edit to an inline
# script changes its hash; `harmonize_public_shell.py --check` (CI) fails until
# the harmonizer is re-run, which is the intended behaviour.
#
# Known limits, stated in the PR and the privacy notice rather than hidden:
# - style-src keeps 'unsafe-inline' (pages carry inline <style> blocks and a few
#   style attributes). CSS cannot run script or open a connection while
#   connect-src, img-src and font-src are 'self'/'none'.
# - frame-ancestors, report-uri and sandbox are not honoured in a meta policy.
# - connect-src 'none' stops fetch, XHR, WebSocket, EventSource and
#   sendBeacon. It does not stop a link click or a script that sets
#   location, so it is defence in depth, not a proof of "nothing leaves".
# ---------------------------------------------------------------------------
# Pages that run the heavy browser-local tooling (PDF text extraction, OCR,
# workers). They keep wasm and blob: sources, exactly as shipped in #132.
CSP_TOOL_PAGES = frozenset(
    {
        "change-surface-mapper.html",
        "coa-type-finder.html",
        "ctis-clock.html",
        "danish-dhpc-checker.html",
        "danish-pv-literature-register.html",
        "ecoa-delivery-workbench.html",
        "ecoa-lead-time-planner.html",
        "ecoa-visit-burden.html",
        "identifier-check.html",
        "integrity-check.html",
        "integrity-economics.html",
        "integrity-scanner.html",
        "readiness-score.html",
        "regulatory-change-impact.html",
        "sdea-clause-checker.html",
        "technical-file-consistency.html",
    }
)
CSP_META_RE = re.compile(r'<meta http-equiv="Content-Security-Policy"[^>]*>', re.IGNORECASE)
REFERRER_META_RE = re.compile(r'<meta name="referrer"[^>]*>', re.IGNORECASE)
CHARSET_META_RE = re.compile(r"<meta charset=[^>]*>", re.IGNORECASE)
INLINE_SCRIPT_RE = re.compile(r"<script\b(?![^>]*\bsrc=)([^>]*)>(.*?)</script>", re.IGNORECASE | re.DOTALL)
SCRIPT_TYPE_RE = re.compile(r'\btype=["\']([^"\']*)["\']', re.IGNORECASE)
EXECUTABLE_SCRIPT_TYPES = {"", "text/javascript", "application/javascript", "module"}
REFERRER_META = '<meta name="referrer" content="no-referrer">'


def inline_script_hashes(text: str) -> list[str]:
    """CSP source tokens ('sha256-...') for every executable inline script."""
    hashes: list[str] = []
    for attrs, body in INLINE_SCRIPT_RE.findall(text):
        type_match = SCRIPT_TYPE_RE.search(attrs)
        if (type_match.group(1).strip().lower() if type_match else "") not in EXECUTABLE_SCRIPT_TYPES:
            continue  # JSON-LD and JSON data blocks are never executed
        digest = base64.b64encode(hashlib.sha256(body.encode("utf-8")).digest()).decode("ascii")
        token = f"'sha256-{digest}'"
        if token not in hashes:
            hashes.append(token)
    return hashes


def build_csp(relative: str, text: str) -> str:
    hashes = " ".join(inline_script_hashes(text))
    script_src = "'self'" + (f" {hashes}" if hashes else "")
    tool = relative in CSP_TOOL_PAGES
    if tool:
        script_src += " 'wasm-unsafe-eval' blob:"
    directives = [
        "default-src 'self'",
        f"script-src {script_src}",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: blob:" if tool else "img-src 'self' data:",
        "font-src 'self'",
        "connect-src 'none'",
    ]
    if tool:
        directives.append("worker-src 'self' blob:")
    directives += ["object-src 'none'", "frame-src 'none'", "base-uri 'none'", "form-action 'none'"]
    return "; ".join(directives)


def _ensure_security_meta(relative: str, text: str) -> str:
    """Write (or rewrite in place) the CSP and referrer metas. Idempotent."""
    csp_meta = f'<meta http-equiv="Content-Security-Policy" content="{build_csp(relative, text)}">'
    if CSP_META_RE.search(text):
        text = CSP_META_RE.sub(lambda _m: csp_meta, text, count=1)
        if REFERRER_META_RE.search(text):
            text = REFERRER_META_RE.sub(lambda _m: REFERRER_META, text, count=1)
        else:
            text = text.replace(csp_meta, csp_meta + REFERRER_META, 1)
        return text
    if REFERRER_META_RE.search(text):
        text = REFERRER_META_RE.sub(lambda _m: "", text, count=1)
    charset = CHARSET_META_RE.search(text)
    if not charset:
        raise ValueError(f"{relative}: public page has no <meta charset> to anchor the security meta")
    return text[: charset.end()] + csp_meta + REFERRER_META + text[charset.end() :]


# ---------------------------------------------------------------------------
# Tool-page trust notes (plenum lenses 19, 20, 28; PR tool-privacy)
#
# Two static blocks, written here so they are identical on every listed tool
# page and cannot drift:
#   1. "What leaves your browser: nothing." plus a one-line test note. The
#      wording is bounded by what e2e/release_privacy_test.mjs measures: on
#      load, no request to another origin, no cookie, empty browser storage,
#      and that storage keys written during the scripted journeys stay inside
#      an allow-list. It must not claim more than that.
#   2. "What is missing?": a plain mailto link (subject prefix "Request:"),
#      no form and no script, to the address already public on the site.
# The 12 listed tools are pinned to tools.html by tests/test_tool_privacy_pack.py.
# ---------------------------------------------------------------------------
LISTED_TOOL_PAGES = (
    "change-surface-mapper.html",
    "coa-type-finder.html",
    "ctis-clock.html",
    "danish-dhpc-checker.html",
    "danish-pv-literature-register.html",
    "ecoa-delivery-workbench.html",
    "ecoa-lead-time-planner.html",
    "ecoa-visit-burden.html",
    "integrity-check.html",
    "integrity-scanner.html",
    "sdea-clause-checker.html",
    "technical-file-consistency.html",
)
REQUEST_ADDRESS = "info@clinicops.dk"
LOCAL_NOTE_ID = "what-leaves-your-browser"
REQUEST_NOTE_ID = "whats-missing"
LOCAL_NOTE_RE = re.compile(
    r'<div class="callout" id="' + LOCAL_NOTE_ID + r'" role="note">.*?</div>\n?', re.DOTALL
)
REQUEST_NOTE_RE = re.compile(
    r'<div class="callout" id="' + REQUEST_NOTE_ID + r'" role="note">.*?</div>\n?', re.DOTALL
)
MAIN_CLOSE_RE = re.compile(r"</main>", re.IGNORECASE)

# Tools that keep a small amount of working data in this browser. The note
# names it, because "nothing leaves" is true while "nothing is stored" is not.
STORAGE_CLAUSES = {
    "integrity-scanner.html": (
        " If you save a mapping profile, its name and column mappings are kept in this "
        "browser&rsquo;s local storage until you delete them."
    ),
    "change-surface-mapper.html": (
        " If you choose to scope a review, a short summary is held in this tab&rsquo;s session "
        "storage for the next page, which removes it when it reads it."
    ),
}


def _local_note(relative: str) -> str:
    extra = STORAGE_CLAUSES.get(relative, "")
    return (
        f'<div class="callout" id="{LOCAL_NOTE_ID}" role="note">'
        "<p><strong>What leaves your browser: nothing.</strong> "
        "This page does not send what you type, paste or import to ClinicOps or to anyone else, "
        "and it loads nothing from other sites. The page&rsquo;s security policy also tells "
        "your browser to block its scripts from opening network connections. Exports are saved "
        f"to your device; emailing one is your own action.{extra}</p>"
        "<p class=\"small muted\">Test note: before each release an automated browser test opens "
        "this page and fails if, on load, it contacts another site, sets a cookie or writes to "
        "browser storage.</p>"
        "</div>\n"
    )


def _request_subject(relative: str, text: str) -> str:
    if relative == "tools.html":
        return "Request: new tool"
    match = TITLE_TAG_RE.search(text)
    name = html.unescape(match.group(2)) if match else relative.removesuffix(".html")
    name = name.split(" | ")[0].strip()
    return f"Request: {name}"


def _request_note(relative: str, text: str) -> str:
    subject = quote(_request_subject(relative, text), safe="")
    body = quote("What is missing:\n\n", safe="")
    href = f"mailto:{REQUEST_ADDRESS}?subject={subject}&amp;body={body}"
    lead = (
        "If a tool you need is not on this shelf,"
        if relative == "tools.html"
        else "If this tool lacks a check, field or source you need,"
    )
    return (
        f'<div class="callout" id="{REQUEST_NOTE_ID}" role="note">'
        f'<p><strong>What is missing?</strong> {lead} <a href="{href}">email a request</a>. '
        "There is no form and no account. Please do not include patient-identifiable or "
        "confidential data.</p>"
        "</div>\n"
    )


def _ensure_tool_notes(relative: str, text: str) -> str:
    """Insert or rewrite the trust notes immediately before </main>. Idempotent."""
    text = LOCAL_NOTE_RE.sub("", text)
    text = REQUEST_NOTE_RE.sub("", text)
    blocks = ""
    if relative in LISTED_TOOL_PAGES:
        blocks += _local_note(relative)
    if relative in LISTED_TOOL_PAGES or relative == "tools.html":
        blocks += _request_note(relative, text)
    if not blocks:
        return text
    if not MAIN_CLOSE_RE.search(text):
        raise ValueError(f"{relative}: tool page has no </main> to anchor the trust notes")
    return MAIN_CLOSE_RE.sub(lambda _m: blocks + "</main>", text, count=1)


NAV_ITEMS = (
    ("Home", "index.html"),
    ("Medical devices", "services.html"),
    ("Clinical operations", "ecoa.html"),
    ("Tools", "tools.html"),
    ("Research", "research.html"),
    ("About", "about.html"),
    ("Contact", "contact.html"),
)

# Page -> highlighted nav label. Pages absent from this map (e.g. the privacy notice)
# carry no aria-current. Unknown new pages fail loudly so the map is kept current.
SECTION_BY_PAGE = {
    "index.html": "Home",
    "services.html": "Medical devices",
    "assessment-intake.html": "Medical devices",
    "evidence-change-control-pack.html": "Medical devices",
    "what-a-pilot-looks-like.html": "Medical devices",
    "evidence-pack-checklist.html": "Medical devices",
    "integrity-gate.html": "Medical devices",
    "eu-authorised-representative.html": "Medical devices",
    "use-cases.html": "Medical devices",
    "authorised-representative-portfolio-intelligence.html": "Medical devices",
    "class-iii-transition.html": "Medical devices",
    "denmark-market-access.html": "Medical devices",
    "eu-mdr-regulatory-integrity.html": "Medical devices",
    "eudamed-transition.html": "Medical devices",
    "medical-device-document-control.html": "Medical devices",
    "regulatory-intelligence.html": "Medical devices",
    "sscp-operations.html": "Medical devices",
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
    "ecoa-delivery-workbench.html": "Clinical operations",
    "ecoa.html": "Clinical operations",
    "coa-types.html": "Clinical operations",
    "ecoa-workflow.html": "Clinical operations",
    "coa-nordic.html": "Clinical operations",
    "coa-type-finder.html": "Clinical operations",
    "ecoa-lead-time-planner.html": "Clinical operations",
    "ecoa-visit-burden.html": "Clinical operations",
    "ctis-clock.html": "Clinical operations",
    "clinical-operations-workflow-map.html": "Clinical operations",
    "danish-pv-literature-register.html": "Clinical operations",
    "sdea-clause-checker.html": "Clinical operations",
    "danish-dhpc-checker.html": "Clinical operations",
    "transition-map-sample/index.html": "Tools",
    "about.html": "About",
    "expert-network.html": "About",
    "expert-network-interest.html": "About",
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
        links.append(f'<a href="{_nav_href(prefix, href)}"{active}>{html.escape(label)}</a>')
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


# Legal-identification (imprint) line for the shared footer. EMPTY BY DEFAULT.
#
# Decision D1 (publish a registered business domicile and tax ID, or take the
# adviser's written view that "on request" is enough) is still open, so nothing
# is published. When D1 is decided, set this ONE string to the exact line the
# adviser approves and re-run this script: it is added to every standard footer
# inside a marked <div> and replaced or removed if the value later changes.
# Nothing in the test suite requires it to be visible; a test only requires
# that it stays empty until D1 is recorded.
FOOTER_IMPRINT_LINE = ""
FOOTER_IMPRINT_RE = re.compile(r'<div class="footer-inner" data-imprint>.*?</div>', re.DOTALL)

# "What to do with this result" block on the twelve listed tool pages (lens 19,
# section 5). Static HTML, no script. One config row per page keeps the block
# identical in position and shape everywhere and lets it be regenerated instead
# of hand-edited. Each row: result-specific line, neighbouring page
# (href, label), question subject, offer the share-safe summary button.
# Copy rules: no claim about any named party, no urgency, no "book a call".
NEXT_STEP_START = "<!-- next-step:start -->"
NEXT_STEP_END = "<!-- next-step:end -->"
NEXT_STEP_RE = re.compile(re.escape(NEXT_STEP_START) + r".*?" + re.escape(NEXT_STEP_END), re.DOTALL)
NEXT_STEP_BY_PAGE = {
    "integrity-scanner.html": (
        "Exceptions are signals to check, not findings. Assign an owner to each before anything is changed.",
        ("change-surface-mapper", "Change Surface Mapper"),
        "Regulatory Integrity Scanner",
        True,
    ),
    "integrity-check.html": (
        "Keep the evidence JSON and its fingerprint with the change record. If you ask a question, send only the fingerprint and counts.",
        ("integrity-scanner", "Regulatory Integrity Scanner"),
        "Regulatory Change Integrity Check",
        False,
    ),
    "change-surface-mapper.html": (
        "Take the list to your regulatory owner before the next change meeting.",
        ("integrity-check", "Regulatory Change Integrity Check"),
        "Change Surface Mapper",
        False,
    ),
    "technical-file-consistency.html": (
        "A difference is a question for the document owner, not a finding about the document.",
        ("integrity-scanner", "Regulatory Integrity Scanner"),
        "Technical File Consistency Check",
        False,
    ),
    "ecoa-delivery-workbench.html": (
        "Export the workspace file to keep your work. The open items on your plan are the ones to move first.",
        ("ecoa-lead-time-planner", "eCOA lead-time planner"),
        "eCOA delivery workbench",
        False,
    ),
    "coa-type-finder.html": (
        "The inventory is the input to the licence and translation plan.",
        ("ecoa-lead-time-planner", "eCOA lead-time planner"),
        "COA type finder",
        False,
    ),
    "ecoa-lead-time-planner.html": (
        "The language version that is ready last sets the earliest start date in this plan. Confirm its licence and translation dates first.",
        ("ecoa-delivery-workbench", "eCOA delivery workbench"),
        "eCOA lead-time planner",
        True,
    ),
    "ecoa-visit-burden.html": (
        "Check the figure against the protocol schedule.",
        ("ecoa-delivery-workbench", "eCOA delivery workbench"),
        "Visit and diary burden estimator",
        False,
    ),
    "ctis-clock.html": (
        "This is a planning aid. Check the current EMA handbook for your submission.",
        ("ecoa-delivery-workbench", "eCOA delivery workbench"),
        "CTIS initial application clock",
        False,
    ),
    "danish-dhpc-checker.html": (
        "Confirm the current process with the competent authority before you submit.",
        ("danish-pv-literature-register", "Danish local-literature source register"),
        "Danish DHPC submission checker",
        False,
    ),
    "sdea-clause-checker.html": (
        "Take the missing-clause list to whoever signs the agreement.",
        ("danish-dhpc-checker", "Danish DHPC submission checker"),
        "SDEA clause checker",
        False,
    ),
    "danish-pv-literature-register.html": (
        "Check each entry against its source before you rely on it.",
        ("sdea-clause-checker", "SDEA / PV agreement clause checker"),
        "Danish local-literature source register",
        False,
    ),
}


def _next_step_block(relative: str) -> str:
    line, (href, label), subject, share = NEXT_STEP_BY_PAGE[relative]
    ask = f"mailto:support@clinicops.dk?subject={quote('Question: ' + subject)}"
    summary = (
        " Use <em>Copy share-safe summary</em> above to share counts and rule names with no values."
        if share
        else ""
    )
    return (
        f"{NEXT_STEP_START}"
        '<section class="next-step" aria-labelledby="next-step-h"><h2 id="next-step-h">What to do with this result</h2><ol>'
        f"<li>{html.escape(line, quote=False)}</li>"
        f'<li>Next: <a href="{href}">{html.escape(label, quote=False)}</a>.</li>'
        "<li>If you want a second pair of eyes, send a question that contains no identifiers: "
        f'<a href="{html.escape(ask)}">Ask a question</a> '
        f'(<a href="contact#ask">template</a>).{summary} Nothing leaves your browser until you send it.</li>'
        f"</ol></section>{NEXT_STEP_END}"
    )


def _ensure_next_step(relative: str, text: str) -> str:
    """Insert (or refresh) the next-step block just before the closing </main>.
    Pages not in NEXT_STEP_BY_PAGE are left alone; a stray block is removed."""
    block = _next_step_block(relative) if relative in NEXT_STEP_BY_PAGE else ""
    if NEXT_STEP_RE.search(text):
        return NEXT_STEP_RE.sub(lambda _: block, text, count=1)
    if not block:
        return text
    index = text.rfind("</main>")
    if index == -1:
        raise ValueError(f"{relative}: tool page has no </main> for the next-step block")
    return text[:index] + block + "\n" + text[index:]


def _ensure_footer_imprint(text: str) -> str:
    """Add, refresh or remove the optional imprint line (see FOOTER_IMPRINT_LINE)."""
    match = FOOTER_RE.search(text)
    if not match:
        return text
    footer = match.group(0)
    line = (
        f'<div class="footer-inner" data-imprint><span>{html.escape(FOOTER_IMPRINT_LINE, quote=False)}</span></div>'
        if FOOTER_IMPRINT_LINE
        else ""
    )
    if FOOTER_IMPRINT_RE.search(footer):
        footer = FOOTER_IMPRINT_RE.sub(lambda _: line, footer, count=1)
    elif line:
        footer = FOOTER_CLOSE_RE.sub(f"{line}</footer>", footer, count=1)
    return text[: match.start()] + footer + text[match.end() :]


def transform(page: Path, text: str) -> str:
    relative = page.relative_to(DOCS).as_posix()
    text = sync_meta_consistency(text, is_home=relative == "index.html")
    if relative in EXCLUDED:
        return _ensure_security_meta(relative, _ensure_footer_imprint(_ensure_footer_boundary(text)))
    if not HEADER_RE.search(text):
        raise ValueError(f"{relative}: public page has no replaceable <header>")
    transformed = HEADER_RE.sub(_header(page), text, count=1)
    transformed = _ensure_footer_imprint(_ensure_footer_boundary(transformed))
    transformed = _ensure_next_step(relative, transformed)
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
    transformed = _ensure_tool_notes(relative, transformed)
    # Last, so the script hashes cover the final page text.
    return _ensure_security_meta(relative, transformed)


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
