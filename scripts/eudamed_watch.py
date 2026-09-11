#!/usr/bin/env python3
"""EUDAMED watchlist monitor (stdlib only).

Monitors the public EUDAMED JSON API for a watchlist of trade names, writes a
versioned snapshot of what the public record shows, and diffs it against the
previous snapshot.

Everything this tool writes is a snapshot of the *public record* at extraction
time. It is never a compliance, conformity or diligence statement about any
named company. See scripts/README_eudamed_watch.md.

Usage:
    python scripts/eudamed_watch.py run --watchlist data/eudamed/watchlist.json \
        --out data/eudamed/ [--max-pages 5] [--sleep 1.0] [--fetch-fixture f.json]
    python scripts/eudamed_watch.py diff <old.json> <new.json> [--out diff.md]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

TOOL_NAME = "eudamed_watch"
TOOL_VERSION = "1.0.0"
USER_AGENT = "ClinicOps-eudamed-watch/1.0 (+https://clinicops.dk)"
BASE = "https://ec.europa.eu/tools/eudamed/api/devices"
PAGE_SIZE = 50  # The API silently caps pageSize at 50; asking for more is pointless.
DEFAULT_MAX_PAGES = 5
DEFAULT_SLEEP = 1.0
DEFAULT_TIMEOUT = 30.0

SRN_RE = re.compile(r"^(?P<country>[A-Z]{2})-(?P<role>MF|AR|IM|PR)-(?P<number>\d{9})$")

# Classification codes for each distinct Basic UDI-DI.
CLS_LEGACY = "legacy_no_sscp_possible"
CLS_PR = "pr_no_sscp_duty"
CLS_LINKED = "sscp_linked"
CLS_ABSENT = "sscp_link_absent"
CLS_EXPECTED_ABSENT = "sscp_expected_but_absent"
CLS_LOOKUP_FAILED = "lookup_failed"

SSCP_FIELDS = ("referenceNumber", "revisionNumber", "issueDate", "validated", "inactive")

# API code values look like "refdata.risk-class.class-iii"; the group prefix is
# stripped for the normalised form and the raw code is kept alongside.
REFDATA_PREFIX_RE = re.compile(r"^refdata\.[^.]+\.")

# Standing limits. These are written into every snapshot and every markdown.
STANDING_LIMITS = [
    "This is a snapshot of what the public EUDAMED record showed at the extraction "
    "date. It is not a compliance, conformity or diligence statement about any "
    "named company, and must not be quoted as one.",
    "Trade-name search is a case-insensitive, unanchored substring match. Results "
    "can include unrelated devices; rows are filtered client-side by "
    "manufacturer_contains where configured.",
    "Zero results means 'not findable under that search string at that time', "
    "not 'not registered'.",
    "totalElements counts returned by the API are unstable and are reported as "
    "approximate; they are for display only.",
    "pageSize is capped at 50 by the API; page coverage is bounded by --max-pages, "
    "so long result lists may be truncated (flagged per entry).",
    "riskClass/legislation query parameters are ignored by the API; risk class is "
    "taken from each row and filtering is client-side.",
    "No Basic UDI-DI lookup endpoint exists; detail lookups go through a UDI-DI "
    "uuid. Only identifiers and link metadata are retrievable; SS(C)P content is "
    "never retrievable through this API.",
    "A basicUdi starting with 'B-' is a legacy (MDD/AIMDD) EUDAMED-generated DI "
    "that structurally cannot carry an SS(C)P link (ClinicOps derived screening "
    "logic, not quoted Commission law).",
    "SRN role PR (system/procedure pack producer) records carry no SS(C)P duty "
    "and are not looked up.",
    "sscp_expected is ClinicOps derived screening logic (class III or implantable, "
    "MDR, not legacy, not PR). 'sscp_expected_but_absent' means no SS(C)P link was "
    "visible in the public record at extraction; it is not a finding that any "
    "obligation is unmet.",
    "Failed pages and lookups are recorded explicitly; a device 'no longer seen' "
    "next to a recorded failure may be an extraction artefact, not a registry "
    "change.",
]


class FetchError(Exception):
    """Raised for any transport, HTTP or decode failure."""


# --------------------------------------------------------------------------- URLs


def search_url(trade_name: str, page: int) -> str:
    query = (
        f"page={page}&pageSize={PAGE_SIZE}&size={PAGE_SIZE}"
        f"&iso2Code=en&languageIso2Code=en&tradeName={quote(trade_name, safe='')}"
    )
    return f"{BASE}/udiDiData?{query}"


def detail_url(uuid: str) -> str:
    return f"{BASE}/basicUdiData/udiDiData/{quote(uuid, safe='')}?languageIso2Code=en"


# ----------------------------------------------------------------------- Fetchers


class LiveFetcher:
    """Polite urllib fetcher: fixed User-Agent, sleep between calls."""

    mode = "live"

    def __init__(self, sleep: float = DEFAULT_SLEEP, timeout: float = DEFAULT_TIMEOUT):
        self.sleep = sleep
        self.timeout = timeout
        self._calls = 0

    def get_json(self, url: str) -> Any:
        if self._calls and self.sleep > 0:
            time.sleep(self.sleep)
        self._calls += 1
        request = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            raise FetchError(f"HTTP {exc.code}: {exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise FetchError(f"URL error: {exc.reason}") from exc
        except (TimeoutError, OSError) as exc:
            raise FetchError(f"transport error: {exc}") from exc
        try:
            return json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise FetchError(f"invalid JSON body: {exc}") from exc


class FixtureFetcher:
    """Offline fetcher reading responses from a JSON file keyed by URL.

    File shape: {"responses": {"<url>": <body> | {"__error__": "message"}}}.
    A missing URL or an "__error__" entry raises FetchError, so failure paths can
    be exercised without the network.
    """

    mode = "fixture"

    def __init__(self, path: Path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.responses = data.get("responses", data)
        self.requested: list[str] = []

    def get_json(self, url: str) -> Any:
        self.requested.append(url)
        if url not in self.responses:
            raise FetchError(f"fixture has no response for {url}")
        body = self.responses[url]
        if isinstance(body, dict) and "__error__" in body:
            raise FetchError(str(body["__error__"]))
        return body


# ---------------------------------------------------------------------- Watchlist


def load_watchlist(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = raw.get("entries") if isinstance(raw, dict) else raw
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{path}: expected a non-empty list of entries")
    seen: set[str] = set()
    out = []
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"{path}: entry {i} is not a mapping")
        label = str(entry.get("label", "")).strip()
        query = str(entry.get("trade_name_query", "")).strip()
        if not label or not query:
            raise ValueError(f"{path}: entry {i} needs 'label' and 'trade_name_query'")
        if label in seen:
            raise ValueError(f"{path}: duplicate label {label!r}")
        seen.add(label)
        out.append(
            {
                "label": label,
                "trade_name_query": query,
                "manufacturer_contains": (entry.get("manufacturer_contains") or None),
                "expected_srn": (entry.get("expected_srn") or None),
                "note": (entry.get("note") or None),
            }
        )
    return out


# ------------------------------------------------------------------- Extraction


def srn_role(srn: str | None) -> str | None:
    if not srn:
        return None
    match = SRN_RE.fullmatch(str(srn).strip().upper())
    return match.group("role") if match else None


def raw_code(value: Any) -> str | None:
    """Return the raw code from a {"code": ...} object or a bare string."""
    if isinstance(value, dict):
        code = value.get("code")
        return str(code) if code is not None else None
    return str(value) if isinstance(value, str) and value else None


def normalise_code(value: Any) -> str | None:
    """'refdata.risk-class.class-iii' -> 'class-iii'; bare strings lower-cased."""
    code = raw_code(value)
    if code is None:
        return None
    return REFDATA_PREFIX_RE.sub("", code).strip().lower() or None


def basic_udi_code(value: Any) -> str:
    """basicUdi is a string in listing rows and a {code: ...} object in detail."""
    if isinstance(value, dict):
        return str(value.get("code") or "").strip()
    return str(value or "").strip()


def _normalise_sscp(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    return {field: value.get(field) for field in SSCP_FIELDS}


def _truthy(value: Any) -> bool | None:
    """implantable/active arrive 'boolean-ish'; map common encodings, else None."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "yes", "y", "1"}:
        return True
    if text in {"false", "no", "n", "0", ""}:
        return False
    return None


