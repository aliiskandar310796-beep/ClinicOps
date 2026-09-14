from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

COMMERCIAL_STAGES = tuple(f"E{index}" for index in range(10))
EVENT_KINDS = {
    "market-budget-signal",
    "buyer-response",
    "pain-confirmation",
    "commercial-commitment",
    "activation",
    "accepted-delivery",
    "payment",
    "expansion",
}
MIN_STAGE_BY_KIND = {
    "market-budget-signal": 1,
    "buyer-response": 4,
    "pain-confirmation": 5,
    "commercial-commitment": 6,
    "activation": 7,
    "accepted-delivery": 8,
    "payment": 8,
    "expansion": 9,
}
DIRECT_BUYER_KINDS = EVENT_KINDS - {"market-budget-signal"}


def _required_string(row: dict[str, object], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _optional_string(row: dict[str, object], key: str) -> str | None:
    value = row.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string or null")
    value = value.strip()
    return value or None


def _optional_number(row: dict[str, object], key: str) -> float | None:
    value = row.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{key} must be a number or null")
    return float(value)


def _required_int(row: dict[str, object], key: str) -> int:
    value = row.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{key} must be an integer")
    if value < 0:
        raise ValueError(f"{key} must be >= 0")
    return value


def _required_number(row: dict[str, object], key: str) -> float:
    value = row.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{key} must be a number")
    return float(value)


def _string_tuple(row: dict[str, object], key: str) -> tuple[str, ...]:
    value = row.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"{key} must be a list of strings")
    return tuple(item.strip() for item in value if item.strip())


@dataclass(frozen=True)
class EconomicThresholds:
    min_qualified_conversations: int
    min_pain_confirmations: int
    min_commitments: int
    min_paid_buyers: int
    min_paid_buyers_for_repeatability: int
    min_contribution_before_labor_eur: float
    min_revenue_per_delivery_hour_eur: float | None

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> EconomicThresholds:
        if not isinstance(row, dict):
            raise TypeError("thresholds must be a JSON object")
        return cls(
            min_qualified_conversations=_required_int(row, "min_qualified_conversations"),
            min_pain_confirmations=_required_int(row, "min_pain_confirmations"),
            min_commitments=_required_int(row, "min_commitments"),
            min_paid_buyers=_required_int(row, "min_paid_buyers"),
            min_paid_buyers_for_repeatability=_required_int(
                row, "min_paid_buyers_for_repeatability"
            ),
            min_contribution_before_labor_eur=_required_number(
                row, "min_contribution_before_labor_eur"
            ),
            min_revenue_per_delivery_hour_eur=_optional_number(
                row, "min_revenue_per_delivery_hour_eur"
            ),
        )


@dataclass(frozen=True)
class EconomicEvent:
    event_id: str
    kind: str
    commercial_stage: str
    buyer_key: str | None
    evidence_refs: tuple[str, ...]
    amount_eur: float | None
    direct_cash_cost_eur: float | None
    delivery_hours: float | None
    notes: str | None

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> EconomicEvent:
        if not isinstance(row, dict):
            raise TypeError("economic event must be a JSON object")

        kind = _required_string(row, "kind")
        if kind not in EVENT_KINDS:
            known = ", ".join(sorted(EVENT_KINDS))
            raise ValueError(f"unknown kind '{kind}'; expected one of: {known}")

        commercial_stage = _required_string(row, "commercial_stage").upper()
        if commercial_stage not in COMMERCIAL_STAGES:
            known = ", ".join(COMMERCIAL_STAGES)
            raise ValueError(
                f"unknown commercial_stage '{commercial_stage}'; expected one of: {known}"
            )

        amount = _optional_number(row, "amount_eur")
        direct_cost = _optional_number(row, "direct_cash_cost_eur")
        delivery_hours = _optional_number(row, "delivery_hours")
        if amount is not None and amount < 0:
            raise ValueError("amount_eur must be >= 0")
        if direct_cost is not None and direct_cost < 0:
            raise ValueError("direct_cash_cost_eur must be >= 0")
        if delivery_hours is not None and delivery_hours <= 0:
            raise ValueError("delivery_hours must be > 0 when supplied")

        return cls(
            event_id=_required_string(row, "event_id"),
            kind=kind,
            commercial_stage=commercial_stage,
            buyer_key=_optional_string(row, "buyer_key"),
            evidence_refs=_string_tuple(row, "evidence_refs"),
            amount_eur=amount,
            direct_cash_cost_eur=direct_cost,
            delivery_hours=delivery_hours,
            notes=_optional_string(row, "notes"),
        )

    @property
    def stage_number(self) -> int:
        return int(self.commercial_stage[1:])


