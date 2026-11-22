"""Generate the visible freshness stamps from the claim registry.

Three generated pieces, each wrapped in marker comments so the render step can
replace it in place and `--check` can detect drift:

- a "Rules as of" line under the page lead (every governed page and every tool),
- a "Last verified" block at the end of the page (claim-governed pages only), and
- an answer-first block above a tool (direct answer, dated source, boundary).

Nothing here invents a date: every date shown is a registry field that a person
set after reading the source. A claim that was carried forward says so.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .claim_registry import RegistryClaim
from .page_claims import declared_ids

MONTHS = (
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
)
METHOD_LABELS = {
    "read-primary": "Read at the source",
    "read-secondary": "Read at a guidance or secondary source",
    "observation": "ClinicOps observation (sample date shown)",
    "carried-forward": "Carried forward; not re-read for this release",
}
LINE_RE = re.compile(r"<!-- stamp:line:start -->.*?<!-- stamp:line:end -->", re.DOTALL)
BLOCK_RE = re.compile(r"\n?<!-- stamp:block:start -->.*?<!-- stamp:block:end -->\n?", re.DOTALL)
ANSWER_RE = re.compile(r"\n?<!-- answer-first:start -->.*?<!-- answer-first:end -->", re.DOTALL)
LEDE_RE = re.compile(r'<p class="lede">.*?</p>', re.DOTALL)
H1_END_RE = re.compile(r"</h1>")
HERO_RE = re.compile(r'<section class="hero"[^>]*>.*?</section>', re.DOTALL)
DIGITS_RE = re.compile(r"\d+(?:[/.,]\d+)*")


def long_date(value: date) -> str:
    return f"{value.day} {MONTHS[value.month - 1]} {value.year}"


@dataclass(frozen=True)
class StampConfig:
    tool_pages: dict[str, dict]
    full_block_exclude: dict[str, str]
    answer_first: dict[str, dict]

    @classmethod
    def load(cls, path: Path) -> StampConfig:
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            tool_pages=data["tool_pages"],
            full_block_exclude=data["full_block_exclude"],
            answer_first=data["answer_first"],
        )


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


def _prefix(rel: str) -> str:
    """Relative prefix from a docs page to the docs root."""
    depth = len(Path(rel).relative_to("docs").parts) - 1
    return "../" * depth


def _http_sources(claim: RegistryClaim) -> list[str]:
    return [source for source in claim.sources if source.startswith("http")]


def _live(claims: list[RegistryClaim]) -> list[RegistryClaim]:
    return [claim for claim in claims if not claim.superseded_by]


def page_claims(text: str, registry: dict[str, RegistryClaim]) -> list[RegistryClaim]:
    ids = sorted(declared_ids(text))
    return _live([registry[claim_id] for claim_id in ids if claim_id in registry])


def rules_as_of(claims: list[RegistryClaim]) -> date | None:
    """Oldest read date among the rule claims. ClinicOps observations (class D)
    carry their own sample dates and do not set the legal position date."""
    dates = [c.last_verified for c in claims if c.risk_class != "D" and c.last_verified]
    return min(dates) if dates else None


def next_review(claims: list[RegistryClaim]) -> date | None:
    dates = [claim.review_after for claim in claims if claim.review_after]
    return min(dates) if dates else None


def registry_digest(claims: list[RegistryClaim]) -> str:
    payload = [
        {
            "id": c.claim_id,
            "text": c.text,
            "sources": list(c.sources),
            "lv": c.last_verified.isoformat() if c.last_verified else None,
            "ra": c.review_after.isoformat() if c.review_after else None,
            "m": c.verified_method,
            "sd": c.source_date,
            "ne": list(c.not_established),
            "fk": c.fact_key,
            "v": c.value,
        }
        for c in claims
    ]
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:8]


# ---- the "Rules as of" line -------------------------------------------------


def render_line(rel: str, text: str, registry: dict[str, RegistryClaim], config: StampConfig) -> str | None:
    prefix = _prefix(rel)
    tool = config.tool_pages.get(rel)
    claims = page_claims(text, registry)
    if tool is not None and tool["variant"] == "none-stated":
        reviewed = date.fromisoformat(tool["reviewed"])
        body = (
            f"Rules as of {long_date(reviewed)} &middot; this tool applies no regulatory rule of its own "
            "and states none; it works on the values you enter. "
            f'<a href="{prefix}primary-sources">Primary sources</a>.'
        )
    elif tool is not None and tool["variant"] == "unregistered":
        body = (
            "Rules as of: not stamped &middot; this page names regulatory rules or dates that are not yet in "
            "the ClinicOps claim registry, so none is shown as checked. Confirm any figure against the "
            f'official source. <a href="{prefix}primary-sources">Primary sources</a>.'
        )
    elif tool is not None:
        as_of = rules_as_of(claims)
        if not claims or as_of is None:
            raise ValueError(f"{rel}: tool stamp variant 'claims' needs registry claims on the page")
        parts = []
        for claim in claims:
            sources = _http_sources(claim)
            link = f'<a href="{_esc(sources[0])}">{_esc(claim.claim_id)}</a>' if sources else _esc(claim.claim_id)
            parts.append(f"{link}: {_esc(claim.label or '')}")
        body = (
            f"Rules as of {long_date(as_of)} &middot; read at the source; registry "
            + "; ".join(parts)
            + "."
        )
    else:
        as_of = rules_as_of(claims)
        dated = f"Rules as of {long_date(as_of)}" if as_of else "Observations as of " + long_date(
            min(c.last_verified for c in claims if c.last_verified)
        )
        review = next_review(claims)
        body = (
            f"{dated} &middot; <a href=\"#last-verified\">last verified</a> against the sources named below"
            + (f" &middot; next review by {long_date(review)}" if review else "")
            + "."
        )
    return f'<!-- stamp:line:start --><p class="meta stamp-line">{body}</p><!-- stamp:line:end -->'


# ---- the "Last verified" block ----------------------------------------------


def _source_cell(claim: RegistryClaim) -> str:
    links = []
    for url in _http_sources(claim):
        host = re.sub(r"^https?://(www\.)?", "", url).split("/", 1)[0]
        links.append(f'<a href="{_esc(url)}">{_esc(host)}</a>')
    where = ", ".join(links) if links else "ClinicOps sample records"
    return f"{where}<br>{_esc(claim.source_date or '')}"


def render_block(rel: str, text: str, registry: dict[str, RegistryClaim]) -> str:
    prefix = _prefix(rel)
    claims = page_claims(text, registry)
    as_of = rules_as_of(claims)
    rows = []
    for claim in claims:
        read_on = long_date(claim.last_verified) if claim.last_verified else ""
        review = long_date(claim.review_after) if claim.review_after else ""
        rows.append(
            "<tr>"
            f'<th scope="row">{_esc(claim.claim_id)}<br><span class="small muted">{_esc(claim.label or "")}</span></th>'
            f"<td>{_source_cell(claim)}</td>"
            f"<td>{read_on}</td>"
            f"<td>{_esc(METHOD_LABELS.get(claim.verified_method or '', ''))}</td>"
            f"<td>{_esc(' '.join(claim.not_established))}</td>"
            f"<td>{review}</td>"
            "</tr>"
        )
    version = f"{(as_of or max(c.last_verified for c in claims if c.last_verified)).isoformat()}-{registry_digest(claims)}"
    return (
        "<!-- stamp:block:start -->"
        '<section class="stamp-block" id="last-verified" aria-labelledby="last-verified-h">'
        '<h2 id="last-verified-h">Last verified</h2>'
        '<p class="small muted">Every claim above is registered with the ClinicOps claim registry. '
        "The table says what was read, when, how, and what is not established. It is a record of a reading, "
        "not continuous monitoring: a rule that changed after the read date is not shown here. "
        f'Corrections are logged on <a href="{prefix}research#cite-and-correct">the research page</a>.</p>'
        '<div class="table-scroll" tabindex="0" role="region" aria-label="Last verified claims, scrollable table">'
        "<table><thead><tr>"
        '<th scope="col">Claim</th><th scope="col">Source and source date</th><th scope="col">Read on</th>'
        '<th scope="col">Method</th><th scope="col">Not established</th><th scope="col">Next review</th>'
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
        f'<p class="meta">Page version <code>{version}</code> (stamp date and a digest of the registry rows shown).</p>'
        "</section>"
        "<!-- stamp:block:end -->"
    )


# ---- the answer-first block -------------------------------------------------


def render_answer(rel: str, spec: dict, registry: dict[str, RegistryClaim]) -> str:
    claims = [registry[claim_id] for claim_id in spec["claims"]]
    if claims:
        read_on = max(c.last_verified for c in claims if c.last_verified)
        first = _http_sources(claims[0])
        link = (
            f'<a href="{_esc(first[0])}">{_esc(spec["source_label"])}</a>'
            if first
            else _esc(spec["source_label"])
        )
        ids = ", ".join(c.claim_id for c in claims)
        source = (
            f"Source: {link}; {_esc(claims[0].source_date or '')}. Read at the source on "
            f"{long_date(read_on)}. Registry {_esc(ids)}."
        )
    else:
        source = f"Source: {_esc(spec['source_note'])}"
    return (
        "<!-- answer-first:start -->"
        '<section class="answer-first" aria-labelledby="answer-first-h">'
        '<h2 id="answer-first-h">Short answer</h2>'
        f"<p>{_esc(spec['answer'])}</p>"
        f'<p class="small muted">{source}</p>'
        f'<p class="small"><strong>Boundary.</strong> {_esc(spec["boundary"])}</p>'
        "</section>"
        "<!-- answer-first:end -->"
    )


def answer_digits_outside_claims(spec: dict, registry: dict[str, RegistryClaim]) -> list[str]:
    """Numbers in an answer that no cited claim contains (wording from the registry only)."""
    allowed = {
        token
        for claim_id in spec["claims"]
        for token in DIGITS_RE.findall(registry[claim_id].text)
    }
    return [token for token in DIGITS_RE.findall(spec["answer"]) if token not in allowed]


# ---- placing the pieces -------------------------------------------------------


def _place_line(text: str, line: str) -> str:
    if LINE_RE.search(text):
        return LINE_RE.sub(lambda _m: line, text, count=1)
    h1 = H1_END_RE.search(text)
    if h1 is None:
        raise ValueError("page has no h1 to place the stamp line under")
    lede = LEDE_RE.search(text, h1.end())
    at = lede.end() if lede else h1.end()
    return text[:at] + line + text[at:]


def _place_block(text: str, block: str) -> str:
    cleaned = BLOCK_RE.sub("", text)
    end = cleaned.find("</main>")
    if end == -1:
        raise ValueError("page has no </main> to place the last-verified block before")
    return cleaned[:end] + "\n" + block + "\n" + cleaned[end:]


def _place_answer(text: str, answer: str) -> str:
    cleaned = ANSWER_RE.sub("", text)
    hero = HERO_RE.search(cleaned)
    if hero is None:
        raise ValueError("page has no hero section to place the answer-first block after")
    return cleaned[: hero.end()] + "\n" + answer + cleaned[hero.end() :]


def governed_full_block(rel: str, text: str, config: StampConfig) -> bool:
    return (
        rel not in config.tool_pages
        and rel not in config.full_block_exclude
        and bool(declared_ids(text))
    )


def render_page(rel: str, text: str, registry: dict[str, RegistryClaim], config: StampConfig) -> str:
    out = text
    if rel in config.answer_first:
        out = _place_answer(out, render_answer(rel, config.answer_first[rel], registry))
    if rel in config.tool_pages:
        line = render_line(rel, out, registry, config)
        if line:
            out = _place_line(out, line)
    elif governed_full_block(rel, out, config):
        out = _place_line(out, render_line(rel, out, registry, config) or "")
        out = _place_block(out, render_block(rel, out, registry))
    return out


def managed_pages(root: Path, config: StampConfig) -> list[str]:
    pages = set(config.tool_pages) | set(config.answer_first)
    for path in sorted((root / "docs").rglob("*.html")):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        if governed_full_block(rel, text, config):
            pages.add(rel)
    return sorted(pages)
