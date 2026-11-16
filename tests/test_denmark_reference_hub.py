"""Denmark reference hub (/denmark-market-access): structure, claim ids, banned phrases.

The hub is a dated reference page. Every number and date in a sourced row must
come from a registry entry (primary evidence, website allowed, review within 90
days of the 16 November 2026 read), and nothing may be shown that the page says
it does not show.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

from clinicops_os.claim_registry import load_registry
from clinicops_os.publication import build_publication_pack

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "denmark-market-access.html"
REGISTRY = ROOT / "research" / "claims.jsonl"

READ_DATE = date(2026, 11, 16)
MAX_REVIEW = READ_DATE + timedelta(days=90)
HUB_CLAIM_RANGE = range(401, 456)
ALLOWED_SOURCE_HOSTS = {
    "laegemiddelstyrelsen.dk",
    "www.videnskabsetik.dk",
    "trialnation.dk",
}
SECTION_IDS = ("trial-nation", "ctr-route", "device-route", "language", "change-log", "not-shown", "danish-pv")


def _html() -> str:
    return PAGE.read_text(encoding="utf-8")


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)).replace("&amp;", "&")


def _declared_ids(html: str) -> list[str]:
    match = re.search(r"<!--\s*claim-ids:\s*([^>]+?)\s*-->", html)
    assert match, "claim-ids comment missing"
    return [item.strip() for item in match.group(1).split(",") if item.strip()]


def _registry() -> dict:
    return {claim.claim_id: claim for claim in load_registry(REGISTRY)}


def _hub_claims() -> dict:
    return {cid: claim for cid, claim in _registry().items() if int(cid[-4:]) in HUB_CLAIM_RANGE}


def test_page_structure_and_framing() -> None:
    html = _html()
    assert "<title>Denmark Reference: Clinical Trial and Device Study Routes | ClinicOps</title>" in html
    assert 'rel="canonical" href="https://clinicops.dk/denmark-market-access"' in html
    for section_id in SECTION_IDS:
        assert f'id="{section_id}"' in html, section_id
    # one h1, sections in the brief's order
    assert len(re.findall(r"<h1>", html)) == 1
    order = [html.index(f'id="{s}"') for s in SECTION_IDS[:6]]
    assert order == sorted(order)
    assert "Denmark-specialised and EU-wide" in html
    assert "Danish-led" not in html
    assert "Review due by 14 February 2027" in html
    assert "sources read 2026-11-16" in html
    # the lane the existing positioning test depends on stays discoverable
    assert 'id="danish-pv"' in html


def test_blocked_sources_are_declared_not_scraped() -> None:
    html = _html()
    assert "nvk.dk and nationaltcentre.dk refuse automated access" in html
    assert "nvk.dk" not in re.findall(r'href="https?://([^/"]+)', html)
    assert "nationaltcentre.dk" not in re.findall(r'href="https?://([^/"]+)', html)
    assert "retsinformation.dk needs JavaScript" in html


def test_trial_nation_is_linked_never_mirrored() -> None:
    html = _html()
    assert "trialnation.dk/professional/resources-2-2-3-5/" in html
    for token in (".docx", ".xlsx", "trialnation.dk/wp-content"):
        assert token not in html, token
    assert "does not host or mirror any template" in html


def test_claim_ids_are_declared_and_pass_the_website_gate() -> None:
    html = _html()
    declared = _declared_ids(html)
    referenced = set(re.findall(r"CO-CLM-\d{4}", html))
    assert referenced == set(declared), referenced ^ set(declared)
    assert "<!-- claim-use: website -->" in html
    # same gate as the markdown content validator, evaluated today
    build_publication_pack(
        list(_registry().values()), declared, title="denmark-market-access", use="website", as_of=datetime.now(UTC).date()
    )


def test_every_hub_entry_is_primary_website_allowed_and_reviewed_within_90_days() -> None:
    claims = _hub_claims()
    assert len(claims) >= 30
    declared = set(_declared_ids(_html()))
    assert set(claims) == declared, "registry hub entries and page ids must match exactly"
    for cid, claim in claims.items():
        assert claim.evidence_class.value == "primary", cid
        assert claim.status.value == "qualified", cid
        assert "website" in claim.allowed_uses, cid
        assert claim.limitations, cid
        assert claim.review_after is not None and claim.review_after <= MAX_REVIEW, cid
        assert claim.sources, cid
        for source in claim.sources:
            assert urlparse(source).netloc in ALLOWED_SOURCE_HOSTS, (cid, source)


def test_numbers_and_dates_in_sourced_rows_come_from_their_claims() -> None:
    html = _html()
    registry = _registry()
    checked = 0
    for match in re.finditer(r'<(tr|p|div)\b[^>]*data-claims="([^"]+)"[^>]*>(.*?)</\1>', html, re.DOTALL):
        ids = [item.strip() for item in match.group(2).split(",")]
        row_numbers = {str(int(n)) for n in re.findall(r"\d+", _text(match.group(3)))}
        claim_numbers: set[str] = set()
        for cid in ids:
            assert cid in registry, cid
            claim_numbers |= {str(int(n)) for n in re.findall(r"\d+", registry[cid].text)}
        extra = row_numbers - claim_numbers
        assert not extra, f"{ids}: numbers not in the cited claims: {sorted(extra)} in {_text(match.group(3))[:80]!r}"
        checked += 1
    assert checked >= 60


def test_device_fee_table_is_exactly_the_four_read_amounts() -> None:
    html = _html()
    amounts = set(re.findall(r"DKK\s?([\d,]+)", html))
    assert amounts == {"46,835", "62,947", "10,364", "13,069"}
    assert "Fee review due by 8 January 2027" in html
    assert "period 2025-2027" in html
    assert "adjusted once a year on 1 January" in html


def test_no_drug_fee_figures_compensation_caps_or_unread_rules() -> None:
    lower = _html().lower()
    for token in ("25 million", "dkk 5 million", "dkk 10,000", "compensation cap", "per injured person"):
        assert token not in lower, token
    # the drug-trial fee row says nothing is shown
    assert "fee amounts for drug trials are not shown" in lower
    assert "no figure is shown: not verified at source" in lower
    # rules the page declares it does not know must not appear as rules
    assert "gene-therapy trial notifications" in lower and "not found on the pages read" in lower


def test_banned_and_out_of_scope_wording() -> None:
    html = _html()
    lower = html.lower()
    for token in (
        "danish-led",
        "audit-ready",
        "audit ready",
        "iso-aligned",
        "trusted by",
        "insured",
        "certified",
        "validated",
        "we act as your legal representative",
        "cold email",
        "reach out to",
        "iskandar",
        "kokkedal",
        "linkedin.com/in/",
        "physician",
    ):
        assert token not in lower, token
    # boundary: no mandate offered, stated plainly
    assert "ClinicOps is not a sponsor, legal representative, authorised representative, monitor or contact point" in html
    assert "ClinicOps is not a legal representative and does not offer the role" in html


def test_ctis_email_statement_is_marked_superseded_not_current() -> None:
    html = _html()
    assert "The later item is the current statement." in html
    assert html.count("does not send email notifications") == 1
    assert "An older Agency page (27 October 2025) says CTIS does not send email notifications" in html


def test_change_log_entries_are_dated_newest_first() -> None:
    html = _html()
    section = html[html.index('id="change-log"') : html.index('id="not-shown"')]
    months = {m: i for i, m in enumerate(
        ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}
    dates: list[date] = []
    for row in re.findall(r"<tr data-claims=[^>]*><th scope=\"row\">(.*?)</th>", section):
        parts = row.split()
        if len(parts) == 3:
            dates.append(date(int(parts[2]), months[parts[1]], int(parts[0])))
    assert len(dates) >= 12
    assert dates == sorted(dates, reverse=True)
    assert "Next scheduled check: fee table on 1 January 2027" in section
