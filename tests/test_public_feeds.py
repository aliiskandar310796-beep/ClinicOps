from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from xml.etree import ElementTree

import pytest

from clinicops_os.claim_registry import CLAIM_ID_RE, RegistryClaim
from clinicops_os.public_feeds import (
    PublishedClaim,
    build_entries,
    build_events,
    check_correction_ids,
    eligible_claims,
    events_for,
    fold_line,
    load_rows,
    page_index,
    parse_corrections,
    render_atom,
    render_ics,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CLAIMS = ROOT / "research" / "claims.jsonl"
ATOM = "{http://www.w3.org/2005/Atom}"
AS_OF = date(2026, 11, 16)


# ------------------------------------------------------------------ fixtures


def _row(claim_id: str = "CO-CLM-0900", **overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "id": claim_id,
        "claim": "A test claim, with a comma; and a semicolon.",
        "evidence_class": "primary",
        "status": "qualified",
        "sources": [
            "https://eur-lex.europa.eu/eli/dec/2025/2371/oj",
            "https://github.com/some/repo/actions/runs/1",
            "research/corrections/local-note.md",
        ],
        "limitations": ["Only the stated scope is covered."],
        "allowed_uses": ["internal", "website"],
        "review_after": "2027-01-31",
        "supersedes": [],
        "superseded_by": None,
        "last_verified": "2026-11-16",
    }
    row.update(overrides)
    return row


def _docs(tmp_path: Path, claim_ids: str = "CO-CLM-0900") -> Path:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "page.html").write_text(
        '<!doctype html><html><head><link rel="canonical" href="https://clinicops.dk/page">'
        f"</head><body><!-- claim-ids: {claim_ids} --></body></html>",
        encoding="utf-8",
    )
    return docs


def _published(tmp_path: Path, rows: list[dict[str, object]], as_of: date = AS_OF):
    published, skipped = eligible_claims(rows, page_index(_docs(tmp_path)), as_of)
    return published, skipped


# ------------------------------------------------------------ strict ICS check

_TEXT_VALUE = re.compile(r"(?:[^\\;,]|\\[\\;,nN])*")
_TEXT_PROPS = {"SUMMARY", "DESCRIPTION", "X-WR-CALNAME", "X-WR-CALDESC"}


def unfold(data: bytes) -> list[str]:
    text = data.decode("utf-8")
    assert text.endswith("\r\n")
    assert "\n" not in text.replace("\r\n", "")
    assert "\r" not in text.replace("\r\n", "")
    physical = text[:-2].split("\r\n")
    for line in physical:
        assert len(line.encode("utf-8")) <= 75, f"line over 75 octets: {line!r}"
    logical: list[str] = []
    for line in physical:
        if line.startswith(" "):
            assert logical, "continuation line with nothing to continue"
            logical[-1] += line[1:]
        else:
            logical.append(line)
    return logical


