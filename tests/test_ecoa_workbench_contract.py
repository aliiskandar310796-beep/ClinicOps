"""Contract tests for the eCOA Delivery Workbench (sanitized prototype).

The page, its three scripts and the surrounding site must keep these promises:

- it is presented as a sanitized prototype with the compliance boundary;
- every DOM id the behaviour script needs exists exactly once in the page;
- every source id cited by the content data is registered on the page, and
  every registered source is used or declared as context only;
- it stays browser-local: no network primitive, no storage API, no inline
  handlers, no external script or form target, no dynamic code evaluation;
- it is registered in the sitemap, llms.txt, tools index and live-site checks;
- it keeps clear of the archived category words and the claim vocabulary the
  positioning contract forbids, and names no client, vendor or translation
  company on a public page.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAGE = DOCS / "ecoa-delivery-workbench.html"
SCRIPTS = [DOCS / "assets" / f"ecoa-workbench{s}.js" for s in ("-core", "-data", "")]


def _html() -> str:
    return PAGE.read_text(encoding="utf-8")


def _all_text() -> str:
    return _html() + "\n".join(p.read_text(encoding="utf-8") for p in SCRIPTS)


def test_identity_and_boundary() -> None:
    html = _html()
    lower = html.lower()
    assert '<link rel="canonical" href="https://clinicops.dk/ecoa-delivery-workbench">' in html
    assert "<title>eCOA Delivery Workbench | ClinicOps</title>" in html
    assert html.count("<h1") == 1
    assert 'lang="en"' in html
    assert "sanitized prototype" in lower
    assert "not a compliance determination" in lower
    assert "do not enter participant data" in lower
    assert "privacy-notice/" in html
    assert "<noscript>" in html
    assert "PRINCE2® is a registered trademark of PeopleCert" in html
    assert "used under licence" not in lower


def test_no_claims_or_names_a_public_prototype_may_not_make() -> None:
    lower = _all_text().lower()
    for banned in (
        "proven", "certified", "we manage", "track record", "guaranteed",
        "trialops", "qualityops", "clinical ai ops", "labops",
        "transperfect", "welocalize", "iqvia", "medable", "stryker",
    ):
        assert banned not in lower, f"banned word on public page: {banned!r}"


def test_every_dom_id_the_script_uses_exists_exactly_once() -> None:
    html = _html()
    script = (DOCS / "assets" / "ecoa-workbench.js").read_text(encoding="utf-8")
    ids = set(re.findall(r"""(?:byId|getElementById|\$|checklist|register)\(\s*['"]([A-Za-z][\w-]*)['"]""", script))
    assert len(ids) > 55, "id extraction looks broken"
    declared = re.findall(r'\bid="([^"]+)"', html)
    for dom_id in sorted(ids):
        assert declared.count(dom_id) == 1, f"id {dom_id!r} appears {declared.count(dom_id)} times"
    assert len(declared) == len(set(declared)), "duplicate ids on page"


def test_tabs_and_panels_are_paired() -> None:
    html = _html()
    tabs = re.findall(r'<button[^>]*role="tab"[^>]*id="(tab-[a-z]+)"[^>]*aria-controls="(panel-[a-z]+)"', html)
    assert len(tabs) == 7
    for tab, panel in tabs:
        assert f'id="{panel}"' in html and f'aria-labelledby="{tab}"' in html


def test_sources_are_registered_and_used() -> None:
    html = _html()
    registered = set(re.findall(r'<tr id="src-([a-z0-9-]+)"', html))
    assert len(registered) >= 18
    for row in re.findall(r'<tr id="src-[^"]+" data-short="[^"]*">', html):
        assert row
    assert len(re.findall(r'<tr id="src-[a-z0-9-]+" data-short="[^"]+">', html)) == len(registered)
    for href in re.findall(r'href="#src-([a-z0-9-]+)"', html):
        assert href in registered, href
    for row in re.findall(r"<tr id=\"src-[\s\S]*?</tr>", html):
        assert 'rel="noopener"' in row and "https://" in row, "source row without verifiable link"


def test_browser_local_and_no_dynamic_code() -> None:
    text = _all_text().lower()
    for primitive in ("fetch(", "xmlhttprequest", "sendbeacon", "websocket", "eventsource", "importscripts"):
        assert primitive not in text, primitive
    for storage in ("localstorage", "sessionstorage", "indexeddb", "document.cookie", "caches.", "serviceworker"):
        assert storage not in text, storage
    for sink in ("eval(", "new function(", "document.write(", "settimeout('", 'settimeout("', ".innerhtml", "insertadjacenthtml", "outerhtml"):
        assert sink not in text, f"unsafe sink {sink!r}"
    html = _html()
    assert not re.search(r"\son[a-z]+\s*=", html), "inline event handler"
    assert not re.search(r"<script[^>]+src=\"https?://", html)
    assert not re.search(r"<form", html), "no form should submit anywhere"
    assert "target=\"_blank\"" not in html


def test_registered_across_site_contracts() -> None:
    assert "https://clinicops.dk/ecoa-delivery-workbench" in (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    assert "ecoa-delivery-workbench" in (DOCS / "llms.txt").read_text(encoding="utf-8")
    assert 'href="ecoa-delivery-workbench"' in (DOCS / "tools.html").read_text(encoding="utf-8")
    assert "ecoa-delivery-workbench" in (ROOT / "scripts" / "check_live_site.py").read_text(encoding="utf-8")
    assert "ecoa-delivery-workbench" in (ROOT / "scripts" / "harmonize_public_shell.py").read_text(encoding="utf-8")
    assert "ecoa-delivery-workbench" in (ROOT / "e2e" / "site_acceptance.mjs").read_text(encoding="utf-8")


def test_example_is_labelled_fictional_and_no_real_names() -> None:
    data = (DOCS / "assets" / "ecoa-workbench-data.js").read_text(encoding="utf-8")
    assert "fictional" in data.lower()
    assert "invented for demonstration" in data.lower()


def test_no_pre_filled_targets_outside_the_example() -> None:
    """Targets, tolerance limits and risk ratings stay blank (requirement R5)."""
    data = (DOCS / "assets" / "ecoa-workbench-data.js").read_text(encoding="utf-8")
    start = data.index("RISKS")
    block = data[start : data.index("SURFACES", start)]
    assert not re.search(r"probability:\s*'(low|medium|high)'", block)
    assert not re.search(r"impact:\s*'(low|medium|high)'", block)
