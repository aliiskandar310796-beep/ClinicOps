"""Deterministic fail-closed controls for ClinicOps outbound execution.

This module does not send email or store prospect data. It evaluates a private,
runtime-supplied mailbox snapshot before an external send. The caller remains
responsible for obtaining a complete live snapshot from every ClinicOps mailbox
that may have sent company outreach.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Literal

DAILY_COLD_LIMIT = 15
SNAPSHOT_MAX_AGE = timedelta(minutes=5)
PERMANENT_SUPPRESSIONS = frozenset({"ergomed group", "primevigilance"})

Relationship = Literal["cold", "warm", "transactional"]


class ReasonCode(StrEnum):
    ALLOW = "ALLOW"
    INCOMPLETE_SNAPSHOT = "INCOMPLETE_SNAPSHOT"
    STALE_SNAPSHOT = "STALE_SNAPSHOT"
    INVALID_SNAPSHOT_TIME = "INVALID_SNAPSHOT_TIME"
    PERMANENT_SUPPRESSION = "PERMANENT_SUPPRESSION"
    COLD_COUNTRY_UNKNOWN = "COLD_COUNTRY_UNKNOWN"
    DENMARK_COLD_BLOCK = "DENMARK_COLD_BLOCK"
    COLD_DOMAIN_UNKNOWN = "COLD_DOMAIN_UNKNOWN"
    PRIOR_DOMAIN_CONTACT = "PRIOR_DOMAIN_CONTACT"
    COLD_DAILY_LIMIT = "COLD_DAILY_LIMIT"


def _norm(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def _norm_domain(value: str | None) -> str:
    domain = _norm(value)
    if domain.startswith("@"):
        domain = domain[1:]
    return domain


@dataclass(frozen=True, slots=True)
class OutboundEvent:
    """One already-sent company message represented without message content."""

    sent_on: date
    relationship: Relationship
    recipient_domain: str = ""
    organization_name: str = ""


@dataclass(frozen=True, slots=True)
class OutboundCandidate:
    """Minimal metadata needed to evaluate one proposed send."""

    relationship: Relationship
    recipient_domain: str = ""
    organization_name: str = ""
    destination_country_code: str | None = None


@dataclass(frozen=True, slots=True)
class OutboundSnapshot:
    """A live, private observation of company-wide outbound state.

    ``complete`` means the caller reconciled every mailbox/source that could
    have sent ClinicOps outreach for the company day. ``pending_cold_reservations``
    represents slots already reserved by the single-writer controller but not
    yet visible in Sent Items.
    """

    snapshot_at: datetime
    events: tuple[OutboundEvent, ...]
    complete: bool
    pending_cold_reservations: int = 0


@dataclass(frozen=True, slots=True)
class OutboundDecision:
    allowed: bool
    reason_codes: tuple[ReasonCode, ...]
    cold_sent_today: int
    pending_cold_reservations: int
    cold_slots_remaining: int


def evaluate_outbound(
    candidate: OutboundCandidate,
    snapshot: OutboundSnapshot,
    *,
    company_day: date,
    now: datetime,
    daily_cold_limit: int = DAILY_COLD_LIMIT,
    snapshot_max_age: timedelta = SNAPSHOT_MAX_AGE,
) -> OutboundDecision:
    """Evaluate a proposed send against shared ClinicOps controls.

    The function fails closed for cold outreach when live state is incomplete,
    stale, the destination jurisdiction is unknown, the organization is
    permanently suppressed, the domain has already been contacted, or the
    shared daily cold ceiling is exhausted. Warm/transactional messages do not
    consume cold quota, but permanent suppressions and snapshot integrity still
    apply.
    """

    if daily_cold_limit < 1:
        raise ValueError("daily_cold_limit must be positive")
    if snapshot.pending_cold_reservations < 0:
        raise ValueError("pending_cold_reservations cannot be negative")
    if snapshot.snapshot_at.tzinfo is None or now.tzinfo is None:
        raise ValueError("snapshot_at and now must be timezone-aware")

    cold_sent_today = sum(
        event.relationship == "cold" and event.sent_on == company_day
        for event in snapshot.events
    )
    committed = cold_sent_today + snapshot.pending_cold_reservations
    slots_remaining = max(0, daily_cold_limit - committed)
    reasons: list[ReasonCode] = []

    if not snapshot.complete:
        reasons.append(ReasonCode.INCOMPLETE_SNAPSHOT)

    age = now - snapshot.snapshot_at
    if age < timedelta(seconds=-60):
        reasons.append(ReasonCode.INVALID_SNAPSHOT_TIME)
    elif age > snapshot_max_age:
        reasons.append(ReasonCode.STALE_SNAPSHOT)

    if _norm(candidate.organization_name) in PERMANENT_SUPPRESSIONS:
        reasons.append(ReasonCode.PERMANENT_SUPPRESSION)

    if candidate.relationship == "cold":
        country = _norm(candidate.destination_country_code).upper()
        domain = _norm_domain(candidate.recipient_domain)

        if not country:
            reasons.append(ReasonCode.COLD_COUNTRY_UNKNOWN)
        elif country in {"DK", "DNK", "DENMARK"}:
            reasons.append(ReasonCode.DENMARK_COLD_BLOCK)

        if not domain:
            reasons.append(ReasonCode.COLD_DOMAIN_UNKNOWN)
        elif any(
            _norm_domain(event.recipient_domain) == domain
            for event in snapshot.events
            if event.recipient_domain
        ):
            reasons.append(ReasonCode.PRIOR_DOMAIN_CONTACT)

        if committed >= daily_cold_limit:
            reasons.append(ReasonCode.COLD_DAILY_LIMIT)

    if reasons:
        return OutboundDecision(
            allowed=False,
            reason_codes=tuple(reasons),
            cold_sent_today=cold_sent_today,
            pending_cold_reservations=snapshot.pending_cold_reservations,
            cold_slots_remaining=slots_remaining,
        )

    return OutboundDecision(
        allowed=True,
        reason_codes=(ReasonCode.ALLOW,),
        cold_sent_today=cold_sent_today,
        pending_cold_reservations=snapshot.pending_cold_reservations,
        cold_slots_remaining=slots_remaining,
    )