def validate_ics(data: bytes) -> list[dict[str, list[str]]]:
    """Strict structural validation of what this repo emits (RFC 5545 subset).
    Returns the list of VEVENTs as {property name: [values]}."""
    lines = unfold(data)
    assert lines[0] == "BEGIN:VCALENDAR"
    assert lines[-1] == "END:VCALENDAR"
    stack: list[str] = []
    calendar: dict[str, list[str]] = {}
    events: list[dict[str, list[str]]] = []
    current: dict[str, list[str]] | None = None
    alarm: dict[str, list[str]] | None = None
    for line in lines:
        assert ":" in line, f"content line without colon: {line!r}"
        name_part, value = line.split(":", 1)
        name = name_part.split(";", 1)[0].upper()
        assert re.fullmatch(r"[A-Z0-9-]+", name), f"bad property name {name!r}"
        if name == "BEGIN":
            stack.append(value)
            if value == "VEVENT":
                assert len(stack) == 2
                current = {}
            elif value == "VALARM":
                assert stack[-2] == "VEVENT"
                alarm = {}
            else:
                assert value == "VCALENDAR" and len(stack) == 1
            continue
        if name == "END":
            assert stack and stack.pop() == value
            if value == "VALARM":
                assert alarm is not None and current is not None
                assert alarm["ACTION"] == ["DISPLAY"]
                assert alarm["TRIGGER"] == ["-P14D"]
                assert "DESCRIPTION" in alarm
                current.setdefault("_ALARMS", []).append("1")
                alarm = None
            elif value == "VEVENT":
                assert current is not None
                events.append(current)
                current = None
            continue
        if name in _TEXT_PROPS:
            assert _TEXT_VALUE.fullmatch(value), f"bad TEXT escaping in {name}: {value!r}"
        target = alarm if alarm is not None else current if current is not None else calendar
        target.setdefault(name, []).append(value)
        if alarm is None and current is not None:
            current.setdefault("_PARAMS_" + name, []).append(name_part)
    assert not stack
    assert calendar["VERSION"] == ["2.0"]
    assert calendar["PRODID"]
    assert calendar["X-WR-CALNAME"]
    assert calendar["METHOD"] == ["PUBLISH"]
    uids: set[str] = set()
    for event in events:
        for required in ("UID", "DTSTAMP", "DTSTART", "SUMMARY", "DESCRIPTION", "URL", "SEQUENCE"):
            assert len(event[required]) == 1, f"{required} must appear exactly once"
        uid = event["UID"][0]
        assert re.fullmatch(r"reg-co-clm-\d{4}-[a-z0-9-]+@clinicops\.dk", uid), uid
        assert uid not in uids
        uids.add(uid)
        assert re.fullmatch(r"\d{8}T\d{6}Z", event["DTSTAMP"][0])
        assert event["_PARAMS_DTSTART"] == ["DTSTART;VALUE=DATE"]
        assert re.fullmatch(r"\d{8}", event["DTSTART"][0])
        assert event["SEQUENCE"][0].isdigit()
        assert event["URL"][0].startswith("https://clinicops.dk/") or event["URL"][0].startswith("https://")
        assert "Rules as of" in event["DESCRIPTION"][0]
        assert "ClinicOps registry id CO-CLM-" in event["DESCRIPTION"][0]
        assert event["_ALARMS"] == ["1"]
    return events


def _unescape(value: str) -> str:
    return re.sub(r"\\(.)", lambda m: "\n" if m.group(1) in "nN" else m.group(1), value)


def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------ eligibility


def test_eligible_claims_fail_closed(tmp_path: Path) -> None:
    rows = [
        _row("CO-CLM-0900"),
        _row("CO-CLM-0901", last_verified=None),
        _row("CO-CLM-0902", allowed_uses=["internal"]),
        _row("CO-CLM-0903", status="rejected"),
        _row("CO-CLM-0904", superseded_by="CO-CLM-0900"),
        _row("CO-CLM-0905", review_after="2026-11-01"),
        _row("CO-CLM-0906", status="unchecked"),
    ]
    published, skipped = _published(tmp_path, rows)
    assert [item.claim.claim_id for item in published] == ["CO-CLM-0900"]
    reasons = dict(skipped)
    assert "no last_verified" in reasons["CO-CLM-0901"]
    assert "not allowed" in reasons["CO-CLM-0902"]
    assert "rejected" in reasons["CO-CLM-0903"]
    assert "superseded" in reasons["CO-CLM-0904"]
    assert "review expired" in reasons["CO-CLM-0905"]
    assert "unchecked" in reasons["CO-CLM-0906"]
    # none of them has a page either except 0900 (the fixture page declares 0900 only)
    assert "no indexable page" in reasons["CO-CLM-0901"]


def test_claim_without_a_declaring_page_is_left_out(tmp_path: Path) -> None:
    docs = _docs(tmp_path, claim_ids="CO-CLM-0999")
    _, skipped = eligible_claims([_row()], page_index(docs), AS_OF)
    assert "no indexable page" in dict(skipped)["CO-CLM-0900"]


