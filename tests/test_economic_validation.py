from __future__ import annotations

import copy

from clinicops_os.economic_validation import EconomicLedger, evaluate_economic_ledger

BASE_LEDGER = {
    "schema_version": "1.0",
    "offer_id": "TEST-OFFER",
    "ledger_class": "real",
    "thresholds": {
        "min_qualified_conversations": 3,
        "min_pain_confirmations": 2,
        "min_commitments": 1,
        "min_paid_buyers": 1,
        "min_paid_buyers_for_repeatability": 3,
        "min_contribution_before_labor_eur": 0,
        "min_revenue_per_delivery_hour_eur": 75,
    },
    "events": [
        {
            "event_id": "B1-E4",
            "kind": "buyer-response",
            "commercial_stage": "E4",
            "buyer_key": "A",
            "evidence_refs": ["private:a"],
            "amount_eur": None,
            "direct_cash_cost_eur": None,
            "delivery_hours": None,
            "notes": None,
        },
        {
            "event_id": "B2-E4",
            "kind": "buyer-response",
            "commercial_stage": "E4",
            "buyer_key": "B",
            "evidence_refs": ["private:b"],
            "amount_eur": None,
            "direct_cash_cost_eur": None,
            "delivery_hours": None,
            "notes": None,
        },
        {
            "event_id": "B3-E4",
            "kind": "buyer-response",
            "commercial_stage": "E4",
            "buyer_key": "C",
            "evidence_refs": ["private:c"],
            "amount_eur": None,
            "direct_cash_cost_eur": None,
            "delivery_hours": None,
            "notes": None,
        },
        {
            "event_id": "B1-E5",
            "kind": "pain-confirmation",
            "commercial_stage": "E5",
            "buyer_key": "A",
            "evidence_refs": ["private:a-pain"],
            "amount_eur": None,
            "direct_cash_cost_eur": None,
            "delivery_hours": None,
            "notes": None,
        },
        {
            "event_id": "B2-E5",
            "kind": "pain-confirmation",
            "commercial_stage": "E5",
            "buyer_key": "B",
            "evidence_refs": ["private:b-pain"],
            "amount_eur": None,
            "direct_cash_cost_eur": None,
            "delivery_hours": None,
            "notes": None,
        },
        {
            "event_id": "B1-E6",
            "kind": "commercial-commitment",
            "commercial_stage": "E6",
            "buyer_key": "A",
            "evidence_refs": ["private:a-commitment"],
            "amount_eur": None,
            "direct_cash_cost_eur": None,
            "delivery_hours": None,
            "notes": None,
        },
    ],
}


def _ledger() -> dict[str, object]:
    return copy.deepcopy(BASE_LEDGER)


def test_exp001_can_pass_without_economic_transaction_proof() -> None:
    evaluation = evaluate_economic_ledger(EconomicLedger.from_dict(_ledger()))

    assert evaluation.control_pass is True
    assert evaluation.exp001_pass is True
    assert evaluation.initial_economic_proof is False
    assert evaluation.paid_buyers == 0


def test_payment_can_create_initial_economic_proof() -> None:
    row = _ledger()
    row["events"].append(
        {
            "event_id": "B1-E8P",
            "kind": "payment",
            "commercial_stage": "E8",
            "buyer_key": "A",
            "evidence_refs": ["private:a-payment"],
            "amount_eur": 900,
            "direct_cash_cost_eur": 50,
            "delivery_hours": 6,
            "notes": None,
        }
    )

    evaluation = evaluate_economic_ledger(EconomicLedger.from_dict(row))

    assert evaluation.control_pass is True
    assert evaluation.initial_economic_proof is True
    assert evaluation.repeatability_proof is False
    assert evaluation.revenue_per_delivery_hour_eur == 150


def test_payment_requires_amount_and_cost() -> None:
    row = _ledger()
    row["events"].append(
        {
            "event_id": "BAD-PAYMENT",
            "kind": "payment",
            "commercial_stage": "E8",
            "buyer_key": "A",
            "evidence_refs": ["private:a-payment"],
            "amount_eur": None,
            "direct_cash_cost_eur": None,
            "delivery_hours": 2,
            "notes": None,
        }
    )

    evaluation = evaluate_economic_ledger(EconomicLedger.from_dict(row))

    assert evaluation.control_pass is False
    assert any("amount_eur > 0" in item.message for item in evaluation.findings)
    assert any("direct_cash_cost_eur" in item.message for item in evaluation.findings)


