"""Stamps generated from the registry: "Rules as of", "Last verified", answer-first."""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from clinicops_os.claim_registry import RegistryClaim, load_registry
from clinicops_os.evidence import EvidenceClass, VerificationStatus
from clinicops_os.page_claims import declared_ids
from clinicops_os.page_stamps import (
    METHOD_LABELS,
    StampConfig,
    answer_digits_outside_claims,
    long_date,
    managed_pages,
    next_review,
    registry_digest,
    render_block,
    render_line,
    render_page,
    rules_as_of,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = StampConfig.load(ROOT / "research" / "page_stamps.json")
REGISTRY = {c.claim_id: c for c in load_registry(ROOT / "research" / "claims.jsonl")}


def _claim(claim_id: str, **over) -> RegistryClaim:
    values = {
        "claim_id": claim_id,
        "text": "Claim text 10 days.",
        "evidence_class": EvidenceClass.PRIMARY,
        "status": VerificationStatus.QUALIFIED,
        "sources": ("https://example.com/a",),
        "limitations": ("x",),
        "allowed_uses": ("website",),
        "review_after": date(2026, 12, 1),
        "supersedes": (),
        "superseded_by": None,
        "risk_class": "A",
        "last_verified": date(2026, 11, 16),
        "verified_method": "read-primary",
        "source_date": "undated",
        "not_established": ("Nothing else.",),
        "label": "A label",
    }
    values.update(over)
    return RegistryClaim(**values)


def test_long_date() -> None:
    assert long_date(date(2026, 11, 3)) == "3 November 2026"


def test_rules_as_of_is_the_oldest_rule_read_and_ignores_observations() -> None:
    claims = [
        _claim("CO-CLM-0001", last_verified=date(2026, 11, 14)),
        _claim("CO-CLM-0002", last_verified=date(2026, 11, 16)),
        _claim("CO-CLM-0003", risk_class="D", last_verified=date(2026, 9, 8)),
    ]
    assert rules_as_of(claims) == date(2026, 11, 14)
    assert next_review(claims) == date(2026, 12, 1)


def test_digest_changes_when_a_claim_changes() -> None:
    one = _claim("CO-CLM-0001")
    assert registry_digest([one]) == registry_digest([one])
    assert registry_digest([one]) != registry_digest([_claim("CO-CLM-0001", review_after=date(2026, 12, 2))])


PAGE = (
    '<html><body><main id="main"><!-- claim-use: website --><!-- claim-ids: CO-CLM-0001 -->'
    '<section class="hero"><h1>T</h1><p class="lede">Lede.</p></section>'
    '<h2>Body</h2></main></body></html>'
)
CFG = StampConfig(tool_pages={}, full_block_exclude={}, answer_first={})


def test_block_shows_source_dates_method_gap_and_next_review() -> None:
    registry = {"CO-CLM-0001": _claim("CO-CLM-0001", source_date="OJ of 27 November 2025")}
    block = render_block("docs/p.html", PAGE, registry)
    assert 'id="last-verified"' in block
    for needle in (
        "CO-CLM-0001",
        "https://example.com/a",
        "OJ of 27 November 2025",
        "16 November 2026",
        METHOD_LABELS["read-primary"],
        "Nothing else.",
        "1 December 2026",
        "Page version",
    ):
        assert needle in block, needle
    assert "<script" not in block


def test_render_page_is_idempotent_and_places_line_after_the_lede() -> None:
    registry = {"CO-CLM-0001": _claim("CO-CLM-0001")}
    once = render_page("docs/p.html", PAGE, registry, CFG)
    twice = render_page("docs/p.html", once, registry, CFG)
    assert once == twice
    assert once.index("Lede.</p><!-- stamp:line:start -->") > 0
    assert once.index("Rules as of 16 November 2026") < once.index('id="last-verified"')
    assert once.index('id="last-verified"') < once.index("</main>")


def test_carried_forward_claims_say_so() -> None:
    registry = {"CO-CLM-0001": _claim("CO-CLM-0001", verified_method="carried-forward")}
    assert "not re-read for this release" in render_block("docs/p.html", PAGE, registry)


def test_none_stated_and_unregistered_variants() -> None:
    cfg = StampConfig(
        tool_pages={
            "docs/a.html": {"variant": "none-stated", "reviewed": "2026-11-16"},
            "docs/b.html": {"variant": "unregistered"},
        },
        full_block_exclude={},
        answer_first={},
    )
    none_stated = render_line("docs/a.html", "<h1>x</h1>", {}, cfg)
    assert "Rules as of 16 November 2026" in none_stated and "applies no regulatory rule" in none_stated
    unregistered = render_line("docs/b.html", "<h1>x</h1>", {}, cfg)
    assert "Rules as of: not stamped" in unregistered and "not yet in the ClinicOps claim registry" in unregistered


def test_a_claims_tool_stamp_links_the_registry_source() -> None:
    cfg = StampConfig(tool_pages={"docs/t.html": {"variant": "claims"}}, full_block_exclude={}, answer_first={})
    line = render_line("docs/t.html", PAGE, {"CO-CLM-0001": _claim("CO-CLM-0001")}, cfg)
    assert 'href="https://example.com/a">CO-CLM-0001</a>' in line and "Rules as of 16 November 2026" in line


# ---- the real site ------------------------------------------------------------


def test_render_page_stamps_check_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "render_page_stamps.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": ""},
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _listed_tools() -> set[str]:
    docs = ROOT / "docs"
    html = (docs / "tools.html").read_text(encoding="utf-8")
    main = html.split("<main", 1)[1].split("</main>", 1)[0]
    links = re.findall(r'<a href="([a-z0-9-]+(?:/)?)"', main)
    pages = {p.stem for p in docs.glob("*.html")} | {"specimen-register/", "transition-map-sample/"}
    skip = {"specimen-register", "transition-map-sample", "tools", "ecoa", "services",
            "evidence-change-control-pack", "contact", "about", "assessment-intake"}
    return {l.rstrip("/") for l in links if (l in pages or l.rstrip("/") in pages) and l.rstrip("/") not in skip}