def parse_detail(detail: Any) -> dict[str, Any]:
    """Extract the fields this tool records from a Basic UDI-DI detail response."""
    if not isinstance(detail, dict):
        return {"detail_parse_note": "detail body was not a JSON object"}
    legislation = detail.get("legislation")
    nb = detail.get("nbDecision")
    certs = detail.get("deviceCertificateInfoList")
    first_cert = certs[0] if isinstance(certs, list) and certs and isinstance(certs[0], dict) else None
    out: dict[str, Any] = {
        "detail_basic_udi": basic_udi_code(detail.get("basicUdi")) or None,
        "detail_uuid": detail.get("uuid"),
        "linked_sscp": _normalise_sscp(detail.get("linkedSscp")),
        "legislation": normalise_code(legislation),
        "legislation_raw": raw_code(legislation),
        "legacy_directive": _truthy(legislation.get("legacyDirective")) if isinstance(legislation, dict) else None,
        "implantable": _truthy(detail.get("implantable")),
        "active": _truthy(detail.get("active")),
        "nb_decision_reason": normalise_code(nb.get("reason")) if isinstance(nb, dict) else None,
        "nb_decision_date": nb.get("date") if isinstance(nb, dict) else None,
        "certificates_count": len(certs) if isinstance(certs, list) else None,
        "first_certificate_type": normalise_code(first_cert.get("certificateType")) if first_cert else None,
        "first_certificate_number": first_cert.get("certificateNumber") if first_cert else None,
        "device_name": detail.get("deviceName"),
        "device_model": detail.get("deviceModel"),
        "last_updated": detail.get("lastUpdated"),
    }
    return out


