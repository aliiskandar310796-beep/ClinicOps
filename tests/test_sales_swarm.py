from __future__ import annotations

import pytest

from clinicops_os.sales_swarm import (
    EXPECTED_CELL_COUNT,
    EXPECTED_LEAD_TARGET,
    LeadCandidate,
    SalesSwarm,
    evaluate_lead,
    evaluate_leads,
    validate_swarm,
)


def _cell(index: int) -> dict[str, object]:
    return {
        "cell_id": f"S{index:02d}",
        "market": f"Market {index}",
        "buyer": "RA/QA leader",
        "channel": "cold_email" if index % 2 else "partner_intro",
        "lead_quota": 3,
        "outcome": "3 net-new qualified accounts",
    }


def test_swarm_contract_requires_33_cells_and_99_leads() -> None:
    swarm = SalesSwarm.from_dict({"cells": [_cell(i) for i in range(1, 34)]})
    assert len(swarm.cells) == EXPECTED_CELL_COUNT
    assert sum(cell.lead_quota for cell in swarm.cells) == EXPECTED_LEAD_TARGET
    assert validate_swarm(swarm) == []


def test_swarm_rejects_duplicate_cell_ids() -> None:
    cells = [_cell(i) for i in range(1, 34)]
    cells[-1]["cell_id"] = "S01"
    with pytest.raises(ValueError, match="unique"):
        SalesSwarm.from_dict({"cells": cells})


def test_lead_gate_fails_closed_without_dedupe_checks() -> None:
    lead = LeadCandidate.from_dict(
        {
            "account_name": "Net New MedTech",
            "country": "US",
            "channel": "cold_email",
            "master_log_checked": False,
            "outlook_sent_checked": True,
            "gmail_sent_checked": True,
            "prior_account_contacted": False,
            "route_verified": True,
        }
    )
    decision = evaluate_lead(lead)
    assert not decision.eligible
    assert "private outreach master not checked" in decision.reasons


def test_lead_gate_suppresses_prior_account_and_denmark_cold_email() -> None:
    lead = LeadCandidate.from_dict(
        {
            "account_name": "Previously Contacted A/S",
            "country": "DK",
            "channel": "cold_email",
            "master_log_checked": True,
            "outlook_sent_checked": True,
            "gmail_sent_checked": True,
            "prior_account_contacted": True,
            "route_verified": True,
        }
    )
    decision = evaluate_lead(lead)
    assert not decision.eligible
    assert "account previously contacted" in decision.reasons
    assert "Danish-domiciled organisations are not cold-emailed" in decision.reasons


def test_permanent_do_not_contact_accounts_are_blocked() -> None:
    lead = LeadCandidate.from_dict(
        {
            "account_name": "PrimeVigilance",
            "country": "GB",
            "channel": "partner_intro",
            "master_log_checked": True,
            "outlook_sent_checked": True,
            "gmail_sent_checked": True,
            "prior_account_contacted": False,
            "route_verified": True,
        }
    )
    decision = evaluate_lead(lead)
    assert not decision.eligible
    assert "permanent do-not-contact account" in decision.reasons


def test_daily_send_cap_is_15() -> None:
    rows = [
        {
            "account_name": f"New Account {i}",
            "country": "US",
            "channel": "cold_email",
            "master_log_checked": True,
            "outlook_sent_checked": True,
            "gmail_sent_checked": True,
            "prior_account_contacted": False,
            "route_verified": True,
        }
        for i in range(20)
    ]
    payload = evaluate_leads(rows)
    assert payload["eligible_count"] == 20
    assert payload["sendable_today"] == 15