def test_direct_buyer_event_requires_private_buyer_key() -> None:
    row = _ledger()
    row["events"][0]["buyer_key"] = None

    evaluation = evaluate_economic_ledger(EconomicLedger.from_dict(row))

    assert evaluation.control_pass is False
    assert any("buyer_key" in item.message for item in evaluation.findings)


def test_e4_plus_requires_evidence() -> None:
    row = _ledger()
    row["events"][0]["evidence_refs"] = []

    evaluation = evaluate_economic_ledger(EconomicLedger.from_dict(row))

    assert evaluation.control_pass is False
    assert any("requires private external evidence" in item.message for item in evaluation.findings)


def test_kind_cannot_be_claimed_below_minimum_stage() -> None:
    row = _ledger()
    row["events"][3]["commercial_stage"] = "E4"

    evaluation = evaluate_economic_ledger(EconomicLedger.from_dict(row))

    assert evaluation.control_pass is False
    assert any("pain-confirmation requires at least E5" in item.message for item in evaluation.findings)


def test_three_paid_buyers_create_repeatability_proof() -> None:
    row = _ledger()
    for buyer in ("A", "B", "C"):
        row["events"].append(
            {
                "event_id": f"{buyer}-PAY",
                "kind": "payment",
                "commercial_stage": "E8",
                "buyer_key": buyer,
                "evidence_refs": [f"private:{buyer}-pay"],
                "amount_eur": 900,
                "direct_cash_cost_eur": 50,
                "delivery_hours": 6,
                "notes": None,
            }
        )

    evaluation = evaluate_economic_ledger(EconomicLedger.from_dict(row))

    assert evaluation.initial_economic_proof is True
    assert evaluation.repeatability_proof is True


def test_expansion_can_create_repeatability_signal_after_initial_proof() -> None:
    row = _ledger()
    row["events"].extend(
        [
            {
                "event_id": "A-PAY",
                "kind": "payment",
                "commercial_stage": "E8",
                "buyer_key": "A",
                "evidence_refs": ["private:a-pay"],
                "amount_eur": 900,
                "direct_cash_cost_eur": 50,
                "delivery_hours": 6,
                "notes": None,
            },
            {
                "event_id": "A-EXPAND",
                "kind": "expansion",
                "commercial_stage": "E9",
                "buyer_key": "A",
                "evidence_refs": ["private:a-expand"],
                "amount_eur": None,
                "direct_cash_cost_eur": None,
                "delivery_hours": None,
                "notes": None,
            },
        ]
    )

    evaluation = evaluate_economic_ledger(EconomicLedger.from_dict(row))

    assert evaluation.initial_economic_proof is True
    assert evaluation.repeatability_proof is True


def test_synthetic_ledger_never_produces_economic_proof() -> None:
    ledger = _ledger()
    ledger["ledger_class"] = "synthetic"
    # reuse a proof-capable event set from the repeatability test shape
    evaluation = evaluate_economic_ledger(EconomicLedger.from_dict(ledger))

    assert evaluation.ledger_class == "synthetic"
    assert evaluation.initial_economic_proof is False
    assert evaluation.repeatability_proof is False


def test_undeclared_ledger_class_fails_closed_to_synthetic() -> None:
    ledger = _ledger()
    ledger.pop("ledger_class", None)
    evaluation = evaluate_economic_ledger(EconomicLedger.from_dict(ledger))

    assert evaluation.ledger_class == "synthetic"
    assert evaluation.initial_economic_proof is False


def test_example_fixture_is_synthetic_and_proofless() -> None:
    from pathlib import Path

    from clinicops_os.economic_validation import load_economic_ledger

    fixture = Path(__file__).resolve().parents[1] / "examples" / "economic_validation.example.json"
    evaluation = evaluate_economic_ledger(load_economic_ledger(fixture))

    assert evaluation.ledger_class == "synthetic"
    assert evaluation.initial_economic_proof is False
    assert evaluation.repeatability_proof is False
    assert evaluation.control_pass is True
