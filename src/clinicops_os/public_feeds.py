"""Shared logic for the Atom feed and the regulatory-dates calendar.

Both outputs are static files generated from the claims registry. Nothing here
fetches anything, stores personal data or decides what is true: a claim is used
only if it already passes the registry's own publication gate for the
``website`` use, and every entry or event carries the registry id.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from .claim_registry import CLAIM_ID_RE, RegistryClaim
from .site_quality import parse_metadata

BASE_URL = "https://clinicops.dk/"
FEED_URL = f"{BASE_URL}feed.xml"
ICS_URL = f"{BASE_URL}regulatory-dates.ics"
CORRECTIONS_PAGE = "research.html"
CORRECTIONS_ANCHOR = "cite-and-correct"
PUBLIC_USE = "website"
# Hosts that are never published as a "source" link: the hosting platform and
# the (non-public) repository. Feed and calendar URLs live on clinicops.dk only.
EXCLUDED_SOURCE_HOSTS = ("github.com", "github.io", "githubusercontent.com")
EXCLUDED_PAGES = {"404.html", "clinical-operations.html"}

CLAIM_IDS_COMMENT_RE = re.compile(r"<!--\s*claim-ids:\s*(.*?)-->", re.DOTALL)
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EVENT_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EVENT_KINDS = ("date", "deadline", "milestone", "recommendation", "planning_rule")


# ---------------------------------------------------------------- registry


def load_rows(path: str | Path) -> list[dict[str, object]]:
    """Raw registry rows. Optional fields (last_verified, ics_events, fact_key,
    value) are read from the raw JSON so this module does not depend on the
    RegistryClaim dataclass learning about them."""
    rows: list[dict[str, object]] = []
    for number, line in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise TypeError(f"line {number} must contain a JSON object")
        rows.append(row)
    return rows


def parse_iso_date(raw: object, label: str) -> date:
    if not isinstance(raw, str) or not ISO_DATE_RE.match(raw):
        raise ValueError(f"{label}: expected YYYY-MM-DD, got {raw!r}")
    return date.fromisoformat(raw)


def public_source_urls(sources: tuple[str, ...]) -> list[str]:
    """http(s) sources only; repo paths and hosting-platform URLs are dropped."""
    urls: list[str] = []
    for source in sources:
        parsed = urlparse(source)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            continue
        host = parsed.hostname.lower()
        if any(host == bad or host.endswith("." + bad) for bad in EXCLUDED_SOURCE_HOSTS):
            continue
        if source not in urls:
            urls.append(source)
    return urls


def page_index(docs_root: Path) -> dict[str, list[str]]:
    """claim id -> canonical URLs of indexable pages that declare it in a
    ``<!-- claim-ids: ... -->`` comment (the existing governance mechanism)."""
    index: dict[str, set[str]] = {}
    for page in sorted(docs_root.rglob("*.html")):
        relative = page.relative_to(docs_root).as_posix()
        if relative in EXCLUDED_PAGES:
            continue
        text = page.read_text(encoding="utf-8")
        parsed = parse_metadata(text)
        robots = parsed.meta.get("robots", "").lower()
        if "noindex" in {token.strip() for token in robots.split(",")}:
            continue
        canonical = parsed.canonical
        if not canonical or not canonical.startswith(BASE_URL):
            continue
        for comment in CLAIM_IDS_COMMENT_RE.findall(text):
            for claim_id in re.findall(r"CO-CLM-\d{4}", comment):
                index.setdefault(claim_id, set()).add(canonical)
    return {key: sorted(value) for key, value in index.items()}


@dataclass(frozen=True)
class PublishedClaim:
    claim: RegistryClaim
    row: dict[str, object]
    last_verified: date
    pages: tuple[str, ...]
    source_urls: tuple[str, ...]


def eligible_claims(
    rows: list[dict[str, object]],
    pages: dict[str, list[str]],
    as_of: date,
) -> tuple[list[PublishedClaim], list[tuple[str, str]]]:
    """Claims allowed into a public feed or calendar, plus (id, reason) for the
    ones left out. Fail closed: a claim needs to pass the registry gate for the
    ``website`` use (verified or qualified, website allowed, not superseded,
    review not expired), declare a ``last_verified`` date, and be carried by at
    least one indexable page."""
    included: list[PublishedClaim] = []
    skipped: list[tuple[str, str]] = []
    for row in rows:
        claim = RegistryClaim.from_dict(row)
        reasons = claim.gate(PUBLIC_USE, as_of)
        raw_verified = row.get("last_verified")
        if not raw_verified:
            reasons.append("no last_verified date in the registry")
        claim_pages = pages.get(claim.claim_id, [])
        if not claim_pages:
            reasons.append("no indexable page declares this claim id")
        if reasons:
            skipped.append((claim.claim_id, "; ".join(reasons)))
            continue
        included.append(
            PublishedClaim(
                claim=claim,
                row=row,
                last_verified=parse_iso_date(
                    raw_verified, f"{claim.claim_id} last_verified"
                ),
                pages=tuple(claim_pages),
                source_urls=tuple(public_source_urls(claim.sources)),
            )
        )
    return included, skipped


# ------------------------------------------------------------- corrections


@dataclass(frozen=True)
class Correction:
    day: date
    text: str
    claim_ids: tuple[str, ...]
    ordinal: int  # 1-based position among entries of the same day
    # A correction to ClinicOps' own self-description (staffing, wording) that no registry
    # claim backs. It stays on the page but is not published in the feed. It must carry no ids.
    editorial: bool = False


_LI_RE = re.compile(
    r"<li(?P<attrs>[^>]*)>\s*<strong>(?P<date>[^<]*?)\.?</strong>\s*(?P<text>.*?)</li>",
    re.DOTALL,
)
# The ids are written as bare numbers ("0018,0019"), not as full registry ids: the page claim gate
# treats every full id in a page as a statement the page makes, and a correction entry points at
# claims that may since have been superseded or rejected.
_CLAIM_ATTR_RE = re.compile(r'data-feed-claims="([^"]*)"')
_EDITORIAL_ATTR_RE = re.compile(r'data-feed="editorial"')
_TAG_RE = re.compile(r"<[^>]+>")


def _full_claim_id(part: str) -> str:
    return f"CO-CLM-{part.zfill(4)}" if part.isdigit() else part


def parse_corrections(research_html: str) -> list[Correction]:
    """The public corrections log is the list under "Corrections so far" in
    docs/research.html. Each <li> names its registry ids in data-feed-claims (numbers only,
    "0018,0019") or is marked data-feed="editorial" and carries none."""
    start = research_html.find("Corrections so far")
    if start < 0:
        raise ValueError("research.html has no 'Corrections so far' heading")
    block_match = re.search(r"<ul>(.*?)</ul>", research_html[start:], re.DOTALL)
    if not block_match:
        raise ValueError("research.html corrections log has no list")
    corrections: list[Correction] = []
    seen_per_day: dict[date, int] = {}
    for match in _LI_RE.finditer(block_match.group(1)):
        label = match.group("date").strip().rstrip(".")
        try:
            day = _parse_long_date(label)
        except ValueError as exc:
            raise ValueError(f"corrections log: unparseable date {label!r}") from exc
        attr = _CLAIM_ATTR_RE.search(match.group("attrs"))
        ids = tuple(
            _full_claim_id(part.strip())
            for part in (attr.group(1) if attr else "").split(",")
            if part.strip()
        )
        editorial = bool(_EDITORIAL_ATTR_RE.search(match.group("attrs")))
        text = " ".join(html.unescape(_TAG_RE.sub("", match.group("text"))).split())
        seen_per_day[day] = seen_per_day.get(day, 0) + 1
        corrections.append(Correction(day, text, ids, seen_per_day[day], editorial))
    if not corrections:
        raise ValueError("corrections log is empty")
    return corrections


_MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def _parse_long_date(label: str) -> date:
    parts = label.split()
    if len(parts) != 3 or parts[1] not in _MONTHS:
        raise ValueError(label)
    return date(int(parts[2]), _MONTHS.index(parts[1]) + 1, int(parts[0]))


def correction_sources(
    correction: Correction, by_id: dict[str, RegistryClaim]
) -> list[str]:
    urls: list[str] = []
    for claim_id in correction.claim_ids:
        for url in public_source_urls(by_id[claim_id].sources):
            if url not in urls:
                urls.append(url)
    return urls


def check_correction_ids(
    corrections: list[Correction], by_id: dict[str, RegistryClaim]
) -> None:
    for item in corrections:
        if item.editorial:
            if item.claim_ids:
                raise ValueError(
                    f"corrections log entry of {item.day.isoformat()} is editorial "
                    "and must not carry data-feed-claims"
                )
            continue
        if not item.claim_ids:
            raise ValueError(
                f"corrections log entry of {item.day.isoformat()} has no data-feed-claims "
                '(mark it data-feed="editorial" if no registry claim backs it)'
            )
        for claim_id in item.claim_ids:
            if not CLAIM_ID_RE.fullmatch(claim_id) or claim_id not in by_id:
                raise ValueError(
                    f"corrections log entry of {item.day.isoformat()} cites "
                    f"unknown registry id {claim_id!r}"
                )


# --------------------------------------------------------------- ICS events


@dataclass(frozen=True)
class IcsEvent:
    claim_id: str
    key: str
    day: date
    summary: str
    kind: str
    sequence: int
    note: str
    last_verified: date
    status: str
    pages: tuple[str, ...]
    source_urls: tuple[str, ...]

    @property
    def uid(self) -> str:
        return f"reg-{self.claim_id.lower()}-{self.key}@clinicops.dk"


def events_for(published: PublishedClaim) -> list[IcsEvent]:
    """Dated events a claim contributes to the calendar.

    Two optional registry shapes are read; neither is required:
    * ``ics_events``: list of {key, date, summary, kind?, sequence?, note?}
    * ``fact_key`` + ``value`` where ``value`` is an ISO date (YYYY-MM-DD);
      ``ics_summary``, ``ics_note`` and ``kind`` are optional companions.
    Month-only or free-text values are not dates and are ignored."""
    row = published.row
    claim_id = published.claim.claim_id
    events: list[IcsEvent] = []

    def build(
        key: str,
        day: date,
        summary: str,
        kind: str,
        sequence: int,
        note: str,
    ) -> IcsEvent:
        if not EVENT_KEY_RE.match(key):
            raise ValueError(f"{claim_id}: invalid ics event key {key!r}")
        if kind not in EVENT_KINDS:
            raise ValueError(f"{claim_id}: invalid ics event kind {kind!r}")
        if not summary.strip():
            raise ValueError(f"{claim_id}: ics event {key!r} has no summary")
        return IcsEvent(
            claim_id=claim_id,
            key=key,
            day=day,
            summary=summary.strip(),
            kind=kind,
            sequence=sequence,
            note=note.strip(),
            last_verified=published.last_verified,
            status=published.claim.status.value,
            pages=published.pages,
            source_urls=published.source_urls,
        )

    declared = row.get("ics_events")
    if declared is not None:
        if not isinstance(declared, list):
            raise ValueError(f"{claim_id}: ics_events must be a list")
        for position, item in enumerate(declared, start=1):
            if not isinstance(item, dict):
                raise TypeError(f"{claim_id}: ics_events[{position}] must be an object")
            sequence = item.get("sequence", 0)
            if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
                raise ValueError(f"{claim_id}: ics_events[{position}] sequence must be >= 0")
            events.append(
                build(
                    str(item.get("key", "")),
                    parse_iso_date(item.get("date"), f"{claim_id} ics_events[{position}].date"),
                    str(item.get("summary", "")),
                    str(item.get("kind", "date")),
                    sequence,
                    str(item.get("note", "")),
                )
            )

    value = row.get("value")
    # An explicitly empty ics_events list means "this claim states the same fact as another claim
    # that carries the calendar event": the fact_key/value pair stays for reconciliation but the
    # calendar does not get a second, identical event.
    suppressed = declared == []
    if not suppressed and row.get("fact_key") and isinstance(value, str) and ISO_DATE_RE.match(value):
        events.append(
            build(
                "value",
                parse_iso_date(value, f"{claim_id} value"),
                str(row.get("ics_summary") or row["fact_key"]),
                str(row.get("kind", "date")) if row.get("kind") in EVENT_KINDS else "date",
                0,
                str(row.get("ics_note", "")),
            )
        )

    keys = [event.key for event in events]
    if len(keys) != len(set(keys)):
        raise ValueError(f"{claim_id}: duplicate ics event keys")
    return events


# --------------------------------------------------------------- Atom feed

CLAIMS_SCHEME = f"{BASE_URL}claims"
FEED_TITLE = "ClinicOps: verified regulatory changes and corrections"
FEED_SUBTITLE = (
    "Claims from the ClinicOps claims registry that have been read at source and "
    "carry a registry id, plus the dated corrections log. Not legal advice."
)


@dataclass(frozen=True)
class FeedEntry:
    entry_id: str
    title: str
    updated: date
    summary: str
    content_html: str
    page_urls: tuple[str, ...]
    source_urls: tuple[str, ...]
    claim_ids: tuple[str, ...]
    kind: str  # "claim" or "correction"


def _first_sentence(text: str) -> str:
    """First sentence of a claim, where a sentence ends at '. ' followed by a capital."""
    text = " ".join(text.split())
    match = re.search(r"(?<=[a-z0-9\)\"”])\.\s+(?=[A-Z])", text)
    return text[: match.start()] if match else text.rstrip(".")


def _shorten(text: str, limit: int = 110) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:.")
    return f"{cut}…"


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def claim_entry(published: PublishedClaim) -> FeedEntry:
    claim = published.claim
    parts = [f"<p>{_esc(claim.text)}</p>"]
    if claim.limitations:
        items = "".join(f"<li>{_esc(item)}</li>" for item in claim.limitations)
        parts.append(f"<p><strong>Not established or limited:</strong></p><ul>{items}</ul>")
    if published.source_urls:
        links = "".join(
            f'<li><a href="{_esc(url)}">{_esc(url)}</a></li>' for url in published.source_urls
        )
        parts.append(f"<p><strong>Source:</strong></p><ul>{links}</ul>")
    parts.append(
        f"<p>Registry id {claim.claim_id}. Status: {claim.status.value}; "
        f"evidence class: {claim.evidence_class.value}. "
        f"Last read at source: {published.last_verified.isoformat()}. "
        "Check the source for your own devices or trials.</p>"
    )
    return FeedEntry(
        entry_id=f"tag:clinicops.dk,2026:claim/{claim.claim_id}",
        title=_shorten(_first_sentence(claim.text), 150),
        updated=published.last_verified,
        summary=claim.text,
        content_html="".join(parts),
        page_urls=published.pages,
        source_urls=published.source_urls,
        claim_ids=(claim.claim_id,),
        kind="claim",
    )


def correction_entry(item: Correction, by_id: dict[str, RegistryClaim]) -> FeedEntry:
    sources = correction_sources(item, by_id)
    parts = [f"<p>{_esc(item.text)}</p>"]
    if sources:
        links = "".join(f'<li><a href="{_esc(url)}">{_esc(url)}</a></li>' for url in sources)
        parts.append(f"<p><strong>Source:</strong></p><ul>{links}</ul>")
    parts.append(
        f"<p>Registry ids: {', '.join(item.claim_ids)}. This entry is from the dated "
        "corrections log on the Research page.</p>"
    )
    return FeedEntry(
        entry_id=(
            f"tag:clinicops.dk,2026:correction/{item.day.isoformat()}-{item.ordinal}"
        ),
        title=(
            f"Correction, {item.day.day} {_MONTHS[item.day.month - 1]} {item.day.year}: "
            f"{_shorten(_first_sentence(item.text), 90)}"
        ),
        updated=item.day,
        summary=item.text,
        content_html="".join(parts),
        page_urls=(f"{BASE_URL}research#{CORRECTIONS_ANCHOR}",),
        source_urls=tuple(sources),
        claim_ids=item.claim_ids,
        kind="correction",
    )


def build_entries(
    published: list[PublishedClaim],
    corrections: list[Correction],
    by_id: dict[str, RegistryClaim],
) -> list[FeedEntry]:
    entries = [claim_entry(item) for item in published]
    entries += [correction_entry(item, by_id) for item in corrections if not item.editorial]
    ids = [entry.entry_id for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate feed entry ids")
    return sorted(entries, key=lambda e: (-e.updated.toordinal(), e.entry_id))


def _rfc3339(day: date) -> str:
    return f"{day.isoformat()}T00:00:00Z"


def render_atom(entries: list[FeedEntry]) -> str:
    if not entries:
        raise ValueError("feed has no entries")
    updated = max(entry.updated for entry in entries)
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en">',
        f"  <id>{FEED_URL}</id>",
        f"  <title>{_esc(FEED_TITLE)}</title>",
        f"  <subtitle>{_esc(FEED_SUBTITLE)}</subtitle>",
        f"  <updated>{_rfc3339(updated)}</updated>",
        f'  <link rel="self" type="application/atom+xml" href="{FEED_URL}"/>',
        f'  <link rel="alternate" type="text/html" href="{BASE_URL}research"/>',
        "  <author><name>ClinicOps</name></author>",
    ]
    for entry in entries:
        lines.append("  <entry>")
        lines.append(f"    <id>{_esc(entry.entry_id)}</id>")
        lines.append(f"    <title>{_esc(entry.title)}</title>")
        lines.append(f"    <updated>{_rfc3339(entry.updated)}</updated>")
        for position, url in enumerate(entry.page_urls):
            rel = "alternate" if position == 0 else "related"
            lines.append(f'    <link rel="{rel}" type="text/html" href="{_esc(url)}"/>')
        for url in entry.source_urls:
            lines.append(f'    <link rel="related" title="Source" href="{_esc(url)}"/>')
        for claim_id in entry.claim_ids:
            lines.append(
                f'    <category scheme="{CLAIMS_SCHEME}" term="{claim_id}" '
                'label="Claims-registry id"/>'
            )
        lines.append(f'    <category term="{entry.kind}"/>')
        lines.append(f'    <summary type="text">{_esc(entry.summary)}</summary>')
        lines.append(f'    <content type="html">{_esc(entry.content_html)}</content>')
        lines.append("  </entry>")
    lines.append("</feed>")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------ ICS calendar

CAL_NAME = "ClinicOps regulatory dates"
CAL_DESC = (
    "Dates from the ClinicOps claims registry that have been read at source. "
    "Dates are shown as stated in the source, with no weekend roll-forward. "
    "Not legal advice: check the instrument for your own devices or trials."
)
PRODID = "-//ClinicOps//Regulatory dates//EN"
ALARM_TRIGGER = "-P14D"
_KIND_NOTE = {
    "recommendation": (
        "This is a recommended date from a non-binding document, not a legal deadline."
    ),
    "planning_rule": "This is a ClinicOps planning rule, not a date set by law.",
}


def ics_escape(text: str) -> str:
    """RFC 5545 TEXT escaping (section 3.3.11)."""
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )


def fold_line(line: str) -> list[str]:
    """RFC 5545 section 3.1: fold at 75 octets, never inside a UTF-8 character.
    Continuation lines start with one space, which counts toward their 75."""
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return [line]
    out: list[str] = []
    current = b""
    limit = 75
    for char in line:
        encoded = char.encode("utf-8")
        if len(current) + len(encoded) > limit:
            out.append(current.decode("utf-8"))
            current = b""
            limit = 74
        current += encoded
    out.append(current.decode("utf-8"))
    return [out[0], *(" " + part for part in out[1:])]


def _ics_date(day: date) -> str:
    return day.strftime("%Y%m%d")


def _long_date(day: date) -> str:
    return f"{day.day} {_MONTHS[day.month - 1]} {day.year}"


def event_description(event: IcsEvent) -> str:
    lines = [event.summary]
    if event.note:
        lines.append(event.note)
    if event.kind in _KIND_NOTE:
        lines.append(_KIND_NOTE[event.kind])
    if event.day.weekday() >= 5:
        weekday = event.day.strftime("%A")
        lines.append(
            f"{_long_date(event.day)} is a {weekday}. No weekend roll-forward is applied: "
            "the date is shown as stated in the source."
        )
    lines.append(
        f"Rules as of {_long_date(event.last_verified)}, the date ClinicOps last read the source."
    )
    for url in event.source_urls:
        lines.append(f"Source: {url}")
    for url in event.pages:
        lines.append(f"Page: {url}")
    lines.append(f"ClinicOps registry id {event.claim_id} (status: {event.status}).")
    lines.append("Verify against the instrument for your own devices or trials. Not legal advice.")
    return "\n".join(lines)


def event_lines(event: IcsEvent) -> list[str]:
    stamp = f"{_ics_date(event.last_verified)}T000000Z"
    url = event.pages[0] if event.pages else event.source_urls[0]
    summary = event.summary
    return [
        "BEGIN:VEVENT",
        f"UID:{event.uid}",
        f"DTSTAMP:{stamp}",
        f"LAST-MODIFIED:{stamp}",
        f"SEQUENCE:{event.sequence}",
        f"DTSTART;VALUE=DATE:{_ics_date(event.day)}",
        f"DTEND;VALUE=DATE:{_ics_date(date.fromordinal(event.day.toordinal() + 1))}",
        f"SUMMARY:{ics_escape(summary)}",
        f"DESCRIPTION:{ics_escape(event_description(event))}",
        f"URL:{url}",
        "STATUS:CONFIRMED",
        "TRANSP:TRANSPARENT",
        "CLASS:PUBLIC",
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        f"DESCRIPTION:{ics_escape('In 14 days: ' + summary)}",
        f"TRIGGER:{ALARM_TRIGGER}",
        "END:VALARM",
        "END:VEVENT",
    ]


def build_events(published: list[PublishedClaim]) -> list[IcsEvent]:
    events = [event for item in published for event in events_for(item)]
    uids = [event.uid for event in events]
    if len(uids) != len(set(uids)):
        raise ValueError("duplicate ics UIDs")
    return sorted(events, key=lambda e: (e.day, e.uid))


def render_ics(events: list[IcsEvent]) -> bytes:
    description = CAL_DESC if events else f"{CAL_DESC} No dates are listed yet."
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PRODID}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{ics_escape(CAL_NAME)}",
        f"X-WR-CALDESC:{ics_escape(description)}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
    ]
    for event in events:
        lines.extend(event_lines(event))
    lines.append("END:VCALENDAR")
    folded = [piece for line in lines for piece in fold_line(line)]
    return ("\r\n".join(folded) + "\r\n").encode("utf-8")