def test_noindex_pages_do_not_carry_a_claim(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    (docs / "page.html").write_text(
        '<html><head><link rel="canonical" href="https://clinicops.dk/page">'
        '<meta name="robots" content="noindex,follow"></head>'
        "<body><!-- claim-ids: CO-CLM-0900 --></body></html>",
        encoding="utf-8",
    )
    assert page_index(docs) == {}


def test_review_expiry_depends_only_on_as_of(tmp_path: Path) -> None:
    rows = [_row(review_after="2026-12-01")]
    docs = page_index(_docs(tmp_path))
    assert eligible_claims(rows, docs, date(2026, 12, 1))[0]
    assert not eligible_claims(rows, docs, date(2026, 12, 2))[0]


# ------------------------------------------------------------------- feed


def test_claim_entry_fields(tmp_path: Path) -> None:
    published, _ = _published(tmp_path, [_row()])
    entries = build_entries(published, [], {})
    feed = ElementTree.fromstring(render_atom(entries))
    entry = feed.find(f"{ATOM}entry")
    assert entry is not None
    assert entry.findtext(f"{ATOM}id") == "tag:clinicops.dk,2026:claim/CO-CLM-0900"
    assert entry.findtext(f"{ATOM}updated") == "2026-11-16T00:00:00Z"
    hrefs = [link.get("href") for link in entry.findall(f"{ATOM}link")]
    assert "https://clinicops.dk/page" in hrefs
    assert "https://eur-lex.europa.eu/eli/dec/2025/2371/oj" in hrefs
    assert not any("github" in (href or "") for href in hrefs)
    assert not any("local-note" in (href or "") for href in hrefs)
    terms = [c.get("term") for c in entry.findall(f"{ATOM}category")]
    assert "CO-CLM-0900" in terms
    content = entry.findtext(f"{ATOM}content") or ""
    assert "Only the stated scope is covered." in content
    assert "Registry id CO-CLM-0900" in content
    assert "Last read at source: 2026-11-16" in content


def test_feed_updated_comes_from_last_verified_not_the_clock(tmp_path: Path) -> None:
    published, _ = _published(tmp_path, [_row(last_verified="2026-10-02")])
    feed = ElementTree.fromstring(render_atom(build_entries(published, [], {})))
    assert feed.findtext(f"{ATOM}updated") == "2026-10-02T00:00:00Z"


def test_feed_is_deterministic_and_order_independent(tmp_path: Path) -> None:
    rows = [_row("CO-CLM-0900"), _row("CO-CLM-0901", last_verified="2026-11-10")]
    docs = _docs(tmp_path, claim_ids="CO-CLM-0900,CO-CLM-0901")
    first, _ = eligible_claims(rows, page_index(docs), AS_OF)
    second, _ = eligible_claims(list(reversed(rows)), page_index(docs), AS_OF)
    assert render_atom(build_entries(first, [], {})) == render_atom(build_entries(second, [], {}))


def test_real_corrections_log_parses_and_resolves() -> None:
    corrections = parse_corrections((DOCS / "research.html").read_text(encoding="utf-8"))
    assert len(corrections) >= 4
    assert corrections == sorted(corrections, key=lambda c: c.day)
    by_id = {c.claim_id: c for c in map(RegistryClaim.from_dict, load_rows(CLAIMS))}
    check_correction_ids(corrections, by_id)
    for item in corrections:
        assert item.text
        assert item.claim_ids or item.editorial, item.text
        assert not (item.claim_ids and item.editorial), item.text


def test_corrections_without_claim_ids_are_rejected() -> None:
    page = "<h3>Corrections so far</h3><ul><li><strong>8 September 2026.</strong> Text.</li></ul>"
    corrections = parse_corrections(page)
    with pytest.raises(ValueError, match="no data-feed-claims"):
        check_correction_ids(corrections, {})


def test_editorial_corrections_are_explicit_carry_no_ids_and_stay_out_of_the_feed() -> None:
    page = (
        '<h3>Corrections so far</h3><ul>'
        '<li data-feed-claims="0001"><strong>8 September 2026.</strong> Registered.</li>'
        '<li data-feed="editorial"><strong>9 September 2026.</strong> Self-description fixed.</li></ul>'
    )
    corrections = parse_corrections(page)
    assert [c.editorial for c in corrections] == [False, True]
    by_id = {c.claim_id: c for c in [RegistryClaim.from_dict(_row("CO-CLM-0001"))]}
    check_correction_ids(corrections, by_id)
    assert len(build_entries([], corrections, by_id)) == 1
    both = (
        '<h3>Corrections so far</h3><ul>'
        '<li data-feed="editorial" data-feed-claims="0001"><strong>9 September 2026.</strong> X.</li></ul>'
    )
    with pytest.raises(ValueError, match="must not carry"):
        check_correction_ids(parse_corrections(both), by_id)


def test_corrections_unknown_registry_id_is_rejected() -> None:
    page = (
        '<h3>Corrections so far</h3><ul><li data-feed-claims="9999">'
        "<strong>8 September 2026.</strong> Text.</li></ul>"
    )
    with pytest.raises(ValueError, match="unknown registry id"):
        check_correction_ids(parse_corrections(page), {})


def test_same_day_corrections_get_distinct_ids() -> None:
    page = (
        '<h3>Corrections so far</h3><ul>'
        '<li data-feed-claims="0001"><strong>8 September 2026.</strong> One.</li>'
        '<li data-feed-claims="0001"><strong>8 September 2026.</strong> Two.</li></ul>'
    )
    by_id = {c.claim_id: c for c in [RegistryClaim.from_dict(_row("CO-CLM-0001"))]}
    entries = build_entries([], parse_corrections(page), by_id)
    assert len({entry.entry_id for entry in entries}) == 2


def test_real_feed_is_current_valid_and_registry_linked() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "render_feed.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": ""},
    )
    assert result.returncode == 0, result.stdout + result.stderr

    data = (DOCS / "feed.xml").read_text(encoding="utf-8")
    assert "github.io" not in data
    feed = ElementTree.fromstring(data)
    assert feed.tag == f"{ATOM}feed"
    for required in ("id", "title", "updated"):
        assert feed.findtext(f"{ATOM}{required}")
    assert feed.find(f"{ATOM}author/{ATOM}name") is not None
    selfs = [
        link.get("href")
        for link in feed.findall(f"{ATOM}link")
        if link.get("rel") == "self"
    ]
    assert selfs == ["https://clinicops.dk/feed.xml"]

    registry = {row["id"]: row for row in load_rows(CLAIMS)}
    entries = feed.findall(f"{ATOM}entry")
    assert entries
    ids = [entry.findtext(f"{ATOM}id") for entry in entries]
    assert len(ids) == len(set(ids))
    for entry in entries:
        entry_id = entry.findtext(f"{ATOM}id") or ""
        assert entry_id.startswith("tag:clinicops.dk,")
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T00:00:00Z", entry.findtext(f"{ATOM}updated") or "")
        terms = [
            c.get("term")
            for c in entry.findall(f"{ATOM}category")
            if c.get("scheme") == "https://clinicops.dk/claims"
        ]
        assert terms, f"{entry_id} has no claims-registry id"
        for term in terms:
            assert CLAIM_ID_RE.fullmatch(term or "")
            assert term in registry
        if "/claim/" in entry_id:
            # claim entries only for verified or qualified, website-allowed claims
            row = registry[terms[0]]
            assert row["status"] in {"verified", "qualified"}
            assert "website" in row["allowed_uses"]
            assert row.get("last_verified")
        alternates = [
            link.get("href") for link in entry.findall(f"{ATOM}link") if link.get("rel") == "alternate"
        ]
        assert alternates and alternates[0].startswith("https://clinicops.dk/")


