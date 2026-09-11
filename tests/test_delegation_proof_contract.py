import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_delegation_policy_keeps_one_paid_or_two_dry_run_threshold() -> None:
    policy = (ROOT / "sales" / "commercial-activation-gate.md").read_text(
        encoding="utf-8"
    )
    protocol = (ROOT / "sales" / "delegation-proof-protocol.md").read_text(
        encoding="utf-8"
    )

    assert "next eligible paid pilot, or two complete controlled dry runs" in policy
    assert "one qualifying real eligible paid pilot" in protocol
    assert "two qualifying complete controlled dry runs" in protocol
    assert "clinicops-delegation-proof" in protocol


def test_public_delegation_example_is_ineligible_by_construction() -> None:
    payload = json.loads(
        (ROOT / "examples" / "delegation_proof.example.json").read_text(
            encoding="utf-8"
        )
    )
    run = payload["runs"][0]

    assert run["private_operational_record"] is False
    assert run["proof_use_allowed"] is False
    assert run["ci_or_automated_smoke"] is True


def test_dry_run_protocol_cannot_be_counted_as_buyer_validation() -> None:
    protocol = (ROOT / "sales" / "delegation-proof-protocol.md").read_text(
        encoding="utf-8"
    )

    assert "does not count as a qualified buyer conversation" in protocol
    assert "Two perfect dry runs can prove the first and prove nothing about the second" in protocol
