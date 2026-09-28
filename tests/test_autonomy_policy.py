from __future__ import annotations

import copy
from pathlib import Path

import pytest

from clinicops_os.autonomy import policy
from clinicops_os.autonomy.policy import Decision, decide, run_selftest
from clinicops_os.autonomy.rules import load_rules

ROOT = Path(__file__).resolve().parents[1]
RULES = load_rules(ROOT / "autonomy" / "rules.json")


def d(action: str, **context: object) -> Decision:
    return decide(action, context, RULES)


@pytest.mark.parametrize(
    "action",
    ["research", "draft_email", "crm_read", "backup_write", "open_pr", "create_calendar_event"],
)
def test_tier0_actions_are_allowed(action: str) -> None:
    decision = d(action)
    assert decision.allow and not decision.park
    assert decision.tier == 0


def test_send_email_is_parked_unless_human_approved() -> None:
    parked = d("send_email")
    assert not parked.allow and parked.park and parked.tier == 2
    released = d("send_email", human_approved=True)
    assert released.allow and not released.park and released.tier == 2


def test_publish_post_is_parked_and_respects_weekly_cap() -> None:
    assert d("publish_post").park
    assert d("publish_post", human_approved=True).allow
    capped = d("publish_post", human_approved=True, weekly_posts_so_far=3)
    assert not capped.allow and not capped.park
    assert "weekly LinkedIn post cap" in capped.reason


@pytest.mark.parametrize("country", ["DK", "dk", "Denmark", "Danmark", "DNK"])
def test_cold_email_to_denmark_is_denied_even_with_human_approval(country: str) -> None:
    decision = d("cold_email", recipient_country=country, human_approved=True)
    assert not decision.allow and not decision.park
    assert "Danish-domiciled" in decision.reason


def test_cold_draft_and_cold_dm_to_denmark_are_denied() -> None:
    draft = d("draft_email", recipient_country="DK", is_cold=True)
    assert not draft.allow and not draft.park
    dm = d("send_dm", recipient_country="DK", is_cold=True)
    assert not dm.allow and not dm.park
    warm_send = d("send_email", recipient_country="DK", is_cold=False)
    assert warm_send.park, "a warm reply to a Danish contact is parked like any send, not denied"


def test_cold_email_elsewhere_is_parked_then_released_by_human() -> None:
    parked = d("cold_email", recipient_country="SE")
    assert parked.park and parked.tier == 2
    assert d("cold_email", recipient_country="SE", human_approved=True).allow


def test_daily_cap_is_a_ceiling_that_human_approval_cannot_lift() -> None:
    under = d("cold_email", recipient_country="SE", daily_sends_so_far=49)
    assert under.park
    at_cap = d("cold_email", recipient_country="SE", daily_sends_so_far=50)
    assert not at_cap.allow and not at_cap.park
    assert "ceiling" in at_cap.reason
    over = d("cold_email", recipient_country="SE", daily_sends_so_far=51, human_approved=True)
    assert not over.allow and not over.park
    warm = d("send_email", is_cold=True, daily_sends_so_far=50)
    assert not warm.allow and not warm.park, "cold flag on send_email uses the same cap"


def test_sub_batch_above_five_is_denied() -> None:
    assert d("cold_email", recipient_country="SE", batch_size=5).park
    denied = d("cold_email", recipient_country="SE", batch_size=6)
    assert not denied.allow and not denied.park
    assert "sub-batch" in denied.reason


def test_german_and_austrian_cold_email_name_the_legal_basis() -> None:
    de = d("cold_email", recipient_country="Germany")
    assert de.park and "UWG §7" in de.reason
    at = d("cold_email", recipient_country="AT", human_approved=True)
    assert at.allow and "TKG §174" in at.reason


@pytest.mark.parametrize(
    "action",
    [
        "payment",
        "create_account",
        "push_main",
        "delete_file",
        "enter_credentials",
        "solve_captcha",
        "sign_contract",
        "compliance_statement",
        "danish_e_marketing",
        "change_github_settings",
        "rewrite_history",
    ],
)
def test_tier3_actions_are_denied_even_with_human_approval(action: str) -> None:
    decision = d(action, human_approved=True)
    assert not decision.allow and not decision.park
    assert decision.tier == 3
    assert "Ali himself" in decision.reason


def test_unknown_action_fails_closed() -> None:
    decision = d("launch_rocket", human_approved=True)
    assert not decision.allow and not decision.park
    assert "unknown action" in decision.reason


def test_halt_denies_everything() -> None:
    decision = d("research", halted=True)
    assert not decision.allow and "HALT" in decision.reason


def test_tier1_is_parked_until_enabled() -> None:
    parked = d("crm_write")
    assert parked.park and parked.tier == 1
    assert d("crm_write", human_approved=True).allow

    enabled_rules = copy.deepcopy(RULES)
    enabled_rules["tiers"]["1"]["enabled"] = True
    decision = decide("crm_write", {}, enabled_rules)
    assert decision.allow and "standing order" in decision.reason


def test_invalid_context_is_denied_not_crashed() -> None:
    decision = d("cold_email", recipient_country="SE", daily_sends_so_far="many")
    assert not decision.allow and "invalid context" in decision.reason


def test_action_names_are_normalised() -> None:
    assert d("Send-Email").park
    assert d("PUSH MAIN").tier == 3


def test_decision_serialises_with_verdict() -> None:
    payload = d("send_email").to_dict()
    assert payload["verdict"] == "PARK"
    assert set(payload) == {"allow", "tier", "reason", "park", "verdict"}


def test_selftest_passes_and_detects_weakened_rules() -> None:
    assert run_selftest(RULES) == []
    weakened = copy.deepcopy(RULES)
    weakened["tiers"]["3"]["deny"].remove("payment")
    weakened["tiers"]["0"]["allow"].append("payment")
    failures = run_selftest(weakened)
    assert failures and any("payment" in item for item in failures)


def test_cli_exit_codes(capsys: pytest.CaptureFixture[str]) -> None:
    rules_arg = ["--rules", str(ROOT / "autonomy" / "rules.json")]
    assert policy.main(["selftest", *rules_arg]) == 0
    assert policy.main(["decide", "research", *rules_arg]) == 0
    assert policy.main(["decide", "send_email", *rules_arg]) == 3
    assert policy.main(["decide", "payment", "human_approved=true", *rules_arg]) == 2
    assert policy.main(["decide", "cold_email", "recipient_country=DK", *rules_arg]) == 2
    assert policy.main([]) == 2
    out = capsys.readouterr().out
    assert "policy selftest" in out
    assert "DENY tier=3" in out
