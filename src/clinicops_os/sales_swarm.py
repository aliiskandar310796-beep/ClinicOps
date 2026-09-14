from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

EXPECTED_CELL_COUNT = 33
EXPECTED_LEAD_TARGET = 99
MAX_DAILY_SENDS = 15
SUPPRESSED_ACCOUNTS = {"ergomed group", "primevigilance"}
DENMARK_CODES = {"dk", "denmark"}
OUTBOUND_CHANNELS = {"cold_email", "contact_form", "partner_intro", "directory", "community", "event"}


def _required_string(row: dict[str, object], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _required_bool(row: dict[str, object], key: str) -> bool:
    value = row.get(key)
    if not isinstance(value, bool):
        raise TypeError(f"{key} must be a boolean")
    return value


def _required_int(row: dict[str, object], key: str) -> int:
    value = row.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{key} must be an integer")
    return value


@dataclass(frozen=True)
class SalesCell:
    cell_id: str
    market: str
    buyer: str
    channel: str
    lead_quota: int
    outcome: str

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> SalesCell:
        channel = _required_string(row, "channel")
        if channel not in OUTBOUND_CHANNELS:
            raise ValueError(f"unsupported channel '{channel}'")
        quota = _required_int(row, "lead_quota")
        if quota < 1:
            raise ValueError("lead_quota must be at least 1")
        return cls(
            cell_id=_required_string(row, "cell_id"),
            market=_required_string(row, "market"),
            buyer=_required_string(row, "buyer"),
            channel=channel,
            lead_quota=quota,
            outcome=_required_string(row, "outcome"),
        )


@dataclass(frozen=True)
class SalesSwarm:
    cells: tuple[SalesCell, ...]

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> SalesSwarm:
        raw = row.get("cells")
        if not isinstance(raw, list):
            raise TypeError("cells must be a list")
        cells = tuple(SalesCell.from_dict(item) for item in raw)
        ids = [cell.cell_id for cell in cells]
        if len(ids) != len(set(ids)):
            raise ValueError("cell_id values must be unique")
        return cls(cells=cells)


@dataclass(frozen=True)
class LeadCandidate:
    account_name: str
    country: str
    channel: str
    master_log_checked: bool
    outlook_sent_checked: bool
    gmail_sent_checked: bool
    prior_account_contacted: bool
    route_verified: bool

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> LeadCandidate:
        channel = _required_string(row, "channel")
        if channel not in OUTBOUND_CHANNELS:
            raise ValueError(f"unsupported channel '{channel}'")
        return cls(
            account_name=_required_string(row, "account_name"),
            country=_required_string(row, "country"),
            channel=channel,
            master_log_checked=_required_bool(row, "master_log_checked"),
            outlook_sent_checked=_required_bool(row, "outlook_sent_checked"),
            gmail_sent_checked=_required_bool(row, "gmail_sent_checked"),
            prior_account_contacted=_required_bool(row, "prior_account_contacted"),
            route_verified=_required_bool(row, "route_verified"),
        )


@dataclass(frozen=True)
class LeadDecision:
    account_name: str
    eligible: bool
    reasons: tuple[str, ...]


def validate_swarm(swarm: SalesSwarm) -> list[str]:
    errors: list[str] = []
    if len(swarm.cells) != EXPECTED_CELL_COUNT:
        errors.append(f"expected {EXPECTED_CELL_COUNT} sales cells, found {len(swarm.cells)}")
    total_quota = sum(cell.lead_quota for cell in swarm.cells)
    if total_quota != EXPECTED_LEAD_TARGET:
        errors.append(f"lead quota must total {EXPECTED_LEAD_TARGET}, found {total_quota}")
    return errors


def evaluate_lead(lead: LeadCandidate) -> LeadDecision:
    reasons: list[str] = []
    account_key = lead.account_name.casefold().strip()
    country_key = lead.country.casefold().strip()

    if account_key in SUPPRESSED_ACCOUNTS:
        reasons.append("permanent do-not-contact account")
    if not lead.master_log_checked:
        reasons.append("private outreach master not checked")
    if not lead.outlook_sent_checked:
        reasons.append("Outlook Sent Items not checked")
    if not lead.gmail_sent_checked:
        reasons.append("Gmail Sent Items not checked")
    if lead.prior_account_contacted:
        reasons.append("account previously contacted")
    if not lead.route_verified:
        reasons.append("contact/distribution route not verified")
    if lead.channel == "cold_email" and country_key in DENMARK_CODES:
        reasons.append("Danish-domiciled organisations are not cold-emailed")

    return LeadDecision(
        account_name=lead.account_name,
        eligible=not reasons,
        reasons=tuple(reasons),
    )


def evaluate_leads(rows: list[dict[str, object]]) -> dict[str, object]:
    decisions = [evaluate_lead(LeadCandidate.from_dict(row)) for row in rows]
    eligible = [item for item in decisions if item.eligible]
    return {
        "schema_version": "1.0",
        "max_daily_sends": MAX_DAILY_SENDS,
        "eligible_count": len(eligible),
        "sendable_today": min(len(eligible), MAX_DAILY_SENDS),
        "decisions": [
            {
                "account_name": item.account_name,
                "eligible": item.eligible,
                "reasons": list(item.reasons),
            }
            for item in decisions
        ],
    }


def load_swarm(path: str | Path) -> SalesSwarm:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("sales swarm file must be a JSON object")
    return SalesSwarm.from_dict(raw)


def load_leads(path: str | Path) -> list[dict[str, object]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
        raise TypeError("lead file must be a JSON array of objects")
    return raw