def sscp_expected(record: dict[str, Any]) -> bool:
    """ClinicOps derived screening logic for the MDR Art. 32 SS(C)P population.

    True when (class III or implantable) and MDR (not a legacy directive) and
    the record is neither a legacy B- DI nor a PR-role record.
    """
    if record.get("classification") in (CLS_LEGACY, CLS_PR):
        return False
    if str(record.get("basic_udi") or "").startswith("B-") or record.get("srn_role") == "PR":
        return False
    high_risk = record.get("risk_class") == "class-iii" or record.get("implantable") is True
    is_mdr = record.get("legislation") == "mdr" and record.get("legacy_directive") is not True
    return bool(high_risk and is_mdr)


def manufacturer_matches(row: dict[str, Any], needle: str | None) -> bool:
    if not needle:
        return True
    name = str(row.get("manufacturerName") or "")
    return needle.lower() in name.lower()


def fetch_search_rows(
    fetcher: Any, entry: dict[str, Any], max_pages: int, failures: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Page through search results; returns (rows, page_meta)."""
    rows: list[dict[str, Any]] = []
    meta: dict[str, Any] = {
        "pages_fetched": 0,
        "pages_failed": 0,
        "total_elements_approximate": None,
        "total_pages_reported": None,
        "truncated_by_max_pages": False,
    }
    for page in range(max_pages):
        url = search_url(entry["trade_name_query"], page)
        try:
            body = fetcher.get_json(url)
        except FetchError as exc:
            meta["pages_failed"] += 1
            failures.append(
                {
                    "entry_label": entry["label"],
                    "kind": "search_page",
                    "page": page,
                    "url": url,
                    "error": str(exc),
                }
            )
            # A failed page breaks the page sequence; later pages are not
            # trustworthy as a continuation, so stop here and record it.
            break
        meta["pages_fetched"] += 1
        content = body.get("content") if isinstance(body, dict) else None
        if not isinstance(content, list):
            content = []
        if isinstance(body, dict):
            if isinstance(body.get("totalElements"), int):
                meta["total_elements_approximate"] = body["totalElements"]
            if isinstance(body.get("totalPages"), int):
                meta["total_pages_reported"] = body["totalPages"]
        rows.extend(r for r in content if isinstance(r, dict))
        if not content or len(content) < PAGE_SIZE:
            break
        total_pages = meta["total_pages_reported"]
        if isinstance(total_pages, int) and page + 1 >= total_pages:
            break
        if page + 1 >= max_pages:
            meta["truncated_by_max_pages"] = True
    return rows, meta


def classify_devices(
    fetcher: Any,
    entry: dict[str, Any],
    rows: list[dict[str, Any]],
    failures: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Dedupe rows by basicUdi and classify each distinct device."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        basic_udi = basic_udi_code(row.get("basicUdi"))
        if not basic_udi:
            basic_udi = f"(no basicUdi) uuid={row.get('uuid')}"
        grouped.setdefault(basic_udi, []).append(row)

    devices: dict[str, dict[str, Any]] = {}
    for basic_udi in sorted(grouped):
        family = grouped[basic_udi]
        first = family[0]
        srn = first.get("manufacturerSrn")
        role = srn_role(srn)
        record: dict[str, Any] = {
            "basic_udi": basic_udi,
            "rows_collapsed": len(family),
            "uuid": first.get("uuid"),
            "trade_names": sorted({str(r.get("tradeName")) for r in family if r.get("tradeName")}),
            "manufacturer_name": first.get("manufacturerName"),
            "manufacturer_srn": srn,
            "srn_role": role,
            "risk_class": normalise_code(first.get("riskClass")),
            "risk_class_raw": raw_code(first.get("riskClass")),
            "status": normalise_code(first.get("deviceStatusType")),
            "status_raw": raw_code(first.get("deviceStatusType")),
            "statuses_seen": sorted(
                {s for s in (normalise_code(r.get("deviceStatusType")) for r in family) if s}
            ),
            "manufacturer_status": normalise_code(first.get("manufacturerStatus")),
            "classification": None,
            "linked_sscp": None,
            "legislation": None,
            "legacy_directive": None,
            "implantable": None,
            "sscp_expected": False,
            "detail_lookup_done": False,
        }
        if entry.get("expected_srn") and srn:
            record["srn_matches_expected"] = (
                str(srn).strip().upper() == str(entry["expected_srn"]).strip().upper()
            )

        if basic_udi.startswith("B-"):
            record["classification"] = CLS_LEGACY
        elif role == "PR":
            record["classification"] = CLS_PR
        elif not first.get("uuid"):
            record["classification"] = CLS_LOOKUP_FAILED
            failures.append(
                {
                    "entry_label": entry["label"],
                    "kind": "detail_lookup",
                    "basic_udi": basic_udi,
                    "url": None,
                    "error": "row carries no uuid; detail lookup impossible",
                }
            )
        else:
            url = detail_url(str(first["uuid"]))
            try:
                detail = fetcher.get_json(url)
            except FetchError as exc:
                record["classification"] = CLS_LOOKUP_FAILED
                failures.append(
                    {
                        "entry_label": entry["label"],
                        "kind": "detail_lookup",
                        "basic_udi": basic_udi,
                        "url": url,
                        "error": str(exc),
                    }
                )
            else:
                record["detail_lookup_done"] = True
                record.update(parse_detail(detail))
                if record.get("detail_basic_udi") and record["detail_basic_udi"] != basic_udi:
                    record["detail_basic_udi_mismatch"] = True
                # Detail risk class is authoritative if the listing row lacked one.
                if record["risk_class"] is None and isinstance(detail, dict):
                    record["risk_class"] = normalise_code(detail.get("riskClass"))
                    record["risk_class_raw"] = raw_code(detail.get("riskClass"))
                record["sscp_expected"] = sscp_expected(record)
                if record["linked_sscp"]:
                    record["classification"] = CLS_LINKED
                elif record["sscp_expected"]:
                    record["classification"] = CLS_EXPECTED_ABSENT
                else:
                    record["classification"] = CLS_ABSENT
        devices[basic_udi] = record
    return devices


def run_entry(fetcher: Any, entry: dict[str, Any], max_pages: int, failures: list[dict[str, Any]]) -> dict[str, Any]:
    rows, meta = fetch_search_rows(fetcher, entry, max_pages, failures)
    kept = [r for r in rows if manufacturer_matches(r, entry.get("manufacturer_contains"))]
    devices = classify_devices(fetcher, entry, kept, failures)
    counts: dict[str, int] = {}
    for device in devices.values():
        counts[device["classification"]] = counts.get(device["classification"], 0) + 1
    result = dict(entry)
    result.update(meta)
    result.update(
        {
            "rows_seen": len(rows),
            "rows_filtered_out_by_manufacturer": len(rows) - len(kept),
            "distinct_devices": len(devices),
            "classification_counts": dict(sorted(counts.items())),
            "devices": devices,
        }
    )
    return result


def canonical_sha256(payload: dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_snapshot(
    fetcher: Any,
    watchlist: list[dict[str, Any]],
    *,
    max_pages: int,
    snapshot_date: str,
    watchlist_path: str,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    entries = [run_entry(fetcher, entry, max_pages, failures) for entry in watchlist]
    payload: dict[str, Any] = {
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "extracted_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "snapshot_date": snapshot_date,
        "mode": getattr(fetcher, "mode", "unknown"),
        "watchlist_path": watchlist_path,
        "max_pages": max_pages,
        "page_size": PAGE_SIZE,
        "counts_note": "total_elements_approximate values are unstable API counts; display only.",
        "limits": STANDING_LIMITS,
        "entries": entries,
        "failures": failures,
    }
    payload["sha256"] = canonical_sha256(payload)
    return payload


# ------------------------------------------------------------------------ Diff


def _device_map(snapshot: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    out = {}
    for entry in snapshot.get("entries", []):
        for basic_udi, device in (entry.get("devices") or {}).items():
            out[(entry["label"], basic_udi)] = device
    return out


def _labels_with_failures(snapshot: dict[str, Any]) -> set[str]:
    return {f.get("entry_label") for f in snapshot.get("failures", [])}


def compute_diff(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    old_map, new_map = _device_map(old), _device_map(new)
    old_labels = {e["label"] for e in old.get("entries", [])}
    new_labels = {e["label"] for e in new.get("entries", [])}
    old_fail, new_fail = _labels_with_failures(old), _labels_with_failures(new)

    new_devices, gone_devices, sscp_changes, status_changes, class_changes = [], [], [], [], []
    entered_expected_absent, left_expected_absent = [], []
    for key in sorted(new_map.keys() - old_map.keys()):
        if key[0] in old_labels:
            new_devices.append({"label": key[0], "basic_udi": key[1], **_brief(new_map[key])})
    for key in sorted(old_map.keys() - new_map.keys()):
        if key[0] in new_labels:
            gone_devices.append(
                {
                    "label": key[0],
                    "basic_udi": key[1],
                    **_brief(old_map[key]),
                    "possible_extraction_artefact": key[0] in new_fail or key[0] in old_fail,
                }
            )
    for key in sorted(old_map.keys() & new_map.keys()):
        before, after = old_map[key], new_map[key]
        if (before.get("linked_sscp") or None) != (after.get("linked_sscp") or None):
            changed = [
                f
                for f in SSCP_FIELDS
                if (before.get("linked_sscp") or {}).get(f) != (after.get("linked_sscp") or {}).get(f)
            ]
            sscp_changes.append(
                {
                    "label": key[0],
                    "basic_udi": key[1],
                    "fields": changed,
                    "before": before.get("linked_sscp"),
                    "after": after.get("linked_sscp"),
                }
            )
        if before.get("status") != after.get("status"):
            status_changes.append(
                {"label": key[0], "basic_udi": key[1], "before": before.get("status"), "after": after.get("status")}
            )
        if before.get("classification") != after.get("classification"):
            change = {
                "label": key[0],
                "basic_udi": key[1],
                "before": before.get("classification"),
                "after": after.get("classification"),
            }
            class_changes.append(change)
            if after.get("classification") == CLS_EXPECTED_ABSENT:
                entered_expected_absent.append({**change, **_brief(after)})
            elif before.get("classification") == CLS_EXPECTED_ABSENT:
                left_expected_absent.append({**change, **_brief(after)})
    for key in sorted(new_map.keys() - old_map.keys()):
        if key[0] in old_labels and new_map[key].get("classification") == CLS_EXPECTED_ABSENT:
            entered_expected_absent.append(
                {"label": key[0], "basic_udi": key[1], "before": None, "after": CLS_EXPECTED_ABSENT, **_brief(new_map[key])}
            )
    return {
        "old_snapshot_date": old.get("snapshot_date"),
        "new_snapshot_date": new.get("snapshot_date"),
        "old_sha256": old.get("sha256"),
        "new_sha256": new.get("sha256"),
        "entries_added": sorted(new_labels - old_labels),
        "entries_removed": sorted(old_labels - new_labels),
        "new_devices": new_devices,
        "gone_devices": gone_devices,
        "sscp_changes": sscp_changes,
        "status_changes": status_changes,
        "classification_changes": class_changes,
        "entered_sscp_expected_but_absent": entered_expected_absent,
        "left_sscp_expected_but_absent": left_expected_absent,
        "old_failures": len(old.get("failures", [])),
        "new_failures": len(new.get("failures", [])),
    }


def _brief(device: dict[str, Any]) -> dict[str, Any]:
    return {
        "manufacturer_name": device.get("manufacturer_name"),
        "risk_class": device.get("risk_class"),
        "classification": device.get("classification"),
        "status": device.get("status"),
    }


# -------------------------------------------------------------------- Markdown


def limits_block(extraction_date: str) -> str:
    lines = ["## Standing limits", "", f"- Extraction date: {extraction_date}."]
    lines += [f"- {limit}" for limit in STANDING_LIMITS]
    return "\n".join(lines) + "\n"


def _sscp_str(value: dict[str, Any] | None) -> str:
    if not value:
        return "none"
    return ", ".join(f"{f}={value.get(f)}" for f in SSCP_FIELDS)


def render_diff_markdown(diff: dict[str, Any]) -> str:
    out = [
        f"# EUDAMED watch diff: {diff['old_snapshot_date']} -> {diff['new_snapshot_date']}",
        "",
        f"- Previous snapshot sha256: `{diff['old_sha256']}`",
        f"- Current snapshot sha256: `{diff['new_sha256']}`",
        f"- Recorded failures: previous {diff['old_failures']}, current {diff['new_failures']}",
        "",
    ]
    if diff["entries_added"] or diff["entries_removed"]:
        out.append("## Watchlist changes")
        out.append("")
        for label in diff["entries_added"]:
            out.append(f"- Entry added: {label}")
        for label in diff["entries_removed"]:
            out.append(f"- Entry removed: {label}")
        out.append("")

    def section(title: str, items: list[dict[str, Any]], fmt) -> None:
        out.append(f"## {title} ({len(items)})")
        out.append("")
        if not items:
            out.append("- none")
        for item in items:
            out.append(fmt(item))
        out.append("")

    section(
        "New devices seen",
        diff["new_devices"],
        lambda d: f"- [{d['label']}] `{d['basic_udi']}` — {d['manufacturer_name']} — class {d['risk_class']} — {d['classification']} — status {d['status']}",
    )
    section(
        "Devices no longer seen",
        diff["gone_devices"],
        lambda d: (
            f"- [{d['label']}] `{d['basic_udi']}` — {d['manufacturer_name']} — class {d['risk_class']} — was {d['classification']}"
            + (" — POSSIBLE EXTRACTION ARTEFACT (recorded failure on this entry)" if d["possible_extraction_artefact"] else "")
        ),
    )
    section(
        "SS(C)P link changes",
        diff["sscp_changes"],
        lambda d: f"- [{d['label']}] `{d['basic_udi']}` — changed {', '.join(d['fields']) or '(presence)'}: before {_sscp_str(d['before'])}; after {_sscp_str(d['after'])}",
    )
    section(
        "Status changes",
        diff["status_changes"],
        lambda d: f"- [{d['label']}] `{d['basic_udi']}` — {d['before']} -> {d['after']}",
    )
    section(
        "Classification changes",
        diff["classification_changes"],
        lambda d: f"- [{d['label']}] `{d['basic_udi']}` — {d['before']} -> {d['after']}",
    )
    section(
        "Entered 'SS(C)P expected but absent' (public record shows no link; not a compliance finding)",
        diff["entered_sscp_expected_but_absent"],
        lambda d: f"- [{d['label']}] `{d['basic_udi']}` — {d['manufacturer_name']} — class {d['risk_class']} — was {d['before'] or 'not previously seen'}",
    )
    section(
        "Left 'SS(C)P expected but absent'",
        diff["left_sscp_expected_but_absent"],
        lambda d: f"- [{d['label']}] `{d['basic_udi']}` — {d['manufacturer_name']} — now {d['after']}",
    )
    out.append(limits_block(str(diff["new_snapshot_date"])))
    return "\n".join(out)


def render_latest_markdown(snapshot: dict[str, Any], diff_path: str | None) -> str:
    out = [
        "# EUDAMED watch — latest snapshot",
        "",
        f"- Snapshot date: {snapshot['snapshot_date']}",
        f"- Extracted at (UTC): {snapshot['extracted_at_utc']}",
        f"- Tool: {snapshot['tool']} {snapshot['tool_version']} (mode: {snapshot['mode']})",
        f"- Snapshot sha256: `{snapshot['sha256']}`",
        f"- Recorded failures: {len(snapshot['failures'])}",
        f"- Diff against previous snapshot: {diff_path or 'none (first snapshot)'}",
        "",
        "## Watchlist results",
        "",
        "| Entry | Query | Approx. total (API) | Rows seen | Filtered out | Distinct devices | Classification counts | Pages | Truncated |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for entry in snapshot["entries"]:
        counts = ", ".join(f"{k}={v}" for k, v in entry["classification_counts"].items()) or "-"
        approx = entry["total_elements_approximate"]
        out.append(
            f"| {entry['label']} | `{entry['trade_name_query']}` | {approx if approx is not None else 'n/a'} (approx.) "
            f"| {entry['rows_seen']} | {entry['rows_filtered_out_by_manufacturer']} | {entry['distinct_devices']} "
            f"| {counts} | {entry['pages_fetched']} ok / {entry['pages_failed']} failed "
            f"| {'yes' if entry['truncated_by_max_pages'] else 'no'} |"
        )
    out.append("")
    out.append("## Linked SS(C)P metadata seen")
    out.append("")
    any_linked = False
    for entry in snapshot["entries"]:
        for device in entry["devices"].values():
            if device.get("linked_sscp"):
                any_linked = True
                out.append(
                    f"- [{entry['label']}] `{device['basic_udi']}` — class {device['risk_class']} — {_sscp_str(device['linked_sscp'])}"
                )
    if not any_linked:
        out.append("- none in this snapshot")
    out.append("")
    out.append("## SS(C)P expected but absent in the public record")
    out.append("")
    out.append(
        "Derived screening population (class III or implantable, MDR, not legacy, not PR) "
        "with no SS(C)P link visible at extraction. Not a compliance finding about any company."
    )
    out.append("")
    any_expected_absent = False
    for entry in snapshot["entries"]:
        for device in entry["devices"].values():
            if device.get("classification") == CLS_EXPECTED_ABSENT:
                any_expected_absent = True
                out.append(
                    f"- [{entry['label']}] `{device['basic_udi']}` — {device['manufacturer_name']} — class {device['risk_class']}"
                    f" — implantable={device.get('implantable')} — legislation={device.get('legislation')} — status {device.get('status')}"
                )
    if not any_expected_absent:
        out.append("- none in this snapshot")
    out.append("")
    out.append("## Recorded failures")
    out.append("")
    if not snapshot["failures"]:
        out.append("- none")
    for failure in snapshot["failures"]:
        out.append(
            f"- [{failure['entry_label']}] {failure['kind']}"
            + (f" page {failure['page']}" if "page" in failure else "")
            + (f" basicUdi `{failure['basic_udi']}`" if failure.get("basic_udi") else "")
            + f": {failure['error']}"
        )
    out.append("")
    out.append(limits_block(str(snapshot["snapshot_date"])))
    return "\n".join(out)


# --------------------------------------------------------------------- Commands


def previous_snapshot(snapshots_dir: Path, current_date: str) -> Path | None:
    candidates = sorted(
        p for p in snapshots_dir.glob("*.json") if p.stem < current_date and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.stem)
    )
    return candidates[-1] if candidates else None


def cmd_run(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    snapshots_dir, diffs_dir = out_dir / "snapshots", out_dir / "diffs"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    diffs_dir.mkdir(parents=True, exist_ok=True)

    watchlist = load_watchlist(Path(args.watchlist))
    fetcher = FixtureFetcher(Path(args.fetch_fixture)) if args.fetch_fixture else LiveFetcher(args.sleep, args.timeout)
    snapshot_date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", snapshot_date):
        print(f"invalid --date {snapshot_date!r}, expected YYYY-MM-DD", file=sys.stderr)
        return 2

    snapshot = build_snapshot(
        fetcher, watchlist, max_pages=args.max_pages, snapshot_date=snapshot_date, watchlist_path=str(args.watchlist)
    )
    snapshot_path = snapshots_dir / f"{snapshot_date}.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    diff_rel: str | None = None
    prev = previous_snapshot(snapshots_dir, snapshot_date)
    if prev is not None:
        old = json.loads(prev.read_text(encoding="utf-8"))
        diff = compute_diff(old, snapshot)
        diff_path = diffs_dir / f"{snapshot_date}.md"
        diff_path.write_text(render_diff_markdown(diff), encoding="utf-8")
        diff_rel = f"diffs/{snapshot_date}.md"
    (out_dir / "LATEST.md").write_text(render_latest_markdown(snapshot, diff_rel), encoding="utf-8")

    print(f"snapshot: {snapshot_path}")
    print(f"diff: {diffs_dir / (snapshot_date + '.md') if diff_rel else 'none (no previous snapshot)'}")
    print(f"latest: {out_dir / 'LATEST.md'}")
    print(f"failures recorded: {len(snapshot['failures'])}")
    for failure in snapshot["failures"]:
        print(f"  - [{failure['entry_label']}] {failure['kind']}: {failure['error']}", file=sys.stderr)
    if args.strict and snapshot["failures"]:
        return 1
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    old = json.loads(Path(args.old).read_text(encoding="utf-8"))
    new = json.loads(Path(args.new).read_text(encoding="utf-8"))
    markdown = render_diff_markdown(compute_diff(old, new))
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(markdown, encoding="utf-8")
        print(f"diff: {args.out}")
    else:
        sys.stdout.write(markdown)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eudamed_watch", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Extract a snapshot, diff against the previous one, refresh LATEST.md")
    run.add_argument("--watchlist", required=True, help="Path to watchlist.json")
    run.add_argument("--out", required=True, help="Output directory (snapshots/, diffs/, LATEST.md)")
    run.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES, help="Max search pages per query (default 5)")
    run.add_argument("--sleep", type=float, default=DEFAULT_SLEEP, help="Seconds between live API calls (default 1.0)")
    run.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Per-request timeout in seconds")
    run.add_argument("--fetch-fixture", help="Offline mode: JSON file of responses keyed by URL")
    run.add_argument("--date", help="Override snapshot date (YYYY-MM-DD); default is today UTC")
    run.add_argument("--strict", action="store_true", help="Exit 1 if any page or lookup failed")
    run.set_defaults(func=cmd_run)

    diff = sub.add_parser("diff", help="Diff two snapshot JSON files")
    diff.add_argument("old")
    diff.add_argument("new")
    diff.add_argument("--out", help="Write markdown here instead of stdout")
    diff.set_defaults(func=cmd_diff)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
