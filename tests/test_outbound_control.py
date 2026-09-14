from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from clinicops_os.outbound_control import (
    OutboundCandidate,
    OutboundEvent,
    OutboundSnapshot,
    ReasonCode,
    evaluate_outbound,
)

DAY = date(2026, 9, 14)
NOW = datetime(2026, 9, 14, 18, 0, tzinfo=timezone.utc)


def snapshot(
    *events: OutboundEvent,
    complete: bool = True,
    pending: int = 0,
    age_minutes: int = 0,
) -> OutboundSnapshot:
    return OutboundSnapshot(
        snapshot_at=NOW - timedelta(minutes=age_minutes),
        events=tuple(events),
        complete=complete,
        pending_cold_reservations=pending,
    )


def cold_event(domain: str) -> OutboundEvent:
    return OutboundEvent(sent_on=DAY, relationship="cold", recipient_domain=domain)


def test_allows_clean_cold_candidate_with_company_capacity() -> None:
    result = evaluate_outbound(
        OutboundCandidate(
            relationship="cold",
            recipient_domain="example.com",
            organization_name="Example Health",
            destination_country_code="GB",
        ),
        snapshot(),
        company_day=DAY,
        now=NOW,
    )
    assert result.allowed is True
    assert result.reason_codes == (ReasonCode.ALLOW,)
    assert result.cold_slots_remaining == 15


def test_company_daily_limit_counts_pending_reservations() -> None:
    events = tuple(cold_event(f"company-{i}.com") for i in range(14))
    result = evaluate_outbound(
        OutboundCandidate(
            relationship="cold",
            recipient_domain="new-company.com",
            destination_country_code="US",
        ),
        snapshot(*events, pending=1),
        company_day=DAY,
        now=NOW,
    )
    assert result.allowed is False
    assert ReasonCode.COLD_DAILY_LIMIT in result.reason_codes
    assert result.cold_slots_remaining == 0


def test_cold_denmark_and_unknown_jurisdiction_fail_closed() -> None:
    denmark = evaluate_outbound(
        OutboundCandidate(
            relationship="cold",
            recipient_domain="example.dk",
            destination_country_code="DK",
        ),
        snapshot(),
        company_day=DAY,
        now=NOW,
    )
    unknown = evaluate_outbound(
        OutboundCandidate(
            relationship="cold",
            recipient_domain="example.org",
            destination_country_code=None,
        ),
        snapshot(),
        company_day=DAY,
        now=NOW,
    )
    assert ReasonCode.DENMARK_COLD_BLOCK in denmark.reason_codes
    assert ReasonCode.COLD_COUNTRY_UNKNOWN in unknown.reason_codes


def test_prior_domain_contact_and_permanent_suppression_block_send() -> None:
    result = evaluate_outbound(
        OutboundCandidate(
            relationship="cold",
            recipient_domain="ergomedgroup.com",
            organization_name="Ergomed Group",
            destination_country_code="GB",
        ),
        snapshot(cold_event("ergomedgroup.com")),
        company_day=DAY,
        now=NOW,
    )
    assert result.allowed is False
    assert ReasonCode.PERMANENT_SUPPRESSION in result.reason_codes
    assert ReasonCode.PRIOR_DOMAIN_CONTACT in result.reason_codes


def test_incomplete_or_stale_company_state_blocks_execution() -> None:
    incomplete = evaluate_outbound(
        OutboundCandidate(relationship="warm", organization_name="Partner"),
        snapshot(complete=False),
        company_day=DAY,
        now=NOW,
    )
    stale = evaluate_outbound(
        OutboundCandidate(relationship="transactional", organization_name="Client"),
        snapshot(age_minutes=6),
        company_day=DAY,
        now=NOW,
    )
    assert ReasonCode.INCOMPLETE_SNAPSHOT in incomplete.reason_codes
    assert ReasonCode.STALE_SNAPSHOT in stale.reason_codes
