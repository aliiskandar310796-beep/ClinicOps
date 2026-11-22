from __future__ import annotations

import json
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"
JSON_LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)

TOOL_PAGES = (
    "change-surface-mapper", "identifier-check", "integrity-check", "integrity-scanner",
    "regulatory-change-impact", "technical-file-consistency", "ecoa-delivery-workbench",
    "coa-type-finder", "ecoa-lead-time-planner", "ecoa-visit-burden", "danish-dhpc-checker",
    "danish-pv-literature-register", "sdea-clause-checker",
)
DATE_DEPENDENT = ("danish-dhpc-checker", "sdea-clause-checker", "danish-pv-literature-register", "ecoa-lead-time-planner", "identifier-check")


def _blocks(slug: str) -> list[dict]:
    html = (DOCS / f"{slug}.html").read_text(encoding="utf-8")
    return [json.loads(b) for b in JSON_LD.findall(html)]


def test_every_tool_page_declares_a_free_web_application_and_breadcrumb() -> None:
    for slug in TOOL_PAGES:
        html = (DOCS / f"{slug}.html").read_text(encoding="utf-8")
        canonical = re.search(r'<link rel="canonical" href="(.*?)"', html).group(1)
        types = {b.get("@type"): b for b in _blocks(slug)}
        app = types.get("WebApplication")
        assert app, slug
        assert app["url"] == canonical and app["isAccessibleForFree"] is True, slug
        crumbs = types.get("BreadcrumbList")
        assert crumbs, slug
        assert crumbs["itemListElement"][-1]["item"] == canonical, slug


def test_structured_data_makes_no_claim_beyond_what_the_page_says() -> None:
    for slug in TOOL_PAGES:
        for block in _blocks(slug):
            assert "aggregateRating" not in block and "review" not in block, slug
            assert "offers" not in block, slug


def test_date_dependent_tools_carry_a_review_due_date() -> None:
    for slug in DATE_DEPENDENT:
        html = (DOCS / f"{slug}.html").read_text(encoding="utf-8")
        assert "Review due by 14 February 2027" in html, slug