def test_feed_is_not_in_the_sitemap_and_has_no_html_page() -> None:
    assert "feed.xml" not in (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    assert not (DOCS / "feed.html").exists()


def test_feed_check_detects_a_stale_file(tmp_path: Path, monkeypatch, capsys) -> None:
    module = _load_script("render_feed")
    stale = tmp_path / "feed.xml"
    stale.write_text("stale", encoding="utf-8")
    monkeypatch.setattr(module, "FEED", stale)
    monkeypatch.setattr(sys, "argv", ["render_feed.py", "--check"])
    with pytest.raises(SystemExit) as exc:
        module.main()
    assert "stale" in str(exc.value)


# ------------------------------------------------------------ autodiscovery


def test_every_public_page_advertises_the_feed() -> None:
    excluded = {"404.html", "clinical-operations.html"}
    pages = [p for p in DOCS.rglob("*.html") if p.relative_to(DOCS).as_posix() not in excluded]
    assert pages
    link = (
        '<link rel="alternate" type="application/atom+xml" '
        'title="ClinicOps verified changes" href="https://clinicops.dk/feed.xml">'
    )
    for page in pages:
        text = page.read_text(encoding="utf-8")
        assert text.count(link) == 1, page
        assert text.index(link) < text.index("</head>")


@pytest.mark.parametrize("page", ["research.html", "eudamed-transition.html"])
def test_subscribe_line_is_visible_static_and_resolves(page: str) -> None:
    text = (DOCS / page).read_text(encoding="utf-8")
    assert (
        'Subscribe: <a href="subscribe">Atom feed</a> / '
        '<a href="regulatory-dates.ics">calendar (.ics)</a>'
    ) in text
    assert (DOCS / "feed.xml").is_file()
    assert (DOCS / "regulatory-dates.ics").is_file()


# -------------------------------------------------------------------- ICS


def test_real_calendar_is_current_and_strictly_valid() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "render_ics.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": ""},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    data = (DOCS / "regulatory-dates.ics").read_bytes()
    events = validate_ics(data)
    registry = {row["id"]: row for row in load_rows(CLAIMS)}
    assert b"github.io" not in data
    for event in events:
        claim_id = "CO-CLM-" + re.search(r"co-clm-(\d{4})", event["UID"][0]).group(1)
        assert claim_id in registry
        row = registry[claim_id]
        assert row["status"] in {"verified", "qualified"}
        assert "website" in row["allowed_uses"]
        assert row.get("last_verified")


