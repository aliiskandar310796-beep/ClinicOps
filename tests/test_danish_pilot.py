"""Danish pilot: English stays authoritative, Danish pages are draft translations.

Pins the contract of docs/da/ (two pages), data/hreflang_pairs.json, the
source-hash stale-twin check, the Danish shell handling in the harmonizer, the
sitemap rule that keeps noindex pages out, and research/glossary-da.csv.

The hreflang sitemap generator is built on another branch (generators-seo);
the sitemap assertions below hold whether or not it has landed.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from xml.etree import ElementTree

import pytest

from clinicops_os.claim_registry import RegistryClaim, audit_registry, load_registry
from clinicops_os.site_quality import parse_metadata, validate_page_metadata
from clinicops_os.translation_sync import (
    check_translation,
    english_hashes,
    english_units,
    read_stamp,
    restamp,
    translated_pages,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAIRS_FILE = ROOT / "data" / "hreflang_pairs.json"
GLOSSARY = ROOT / "research" / "glossary-da.csv"
SITEMAP = DOCS / "sitemap.xml"
BASE = "https://clinicops.dk"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}

BANNER = "Dansk oversættelse. Den engelske version er gældende."
DRAFT_LABEL = "Maskinoversat udkast til gennemlæsning"


def _load_script(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pairs() -> list[dict[str, str]]:
    return json.loads(PAIRS_FILE.read_text(encoding="utf-8"))["pairs"]


def _file_for(url: str) -> Path:
    path = url.removeprefix(BASE)
    return DOCS / ((path.lstrip("/") + "index.html") if path.endswith("/") else path.lstrip("/"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sitemap_locs() -> list[str]:
    root = ElementTree.fromstring(_read(SITEMAP))
    return [el.text.strip() for el in root.findall("sm:url/sm:loc", NS) if el.text]


# --- hreflang pair file ------------------------------------------------------


def test_pairs_file_declares_schema_and_the_two_pilot_pairs() -> None:
    data = json.loads(_read(PAIRS_FILE))
    assert "_schema" in data
    assert data["default_language"] == "en" and data["x_default"] == "en"
    assert [(p["en"], p["da"]) for p in data["pairs"]] == [
        (f"{BASE}/", f"{BASE}/da/"),
        (f"{BASE}/privacy-notice/", f"{BASE}/da/privacy-notice/"),
    ]
    assert all(p["status"] in {"draft_pending_review", "reviewed"} for p in data["pairs"])


def test_every_pair_is_two_self_canonical_pages_in_the_right_languages() -> None:
    for pair in _pairs():
        en_html, da_html = _read(_file_for(pair["en"])), _read(_file_for(pair["da"]))
        assert re.search(r"<html lang=\"en\"", en_html)
        assert re.search(r"<html lang=\"da\"", da_html)
        assert parse_metadata(en_html).canonical == pair["en"]
        # Never canonicalise the Danish page to the English one.
        assert parse_metadata(da_html).canonical == pair["da"]
        assert validate_page_metadata(da_html, expected_url=pair["da"]) == []


def test_danish_pages_are_exactly_the_paired_pages() -> None:
    paired = {_file_for(p["da"]).relative_to(DOCS).as_posix() for p in _pairs()}
    assert {p.relative_to(DOCS).as_posix() for p in translated_pages(DOCS)} == paired


# --- draft status: noindex, not in the sitemap, honest labels -----------------


def _status(html: str) -> str:
    return parse_metadata(html).meta.get("translation-status", "")


def test_draft_danish_pages_are_noindex_labelled_and_pending() -> None:
    for pair in _pairs():
        da = _read(_file_for(pair["da"]))
        meta = parse_metadata(da).meta
        if _status(da) == "draft-pending-founder-review":
            assert pair["status"] == "draft_pending_review"
            assert meta["robots"].replace(" ", "").lower() == "noindex,follow"
            assert BANNER in da and DRAFT_LABEL in da
            assert f'href="{pair["en"].removeprefix(BASE)}"' in da  # visible link to the English twin
        else:
            assert _status(da) == "reviewed"
            assert pair["status"] == "reviewed"
            assert "noindex" not in meta.get("robots", "").lower()
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta.get("translation-reviewed", ""))
            assert DRAFT_LABEL not in da


def test_draft_pages_stay_out_of_sitemap_llms_and_hreflang_alternates() -> None:
    locs = _sitemap_locs()
    llms = _read(DOCS / "llms.txt")
    sitemap_text = _read(SITEMAP)
    for pair in _pairs():
        if pair["status"] != "draft_pending_review":
            continue
        assert pair["da"] not in locs and pair["da"] not in llms
        # hreflang to a noindex page is ignored by Google: never emitted while draft
        assert pair["da"] not in re.findall(r'href="([^"]+)"', sitemap_text)


def test_sitemap_hreflang_block_if_present_is_reciprocal_and_indexable_only() -> None:
    root = ElementTree.fromstring(_read(SITEMAP))
    locs = {el.text.strip() for el in root.findall("sm:url/sm:loc", NS) if el.text}
    alternates: dict[str, dict[str, str]] = {}
    for url in root.findall("sm:url", NS):
        loc = url.find("sm:loc", NS).text.strip()  # type: ignore[union-attr]
        links = {a.get("hreflang"): a.get("href") for a in url.findall("x:link", NS) if a.get("rel") == "alternate"}
        if links:
            alternates[loc] = links
    for loc, links in alternates.items():
        assert links.get("x-default"), loc
        for href in links.values():
            assert href in locs, f"{loc}: alternate {href} is not an indexable sitemap URL"
        assert loc in links.values(), f"{loc}: must list itself"
    # reciprocity: if A lists B, B lists A
    for loc, links in alternates.items():
        for href in links.values():
            assert set(alternates.get(href, {}).values()) == set(links.values()), (loc, href)


def test_render_sitemap_excludes_noindex_pages_and_includes_indexable_ones(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    render_sitemap = _load_script("render_sitemap")
    docs = tmp_path / "docs"
    (docs / "da").mkdir(parents=True)

    def page(canonical: str, robots: str) -> str:
        return (
            f'<!doctype html><html lang="da"><head><meta name="robots" content="{robots}">'
            f'<link rel="canonical" href="{canonical}"></head><body></body></html>'
        )

    (docs / "index.html").write_text(page(f"{BASE}/", "index,follow"), encoding="utf-8")
    (docs / "da" / "index.html").write_text(page(f"{BASE}/da/", "noindex,follow"), encoding="utf-8")
    monkeypatch.setattr(render_sitemap, "DOCS", docs)
    assert render_sitemap.discover_urls() == [f"{BASE}/"]
    (docs / "da" / "index.html").write_text(page(f"{BASE}/da/", "index,follow"), encoding="utf-8")
    assert render_sitemap.discover_urls() == [f"{BASE}/", f"{BASE}/da/"]


def test_real_sitemap_has_no_danish_url_and_ceiling_is_untouched() -> None:
    assert not [loc for loc in _sitemap_locs() if "/da/" in loc]
    strategic = _read(ROOT / "tests" / "test_strategic_invariants.py")
    assert "SITEMAP_URL_CEILING = 48" in strategic


# --- source hashes: English change -> Danish stale ----------------------------


@pytest.mark.parametrize("danish", sorted(p.relative_to(DOCS).as_posix() for p in translated_pages(DOCS)))
def test_danish_page_is_in_sync_with_its_english_source(danish: str) -> None:
    da_html = _read(DOCS / danish)
    stamp = read_stamp(da_html)
    assert stamp.source
    assert check_translation(da_html, _read(DOCS / stamp.source), danish) == []


def test_every_english_unit_is_translated_or_explicitly_skipped() -> None:
    for page in translated_pages(DOCS):
        stamp = read_stamp(_read(page))
        english = set(english_units(_read(DOCS / stamp.source)))  # type: ignore[arg-type]
        assert english - {"head"} == set(stamp.units) | set(stamp.skipped), page


def test_privacy_notice_translation_covers_every_english_section() -> None:
    units = set(english_units(_read(DOCS / "privacy-notice" / "index.html")))
    # The English page's own Danish section (lang="da") is not a source unit.
    assert not any(key.startswith("dansk") for key in units)
    assert {"who-we-are", "this-website", "email-enquiries", "client-engagements",
            "business-development-and-outreach", "recipients-and-processors", "retention",
            "your-rights", "changes"} <= units


def test_changed_english_text_makes_the_danish_unit_stale() -> None:
    source = _read(DOCS / "privacy-notice" / "index.html")
    da_html = _read(DOCS / "da" / "privacy-notice" / "index.html")
    edited = source.replace("any publicly stated regulatory role (for example, a person named as a regulatory contact in a published document)",
                            "any publicly stated regulatory role")
    assert edited != source
    errors = check_translation(da_html, edited)
    assert any("business-development-and-outreach" in e for e in errors)
    assert any("page hash" in e for e in errors)
    # unrelated sections stay clean
    assert not any("retention" in e for e in errors)


def test_markup_only_english_edits_do_not_make_the_danish_stale() -> None:
    source = _read(DOCS / "privacy-notice" / "index.html")
    reformatted = source.replace("<p><strong>Microsoft.</strong>", '<p class="x"><strong>Microsoft.</strong>').replace("\n", "\n ")
    assert check_translation(_read(DOCS / "da" / "privacy-notice" / "index.html"), reformatted) == []


def test_new_or_removed_english_section_is_reported() -> None:
    source = _read(DOCS / "privacy-notice" / "index.html")
    da_html = _read(DOCS / "da" / "privacy-notice" / "index.html")
    added = source.replace("</div>\n</main>", '<section><h2>11. Cookies</h2><div><p>None.</p></div></section></div>\n</main>')
    assert any("'cookies'" in e and "neither translated" in e for e in check_translation(da_html, added))
    removed = re.sub(r"<section><h2>7\. Retention</h2>.*?</section>\n", "", source, flags=re.DOTALL)
    assert any("'retention' no longer exists" in e for e in check_translation(da_html, removed))


def test_changed_english_link_target_is_noticed() -> None:
    source = _read(DOCS / "privacy-notice" / "index.html")
    changed = source.replace("mailto:info@clinicops.dk", "mailto:other@clinicops.dk")
    assert english_hashes(changed) != english_hashes(source)


def test_restamp_records_reconfirmation_and_is_idempotent() -> None:
    source = _read(DOCS / "privacy-notice" / "index.html")
    da_html = _read(DOCS / "da" / "privacy-notice" / "index.html")
    edited = source.replace("twelve months", "eleven months")
    assert check_translation(da_html, edited)
    fixed = restamp(da_html, edited)
    assert check_translation(fixed, edited) == []
    assert restamp(fixed, edited) == fixed
    # restamp changes only hash attributes, never visible text
    assert re.sub(r'data-source[a-z-]*="[^"]*"', "", fixed) == re.sub(r'data-source[a-z-]*="[^"]*"', "", da_html)


def test_sync_script_passes_on_the_repo() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_translation_sync.py")],
        cwd=ROOT, capture_output=True, text=True, check=False,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": ""},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "translation sync contract: OK" in result.stdout


# --- harmonizer: Danish shell, language switcher ------------------------------


def test_danish_header_links_only_danish_pages_and_the_english_twin() -> None:
    for pair in _pairs():
        html = _read(_file_for(pair["da"]))
        header = re.search(r"<header class=\"site\">.*?</header>", html, re.DOTALL).group(0)  # type: ignore[union-attr]
        hrefs = re.findall(r'<nav class="primary".*?</nav>', header, re.DOTALL)[0]
        assert 'href="/da/"' in hrefs and 'href="/da/privacy-notice/"' in hrefs
        assert f'href="{pair["en"].removeprefix(BASE)}" hreflang="en"' in hrefs
        for english_label in ("Medical devices", "Clinical operations", "Tools", "Research", "About", "Contact"):
            assert f">{english_label}<" not in header
        assert "Gå til indhold" in html and "Skip to content" not in html
        assert "ClinicOps er hverken et bemyndiget organ eller en kompetent myndighed" in html


def test_no_auto_redirect_and_no_script_beyond_the_shared_nav_snippet() -> None:
    for page in translated_pages(DOCS):
        html = _read(page)
        assert "http-equiv=\"refresh\"" not in html.lower()
        assert "navigator.language" not in html and "location." not in html
        assert "<script src" not in html
        assert not re.search(r"\b(fetch|XMLHttpRequest|sendBeacon)\b", html)


def test_english_twins_link_to_danish_only_when_the_twin_is_reviewed(monkeypatch: pytest.MonkeyPatch) -> None:
    shell = _load_script("harmonize_public_shell")
    page = DOCS / "privacy-notice" / "index.html"
    text = _read(page)
    # draft: no link, so an unreviewed machine translation is not promoted
    assert 'hreflang="da"' not in text
    assert shell.transform(page, text) == text
    reviewed = [dict(p, status="reviewed") for p in _pairs()]
    monkeypatch.setattr(shell, "_pairs", lambda: reviewed)
    once = shell.transform(page, text)
    assert once.count('hreflang="da"') == 1 and 'href="/da/privacy-notice/"' in once
    assert shell.transform(page, once) == once  # idempotent
    # pages without a twin never get a switcher
    other = DOCS / "about.html"
    assert 'hreflang="da"' not in shell.transform(other, _read(other))


def test_lang_da_is_only_allowed_under_docs_da(tmp_path: Path) -> None:
    shell = _load_script("harmonize_public_shell")
    page = DOCS / "about.html"
    text = _read(page).replace('<html lang="en"', '<html lang="da"', 1)
    with pytest.raises(ValueError, match="lang=\"da\""):
        shell.transform(page, text)


def test_danish_pages_are_registered_in_the_shell_and_llms_registries() -> None:
    shell = _load_script("harmonize_public_shell")
    llms = _load_script("render_llms_txt")
    for relative in ("da/index.html", "da/privacy-notice/index.html"):
        assert relative in shell.SECTION_BY_PAGE
        assert any(match(relative) for _, match in llms.SECTIONS)


# --- content guards -----------------------------------------------------------


def test_danish_pages_keep_the_impersonal_brand_and_make_no_unregistered_claims() -> None:
    for page in translated_pages(DOCS):
        html = _read(page)
        assert "Egedalsv" not in html and "Kokkedal" not in html
        assert not re.search(r"\b(læge|lægen|doktor|physician)\b", html, re.IGNORECASE)
        for banned in ("certificeret", "forsikret", "valideret", "revisionsklar", "betroet af", "ISO-"):
            assert banned.lower() not in html.lower(), (page, banned)
        assert "CO-CLM-" not in html, "Danish pages carry no registered claim IDs; add `translations` entries first"


def test_danish_landing_makes_no_figure_or_dated_claim_the_english_home_does_not() -> None:
    html = _read(DOCS / "da" / "index.html")
    body = re.sub(r"<!--.*?-->|<script.*?</script>|<style.*?</style>|<[^>]+>", " ", html.split("<body", 1)[1].split(">", 1)[1], flags=re.DOTALL)
    assert set(re.findall(r"\d+", body)) <= {"2026"}
    assert "info@clinicops.dk" in html
    for tool in ("ecoa-delivery-workbench", "integrity-scanner", "danish-dhpc-checker"):
        assert f'href="/{tool}"' in html
    assert len(re.findall(r'class="tool-list"', html)) == 1 and html.count("<li><a") == 3


def test_danish_privacy_notice_keeps_every_limit_of_the_english_notice() -> None:
    da = _read(DOCS / "da" / "privacy-notice" / "index.html")
    for needle in (
        "ingen cookies", "ingen analyse", "STOP", "tolv måneder", "højst tre", "Datatilsynet", "Forbrugerombudsmanden",
        "Agencia Española de Protección de Datos (AEPD)", "artikel 21", "artikel 77", "artikel 9", "Microsoft Ireland Operations Limited",
        "GitHub, Inc.", "Spanien (selvstændig erhvervsdrivende, med kunder i Danmark og EU)", "Send ikke patientidentificerbare oplysninger",
        "ikke uopfordret e-mail eller direkte beskeder til organisationer, der er etableret i Danmark", "info@clinicops.dk",
    ):
        assert needle in da, needle
    # numbers in the English notice survive in Danish ("twelve months", "three messages")
    en = _read(DOCS / "privacy-notice" / "index.html")
    assert "twelve months" in en and "at most three messages" in en


# --- glossary -----------------------------------------------------------------


def _glossary() -> list[dict[str, str]]:
    with GLOSSARY.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_glossary_schema_sources_and_blank_rows() -> None:
    rows = _glossary()
    assert list(rows[0]) == ["en", "da", "source_url", "notes"]
    assert len({r["en"].lower() for r in rows}) == len(rows)
    filled = [r for r in rows if r["da"].strip()]
    assert len(filled) >= 25
    for row in filled:
        assert re.match(r"https://eur-lex\.europa\.eu/legal-content/DA/TXT/HTML/\?uri=CELEX:\d{5}[A-Z]\d{4}$", row["source_url"]), row
    for row in rows:
        if not row["da"].strip():
            assert not row["source_url"] and row["notes"].startswith("BLANK:"), row


def test_danish_privacy_notice_uses_the_glossary_terms() -> None:
    text = _read(DOCS / "da" / "privacy-notice" / "index.html").lower()
    stems = ("personoplysninger", "dataansvarlig", "databehandler", "tilsynsmyndighed", "legitim", "samtykke",
             "berigtigelse", "dataportabilitet", "indsigelse", "særlige kategorier af personoplysninger",
             "standardbestemmelser om databeskyttelse", "brugsanvisning", "fabrikant", "helbredsoplysninger")
    glossary_terms = " ".join(r["da"].lower() for r in _glossary() if r["da"])
    for stem in stems:
        assert stem in glossary_terms, stem
        assert stem in text, stem
    assert "producent" not in text  # standing ruling: fabrikant


# --- claims registry `translations` field -------------------------------------


def _claim(**overrides: object) -> RegistryClaim:
    row = {
        "id": "CO-CLM-9001", "claim": "English wording.", "evidence_class": "primary", "status": "verified",
        "sources": ["https://eur-lex.europa.eu/"], "limitations": [], "allowed_uses": ["website"],
        "review_after": "2027-05-14", "supersedes": [], "superseded_by": None,
        # registry-stamps schema: a live claim needs a class, a read date and a method
        "risk_class": "E", "last_verified": "2026-11-16", "verified_method": "read-primary",
        "label": "Test claim", "source_date": "Test source, 2026", "not_established": ["Anything else."],
    }
    row.update(overrides)
    return RegistryClaim.from_dict(row)


def test_registry_claims_accept_optional_translations() -> None:
    from datetime import date

    assert all(c.translations == () for c in load_registry(ROOT / "research" / "claims.jsonl"))
    good = _claim(translations={"da": "Dansk ordlyd."})
    assert good.translations == (("da", "Dansk ordlyd."),)
    assert audit_registry([good], date(2026, 11, 16)) == []
    bad = [_claim(translations={"en": "x"}), _claim(translations={"danish": "x"}), _claim(translations={"da": " "})]
    for claim in bad:
        findings = audit_registry([claim], date(2026, 11, 16))
        assert findings and all(f.severity == "error" for f in findings)


# --- professional-claims gate: Danish boundary phrase only under docs/da/ ------


def test_qppv_boundary_rule_accepts_the_danish_phrase_only_on_danish_pages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    gate = _load_script("validate_professional_claims")
    docs = tmp_path / "docs"
    (docs / "da").mkdir(parents=True)
    (docs / "about.html").write_text("<html>explicitly appointed</html>", encoding="utf-8")
    monkeypatch.setattr(gate, "DOCS", docs)
    sentence = "<html>QPPV skal være udtrykkeligt udpeget</html>"
    (docs / "da" / "page.html").write_text(sentence, encoding="utf-8")
    assert gate.main() == 0
    (docs / "page.html").write_text(sentence, encoding="utf-8")
    assert gate.main() == 1
    assert "page.html: 'QPPV' outside the appointed-only boundary framing" in capsys.readouterr().out
