"""Claim gate over the HTML that is actually served (lens 29, defect 2).

The gate scans docs/**/*.html and docs/assets/*-data.js, reads every
claim-use / claim-ids comment on a page (not just the first), and fails when a
cited claim is missing, not allowed on the website, not verified or qualified,
superseded or past review_after. A ratchet lists pages that name a regulation
but declare no claims: the baseline allowlist is committed and can only shrink.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from clinicops_os.claim_registry import load_registry
from clinicops_os.page_claims import (
    parse_declarations,
    read_allowlist,
    scan_public_files,
    ungoverned_pages,
)

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 11, 16)

BASE = {
    "evidence_class": "primary",
    "status": "qualified",
    "sources": ["https://example.com/s"],
    "limitations": ["Narrow."],
    "allowed_uses": ["website", "research-note"],
    "review_after": "2026-12-16",
    "supersedes": [],
    "superseded_by": None,
    "risk_class": "A",
    "last_verified": "2026-11-16",
    "verified_method": "read-primary",
    "source_date": "undated",
    "not_established": ["Nothing else."],
    "label": "Test claim",
}


def _registry(tmp_path: Path, **per_claim: dict) -> list:
    rows = []
    for claim_id, overrides in per_claim.items():
        row = {"id": claim_id, "claim": f"Claim {claim_id}.", **BASE, **overrides}
        rows.append(json.dumps(row))
    path = tmp_path / "claims.jsonl"
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return load_registry(path)


def _site(tmp_path: Path, files: dict[str, str]) -> Path:
    root = tmp_path / "site"
    for rel, text in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


def _problems(root: Path, registry: list) -> list[str]:
    return scan_public_files(root, registry, as_of=AS_OF)


PAGE = "<!doctype html><body>{comments}<main><p>text</p></main></body>"


def test_every_declaration_pair_on_a_page_is_read() -> None:
    text = (
        "<!-- claim-use: website --><!-- claim-ids: CO-CLM-0004 -->"
        "<p>x</p><!-- claim-use: website -->\n<!-- claim-ids: CO-CLM-0020, CO-CLM-0021 -->"
    )
    declarations = parse_declarations(text)
    assert [(d.use, d.ids) for d in declarations] == [
        ("website", ("CO-CLM-0004",)),
        ("website", ("CO-CLM-0020", "CO-CLM-0021")),
    ]


def test_second_comment_on_a_page_is_gated(tmp_path: Path) -> None:
    registry = _registry(
        tmp_path,
        **{
            "CO-CLM-0004": {},
            "CO-CLM-0020": {"review_after": "2026-11-01"},
        },
    )
    comments = (
        "<!-- claim-use: website --><!-- claim-ids: CO-CLM-0004 -->"
        "<!-- claim-use: website --><!-- claim-ids: CO-CLM-0020 -->"
    )
    root = _site(tmp_path, {"docs/a.html": PAGE.format(comments=comments)})
    problems = _problems(root, registry)
    assert any("CO-CLM-0020" in p and "review expired" in p for p in problems), problems


def test_clean_page_passes(tmp_path: Path) -> None:
    registry = _registry(tmp_path, **{"CO-CLM-0004": {}})
    comments = "<!-- claim-use: website --><!-- claim-ids: CO-CLM-0004 -->"
    root = _site(tmp_path, {"docs/a.html": PAGE.format(comments=comments)})
    assert _problems(root, registry) == []


def test_unknown_claim_is_rejected(tmp_path: Path) -> None:
    registry = _registry(tmp_path, **{"CO-CLM-0004": {}})
    comments = "<!-- claim-use: website --><!-- claim-ids: CO-CLM-0099 -->"
    root = _site(tmp_path, {"docs/a.html": PAGE.format(comments=comments)})
    assert any("CO-CLM-0099" in p and "not found" in p for p in _problems(root, registry))


def test_claim_without_website_use_is_rejected_on_a_website_page(tmp_path: Path) -> None:
    registry = _registry(tmp_path, **{"CO-CLM-0002": {"allowed_uses": ["internal", "research-note"]}})
    comments = "<!-- claim-use: website --><!-- claim-ids: CO-CLM-0002 -->"
    root = _site(tmp_path, {"docs/a.html": PAGE.format(comments=comments)})
    assert any("use 'website' is not allowed" in p for p in _problems(root, registry))


def test_rejected_and_superseded_claims_are_rejected(tmp_path: Path) -> None:
    registry = _registry(
        tmp_path,
        **{
            "CO-CLM-0003": {"status": "rejected", "allowed_uses": ["internal-learning"]},
            "CO-CLM-0008": {"superseded_by": "CO-CLM-0018"},
            "CO-CLM-0018": {},
        },
    )
    comments = "<!-- claim-use: website --><!-- claim-ids: CO-CLM-0003, CO-CLM-0008 -->"
    root = _site(tmp_path, {"docs/a.html": PAGE.format(comments=comments)})
    problems = " ".join(_problems(root, registry))
    assert "status is rejected" in problems
    assert "superseded by CO-CLM-0018" in problems


def test_research_note_use_is_only_allowed_under_docs_research(tmp_path: Path) -> None:
    registry = _registry(tmp_path, **{"CO-CLM-0002": {"allowed_uses": ["internal", "research-note"]}})
    comments = "<!-- claim-use: research-note --><!-- claim-ids: CO-CLM-0002 -->"
    root = _site(
        tmp_path,
        {
            "docs/research/n/index.html": PAGE.format(comments=comments),
            "docs/elsewhere.html": PAGE.format(comments=comments),
        },
    )
    problems = _problems(root, registry)
    assert not any("research/n" in p for p in problems), problems
    assert any("elsewhere.html" in p and "research-note" in p for p in problems), problems


def test_id_in_body_must_be_declared(tmp_path: Path) -> None:
    registry = _registry(tmp_path, **{"CO-CLM-0004": {}, "CO-CLM-0005": {}})
    page = (
        "<!doctype html><body><!-- claim-use: website --><!-- claim-ids: CO-CLM-0004 -->"
        "<main><p>See CO-CLM-0005.</p></main></body>"
    )
    root = _site(tmp_path, {"docs/a.html": page})
    assert any("undeclared" in p and "CO-CLM-0005" in p for p in _problems(root, registry))


def test_page_that_cites_ids_but_declares_none_fails(tmp_path: Path) -> None:
    registry = _registry(tmp_path, **{"CO-CLM-0004": {}})
    root = _site(tmp_path, {"docs/a.html": "<body><main>CO-CLM-0004</main></body>"})
    assert any("declares no claim-use" in p for p in _problems(root, registry))


def test_ids_without_a_use_comment_fail(tmp_path: Path) -> None:
    registry = _registry(tmp_path, **{"CO-CLM-0004": {}})
    root = _site(tmp_path, {"docs/a.html": "<body><!-- claim-ids: CO-CLM-0004 --></body>"})
    assert any("must appear together" in p for p in _problems(root, registry))


def test_data_js_ids_are_gated_as_website_use(tmp_path: Path) -> None:
    registry = _registry(tmp_path, **{"CO-CLM-0002": {"allowed_uses": ["internal"]}})
    root = _site(tmp_path, {"docs/assets/x-data.js": "const RULE = {claim: 'CO-CLM-0002'};"})
    assert any("x-data.js" in p and "not allowed" in p for p in _problems(root, registry))


def test_data_js_with_an_allowed_id_passes(tmp_path: Path) -> None:
    registry = _registry(tmp_path, **{"CO-CLM-0021": {}})
    root = _site(tmp_path, {"docs/assets/x-data.js": "// claim: CO-CLM-0021\nconst A = 1;"})
    assert _problems(root, registry) == []


# ---- ratchet ---------------------------------------------------------------


def test_ungoverned_pages_lists_regulation_names_without_claims(tmp_path: Path) -> None:
    root = _site(
        tmp_path,
        {
            "docs/plain.html": "<body><main>Nothing regulatory here.</main></body>",
            "docs/bare.html": "<body><main>Under MDR and EUDAMED it works.</main></body>",
            "docs/governed.html": (
                "<body><!-- claim-use: website --><!-- claim-ids: CO-CLM-0004 -->"
                "<main>MDR</main></body>"
            ),
            "docs/404.html": "<body>MDR</body>",
        },
    )
    assert sorted(ungoverned_pages(root)) == ["docs/bare.html"]


def test_ungoverned_scan_reads_inline_scripts(tmp_path: Path) -> None:
    root = _site(
        tmp_path,
        {"docs/tool.html": "<body><main>tool</main><script>const r='Directive 2001/83/EC';</script></body>"},
    )
    assert sorted(ungoverned_pages(root)) == ["docs/tool.html"]


def test_allowlist_format(tmp_path: Path) -> None:
    path = tmp_path / "allow.txt"
    path.write_text("# comment\ndocs/a.html | reason one\n\ndocs/b.html | reason two\n", encoding="utf-8")
    assert read_allowlist(path) == {"docs/a.html": "reason one", "docs/b.html": "reason two"}
    path.write_text("docs/a.html\n", encoding="utf-8")
    with pytest.raises(ValueError, match="reason"):
        read_allowlist(path)


# The ceiling is the size of the committed baseline. Lowering it is the only
# direction allowed: pages leave the allowlist when they gain claim-ids.
ALLOWLIST_CEILING = 24
ALLOWLIST = ROOT / "research" / "ungoverned_pages_allowlist.txt"


def test_every_ungoverned_page_is_on_the_allowlist() -> None:
    allowed = read_allowlist(ALLOWLIST)
    flagged = ungoverned_pages(ROOT)
    new = sorted(set(flagged) - set(allowed))
    assert not new, (
        "pages name a regulation but declare no claims; add claim-ids or, only with a "
        f"recorded reason, list them in {ALLOWLIST.name}: {new}"
    )


def test_allowlist_has_no_stale_entries() -> None:
    allowed = read_allowlist(ALLOWLIST)
    flagged = ungoverned_pages(ROOT)
    stale = sorted(set(allowed) - set(flagged))
    assert not stale, f"remove from the allowlist (it can only shrink): {stale}"


def test_allowlist_never_grows_past_its_ceiling() -> None:
    assert len(read_allowlist(ALLOWLIST)) <= ALLOWLIST_CEILING


# ---- the real site ----------------------------------------------------------


def test_real_site_passes_the_html_claim_gate() -> None:
    problems = scan_public_files(ROOT, load_registry(ROOT / "research" / "claims.jsonl"), as_of=AS_OF)
    assert problems == []


def test_validate_content_claims_script_scans_html() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_content_claims.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": ""},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "html" in result.stdout.lower()
