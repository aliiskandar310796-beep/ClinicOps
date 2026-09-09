from __future__ import annotations

from pathlib import Path

import pytest

from clinicops_os.revenue import (
    AccountIntelligence,
    load_accounts,
    rank_accounts,
    revenue_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_unknown_signals_stay_unknown_and_limit_band() -> None:
    account = AccountIntelligence(
        company="Example Sparse Account",
        segment="manufacturer",
        offer_fit=5,
    )

    assert account.budget_signal is None
    assert account.priority_score == pytest.approx(100.0)
    assert account.score_coverage == pytest.approx(20.0)
    assert account.priority_band == "LEARN"
    assert account.next_experiment == "RESEARCH"


def test_partner_account_routes_to_partner_conversation() -> None:
    account = AccountIntelligence(
        company="Example AR",
        segment="authorised_representative",
        evidence_strength=4,
        urgency=4,
        offer_fit=5,
        partner_leverage=5,
        access_strength=3,
        budget_signal=2,
        reuse_potential=5,
    )

    assert account.priority_band == "HOT"
    assert account.next_experiment == "PARTNER CONVERSATION"


def test_manufacturer_with_budget_and_access_routes_to_pilot() -> None:
    account = AccountIntelligence(
        company="Example Manufacturer",
        segment="manufacturer",
        evidence_strength=4,
        urgency=5,
        offer_fit=5,
        partner_leverage=2,
        access_strength=3,
        budget_signal=4,
        reuse_potential=4,
    )

    assert account.priority_band == "HOT"
    assert account.next_experiment == "PILOT"


def test_invalid_segment_is_rejected() -> None:
    with pytest.raises(ValueError, match="segment must be one of"):
        AccountIntelligence(company="Bad", segment="hospital")


def test_sanitized_example_loads_and_ranks_deterministically() -> None:
    accounts = load_accounts(ROOT / "examples" / "revenue_accounts.csv")
    ranked = rank_accounts(accounts)

    assert len(ranked) == 4
    assert ranked[0].company == "Example AR Partner"
    assert ranked[-1].company == "Example Early Signal"

    payload = revenue_payload(accounts)
    assert payload["schema_version"] == "1.0"
    assert payload["summary"]["accounts"] == 4
    assert "not a regulatory" in payload["interpretation"]


def test_scores_outside_range_are_rejected() -> None:
    with pytest.raises(ValueError, match="urgency must be between 0 and 5"):
        AccountIntelligence(company="Bad Score", segment="manufacturer", urgency=6)
