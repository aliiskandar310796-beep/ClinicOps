from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum


class EvidenceClass(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    OBSERVATION = "observation"
    DERIVATION = "derivation"
    HYPOTHESIS = "hypothesis"


class VerificationStatus(StrEnum):
    UNCHECKED = "unchecked"
    VERIFIED = "verified"
    QUALIFIED = "qualified"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Claim:
    text: str
    evidence_class: EvidenceClass
    status: VerificationStatus
    source: str | None = None
    limitation: str | None = None


def publication_gate(claims: list[Claim]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    for claim in claims:
        if claim.status in {VerificationStatus.UNCHECKED, VerificationStatus.REJECTED}:
            reasons.append(f"Claim not publishable: {claim.text}")
        if claim.evidence_class in {EvidenceClass.OBSERVATION, EvidenceClass.DERIVATION} and not claim.limitation:
            reasons.append(f"Observed/derived claim missing limitation: {claim.text}")
        if claim.evidence_class == EvidenceClass.PRIMARY and not claim.source:
            reasons.append(f"Primary-source claim missing source: {claim.text}")
    return (not reasons, reasons)