@dataclass(frozen=True)
class EconomicLedger:
    schema_version: str
    offer_id: str
    thresholds: EconomicThresholds
    events: tuple[EconomicEvent, ...]

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> EconomicLedger:
        if not isinstance(row, dict):
            raise TypeError("economic ledger must be a JSON object")
        schema_version = _required_string(row, "schema_version")
        if schema_version != "1.0":
            raise ValueError("schema_version must be 1.0")
        raw_events = row.get("events")
        if not isinstance(raw_events, list):
            raise TypeError("events must be a list")
        events = tuple(EconomicEvent.from_dict(item) for item in raw_events)
        event_ids = [event.event_id for event in events]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("event_id values must be unique within a ledger")
        thresholds = row.get("thresholds")
        if not isinstance(thresholds, dict):
            raise TypeError("thresholds must be a JSON object")
        return cls(
            schema_version=schema_version,
            offer_id=_required_string(row, "offer_id"),
            thresholds=EconomicThresholds.from_dict(thresholds),
            events=events,
        )


@dataclass(frozen=True)
class EconomicFinding:
    event_id: str
    severity: str
    message: str


@dataclass(frozen=True)
class EconomicEvaluation:
    offer_id: str
    control_pass: bool
    exp001_pass: bool
    initial_economic_proof: bool
    repeatability_proof: bool
    highest_commercial_stage: str
    market_budget_signals: int
    qualified_buyers: int
    pain_confirmed_buyers: int
    commitment_buyers: int
    activated_buyers: int
    accepted_delivery_buyers: int
    paid_buyers: int
    expansion_buyers: int
    paid_revenue_eur: float
    direct_cash_cost_eur: float
    contribution_before_labor_eur: float
    paid_delivery_hours: float
    revenue_per_delivery_hour_eur: float | None
    findings: tuple[EconomicFinding, ...]


def evaluate_economic_ledger(ledger: EconomicLedger) -> EconomicEvaluation:
    findings: list[EconomicFinding] = []

    for event in ledger.events:
        minimum_stage = MIN_STAGE_BY_KIND[event.kind]
        if event.stage_number < minimum_stage:
            findings.append(
                EconomicFinding(
                    event.event_id,
                    "error",
                    f"{event.kind} requires at least E{minimum_stage}",
                )
            )

        if event.kind in DIRECT_BUYER_KINDS and not event.buyer_key:
            findings.append(
                EconomicFinding(
                    event.event_id,
                    "error",
                    f"{event.kind} requires a private stable buyer_key",
                )
            )

        if event.stage_number >= 4 and not event.evidence_refs:
            findings.append(
                EconomicFinding(
                    event.event_id,
                    "error",
                    f"{event.commercial_stage} requires private external evidence refs",
                )
            )

        if event.kind == "payment":
            if event.amount_eur is None or event.amount_eur <= 0:
                findings.append(
                    EconomicFinding(
                        event.event_id,
                        "error",
                        "payment requires amount_eur > 0",
                    )
                )
            if event.direct_cash_cost_eur is None:
                findings.append(
                    EconomicFinding(
                        event.event_id,
                        "error",
                        "payment requires direct_cash_cost_eur for unit-economics learning",
                    )
                )

        if event.delivery_hours is not None and event.kind not in {
            "accepted-delivery",
            "payment",
            "expansion",
        }:
            findings.append(
                EconomicFinding(
                    event.event_id,
                    "warning",
                    "delivery_hours is normally expected only on delivery/payment/expansion evidence",
                )
            )

    def buyers_for(kinds: set[str]) -> set[str]:
        return {
            event.buyer_key
            for event in ledger.events
            if event.kind in kinds and event.buyer_key is not None
        }

    market_budget_signals = sum(
        event.kind == "market-budget-signal" for event in ledger.events
    )
    qualified_buyers = buyers_for(DIRECT_BUYER_KINDS)
    pain_buyers = buyers_for({"pain-confirmation"})
    commitment_buyers = buyers_for({"commercial-commitment"})
    activated_buyers = buyers_for({"activation"})
    accepted_delivery_buyers = buyers_for({"accepted-delivery"})
    payment_events = [event for event in ledger.events if event.kind == "payment"]
    paid_buyers = buyers_for({"payment"})
    expansion_buyers = buyers_for({"expansion"})

    paid_revenue = sum(event.amount_eur or 0.0 for event in payment_events)
    direct_cost = sum(event.direct_cash_cost_eur or 0.0 for event in payment_events)
    contribution = paid_revenue - direct_cost
    paid_hours = sum(event.delivery_hours or 0.0 for event in payment_events)
    revenue_per_hour = paid_revenue / paid_hours if paid_hours > 0 else None

    highest_stage_number = max((event.stage_number for event in ledger.events), default=0)
    highest_stage = f"E{highest_stage_number}"
    thresholds = ledger.thresholds

    exp001_pass = (
        len(qualified_buyers) >= thresholds.min_qualified_conversations
        and len(pain_buyers) >= thresholds.min_pain_confirmations
        and len(commitment_buyers) >= thresholds.min_commitments
    )

    hours_requirement_ok = True
    if paid_buyers:
        paid_buyers_with_hours = {
            event.buyer_key
            for event in payment_events
            if event.buyer_key is not None and event.delivery_hours is not None
        }
        hours_requirement_ok = paid_buyers.issubset(paid_buyers_with_hours)
        if not hours_requirement_ok:
            findings.append(
                EconomicFinding(
                    "ledger",
                    "warning",
                    "not every paid buyer has delivery_hours captured; revenue/hour remains incomplete",
                )
            )

    revenue_hour_ok = True
    if thresholds.min_revenue_per_delivery_hour_eur is not None:
        revenue_hour_ok = (
            revenue_per_hour is not None
            and revenue_per_hour >= thresholds.min_revenue_per_delivery_hour_eur
        )

    initial_economic_proof = (
        exp001_pass
        and len(paid_buyers) >= thresholds.min_paid_buyers
        and contribution >= thresholds.min_contribution_before_labor_eur
        and hours_requirement_ok
        and revenue_hour_ok
    )

    repeatability_proof = initial_economic_proof and (
        len(paid_buyers) >= thresholds.min_paid_buyers_for_repeatability
        or len(expansion_buyers) >= 1
    )

    control_pass = not any(item.severity == "error" for item in findings)

    return EconomicEvaluation(
        offer_id=ledger.offer_id,
        control_pass=control_pass,
        exp001_pass=exp001_pass,
        initial_economic_proof=initial_economic_proof,
        repeatability_proof=repeatability_proof,
        highest_commercial_stage=highest_stage,
        market_budget_signals=market_budget_signals,
        qualified_buyers=len(qualified_buyers),
        pain_confirmed_buyers=len(pain_buyers),
        commitment_buyers=len(commitment_buyers),
        activated_buyers=len(activated_buyers),
        accepted_delivery_buyers=len(accepted_delivery_buyers),
        paid_buyers=len(paid_buyers),
        expansion_buyers=len(expansion_buyers),
        paid_revenue_eur=paid_revenue,
        direct_cash_cost_eur=direct_cost,
        contribution_before_labor_eur=contribution,
        paid_delivery_hours=paid_hours,
        revenue_per_delivery_hour_eur=revenue_per_hour,
        findings=tuple(findings),
    )