def test_ics_check_detects_a_stale_file(tmp_path: Path, monkeypatch) -> None:
    module = _load_script("render_ics")
    stale = tmp_path / "regulatory-dates.ics"
    stale.write_bytes(b"stale")
    monkeypatch.setattr(module, "ICS", stale)
    monkeypatch.setattr(sys, "argv", ["render_ics.py", "--check"])
    with pytest.raises(SystemExit) as exc:
        module.main()
    assert "stale" in str(exc.value)


def _event_row(**overrides: object) -> dict[str, object]:
    base = {
        "ics_events": [
            {
                "key": "deadline",
                "date": "2026-11-28",
                "summary": "Legacy-device registration deadline, UDI/Device module",
                "kind": "deadline",
                "sequence": 2,
            }
        ]
    }
    base.update(overrides)
    return _row(**base)


def test_event_fields_and_description(tmp_path: Path) -> None:
    published, _ = _published(tmp_path, [_event_row()])
    events = build_events(published)
    assert [e.uid for e in events] == ["reg-co-clm-0900-deadline@clinicops.dk"]
    parsed = validate_ics(render_ics(events))
    assert len(parsed) == 1
    event = parsed[0]
    assert event["SEQUENCE"] == ["2"]
    assert event["DTSTART"] == ["20261128"]
    assert event["DTSTAMP"] == ["20261116T000000Z"]
    assert event["URL"] == ["https://clinicops.dk/page"]
    description = event["DESCRIPTION"][0]
    assert "Source: https://eur-lex.europa.eu/eli/dec/2025/2371/oj" in description
    assert "github" not in description
    assert "Rules as of 16 November 2026" in description
    assert "ClinicOps registry id CO-CLM-0900 (status: qualified)" in description
    assert "Verify against the instrument" in description


def test_weekend_dates_are_never_rolled_forward(tmp_path: Path) -> None:
    saturday, sunday = "2026-11-28", "2026-11-29"
    row = _row(
        ics_events=[
            {"key": "sat", "date": saturday, "summary": "Saturday date"},
            {"key": "sun", "date": sunday, "summary": "Sunday date"},
            {"key": "fri", "date": "2026-11-27", "summary": "Friday date"},
        ]
    )
    published, _ = _published(tmp_path, [row])
    parsed = {
        e["UID"][0].split("-")[-1].split("@")[0]: e for e in validate_ics(render_ics(build_events(published)))
    }
    assert parsed["sat"]["DTSTART"] == ["20261128"]
    assert parsed["sun"]["DTSTART"] == ["20261129"]
    assert parsed["fri"]["DTSTART"] == ["20261127"]
    assert "is a Saturday. No weekend roll-forward" in parsed["sat"]["DESCRIPTION"][0]
    assert "is a Sunday. No weekend roll-forward" in parsed["sun"]["DESCRIPTION"][0]
    assert "roll-forward" not in parsed["fri"]["DESCRIPTION"][0]


