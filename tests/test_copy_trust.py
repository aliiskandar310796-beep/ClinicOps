"""Trust-copy contract (plenum lenses 05, 09, 18, 25, 28, 31, 33; 2026-11-16).

Pins the wording corrections so retired phrases cannot return and so the About,
partners, privacy and SS(C)P pages keep saying what they now say: ClinicOps is
one person, nothing implies a standing team or cover that does not exist, and
every date on the SS(C)P explainer comes from a registered claim that is
allowed for website use.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _read(rel: str) -> str:
    return (DOCS / rel).read_text(encoding="utf-8")


def _registry() -> dict[str, dict]:
    rows = [
        json.loads(line)
        for line in (ROOT / "research" / "claims.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {row["id"]: row for row in rows}


# Phrases retired on 2026-11-16. The corrections log paraphrases them on
# purpose, so they must be absent from every served page, the llms.txt, the
# README and the website source pack.
RETIRED_PHRASES = (
    "specialist depth on demand",
    "expert-network model",
    "medicine and nursing",
    "independent clinical subject-matter",
    "extension of your QPPV",
    "contract-ready",
    "audit-ready",
    "danish linguistic validation",
    "danish-led",
    "foot of this page",
    "vigilance contact",
    "vigilance-kontakt",
    "we keep no marketing list",
    "vi f&oslash;rer ingen markedsf&oslash;ringsliste",
    "signs every deliverable",
)


def _scanned_files() -> list[Path]:
    files = list(DOCS.rglob("*.html")) + [DOCS / "llms.txt", ROOT / "README.md"]
    files += sorted((ROOT / "website").glob("*.md"))
    return files


def test_retired_phrases_cannot_return() -> None:
    offenders = []
    for path in _scanned_files():
        text = path.read_text(encoding="utf-8").lower()
        for phrase in RETIRED_PHRASES:
            if phrase.lower() in text:
                offenders.append(f"{path.relative_to(ROOT)}: {phrase}")
    assert not offenders, offenders


def test_retired_phrases_are_in_the_professional_claims_gate() -> None:
    gate = (ROOT / "scripts" / "validate_professional_claims.py").read_text(encoding="utf-8")
    for phrase in ("specialist depth on demand", "expert-network model", "medicine and nursing", "Danish-led", "vigilance contact"):
        assert phrase in gate, phrase


# --- About -----------------------------------------------------------------


def test_about_says_it_is_one_person_and_claims_nothing_it_lacks() -> None:
    html = _read("about.html")
    assert "one-person regulatory data integrity practice" in html
    assert "autónomo" in html or "aut&oacute;nomo" in html
    assert "ClinicOps does the work itself" in html
    assert "No certification is held, and no insurance cover is claimed" in html
    assert "There is no standing team" in html
    # Impersonal: no founder name, address or tax ID (pending the imprint decision).
    for token in ("Iskandar", "NIF", "Egedals", "Kokkedal"):
        assert token not in html, token
    # Pending the independence decision: no language-work disclosure on About.
    lower = html.lower()
    for token in ("freelance", "language-service providers he", "post-editing"):
        assert token not in lower, token


def test_about_discloses_ai_assisted_drafting_without_overclaiming() -> None:
    html = _read("about.html")
    assert "AI-assisted drafting." in html
    assert "AI assistants to help draft and check site text, research notes and code" in html
    assert "language-model agents" in html  # the September SS(C)P scan used them
    assert "not put into AI tools unless the client has agreed in writing" in html
    # The tools statement stays bounded to the tools.
    assert "do not use a language model to produce findings" in html
    assert "The free tools are different" in html


def test_about_carries_a_keepable_corrections_protocol_and_working_rules() -> None:
    html = _read("about.html")
    assert "acknowledged within 2 working days and decided within 10 working days" in html
    assert "under review" in html
    assert 'href="research#cite-and-correct"' in html
    assert 'id="cite-and-correct"' in _read("research.html")
    for line in ("No referral fees.", "No sponsored research.", "Findings are never a sales lever."):
        assert line in html, line
    assert "fewer than 5 entities" in html


# --- Partners --------------------------------------------------------------


def test_partner_page_resolves_the_handover_versus_white_label_contradiction() -> None:
    html = _read("expert-network.html")
    assert "signs every deliverable" not in html
    assert "Signed handover note" in html and "White-label work product" in html
    assert "carries no ClinicOps signature" in html
    assert "<title>Working with partners | ClinicOps</title>" in html


def test_partner_page_has_types_scope_boundary_and_defaults() -> None:
    html = _read("expert-network.html")
    for phrase in (
        "Language-service providers",
        "CROs and eCOA vendors",
        "Manufacturers and authorised representatives",
        "<h2>Not in scope</h2>",
        "LQA scoring",
        "Bulk upload or registration of data in EUDAMED",
        "legal representative",
        "Data default",
        "Working without a written limit of liability is not offered",
        "No price is shown",
        "Notified-body conflict check",
        'id="language-providers"',
        "No translation. No LQA scoring",
    ):
        assert phrase in html, phrase
    assert "EUR" not in html and "&euro;" not in html, "no price before cover or a signed cap"
    assert "There is no standing team" in html
    # No named party anywhere on the partners page.
    for name in ("TransPerfect", "Welocalize", "RWS", "Acolad"):
        assert name not in html, name


def test_notified_body_conflict_check_rests_on_a_registered_website_claim() -> None:
    html = _read("expert-network.html")
    declared = re.search(r"<!--\s*claim-ids:\s*([^>]+?)\s*-->", html)
    assert declared, "partners page must declare the claim ids it relies on"
    ids = [x.strip() for x in declared.group(1).split(",")]
    registry = _registry()
    assert "CO-CLM-0070" in ids
    claim = registry["CO-CLM-0070"]
    assert "website" in claim["allowed_uses"] and claim["status"] in {"verified", "qualified"}
    assert "three years" in claim["claim"] and "1.2.4" in claim["claim"]
    assert claim["limitations"]
    assert "Annex VII point 1.2" in html and "three-year look-back" in html


def test_paused_specialist_page_does_not_describe_a_network() -> None:
    html = _read("expert-network-interest.html")
    assert "private, project-specific specialist network" not in html
    assert "expert-network screening pipeline" not in html
    assert "Working with partners</a>" in html


def test_live_site_title_markers_match_the_served_pages() -> None:
    spec = importlib.util.spec_from_file_location("check_live_site", ROOT / "scripts" / "check_live_site.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    problems = []
    for target in module.TARGETS:
        if not target.marker.startswith("<title>"):
            continue
        path = target.path
        if path == "/":
            page = DOCS / "index.html"
        elif path.endswith("/"):
            page = DOCS / path.strip("/") / "index.html"
        else:
            page = DOCS / path.lstrip("/")
            if not page.suffix:
                page = page.with_suffix(".html")
        if target.marker not in page.read_text(encoding="utf-8"):
            problems.append(f"{target.path}: {target.marker}")
    assert not problems, problems


# --- Privacy notice --------------------------------------------------------


def test_privacy_notice_outreach_data_drops_vigilance_contact_in_both_languages() -> None:
    html = _read("privacy-notice/index.html")
    assert "vigilance" not in html.lower()
    assert "a person named as a regulatory contact in a published document" in html
    assert "regulatorisk kontakt i et offentliggjort dokument" in html


def test_privacy_notice_states_the_list_position_and_the_ai_line() -> None:
    html = _read("privacy-notice/index.html")
    assert "we keep no newsletter or mailing list, only the prospect and suppression records" in html
    assert "ingen nyhedsbrevs- eller mailingliste" in html
    section6 = html.split("<h2>6. Recipients and processors</h2>", 1)[1].split("<h2>7. Retention</h2>", 1)[0]
    assert "AI assistants." in section6
    assert "unless the client has agreed in writing" in section6
    assert "AI-assistenter." in html
    # Pending the imprint decision (D1): the on-request sentence stays untouched.
    assert "Registered business address and tax identification details are available on request" in html


# --- Positioning and the dangling reference --------------------------------


def test_denmark_page_uses_the_agreed_positioning() -> None:
    html = _read("denmark-market-access.html")
    assert "Denmark-specialised and EU-wide" in html
    assert "danish-led" not in html.lower()


def test_home_page_states_the_danish_limits_inline() -> None:
    html = _read("index.html")
    assert "foot of this page" not in html
    assert "within these limits: Danish language and records work only" in html


# --- SS(C)P explainer ------------------------------------------------------


def test_sscp_page_is_an_explainer_with_registered_dates_only() -> None:
    html = _read("sscp-operations.html")
    assert "mailto:" not in html.split("<footer", 1)[0], "no sales call to action on the explainer"
    for phrase in ("What it is", "Who does what", "<h2>Dates</h2>", "ClinicOps does not draw up, validate or approve an SS(C)P"):
        assert phrase in html, phrase
    declared = re.search(r"<!--\s*claim-ids:\s*([^>]+?)\s*-->", html)
    assert declared
    ids = [x.strip() for x in declared.group(1).split(",")]
    registry = _registry()
    today = date.today()  # noqa: DTZ011 - calendar-date expiry, same as the content gate
    for claim_id in ids:
        claim = registry[claim_id]
        assert "website" in claim["allowed_uses"], claim_id
        assert not claim["superseded_by"], claim_id
        assert claim["status"] in {"verified", "qualified"}, claim_id
        review = claim["review_after"]
        assert not review or today <= date.fromisoformat(review), claim_id
    # The two dates on the page, each traceable to a claim it declares.
    body = html.split("<main", 1)[1].split("</main>", 1)[0]
    assert "December 2026" in body and "CO-CLM-0018" in ids
    assert "27 March 2027" in body and "CO-CLM-0019" in ids
    assert "not a statutory deadline" in body or "recommendation" in body
    # No other calendar date than the stamps and the two registered ones.
    allowed = {"December 2026", "July 2026", "27 March 2027", "16 November 2026", "31 January 2027", "October 2026"}
    month = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    for found in re.findall(rf"(?:\d{{1,2}} )?{month} 20\d\d", re.sub(r"<[^>]+>", " ", body)):
        assert found in allowed, found


def test_sscp_page_title_matches_the_live_site_marker() -> None:
    html = _read("sscp-operations.html")
    marker = "<title>SS(C)P operations explained: who does what | ClinicOps</title>"
    assert marker in html
    assert marker in (ROOT / "scripts" / "check_live_site.py").read_text(encoding="utf-8")


# --- Corrections log -------------------------------------------------------


def test_each_wording_correction_is_logged_with_the_date() -> None:
    log = (ROOT / "research" / "corrections" / "2026-11-16-wording-corrections.md").read_text(encoding="utf-8")
    assert log.count("## Correction ") >= 7
    research = _read("research.html")
    assert research.count("<strong>16 November 2026.</strong>") >= 5
    assert "acknowledged within 2 working days and decided within 10 working days" in research
