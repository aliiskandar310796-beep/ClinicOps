from datetime import date
from pathlib import Path

from clinicops_os.claim_registry import (
    RegistryClaim,
    audit_registry,
    load_registry,
)
from clinicops_os.evidence import EvidenceClass, VerificationStatus


def _claim(**overrides):
    values = {
        "claim_id": "CO-CLM-9999",
        "text": "A test claim.",
        "evidence_class": EvidenceClass.PRIMARY,
        "status": VerificationStatus.VERIFIED,
        "sources": ("https://example.com/source",),
        "limitations": (),
        "allowed_uses": ("research-note",),
        "review_after": None,
        "supersedes": (),
        "superseded_by": None,
    }
    values.update(overrides)
    return RegistryClaim(**values)


def test_rejected_claim_cannot_be_public() -> None:
    claim = _claim(status=VerificationStatus.REJECTED)
    findings = audit_registry([claim], as_of=date(2026, 9, 9))
    assert any("rejected claim" in item.message for item in findings)


def test_derived_claim_requires_limitation() -> None:
    claim = _claim(evidence_class=EvidenceClass.DERIVATION, limitations=())
    findings = audit_registry([claim], as_of=date(2026, 9, 9))
    assert any("no limitation" in item.message for item in findings)


def test_external_gate_blocks_stale_claim() -> None:
    claim = _claim(review_after=date(2026, 9, 1))
    reasons = claim.gate("research-note", as_of=date(2026, 9, 9))
    assert any("review expired" in reason for reason in reasons)


def test_seed_registry_has_no_errors() -> None:
    root = Path(__file__).resolve().parents[1]
    claims = load_registry(root / "research" / "claims.jsonl")
    findings = audit_registry(claims, as_of=date(2026, 9, 9))
    assert len(claims) >= 8
    assert not [item for item in findings if item.severity == "error"]
