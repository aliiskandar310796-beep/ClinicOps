"""Render the clinical operations workflow map from data/ops-map/steps.json.

One source of truth feeds two generated outputs:
  * the static step cards, phase strip, lane controls, review block and change log
    between OPS-MAP markers in docs/clinical-operations-workflow-map.html;
  * docs/assets/ops-map-data.js (the slim data the browser filter needs).

Every clock or rule shown on the page must cite a claim in research/claims.jsonl that
allows the `website` use. The renderer copies the registered wording, limits, sources and
review date into the card, so the page cannot drift from the registry, and it refuses to
render a step that cites a missing, rejected, superseded or expired claim.

Usage:
  python scripts/render_ops_map.py            write the outputs
  python scripts/render_ops_map.py --check    fail if the outputs are stale or invalid
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

from clinicops_os.claim_registry import RegistryClaim, load_registry

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ops-map" / "steps.json"
REGISTRY = ROOT / "research" / "claims.jsonl"
PAGE = ROOT / "docs" / "clinical-operations-workflow-map.html"
DATA_JS = ROOT / "docs" / "assets" / "ops-map-data.js"

SCHEMA = "clinicops-ops-map/1"
OVERLAYS = ("drug", "device", "both")
OVERLAY_LABEL = {"drug": "Drug trials (CTR)", "device": "Device investigations (MDR)", "both": "Drug and device"}
STATUSES = ("verified", "qualified", "synthesis", "not_shown")
STATUS_LABEL = {
    "verified": "Verified",
    "qualified": "Qualified",
    "synthesis": "ClinicOps synthesis",
    "not_shown": "Not shown",
}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Document identifiers that carry digits but are names, not figures.
IDENTIFIER_RE = re.compile(r"MDCG\s\d{4}-\d+(?:/\d+)?(?:\srev\.?\d+)?|ICH E\d+\(R\d\)|E6\(R3\)")
DIGITS_RE = re.compile(r"\d+")
MAILTO = "mailto:info@clinicops.dk"

MARKERS = ("CLAIMS", "CONTROLS", "PHASES", "STEPS", "REVIEW", "CHANGELOG")


class MapError(Exception):
    pass


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def load_data() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def _digits(text: str) -> set[str]:
    return set(DIGITS_RE.findall(IDENTIFIER_RE.sub(" ", text)))


def validate(data: dict, claims: dict[str, RegistryClaim], as_of: date) -> tuple[list[str], date | None]:
    """Return (problems, next_review). Problems are strings; empty means the map may be rendered."""
    problems: list[str] = []

    def bad(message: str) -> None:
        problems.append(message)

    if data.get("schema") != SCHEMA:
        bad(f"schema must be {SCHEMA}")
    for key in ("map_date", "sources_opened"):
        if not DATE_RE.match(str(data.get(key, ""))):
            bad(f"{key} must be YYYY-MM-DD")
    phase_ids = [p["id"] for p in data.get("phases", [])]
    lane_ids = [lane["id"] for lane in data.get("lanes", [])]
    if len(phase_ids) != 6 or len(set(phase_ids)) != 6:
        bad("expected 6 distinct phases")
    if len(lane_ids) != 12 or len(set(lane_ids)) != 12:
        bad("expected 12 distinct lanes")

    seen: set[str] = set()
    cited: set[str] = set()
    read_dates: set[str] = set()
    for step in data.get("steps", []):
        slug = step.get("slug", "")
        where = f"step {slug or '?'}"
        if not SLUG_RE.match(slug):
            bad(f"{where}: slug must be lower-case words joined by hyphens")
        if slug in seen:
            bad(f"{where}: duplicate slug")
        seen.add(slug)
        if step.get("phase") not in phase_ids:
            bad(f"{where}: unknown phase")
        step_lanes = step.get("lanes", [])
        if not step_lanes or any(lane not in lane_ids for lane in step_lanes):
            bad(f"{where}: lanes must be a non-empty subset of the 12 lanes")
        if step.get("overlay") not in OVERLAYS:
            bad(f"{where}: overlay must be one of {OVERLAYS}")
        status = step.get("status")
        if status not in STATUSES:
            bad(f"{where}: status must be one of {STATUSES}")
        for key in ("title", "settle", "leaves"):
            if not str(step.get(key, "")).strip():
                bad(f"{where}: {key} is required")
        if not step.get("owners"):
            bad(f"{where}: owners is required")

        step_claims = step.get("claims", [])
        facts = step.get("facts", [])
        not_shown = step.get("not_shown", [])
        if status in ("synthesis", "not_shown") and (step_claims or facts):
            bad(f"{where}: a {status} step cannot cite claims or show facts")
        if status in ("verified", "qualified") and not (step_claims and facts):
            bad(f"{where}: a {status} step needs claims and at least one fact")
        if status == "not_shown" and not not_shown:
            bad(f"{where}: a not_shown step needs a not_shown note")

        claim_digits: set[str] = set()
        statuses: set[str] = set()
        for claim_id in step_claims:
            claim = claims.get(claim_id)
            if claim is None:
                bad(f"{where}: claim {claim_id} is not in the registry")
                continue
            cited.add(claim_id)
            reasons = claim.gate("website", as_of)
            if reasons:
                bad(f"{where}: claim {claim_id} cannot be shown on the website: {'; '.join(reasons)}")
            statuses.add(claim.status.value)
            claim_digits |= _digits(claim.text)
        if status == "verified" and statuses and statuses != {"verified"}:
            bad(f"{where}: chip says Verified but a cited claim is {sorted(statuses)}")
        if status == "qualified" and "qualified" not in statuses and statuses:
            bad(f"{where}: chip says Qualified but every cited claim is verified")

        for fact in facts:
            tag = f"{where} fact '{fact.get('label', '?')}'"
            if fact.get("claim") not in step_claims:
                bad(f"{tag}: claim must be listed in the step's claims")
            if fact.get("kind") not in ("clock", "rule"):
                bad(f"{tag}: kind must be clock or rule")
            if fact.get("overlay") not in OVERLAYS:
                bad(f"{tag}: overlay must be one of {OVERLAYS}")
            elif step.get("overlay") != "both" and fact.get("overlay") not in (step.get("overlay"), "both"):
                bad(f"{tag}: overlay conflicts with the step's overlay")
            if not fact.get("ref") or not fact.get("label"):
                bad(f"{tag}: label and ref are required")
            figure = fact.get("figure")
            if fact.get("kind") == "clock":
                if not figure:
                    bad(f"{tag}: a clock needs a figure")
                else:
                    claim = claims.get(fact.get("claim", ""))
                    if claim is not None:
                        missing = _digits(figure) - _digits(claim.text)
                        if missing:
                            bad(f"{tag}: figure has numbers not in the registered wording: {sorted(missing)}")
            elif figure:
                bad(f"{tag}: a rule has no figure")
            read_on = fact.get("read_on")
            if read_on is not None:
                if not DATE_RE.match(str(read_on)):
                    bad(f"{tag}: read_on must be YYYY-MM-DD or null")
                else:
                    read_dates.add(read_on)
        scope_notes = step.get("notes", [])
        for note in not_shown + scope_notes:
            if note.get("overlay") not in OVERLAYS or not str(note.get("text", "")).strip():
                bad(f"{where}: not_shown and notes entries need an overlay and text")

        # Digit guard: no figure may appear in prose unless the registered wording carries it.
        prose = [str(step.get(k, "")) for k in ("settle", "leaves", "title")] + [str(n.get("text", "")) for n in not_shown + scope_notes]
        for text in prose:
            extra = _digits(text) - claim_digits
            if extra:
                bad(f"{where}: numbers {sorted(extra)} in prose are not in a cited claim: {text[:60]!r}")

    if read_dates and data.get("sources_opened") != max(read_dates):
        bad(f"sources_opened must equal the latest read_on ({max(read_dates)})")
    next_review = min((claims[c].review_after for c in cited if c in claims and claims[c].review_after), default=None)
    return problems, next_review


# --------------------------------------------------------------------------- HTML


def _tag(text: str) -> str:
    return f'<span class="tag">{esc(text)}</span>'


def _chip(status: str) -> str:
    return f'<span class="chip chip-{status}">{esc(STATUS_LABEL[status])}</span>'


def _claim_details(claim: RegistryClaim) -> str:
    limits = " ".join(claim.limitations)
    sources = ", ".join(f'<a href="{esc(url)}" rel="noopener">{esc(_source_label(url))}</a>' for url in claim.sources)
    review = claim.review_after.isoformat() if claim.review_after else "not set"
    return (
        f'<details class="claim"><summary>Registered wording and limits ({esc(claim.claim_id)})</summary>'
        f"<p>{esc(claim.text)}</p>"
        f'<p class="small"><strong>Limits.</strong> {esc(limits)}</p>'
        f'<p class="small"><strong>Evidence class:</strong> {esc(claim.evidence_class.value)}. '
        f"<strong>Status:</strong> {esc(claim.status.value)}. <strong>Review due:</strong> {esc(review)}.</p>"
        f'<p class="small"><strong>Sources:</strong> {sources}</p></details>'
    )


def _source_label(url: str) -> str:
    host = re.sub(r"^https?://(www\.)?", "", url).split("/", 1)[0]
    if "CELEX" in url:
        match = re.search(r"CELEX:([0-9A-Z-]+)", url)
        return f"EUR-Lex consolidated text {match.group(1)}" if match else host
    return host


def _fact_html(fact: dict, claims: dict[str, RegistryClaim]) -> str:
    claim = claims[fact["claim"]]
    review = claim.review_after.isoformat() if claim.review_after else "not set"
    read = f"Read on {esc(fact['read_on'])}" if fact.get("read_on") else "Reading date: see the registered entry"
    kind = "Clock" if fact["kind"] == "clock" else "Rule"
    figure = f'<p class="fact-figure">{esc(fact["figure"])}</p>' if fact.get("figure") else ""
    return (
        f'<section class="fact fact-{fact["kind"]}" data-overlay="{fact["overlay"]}" aria-label="{kind}: {esc(fact["label"])}">'
        f'<p class="fact-label"><span class="fact-kind">{kind}</span> {esc(fact["label"])} {_tag(OVERLAY_LABEL[fact["overlay"]])}</p>'
        f"{figure}"
        f'<p class="small fact-ref">{esc(fact["ref"])} · {esc(claim.claim_id)} · {read} · Review due {esc(review)}</p>'
        f"</section>"
    )


def _not_shown_html(note: dict) -> str:
    return (
        f'<p class="not-shown" data-overlay="{note["overlay"]}">{_chip("not_shown")} {esc(note["text"])} '
        f"{_tag(OVERLAY_LABEL[note['overlay']])}</p>"
    )


def _scope_note_html(note: dict) -> str:
    return (
        f'<p class="scope-note small" data-overlay="{note["overlay"]}"><strong>Scope.</strong> {esc(note["text"])}</p>'
    )


def step_html(step: dict, data: dict, claims: dict[str, RegistryClaim]) -> str:
    lanes = {lane["id"]: lane["title"] for lane in data["lanes"]}
    slug = step["slug"]
    open_tag = (
        f'<article class="step" id="step-{slug}" data-step="{slug}" data-phase="{step["phase"]}" '
        f'data-lanes="{" ".join(step["lanes"])}" data-overlay="{step["overlay"]}" data-status="{step["status"]}" '
        f'aria-labelledby="step-{slug}-h">'
    )
    head = (
        f'<div class="step-head"><h3 id="step-{slug}-h"><a class="step-anchor" href="#step-{slug}">'
        f'{esc(step["title"])}</a></h3>{_chip(step["status"])}</div>'
    )
    meta = (
        '<p class="step-meta">'
        + _tag(OVERLAY_LABEL[step["overlay"]])
        + " "
        + " ".join(_tag(lanes[lane]) for lane in step["lanes"])
        + "</p>"
    )
    dl = (
        '<dl class="step-dl">'
        f"<div><dt>What has to be settled</dt><dd>{esc(step['settle'])}</dd></div>"
        f"<div><dt>What it leaves behind</dt><dd>{esc(step['leaves'])}</dd></div>"
        f"<div><dt>Owner roles</dt><dd>{esc(', '.join(step['owners']))}</dd></div>"
        "</dl>"
    )
    parts = [open_tag, head, meta, dl]
    parts.extend(_fact_html(fact, claims) for fact in step.get("facts", []))
    parts.extend(_not_shown_html(note) for note in step.get("not_shown", []))
    parts.extend(_scope_note_html(note) for note in step.get("notes", []))
    parts.extend(_claim_details(claims[claim_id]) for claim_id in step.get("claims", []))
    if step["status"] == "synthesis":
        parts.append(
            '<p class="small synth-note">ClinicOps synthesis: a reading of how the work is usually organised. '
            "No regulator states it and no clock is attached.</p>"
        )
    links = step.get("links", [])
    if links:
        parts.append(
            '<p class="step-links small">'
            + " · ".join(f'<a href="{esc(link["href"])}">{esc(link["label"])}</a>' for link in links)
            + "</p>"
        )
    subject = f"Map correction: {slug}"
    parts.append(
        f'<p class="small step-report"><a href="{MAILTO}?subject={esc(subject.replace(" ", "%20"))}">Report a mistake in this step</a></p>'
    )
    parts.append(f'<div class="trace" data-trace-slot="{slug}"></div>')
    parts.append("</article>")
    return "".join(parts)


def phases_html(data: dict) -> str:
    items = []
    for phase in data["phases"]:
        count = sum(1 for s in data["steps"] if s["phase"] == phase["id"])
        items.append(
            f'<li><a href="#phase-{phase["id"]}"><span class="phase-n">{phase["n"]}</span> '
            f'<span class="phase-t">{esc(phase["title"])}</span> <span class="phase-c">{count} steps</span></a></li>'
        )
    return '<nav class="phase-strip" aria-label="Phases"><ol>' + "".join(items) + "</ol></nav>"


def controls_html(data: dict) -> str:
    counts = {lane["id"]: sum(1 for s in data["steps"] if lane["id"] in s["lanes"]) for lane in data["lanes"]}
    overlay_buttons = "".join(
        f'<button type="button" class="btn secondary-btn" data-overlay-btn="{key}" aria-pressed="{"true" if key == "both" else "false"}">{label}</button>'
        for key, label in (("both", "Both"), ("drug", "Drug trials (CTR)"), ("device", "Device investigations (MDR)"))
    )
    lane_buttons = (
        f'<button type="button" class="btn secondary-btn" data-lane-btn="all" aria-pressed="true">All lanes ({len(data["steps"])})</button>'
        + "".join(
            f'<button type="button" class="btn secondary-btn" data-lane-btn="{lane["id"]}" aria-pressed="false" title="{esc(lane["summary"])}">'
            f'{esc(lane["title"])} ({counts[lane["id"]]})</button>'
            for lane in data["lanes"]
        )
    )
    return (
        '<fieldset class="filter-group"><legend>Show</legend>'
        f'<div class="btn-row" role="group" aria-label="Regime">{overlay_buttons}</div></fieldset>'
        '<fieldset class="filter-group"><legend>Lane</legend>'
        f'<div class="btn-row" role="group" aria-label="Lane">{lane_buttons}</div></fieldset>'
    )


def steps_html(data: dict, claims: dict[str, RegistryClaim]) -> str:
    out = []
    for phase in data["phases"]:
        steps = [s for s in data["steps"] if s["phase"] == phase["id"]]
        cards = "".join(step_html(s, data, claims) for s in steps)
        out.append(
            f'<section class="phase" id="phase-{phase["id"]}" data-phase-section="{phase["id"]}" aria-labelledby="phase-{phase["id"]}-h">'
            f'<h2 id="phase-{phase["id"]}-h"><span class="phase-n">{phase["n"]}</span> {esc(phase["title"])}</h2>'
            f'<p class="phase-summary">{esc(phase["summary"])}</p>'
            f"{cards}</section>"
        )
    return "\n".join(out)


def review_html(data: dict, claims: dict[str, RegistryClaim], next_review: date | None) -> str:
    cited = sorted({c for s in data["steps"] for c in s.get("claims", [])})
    rows = "".join(
        f"<tr><td>{esc(c)}</td><td>{esc(claims[c].status.value)}</td><td>{esc(claims[c].review_after.isoformat() if claims[c].review_after else 'not set')}</td></tr>"
        for c in cited
    )
    nxt = next_review.isoformat() if next_review else "not set"
    return (
        '<ul class="plain">'
        f"<li><strong>Sources last opened:</strong> {esc(data['sources_opened'])}. Primary texts were opened on that date unless a card says otherwise.</li>"
        f"<li><strong>Next review:</strong> {esc(nxt)}, the nearest review date among the {len(cited)} registered entries this page uses.</li>"
        f"<li><strong>Map version:</strong> {esc(data['version'])}, dated {esc(data['map_date'])}.</li></ul>"
        '<div class="table-scroll" tabindex="0" role="region" aria-label="Registered entries and their review dates, scrollable table">'
        "<table><thead><tr><th scope=\"col\">Registered entry</th><th scope=\"col\">Status</th><th scope=\"col\">Review due</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
    )


def changelog_html(data: dict) -> str:
    return "<ul class=\"plain\">" + "".join(
        f"<li><strong>{esc(item['date'])}.</strong> {esc(item['text'])}</li>" for item in data["changelog"]
    ) + "</ul>"


def claims_comment(data: dict) -> str:
    ids = sorted({c for s in data["steps"] for c in s.get("claims", [])})
    return f"<!-- claim-use: {data['claim_use']} -->\n<!-- claim-ids: {', '.join(ids)} -->"


def render_blocks(data: dict, claims: dict[str, RegistryClaim], next_review: date | None) -> dict[str, str]:
    return {
        "CLAIMS": claims_comment(data),
        "CONTROLS": controls_html(data),
        "PHASES": phases_html(data),
        "STEPS": steps_html(data, claims),
        "REVIEW": review_html(data, claims, next_review),
        "CHANGELOG": changelog_html(data),
    }


def apply_blocks(page_text: str, blocks: dict[str, str]) -> str:
    for name in MARKERS:
        pattern = re.compile(
            rf"(<!-- OPS-MAP:{name}:START -->)(.*?)(<!-- OPS-MAP:{name}:END -->)", re.DOTALL
        )
        if not pattern.search(page_text):
            raise MapError(f"{PAGE.name}: missing OPS-MAP:{name} markers")
        page_text = pattern.sub(lambda m, n=name: f"{m.group(1)}\n{blocks[n]}\n{m.group(3)}", page_text, count=1)
    return page_text


def data_js(data: dict) -> str:
    slim = {
        "schema": data["schema"],
        "version": data["version"],
        "mapDate": data["map_date"],
        "phases": [{"id": p["id"], "n": p["n"], "title": p["title"]} for p in data["phases"]],
        "lanes": [{"id": lane["id"], "title": lane["title"]} for lane in data["lanes"]],
        "steps": [
            {
                "slug": s["slug"],
                "title": s["title"],
                "phase": s["phase"],
                "lanes": s["lanes"],
                "overlay": s["overlay"],
                "status": s["status"],
            }
            for s in data["steps"]
        ],
    }
    body = json.dumps(slim, indent=2, ensure_ascii=False)
    return (
        "/* Generated by scripts/render_ops_map.py from data/ops-map/steps.json. Do not edit by hand. */\n"
        "(function (root) {\n  'use strict';\n"
        f"  const data = {body};\n"
        "  if (typeof module === 'object' && module.exports) module.exports = data;\n"
        "  else root.ClinicOpsOpsMapData = data;\n"
        "})(typeof globalThis === 'object' ? globalThis : this);\n"
    )


def build(as_of: date) -> tuple[str, str]:
    data = load_data()
    claims = {c.claim_id: c for c in load_registry(REGISTRY)}
    problems, next_review = validate(data, claims, as_of)
    if problems:
        raise MapError("\n".join(f"- {p}" for p in problems))
    page = apply_blocks(PAGE.read_text(encoding="utf-8"), render_blocks(data, claims, next_review))
    return page, data_js(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--as-of", help="YYYY-MM-DD, for tests; default is today")
    args = parser.parse_args(argv)
    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()  # noqa: DTZ011 - expiry is calendar-date based
    try:
        page, js = build(as_of)
    except MapError as exc:
        print(f"ops map is invalid:\n{exc}", file=sys.stderr)
        return 2
    if args.check:
        stale = [
            path.relative_to(ROOT).as_posix()
            for path, text in ((PAGE, page), (DATA_JS, js))
            if not path.exists() or path.read_text(encoding="utf-8") != text
        ]
        if stale:
            print(f"stale: {', '.join(stale)}; run `python scripts/render_ops_map.py`", file=sys.stderr)
            return 2
        print("ops map contract: OK")
        return 0
    PAGE.write_text(page, encoding="utf-8")
    DATA_JS.write_text(js, encoding="utf-8")
    print(f"wrote {PAGE.relative_to(ROOT)} and {DATA_JS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