def test_value_based_date_events_and_kinds(tmp_path: Path) -> None:
    rows = [
        _row("CO-CLM-0900", fact_key="eudamed.legacy_deadline", value="2026-11-28",
             ics_summary="Legacy registration deadline"),
        _row("CO-CLM-0901", fact_key="eudamed.legacy_plan", value="2026-11-27", kind="planning_rule"),
        _row("CO-CLM-0902", fact_key="eudamed.production", value="2026-12"),  # month only: not a date
        _row("CO-CLM-0903", fact_key="x", value=None),
        _row("CO-CLM-0904", ics_events=[{"key": "rec", "date": "2027-03-27", "summary": "Upload",
                                          "kind": "recommendation"}]),
    ]
    docs = _docs(tmp_path, claim_ids="CO-CLM-0900,CO-CLM-0901,CO-CLM-0902,CO-CLM-0903,CO-CLM-0904")
    published, _ = eligible_claims(rows, page_index(docs), AS_OF)
    events = build_events(published)
    assert [e.claim_id for e in events] == ["CO-CLM-0901", "CO-CLM-0900", "CO-CLM-0904"]
    by_id = {e.claim_id: e for e in events}
    assert by_id["CO-CLM-0900"].summary == "Legacy registration deadline"
    assert by_id["CO-CLM-0901"].summary == "eudamed.legacy_plan"
    parsed = validate_ics(render_ics(events))
    texts = {e["UID"][0]: _unescape(e["DESCRIPTION"][0]) for e in parsed}
    assert "ClinicOps planning rule, not a date set by law" in texts["reg-co-clm-0901-value@clinicops.dk"]
    assert "non-binding document, not a legal deadline" in texts["reg-co-clm-0904-rec@clinicops.dk"]


@pytest.mark.parametrize(
    "events, message",
    [
        ([{"key": "Bad Key", "date": "2026-11-28", "summary": "x"}], "invalid ics event key"),
        ([{"key": "k", "date": "28 Nov 2026", "summary": "x"}], "expected YYYY-MM-DD"),
        ([{"key": "k", "date": "2026-11-28", "summary": " "}], "no summary"),
        ([{"key": "k", "date": "2026-11-28", "summary": "x", "kind": "magic"}], "invalid ics event kind"),
        ([{"key": "k", "date": "2026-11-28", "summary": "x", "sequence": -1}], "sequence"),
        (
            [
                {"key": "k", "date": "2026-11-28", "summary": "x"},
                {"key": "k", "date": "2026-11-29", "summary": "y"},
            ],
            "duplicate ics event keys",
        ),
        ("2026-11-28", "must be a list"),
    ],
)
def test_malformed_ics_events_fail_the_build(tmp_path: Path, events: object, message: str) -> None:
    published, _ = _published(tmp_path, [_row(ics_events=events)])
    with pytest.raises(ValueError, match=message):
        build_events(published)


def test_claims_that_fail_the_gate_never_reach_the_calendar(tmp_path: Path) -> None:
    template = {"ics_events": [{"key": "k", "date": "2026-11-28", "summary": "x"}]}
    rows = [
        _row("CO-CLM-0901", status="rejected", **template),
        _row("CO-CLM-0902", superseded_by="CO-CLM-0900", **template),
        _row("CO-CLM-0903", last_verified=None, **template),
        _row("CO-CLM-0904", allowed_uses=["internal"], **template),
        _row("CO-CLM-0905", review_after="2026-01-01", **template),
    ]
    docs = _docs(tmp_path, claim_ids=",".join(row["id"] for row in rows))
    published, skipped = eligible_claims(rows, page_index(docs), AS_OF)
    assert published == [] and len(skipped) == 5
    assert build_events(published) == []


def test_ics_is_deterministic_and_has_no_wall_clock(tmp_path: Path) -> None:
    published, _ = _published(tmp_path, [_event_row()])
    first = render_ics(build_events(published))
    second = render_ics(build_events(published))
    assert first == second
    assert first.count(b"DTSTAMP:20261116T000000Z") == first.count(b"DTSTAMP") == 1


def test_empty_calendar_still_parses_and_says_so() -> None:
    data = render_ics([])
    lines = unfold(data)
    assert lines[0] == "BEGIN:VCALENDAR" and lines[-1] == "END:VCALENDAR"
    assert any("No dates are listed yet" in line for line in lines)


def test_calendar_level_properties() -> None:
    lines = unfold(render_ics([]))
    assert "X-WR-CALNAME:ClinicOps regulatory dates" in lines
    assert "VERSION:2.0" in lines
    assert any(line.startswith("PRODID:-//ClinicOps//") for line in lines)
    assert "REFRESH-INTERVAL;VALUE=DURATION:PT12H" in lines