def test_all_twelve_tool_pages_carry_a_rules_as_of_stamp_without_scripts() -> None:
    tools = _listed_tools()
    assert len(tools) == 12
    assert {f"docs/{slug}.html" for slug in tools} == set(CONFIG.tool_pages)
    for slug in sorted(tools):
        html = (ROOT / "docs" / f"{slug}.html").read_text(encoding="utf-8")
        match = re.search(r"<!-- stamp:line:start -->(.*?)<!-- stamp:line:end -->", html, re.DOTALL)
        assert match, slug
        line = match.group(1)
        assert "Rules as of" in line, slug
        assert "<script" not in line, slug
        assert html.count("stamp:line:start") == 1, slug


def test_a_tool_stamp_never_claims_a_date_it_did_not_read() -> None:
    for rel, spec in CONFIG.tool_pages.items():
        if spec["variant"] == "unregistered":
            assert "not stamped" in (ROOT / rel).read_text(encoding="utf-8"), rel
        if spec["variant"] == "claims":
            ids = declared_ids((ROOT / rel).read_text(encoding="utf-8"))
            assert ids, rel
            for claim_id in ids:
                assert REGISTRY[claim_id].verified_method == "read-primary", (rel, claim_id)


def test_claim_governed_pages_carry_rules_as_of_and_last_verified() -> None:
    pages = [p for p in managed_pages(ROOT, CONFIG) if p not in CONFIG.tool_pages and p not in CONFIG.answer_first]
    assert len(pages) >= 10
    assert "docs/eudamed-transition.html" in pages
    for rel in pages:
        html = (ROOT / rel).read_text(encoding="utf-8")
        assert re.search(r"(Rules|Observations) as of \d{1,2} \w+ 20\d\d", html), rel
        assert 'id="last-verified"' in html and "Page version" in html, rel
        ids = declared_ids(html)
        for claim_id in ids:
            if not REGISTRY[claim_id].superseded_by:
                assert claim_id in html.split('id="last-verified"', 1)[1], (rel, claim_id)


def test_excluded_pages_stay_excluded_with_a_reason() -> None:
    for rel, reason in CONFIG.full_block_exclude.items():
        assert reason
        assert "stamp:block:start" not in (ROOT / rel).read_text(encoding="utf-8"), rel


# ---- answer-first ---------------------------------------------------------------


ANSWER_PAGES = [
    "docs/ctis-clock.html",
    "docs/sdea-clause-checker.html",
    "docs/danish-dhpc-checker.html",
    "docs/ecoa-delivery-workbench.html",
    "docs/coa-type-finder.html",
    "docs/ecoa-lead-time-planner.html",
    "docs/ecoa-visit-burden.html",
]


def test_answer_first_pages_are_the_requested_ones() -> None:
    assert sorted(CONFIG.answer_first) == sorted(ANSWER_PAGES)


@pytest.mark.parametrize("rel", ANSWER_PAGES)
def test_answer_first_block_sits_above_the_tool(rel: str) -> None:
    html = (ROOT / rel).read_text(encoding="utf-8")
    match = re.search(r"<!-- answer-first:start -->(.*?)<!-- answer-first:end -->", html, re.DOTALL)
    assert match, rel
    block = match.group(1)
    assert "Short answer" in block and "Boundary." in block and "Source:" in block
    main = html.split("<main", 1)[1]
    tool = re.search(r"<(form|input|textarea|select|button)\b", main)
    assert tool and main.index("answer-first:start") < tool.start(), rel
    assert "<script" not in block


@pytest.mark.parametrize("rel", ANSWER_PAGES)
def test_answer_wording_comes_only_from_registered_claims(rel: str) -> None:
    spec = CONFIG.answer_first[rel]
    stray = answer_digits_outside_claims(spec, REGISTRY)
    assert stray == [], f"numbers in the answer that no cited claim contains: {stray}"
    if not spec["claims"]:
        assert not re.search(r"\d", spec["answer"]), "no registered claim, so no figure"
        assert "source_note" in spec
    for claim_id in spec["claims"]:
        claim = REGISTRY[claim_id]
        assert claim.status in {VerificationStatus.VERIFIED, VerificationStatus.QUALIFIED}
        assert "website" in claim.allowed_uses and not claim.superseded_by
        assert claim_id in declared_ids((ROOT / rel).read_text(encoding="utf-8")), (rel, claim_id)


def test_answer_first_source_line_is_dated_from_the_registry() -> None:
    html = (ROOT / "docs/ctis-clock.html").read_text(encoding="utf-8")
    assert "Read at the source on 16 November 2026. Registry CO-CLM-0021." in html
    assert "https://eur-lex.europa.eu/eli/reg/2014/536/oj" in html
    dhpc = (ROOT / "docs/danish-dhpc-checker.html").read_text(encoding="utf-8")
    assert "laegemiddelstyrelsen.dk/en/sideeffects/direct-healthcare-professional-communication" in dhpc
    assert "roughly ten DHPCs" not in dhpc
