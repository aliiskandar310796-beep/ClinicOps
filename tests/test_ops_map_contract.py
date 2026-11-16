"""Contract for the clinical operations workflow map page and its generator.

The page is generated from data/ops-map/steps.json by scripts/render_ops_map.py. These tests pin the
claim gate (no figure without a registered, website-allowed claim), stable step anchors, the
browser-local privacy boundary, the sitemap and navigation registration, and the generated outputs.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import re
from datetime import date
from pathlib import Path

import pytest

from clinicops_os.claim_registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAGE = DOCS / "clinical-operations-workflow-map.html"
SLUG = "clinical-operations-workflow-map"
AS_OF = date(2026, 11, 16)  # fixed so the tests do not expire; the CI step checks against today


def _load_renderer():
    spec = importlib.util.spec_from_file_location("render_ops_map", ROOT / "scripts" / "render_ops_map.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


R = _load_renderer()
DATA = json.loads((ROOT / "data" / "ops-map" / "steps.json").read_text(encoding="utf-8"))
CLAIMS = {c.claim_id: c for c in load_registry(ROOT / "research" / "claims.jsonl")}
HTML = PAGE.read_text(encoding="utf-8")


def _problems(data: dict, as_of: date = AS_OF) -> list[str]:
    return R.validate(data, CLAIMS, as_of)[0]


def _step(data: dict, slug: str) -> dict:
    return next(s for s in data["steps"] if s["slug"] == slug)


# ---------------------------------------------------------------- generated outputs


def test_generated_outputs_match_the_data() -> None:
    page, js = R.build(AS_OF)
    assert PAGE.read_text(encoding="utf-8") == page, "run python scripts/render_ops_map.py"
    assert (DOCS / "assets" / "ops-map-data.js").read_text(encoding="utf-8") == js


def test_the_committed_data_is_valid_today_and_on_the_fixed_date() -> None:
    assert _problems(DATA) == []


def test_there_are_six_phases_twelve_lanes_and_every_lane_has_a_step() -> None:
    assert len(DATA["phases"]) == 6 and len(DATA["lanes"]) == 12
    used = {lane for s in DATA["steps"] for lane in s["lanes"]}
    assert used == {lane["id"] for lane in DATA["lanes"]}
    assert len(re.findall(r'<section class="phase" ', HTML)) == 6
    assert len(re.findall(r"<article class=\"step\" ", HTML)) == len(DATA["steps"])


# ---------------------------------------------------------------- claim gate


def test_page_declares_every_cited_claim_in_one_comment_and_all_pass_the_website_gate() -> None:
    comments = re.findall(r"<!--\s*claim-ids:\s*([^>]+?)\s*-->", HTML)
    assert len(comments) == 1, "all claim ids must sit in ONE claim-ids comment"
    declared = {c.strip() for c in comments[0].split(",") if c.strip()}
    assert "<!-- claim-use: website -->" in HTML
    cited = {c for s in DATA["steps"] for c in s.get("claims", [])}
    assert declared == cited
    assert set(re.findall(r"CO-CLM-\d{4}", HTML)) == declared
    for claim_id in declared:
        claim = CLAIMS[claim_id]
        assert "website" in claim.allowed_uses, claim_id
        assert claim.status.value in {"verified", "qualified"}, claim_id
        assert claim.superseded_by is None, claim_id
        assert claim.sources, claim_id
        assert claim.review_after is not None, claim_id


def test_new_clock_claims_are_primary_and_read_at_the_official_text() -> None:
    new = [c for c in CLAIMS.values() if 120 <= int(c.claim_id[-4:]) <= 140]
    assert len(new) == 21
    for claim in new:
        assert claim.evidence_class.value == "primary", claim.claim_id
        assert claim.limitations and "16 November 2026" in " ".join(claim.limitations), claim.claim_id
        assert any(
            "eur-lex.europa.eu" in url or "health.ec.europa.eu" in url or "database.ich.org" in url
            for url in claim.sources
        ), claim.claim_id


def test_registered_wording_limits_and_review_dates_are_copied_into_the_cards() -> None:
    for claim_id in {c for s in DATA["steps"] for c in s.get("claims", [])}:
        claim = CLAIMS[claim_id]
        card = re.search(rf"<summary>Registered wording and limits \({claim_id}\)</summary>(.*?)</details>", HTML, re.DOTALL)
        assert card, claim_id
        body = card.group(1)
        import html as _html

        assert _html.escape(claim.text, quote=True) in body, claim_id
        assert claim.review_after.isoformat() in body, claim_id
        assert _html.escape(" ".join(claim.limitations), quote=True) in body, claim_id


def test_every_clock_shows_article_claim_id_and_review_date() -> None:
    facts = re.findall(r'<section class="fact fact-clock".*?</section>', HTML, re.DOTALL)
    assert len(facts) >= 15
    for fact in facts:
        assert re.search(r"CO-CLM-\d{4}", fact)
        assert re.search(r"Review due \d{4}-\d{2}-\d{2}", fact)
        assert re.search(r"(Article|Articles|MDR Article) ", fact)


def test_withheld_items_say_not_shown_rather_than_disappearing() -> None:
    assert HTML.count("No figure shown: not verified at primary source") >= 4
    for slug in ("drug-substantial-modification", "device-adverse-event-reporting", "annual-safety-report", "archive-trial-master-file"):
        card = re.search(rf'<article class="step" id="step-{slug}".*?</article>', HTML, re.DOTALL).group(0)
        assert "chip-not_shown" in card, slug
    assert "MDCG 2020-10/1" in HTML
    # The brief's corrections: no device safety day counts, no DSUR due date, no fixed Art 78(14) date on a step.
    dev = re.search(r'<article class="step" id="step-device-adverse-event-reporting".*?</article>', HTML, re.DOTALL).group(0)
    assert not re.search(r"\b(2|3|7) (calendar )?days", re.sub(r"<details.*?</details>", "", dev, flags=re.DOTALL))
    coord = re.search(r'<article class="step" id="step-device-coordinated-assessment".*?</article>', HTML, re.DOTALL).group(0)
    assert "27 May 2027" not in re.sub(r"<details.*?</details>", "", coord, flags=re.DOTALL)


def test_ich_service_provider_text_is_cited_to_3_6_and_3_9_5_not_3_10_or_3_11() -> None:
    assert "3.6" in HTML and "3.9.5" in HTML
    assert not re.search(r"E6\(R3\)[^<]{0,40}3\.1[01]", HTML)


# ---------------------------------------------------------------- generator refuses bad data


def test_generator_refuses_a_missing_claim() -> None:
    data = copy.deepcopy(DATA)
    _step(data, "susar-reporting")["claims"] = ["CO-CLM-9999"]
    assert any("not in the registry" in p for p in _problems(data))


def test_generator_refuses_a_figure_with_a_number_the_claim_does_not_carry() -> None:
    data = copy.deepcopy(DATA)
    _step(data, "susar-reporting")["facts"][0]["figure"] = "Not later than 9 days after the sponsor became aware"
    assert any("figure has numbers not in the registered wording" in p for p in _problems(data))


def test_generator_refuses_a_number_in_prose_without_a_claim() -> None:
    data = copy.deepcopy(DATA)
    _step(data, "route-and-regime")["settle"] += " It takes 30 days."
    assert any("numbers ['30'] in prose" in p for p in _problems(data))


def test_generator_refuses_a_clock_on_a_synthesis_step() -> None:
    data = copy.deepcopy(DATA)
    step = _step(data, "route-and-regime")
    step["claims"] = ["CO-CLM-0126"]
    assert any("synthesis step cannot cite claims" in p for p in _problems(data))


def test_generator_refuses_an_expired_review() -> None:
    assert any("review expired" in p for p in _problems(DATA, as_of=date(2027, 3, 1)))
    assert _problems(DATA, as_of=date(2026, 12, 14)) == []
    assert any("review expired" in p for p in _problems(DATA, as_of=date(2026, 12, 15)))


def test_generator_refuses_a_website_disallowed_or_rejected_claim() -> None:
    data = copy.deepcopy(DATA)
    claims = dict(CLAIMS)
    original = claims["CO-CLM-0126"]
    from dataclasses import replace

    claims["CO-CLM-0126"] = replace(original, allowed_uses=("internal",))
    assert any("use 'website' is not allowed" in p for p in R.validate(data, claims, AS_OF)[0])


def test_generator_refuses_a_chip_that_does_not_match_the_claims() -> None:
    data = copy.deepcopy(DATA)
    _step(data, "susar-reporting")["status"] = "verified"
    assert any("chip says Verified" in p for p in _problems(data))
    data = copy.deepcopy(DATA)
    _step(data, "susar-reporting")["status"] = "synthesis"
    assert _problems(data)


def test_generator_refuses_duplicate_or_malformed_slugs_and_unknown_lanes() -> None:
    data = copy.deepcopy(DATA)
    data["steps"][1]["slug"] = data["steps"][0]["slug"]
    assert any("duplicate slug" in p for p in _problems(data))
    data = copy.deepcopy(DATA)
    data["steps"][0]["slug"] = "Bad Slug"
    assert any("slug must be" in p for p in _problems(data))
    data = copy.deepcopy(DATA)
    data["steps"][0]["lanes"] = ["nope"]
    assert any("lanes must be" in p for p in _problems(data))


def test_sources_opened_must_match_the_latest_reading() -> None:
    data = copy.deepcopy(DATA)
    data["sources_opened"] = "2026-11-10"
    assert any("sources_opened must equal" in p for p in _problems(data))


# ---------------------------------------------------------------- stable anchors


def test_step_slugs_are_stable_snapshot_is_append_only() -> None:
    snapshot = (ROOT / "tests" / "fixtures" / "ops_map_slugs.txt").read_text(encoding="utf-8").split()
    current = {s["slug"] for s in DATA["steps"]}
    missing = [slug for slug in snapshot if slug not in current]
    assert not missing, f"step slugs are permanent anchors; do not remove or rename: {missing}"
    for slug in snapshot:
        assert f'id="step-{slug}"' in HTML


# ---------------------------------------------------------------- privacy and shell


def test_page_and_scripts_use_no_network_or_persistent_storage() -> None:
    sources = [HTML] + [(DOCS / "assets" / n).read_text(encoding="utf-8") for n in ("ops-map-core.js", "ops-map.js", "ops-map-data.js")]
    text = "\n".join(sources)
    lower = text.lower()
    for token in ("fetch(", "xmlhttprequest", "sendbeacon", "websocket", "localstorage", "sessionstorage", "indexeddb", "document.cookie", "eval(", "new function", "innerhtml"):
        assert token not in lower, token
    assert not re.search(r'<script[^>]+src=["\']https?://', HTML)
    assert "connect-src 'none'" in HTML.split("</head>", 1)[0]


def test_page_carries_shell_metadata_boundary_and_no_author() -> None:
    assert '<link rel="canonical" href="https://clinicops.dk/clinical-operations-workflow-map">' in HTML
    ld = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', HTML, re.DOTALL)]
    page = next(b for b in ld if b.get("@type") == "WebPage")
    assert "author" not in page and "author" not in HTML.lower().split("</head>", 1)[0].replace("authority", "")
    assert page["url"] == "https://clinicops.dk/clinical-operations-workflow-map"
    assert "Planning aid" in HTML and "not advice" in HTML
    assert 'href="mailto:info@clinicops.dk?subject=Map%20correction"' in HTML
    assert "Sources last opened:</strong> 2026-11-16" in HTML
    assert "Map change log" in HTML and "Next review:</strong>" in HTML


def test_next_review_is_the_nearest_review_date_of_the_cited_claims() -> None:
    cited = {c for s in DATA["steps"] for c in s.get("claims", [])}
    nearest = min(CLAIMS[c].review_after for c in cited).isoformat()
    assert f"<strong>Next review:</strong> {nearest}" in HTML


def test_page_is_registered_in_navigation_sitemap_and_llms_but_not_in_the_tool_shelf() -> None:
    assert f'"{SLUG}.html": "Clinical operations"' in (ROOT / "scripts" / "harmonize_public_shell.py").read_text(encoding="utf-8")
    assert f"https://clinicops.dk/{SLUG}" in (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    assert f"https://clinicops.dk/{SLUG}" in (DOCS / "llms.txt").read_text(encoding="utf-8")
    assert f'href="{SLUG}"' not in (DOCS / "tools.html").read_text(encoding="utf-8")
    assert '<a href="ecoa" aria-current="page">Clinical operations</a>' in HTML


@pytest.mark.parametrize("name", ["ecoa", "ecoa-workflow", "research", "index"])
def test_page_is_linked_from_hub_workflow_research_and_home(name: str) -> None:
    assert f'href="{SLUG}"' in (DOCS / f"{name}.html").read_text(encoding="utf-8")


def test_ci_runs_the_generator_check_the_node_tests_and_the_journey() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "render_ops_map.py --check" in ci
    assert "tests/ops_map.test.cjs" in ci
    assert "e2e/ops_map_journey.mjs" in ci