@pytest.mark.parametrize(
    "line",
    [
        "SUMMARY:" + "x" * 200,
        "DESCRIPTION:" + "Dato i København, år 2026 – æøå " * 12,
        "DESCRIPTION:" + "é" * 74,
        "DESCRIPTION:" + "é" * 75,
        "SHORT:abc",
    ],
)
def test_line_folding_is_octet_safe_and_reversible(line: str) -> None:
    folded = fold_line(line)
    for piece in folded:
        assert len(piece.encode("utf-8")) <= 75
    assert "".join([folded[0], *(piece[1:] for piece in folded[1:])]) == line
    assert all(piece.startswith(" ") for piece in folded[1:])


def test_text_escaping_round_trips_through_a_parser(tmp_path: Path) -> None:
    icalendar = pytest.importorskip("icalendar")
    row = _event_row(claim="x")
    row["ics_events"][0]["summary"] = "Comma, semicolon; backslash \\ and ø"
    published, _ = _published(tmp_path, [row])
    data = render_ics(build_events(published))
    validate_ics(data)
    calendar = icalendar.Calendar.from_ical(data)
    vevents = [c for c in calendar.walk() if c.name == "VEVENT"]
    assert len(vevents) == 1
    event = vevents[0]
    assert str(event["SUMMARY"]) == "Comma, semicolon; backslash \\ and ø"
    assert str(event["UID"]) == "reg-co-clm-0900-deadline@clinicops.dk"
    assert event["DTSTART"].dt == date(2026, 11, 28)
    assert "Source: https://eur-lex.europa.eu/eli/dec/2025/2371/oj" in str(event["DESCRIPTION"])
    alarms = [c for c in event.walk() if c.name == "VALARM"]
    assert len(alarms) == 1
    assert alarms[0]["TRIGGER"].dt.days == -14
    assert str(calendar["X-WR-CALNAME"]) == "ClinicOps regulatory dates"


def test_real_calendar_parses_with_icalendar_when_available() -> None:
    icalendar = pytest.importorskip("icalendar")
    calendar = icalendar.Calendar.from_ical((DOCS / "regulatory-dates.ics").read_bytes())
    assert str(calendar["X-WR-CALNAME"]) == "ClinicOps regulatory dates"


def test_every_event_and_entry_maps_to_a_registry_id(tmp_path: Path) -> None:
    rows = [_event_row(), _row("CO-CLM-0901")]
    docs = _docs(tmp_path, claim_ids="CO-CLM-0900,CO-CLM-0901")
    published, _ = eligible_claims(rows, page_index(docs), AS_OF)
    registry = {row["id"] for row in rows}
    assert {event.claim_id for event in build_events(published)} <= registry
    entries = build_entries(published, [], {})
    assert {claim_id for entry in entries for claim_id in entry.claim_ids} == registry
    for entry in entries:
        assert entry.claim_ids


def test_registry_rows_are_valid_json_with_known_optional_fields() -> None:
    for row in load_rows(CLAIMS):
        raw = row.get("last_verified")
        assert raw is None or re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw)
        events = row.get("ics_events")
        assert events is None or isinstance(events, list)
        json.dumps(row)


def test_real_calendar_lists_the_legacy_deadline_once_with_the_saturday_stated() -> None:
    ics = (DOCS / "regulatory-dates.ics").read_bytes().decode("utf-8").replace("\r\n ", "")
    assert ics.count("DTSTART;VALUE=DATE:20261128") == 1, "two claims share the fact; one calendar event"
    assert "28 November 2026 is a Saturday" in ics
    assert "No weekend roll-forward is applied" in ics
    assert "DTSTART;VALUE=DATE:20261127" not in ics and "DTSTART;VALUE=DATE:20261130" not in ics
    assert "SUMMARY:EUDAMED: Commission deadline to register legacy devices" in ics
    assert "DTSTART;VALUE=DATE:20270327" in ics and "27 March 2027 is a Saturday" in ics


def test_empty_ics_events_suppresses_the_duplicate_value_event() -> None:
    row = _row("CO-CLM-0001")
    row.update(fact_key="x.y", value="2026-11-28", ics_events=[])
    published = PublishedClaim(
        claim=RegistryClaim.from_dict(row),
        row=row,
        last_verified=date(2026, 11, 16),
        pages=("https://clinicops.dk/p",),
        source_urls=("https://example.com/s",),
    )
    assert events_for(published) == []
    del row["ics_events"]
    assert len(events_for(published)) == 1