def load_economic_ledger(path: str | Path) -> EconomicLedger:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return EconomicLedger.from_dict(raw)


def render_evaluation(evaluation: EconomicEvaluation) -> str:
    payload = {
        "schema_version": "1.0",
        "offer_id": evaluation.offer_id,
        "control_pass": evaluation.control_pass,
        "exp001_pass": evaluation.exp001_pass,
        "initial_economic_proof": evaluation.initial_economic_proof,
        "repeatability_proof": evaluation.repeatability_proof,
        "metrics": {
            "highest_commercial_stage": evaluation.highest_commercial_stage,
            "market_budget_signals": evaluation.market_budget_signals,
            "qualified_buyers": evaluation.qualified_buyers,
            "pain_confirmed_buyers": evaluation.pain_confirmed_buyers,
            "commitment_buyers": evaluation.commitment_buyers,
            "activated_buyers": evaluation.activated_buyers,
            "accepted_delivery_buyers": evaluation.accepted_delivery_buyers,
            "paid_buyers": evaluation.paid_buyers,
            "expansion_buyers": evaluation.expansion_buyers,
            "paid_revenue_eur": round(evaluation.paid_revenue_eur, 2),
            "direct_cash_cost_eur": round(evaluation.direct_cash_cost_eur, 2),
            "contribution_before_labor_eur": round(
                evaluation.contribution_before_labor_eur, 2
            ),
            "paid_delivery_hours": round(evaluation.paid_delivery_hours, 2),
            "revenue_per_delivery_hour_eur": (
                None
                if evaluation.revenue_per_delivery_hour_eur is None
                else round(evaluation.revenue_per_delivery_hour_eur, 2)
            ),
        },
        "findings": [
            {
                "event_id": item.event_id,
                "severity": item.severity,
                "message": item.message,
            }
            for item in evaluation.findings
        ],
        "interpretation": (
            "Market-budget signals support category plausibility only. Initial economic proof "
            "requires buyer evidence, commitment, actual payment and configured unit-economics "
            "thresholds; repeatability requires multiple paid buyers or expansion."
        ),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
