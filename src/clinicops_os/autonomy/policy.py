"""Action policy for the Tier-0 autonomy layer.

``decide(action, context)`` answers one question: may an unattended job take
this action now, must it park the action for Ali, or is the action denied?
The answer is derived from ``autonomy/rules.json`` (tier lists, standing
caps, jurisdiction rules) and is fail-closed: unknown actions are denied.

Tier semantics
--------------
* Tier 0 — autonomous: allowed.
* Tier 1 — autonomous within standing orders: allowed only while the tier is
  enabled in the rules; otherwise parked exactly like Tier 2.
* Tier 2 — prepared and parked: parked unless ``human_approved`` is true.
* Tier 3 — never automated: denied even when ``human_approved`` is true,
  because those actions are performed by Ali himself, not by automation.

Cross-cutting rules (evaluated before tier permissions):
* a HALT in the context denies everything;
* a cold email or cold draft to a Danish-domiciled recipient is denied;
* a cold send beyond the daily cap or above the sub-batch size is denied;
* a post beyond the weekly LinkedIn cap is denied;
* German and Austrian cold emails are parked with the legal basis named.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from typing import Any

from .rules import RulesError, load_rules

DENMARK_ALIASES = {"dk", "denmark", "danmark", "dnk"}
COUNTRY_ALIASES = {
    "de": "DE",
    "germany": "DE",
    "deutschland": "DE",
    "deu": "DE",
    "at": "AT",
    "austria": "AT",
    "österreich": "AT",
    "aut": "AT",
}
COLD_SEND_ACTIONS = {"cold_email", "send_email", "send_followup_within_standing_order"}
COLD_DRAFT_ACTIONS = {"draft_email"}
COLD_DM_ACTIONS = {"send_dm"}
POST_ACTIONS = {"publish_post"}
UNKNOWN_TIER = 3


@dataclass(frozen=True)
class Decision:
    allow: bool
    tier: int
    reason: str
    park: bool

    @property
    def verdict(self) -> str:
        if self.allow:
            return "ALLOW"
        return "PARK" if self.park else "DENY"

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["verdict"] = self.verdict
        return data


def normalise_action(action: str) -> str:
    return str(action).strip().lower().replace("-", "_").replace(" ", "_")


def normalise_country(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    if text in DENMARK_ALIASES:
        return "DK"
    if text in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[text]
    return text.upper()


def action_tiers(rules: dict[str, Any]) -> dict[str, int]:
    """Map every classified action to its tier number."""
    mapping: dict[str, int] = {}
    for tier_key, tier in rules["tiers"].items():
        for list_key in ("allow", "deny", "park"):
            for action in tier.get(list_key, []):
                mapping[normalise_action(action)] = int(tier_key)
    return mapping


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _as_int(value: object, name: str) -> int:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, not a boolean")
    try:
        number = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer, got {value!r}") from exc
    if number < 0:
        raise ValueError(f"{name} must not be negative")
    return number


def decide(
    action: str,
    context: dict[str, Any] | None = None,
    rules: dict[str, Any] | None = None,
) -> Decision:
    """Decide whether ``action`` is allowed, parked or denied in ``context``.

    Recognised context keys: ``recipient_country``, ``is_cold``,
    ``daily_sends_so_far``, ``weekly_posts_so_far``, ``batch_size``,
    ``human_approved``, ``halted``.
    """
    ctx = dict(context or {})
    document = rules if rules is not None else load_rules()
    name = normalise_action(action)
    tiers = action_tiers(document)
    tier = tiers.get(name, UNKNOWN_TIER)
    human_approved = _as_bool(ctx.get("human_approved", False))

    if _as_bool(ctx.get("halted", False)):
        return Decision(False, tier, "HALT active — every action is denied", False)

    if name not in tiers:
        return Decision(
            False,
            UNKNOWN_TIER,
            f"unknown action {name!r} — unclassified actions are denied (fail closed) "
            "until Ali classifies them in autonomy/rules.json",
            False,
        )

    if tier == 3:
        return Decision(
            False,
            3,
            f"{name} is Tier 3 (never automated); it is done by Ali himself and a "
            "human_approved flag does not release it",
            False,
        )

    try:
        cross = _cross_cutting(name, ctx, document)
    except (TypeError, ValueError) as exc:
        return Decision(False, tier, f"invalid context: {exc}", False)
    if cross is not None:
        return cross

    tier_rules = document["tiers"][str(tier)]
    if tier == 0:
        return Decision(True, 0, f"{name} is Tier 0 (autonomous)", False)

    if tier == 1:
        if _as_bool(tier_rules.get("enabled", False)):
            return Decision(
                True, 1, f"{name} is Tier 1 and the tier is enabled (standing order)", False
            )
        if human_approved:
            return Decision(
                True, 1, f"{name} is Tier 1 (tier not enabled) released by human approval", False
            )
        return Decision(
            False,
            1,
            f"{name} is Tier 1 but Tier 1 is not enabled — parked for Ali",
            True,
        )

    # Tier 2: prepared and parked.
    suffix = _jurisdiction_note(name, ctx, document)
    if human_approved:
        return Decision(
            True, 2, f"{name} is Tier 2 released by human approval{suffix}", False
        )
    return Decision(
        False, 2, f"{name} is Tier 2 — prepared and parked for Ali{suffix}", True
    )


def _is_cold(name: str, ctx: dict[str, Any]) -> bool:
    if name == "cold_email":
        return True
    return _as_bool(ctx.get("is_cold", False))


def _cross_cutting(
    name: str, ctx: dict[str, Any], rules: dict[str, Any]
) -> Decision | None:
    country = normalise_country(ctx.get("recipient_country"))
    cold = _is_cold(name, ctx)
    tier = action_tiers(rules)[name]

    if cold and country == "DK" and name in (
        COLD_SEND_ACTIONS | COLD_DRAFT_ACTIONS | COLD_DM_ACTIONS
    ):
        return Decision(
            False,
            tier,
            "Danish-domiciled organisations are never cold-emailed or cold-messaged "
            "under any framing (public posting only)",
            False,
        )

    caps = rules["standing_caps"]
    if cold and name in COLD_SEND_ACTIONS:
        cold_caps = caps["cold_email"]
        cap = int(cold_caps["daily_cap"])
        sent = _as_int(ctx.get("daily_sends_so_far", 0), "daily_sends_so_far")
        if sent >= cap:
            return Decision(
                False,
                tier,
                f"daily cold-email cap reached ({sent}/{cap}); the cap is a ceiling, "
                "not a target",
                False,
            )
        if "batch_size" in ctx:
            batch = _as_int(ctx["batch_size"], "batch_size")
            sub_batch = int(cold_caps["sub_batch_size"])
            if batch > sub_batch:
                return Decision(
                    False,
                    tier,
                    f"batch of {batch} exceeds the sub-batch size of {sub_batch} "
                    "(NDR check between sub-batches)",
                    False,
                )

    if name in POST_ACTIONS and "weekly_posts_so_far" in ctx:
        posted = _as_int(ctx["weekly_posts_so_far"], "weekly_posts_so_far")
        limit = int(caps["linkedin"]["posts_per_week_max"])
        if posted >= limit:
            return Decision(
                False, tier, f"weekly LinkedIn post cap reached ({posted}/{limit})", False
            )

    return None


def _jurisdiction_note(name: str, ctx: dict[str, Any], rules: dict[str, Any]) -> str:
    if name not in COLD_SEND_ACTIONS or not _is_cold(name, ctx):
        return ""
    country = normalise_country(ctx.get("recipient_country"))
    entry = rules["jurisdictions"].get(country or "", {})
    basis = entry.get("legal_basis")
    if basis:
        return f" ({country}: {basis} applies)"
    return ""


# --- CLI -------------------------------------------------------------------

SELFTEST_CASES: tuple[tuple[str, dict[str, Any], str], ...] = (
    ("research", {}, "ALLOW"),
    ("draft_email", {}, "ALLOW"),
    ("crm_read", {}, "ALLOW"),
    ("backup_write", {}, "ALLOW"),
    ("open_pr", {}, "ALLOW"),
    ("create_calendar_event", {}, "ALLOW"),
    ("send_email", {}, "PARK"),
    ("send_email", {"human_approved": True}, "ALLOW"),
    ("publish_post", {}, "PARK"),
    ("publish_post", {"human_approved": True, "weekly_posts_so_far": 3}, "DENY"),
    ("cold_email", {"recipient_country": "DK"}, "DENY"),
    ("cold_email", {"recipient_country": "Denmark", "human_approved": True}, "DENY"),
    ("draft_email", {"recipient_country": "DK", "is_cold": True}, "DENY"),
    ("cold_email", {"recipient_country": "SE"}, "PARK"),
    ("cold_email", {"recipient_country": "SE", "human_approved": True}, "ALLOW"),
    ("cold_email", {"recipient_country": "SE", "daily_sends_so_far": 50}, "DENY"),
    (
        "cold_email",
        {"recipient_country": "SE", "daily_sends_so_far": 50, "human_approved": True},
        "DENY",
    ),
    ("cold_email", {"recipient_country": "SE", "batch_size": 6}, "DENY"),
    ("cold_email", {"recipient_country": "DE"}, "PARK"),
    ("crm_write", {}, "PARK"),
    ("crm_write", {"human_approved": True}, "ALLOW"),
    ("payment", {"human_approved": True}, "DENY"),
    ("create_account", {"human_approved": True}, "DENY"),
    ("push_main", {"human_approved": True}, "DENY"),
    ("delete_file", {"human_approved": True}, "DENY"),
    ("solve_captcha", {"human_approved": True}, "DENY"),
    ("compliance_statement", {"human_approved": True}, "DENY"),
    ("danish_e_marketing", {"human_approved": True}, "DENY"),
    ("totally_unknown_action", {"human_approved": True}, "DENY"),
    ("research", {"halted": True}, "DENY"),
)


def run_selftest(rules: dict[str, Any] | None = None) -> list[str]:
    """Run the built-in policy assertions; return a list of failure messages."""
    document = rules if rules is not None else load_rules()
    failures: list[str] = []
    for action, context, expected in SELFTEST_CASES:
        decision = decide(action, context, document)
        if decision.verdict != expected:
            failures.append(
                f"{action} {json.dumps(context, sort_keys=True)}: expected {expected}, "
                f"got {decision.verdict} ({decision.reason})"
            )
    return failures


def _parse_kv(pairs: list[str]) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"context arguments must be key=value, got {pair!r}")
        key, raw = pair.split("=", 1)
        value: Any = raw
        low = raw.strip().lower()
        if low in {"true", "false"}:
            value = low == "true"
        elif raw.strip().lstrip("-").isdigit():
            value = int(raw)
        context[key.strip()] = value
    return context


USAGE = (
    "usage:\n"
    "  clinicops-autonomy-policy selftest [--rules PATH]\n"
    "  clinicops-autonomy-policy decide <action> [key=value ...] [--rules PATH] [--json]\n"
    "exit codes for decide: 0 allow, 2 deny, 3 park"
)


def _extract_option(argv: list[str], flag: str) -> tuple[list[str], str | None]:
    if flag not in argv:
        return argv, None
    index = argv.index(flag)
    if index + 1 >= len(argv):
        raise SystemExit(f"{flag} requires a value")
    value = argv[index + 1]
    return argv[:index] + argv[index + 2 :], value


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    args, rules_arg = _extract_option(args, "--rules")
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    if not args:
        print(USAGE)
        return 2
    try:
        document = load_rules(rules_arg)
    except RulesError as exc:
        print(f"error: {exc}")
        return 2

    command = args[0]
    if command == "selftest":
        failures = run_selftest(document)
        if failures:
            print(f"policy selftest: {len(failures)} failure(s)")
            for failure in failures:
                print(f"  FAIL {failure}")
            return 1
        print(f"policy selftest: {len(SELFTEST_CASES)} cases OK")
        return 0

    if command == "decide":
        if len(args) < 2:
            print(USAGE)
            return 2
        decision = decide(args[1], _parse_kv(args[2:]), document)
        if as_json:
            print(json.dumps(decision.to_dict(), indent=2))
        else:
            print(f"{decision.verdict} tier={decision.tier} — {decision.reason}")
        if decision.allow:
            return 0
        return 3 if decision.park else 2

    print(USAGE)
    return 2


def policy_cli() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
