"""Contract for the browser-local privacy pack (plenum lenses 19, 20, 28, 30).

Static guards that sit beside the Playwright release test (e2e/release_privacy_test.mjs):
the meta CSP and referrer policy on every page, the "what leaves your browser" and
"what is missing" blocks on the listed tools, the storage-key allow-list, security.txt and
the Pages setting that lets dot-prefixed files reach production.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

HANDOFF_KEYS = {"clinicops.changeSurface.handoff", "clinicops.readiness.handoff"}
PROFILE_KEYS = {"clinicops.scanner.mappingProfiles"}


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


harmonizer = _load("harmonize_public_shell_for_privacy_pack", ROOT / "scripts" / "harmonize_public_shell.py")
shelf = _load("tool_shelf_for_privacy_pack", ROOT / "tests" / "test_wp07_tool_shelf.py")


def _pages() -> list[Path]:
    return sorted(DOCS.rglob("*.html"))


def _head(html: str) -> str:
    return html.split("</head>", 1)[0]


def _csp(html: str) -> str:
    match = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)">', _head(html))
    assert match, "no meta Content-Security-Policy"
    return match.group(1)


def _directive(csp: str, name: str) -> str:
    for part in csp.split(";"):
        part = part.strip()
        if part.startswith(name + " ") or part == name:
            return part
    return ""


def test_every_public_page_carries_a_hash_based_csp_and_no_referrer_policy() -> None:
    offenders: list[str] = []
    pages = _pages()
    assert len(pages) >= 48
    for page in pages:
        html = page.read_text(encoding="utf-8")
        name = page.relative_to(DOCS).as_posix()
        head = _head(html)
        csp = _csp(html)
        script_src = _directive(csp, "script-src")
        if "connect-src 'none'" not in csp or "default-src 'self'" not in csp:
            offenders.append(f"{name}: connect-src/default-src")
        if "'unsafe-inline'" in script_src or "'unsafe-eval'" in script_src or not script_src:
            offenders.append(f"{name}: script-src is not hash-based ({script_src})")
        if "https:" in csp or "http:" in csp or "*" in csp:
            offenders.append(f"{name}: CSP names an external source")
        if "object-src 'none'" not in csp or "frame-src 'none'" not in csp or "base-uri 'none'" not in csp:
            offenders.append(f"{name}: object/frame/base directives")
        if '<meta name="referrer" content="no-referrer">' not in head:
            offenders.append(f"{name}: no-referrer policy missing")
        # The policy must precede every script and stylesheet it governs.
        policy_at = head.index("Content-Security-Policy")
        for marker in ("<script", "<link", "<style"):
            at = head.find(marker)
            if at != -1 and at < policy_at:
                offenders.append(f"{name}: {marker} appears before the CSP")
        # Every executable inline script must be covered by a hash, or it would be blocked.
        for token in harmonizer.inline_script_hashes(html):
            if token not in script_src:
                offenders.append(f"{name}: inline script hash missing {token[:20]}")
        if re.search(r'\son(?:click|change|input|submit|load|keydown|keyup|error|focus|blur)=', html):
            offenders.append(f"{name}: inline event-handler attribute (blocked by the policy)")
    assert not offenders, "\n".join(offenders)


def test_csp_hashes_match_the_script_text_exactly() -> None:
    """A hash only helps if it is computed over the bytes the browser parses."""
    for page in _pages():
        assert "\r" not in page.read_text(encoding="utf-8", newline=""), page.name


def test_harmonizer_tool_list_is_the_twelve_listed_tools() -> None:
    listed = {f"{slug}.html" for slug in shelf._listed_tools()}
    assert set(harmonizer.LISTED_TOOL_PAGES) == listed
    assert len(harmonizer.LISTED_TOOL_PAGES) == 12


def test_listed_tools_state_what_leaves_the_browser_and_name_their_test() -> None:
    forbidden = ("validated", "certified", "audit-ready", "guarantee", "insured", "iso-aligned")
    for name in harmonizer.LISTED_TOOL_PAGES:
        html = (DOCS / name).read_text(encoding="utf-8")
        blocks = re.findall(r'<div class="callout" id="what-leaves-your-browser" role="note">(.*?)</div>', html, re.DOTALL)
        assert len(blocks) == 1, name
        block = blocks[0]
        assert "What leaves your browser: nothing." in block, name
        # The note may claim no more than the release test measures: page load and named journeys.
        assert "Test note:" in block and "on load" in block, name
        assert "automated browser test" in block, name
        assert not any(word in block.lower() for word in forbidden), name
        assert "<form" not in block and "<script" not in block, name


def test_storage_clauses_are_present_only_where_the_tool_stores_something() -> None:
    scanner = (DOCS / "integrity-scanner.html").read_text(encoding="utf-8")
    mapper = (DOCS / "change-surface-mapper.html").read_text(encoding="utf-8")
    assert "local storage" in scanner.split('id="what-leaves-your-browser"', 1)[1].split("</div>", 1)[0]
    assert "session storage" in mapper.split('id="what-leaves-your-browser"', 1)[1].split("</div>", 1)[0]
    for name in harmonizer.LISTED_TOOL_PAGES:
        if name in {"integrity-scanner.html", "change-surface-mapper.html"}:
            continue
        html = (DOCS / name).read_text(encoding="utf-8")
        note = html.split('id="what-leaves-your-browser"', 1)[1].split("</div>", 1)[0]
        assert "storage" not in note.replace("browser storage", ""), name


def test_what_is_missing_is_a_static_request_mailto_on_tools_and_every_listed_tool() -> None:
    for name in ("tools.html", *harmonizer.LISTED_TOOL_PAGES):
        html = (DOCS / name).read_text(encoding="utf-8")
        blocks = re.findall(r'<div class="callout" id="whats-missing" role="note">(.*?)</div>', html, re.DOTALL)
        assert len(blocks) == 1, name
        block = blocks[0]
        links = re.findall(r'href="([^"]+)"', block)
        assert len(links) == 1, name
        assert links[0].startswith("mailto:info@clinicops.dk?subject=Request%3A%20"), (name, links[0])
        assert "<form" not in block and "<script" not in block and "<input" not in block, name
        assert "patient-identifiable" in block, name


def test_privacy_notice_discloses_the_storage_handoff_in_the_browser_local_section() -> None:
    html = (DOCS / "privacy-notice" / "index.html").read_text(encoding="utf-8")
    section = html.split("<h2>2. This website</h2>", 1)[1].split("<h2>3. Email enquiries</h2>", 1)[0]
    assert "session storage" in section and "local storage" in section
    assert "assessment page deletes" in section
    assert "ClinicOps itself sets no cookies, runs no analytics" in section
    # the disclosure belongs to section 2 only
    assert "session storage" not in html.split("<h2>3. Email enquiries</h2>", 1)[1]


def _storage_calls() -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    sources = [p for p in _pages()] + sorted((DOCS / "assets").glob("*.js"))
    for path in sources:
        text = path.read_text(encoding="utf-8")
        for area in ("localStorage", "sessionStorage"):
            for match in re.finditer(area + r"\.setItem\(([^,]+),", text):
                found.append((path.name, area, match.group(1).strip()))
    return found


def test_storage_writes_use_only_allow_listed_keys() -> None:
    calls = _storage_calls()
    assert calls, "expected the Scanner profile write and the two handoff writes"
    literal = {"PROF_KEY": "clinicops.scanner.mappingProfiles", "HANDOFF_KEY": "clinicops.readiness.handoff"}
    for name, area, raw in calls:
        key = literal.get(raw, raw.strip("\"'"))
        allowed = PROFILE_KEYS if area == "localStorage" else HANDOFF_KEYS
        assert key in allowed, f"{name}: {area}.setItem({raw}) is not on the allow-list"
        if area == "localStorage":
            assert name == "integrity-scanner.js", name


def test_release_test_allow_lists_match_this_contract() -> None:
    script = (ROOT / "e2e" / "release_privacy_test.mjs").read_text(encoding="utf-8")
    local = set(re.findall(r'LOCAL_ALLOW = new Set\(\[([^\]]*)\]', script)[0].replace('"', "").replace(" ", "").split(","))
    session = set(re.findall(r'SESSION_ALLOW = new Set\(\[([^\]]*)\]', script)[0].replace('"', "").replace(" ", "").split(","))
    assert local == PROFILE_KEYS
    assert session == HANDOFF_KEYS


def test_release_test_covers_every_sitemap_url_and_runs_in_ci_and_weekly() -> None:
    script = (ROOT / "e2e" / "release_privacy_test.mjs").read_text(encoding="utf-8")
    assert "docs/sitemap.xml" in script
    for needle in ("allHeaders", "set-cookie", "localStorage", "sessionStorage", "connect-src 'none'", "no-referrer", "securitypolicyviolation"):
        assert needle in script, needle
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "node e2e/release_privacy_test.mjs" in ci
    weekly = (ROOT / ".github" / "workflows" / "e2e.yml").read_text(encoding="utf-8")
    assert "release_privacy_test.mjs" in weekly


def test_sitemap_stays_at_or_under_the_ceiling() -> None:
    root = ElementTree.fromstring((DOCS / "sitemap.xml").read_text(encoding="utf-8"))
    urls = root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
    assert len(urls) <= 48


def test_security_txt_is_valid_and_points_only_at_clinicops_urls() -> None:
    path = DOCS / ".well-known" / "security.txt"
    fields: dict[str, list[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        key, value = line.split(": ", 1)
        fields.setdefault(key, []).append(value)
    assert fields["Contact"] == ["mailto:info@clinicops.dk"]
    assert (DOCS / "contact.html").read_text(encoding="utf-8").count("info@clinicops.dk") >= 1
    assert len(fields["Expires"]) == 1 and len(fields["Canonical"]) == 1
    expires = datetime.fromisoformat(fields["Expires"][0])
    now = datetime.now(UTC)
    assert expires > now, "security.txt has expired: renew the Expires field (RFC 9116)"
    assert expires < now + timedelta(days=366), "Expires must be less than a year ahead (RFC 9116)"
    for key in ("Canonical", "Policy"):
        for value in fields.get(key, []):
            assert re.fullmatch(r"https://clinicops\.dk/[A-Za-z0-9._~/-]*", value), (key, value)
    assert fields["Canonical"] == ["https://clinicops.dk/.well-known/security.txt"]
    assert set(fields) <= {"Contact", "Expires", "Preferred-Languages", "Canonical", "Policy"}


def test_pages_deploy_ships_dot_prefixed_paths() -> None:
    """upload-pages-artifact drops dot-prefixed paths unless told otherwise."""
    assert (DOCS / ".nojekyll").is_file()
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8"))
    steps = workflow["jobs"]["deploy"]["steps"]
    upload = [s for s in steps if str(s.get("uses", "")).startswith("actions/upload-pages-artifact")]
    assert len(upload) == 1
    assert upload[0]["with"]["path"] == "docs"
    assert upload[0]["with"].get("include-hidden-files") is True
    live = (ROOT / "scripts" / "check_live_site.py").read_text(encoding="utf-8")
    assert '"/.well-known/security.txt"' in live


def test_privacy_claim_is_registered_for_website_use_with_its_verification_method() -> None:
    import json

    rows = [json.loads(line) for line in (ROOT / "research" / "claims.jsonl").read_text(encoding="utf-8").splitlines() if line]
    row = next(r for r in rows if r["id"] == "CO-CLM-0090")
    assert "website" in row["allowed_uses"]
    assert "e2e/release_privacy_test.mjs" in row["sources"]
    assert (ROOT / "e2e" / "release_privacy_test.mjs").is_file()
    assert row["limitations"]
