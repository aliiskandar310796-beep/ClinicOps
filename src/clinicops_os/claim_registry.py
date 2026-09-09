from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .evidence import EvidenceClass, VerificationStatus

CLAIM_ID_RE = re.compile(r"^CO-CLM-\d{4}$")
PUBLIC_USES = {
    "research-note",
    "website",
    "linkedin",
    "sales-copy",
    "client-deliverable",
}


@dataclass(frozen=True)
class RegistryClaim:
    claim_id: str
    text: str
    evidence_class: EvidenceClass
    status: VerificationStatus
    sources: tuple[str, ...]
    limitations: tuple[str, ...]
    allowed_uses: tuple[str, ...]
    review_after: date | None
    supersedes: tuple[str, ...]
    superseded_by: str | None

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> RegistryClaim:
        review_raw = row.get("review_after")
        review_after = date.fromisoformat(str(review_raw)) if review_raw else None
        return cls(
            claim_id=str(row["id"]),
            text=str(row["claim"]),
            evidence_class=EvidenceClass(str(row["evidence_class"])),
            status=VerificationStatus(str(row["status"])),
            sources=tuple(str(item) for item in row.get("sources", [])),
            limitations=tuple(str(item) for item in row.get("limitations", [])),
            allowed_uses=tuple(str(item) for item in row.get("allowed_uses", [])),
            review_after=review_after,
            supersedes=tuple(str(item) for item in row.get("supersedes", [])),
            superseded_by=(
                str(row["superseded_by"]) if row.get("superseded_by") else None
            ),
        )

    def gate(self, use: str, as_of: date) -> list[str]:
        reasons: list[str] = []
        if self.status not in {
            VerificationStatus.VERIFIED,
            VerificationStatus.QUALIFIED,
        }:
            reasons.append(f"status is {self.status.value}")
        if use not in self.allowed_uses:
            reasons.append(f"use '{use}' is not allowed")
        if self.superseded_by:
            reasons.append(f"superseded by {self.superseded_by}")
        if self.review_after and as_of > self.review_after and use in PUBLIC_USES:
            reasons.append(f"review expired on {self.review_after.isoformat()}")
        return reasons


@dataclass(frozen=True)
class RegistryFinding:
    severity: str
    claim_id: str
    message: str


def load_registry(path: str | Path) -> list[RegistryClaim]:
    claims: list[RegistryClaim] = []
    for line_number, line in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {line_number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"line {line_number} must contain a JSON object")
        claims.append(RegistryClaim.from_dict(row))
    return claims


def audit_registry(claims: list[RegistryClaim], as_of: date) -> list[RegistryFinding]:
    findings: list[RegistryFinding] = []
    seen: set[str] = set()
    known_ids = {claim.claim_id for claim in claims}

    for claim in claims:
        if not CLAIM_ID_RE.fullmatch(claim.claim_id):
            findings.append(
                RegistryFinding("error", claim.claim_id, "invalid claim ID format")
            )
        if claim.claim_id in seen:
            findings.append(RegistryFinding("error", claim.claim_id, "duplicate claim ID"))
        seen.add(claim.claim_id)

        if not claim.text.strip():
            findings.append(RegistryFinding("error", claim.claim_id, "claim is empty"))
        if claim.evidence_class == EvidenceClass.PRIMARY and not claim.sources:
            findings.append(
                RegistryFinding("error", claim.claim_id, "primary claim has no source")
            )
        if claim.evidence_class in {
            EvidenceClass.OBSERVATION,
            EvidenceClass.DERIVATION,
        } and not claim.limitations:
            findings.append(
                RegistryFinding(
                    "error",
                    claim.claim_id,
                    "observed/derived claim has no limitation",
                )
            )
        if claim.status == VerificationStatus.REJECTED and PUBLIC_USES.intersection(
            claim.allowed_uses
        ):
            findings.append(
                RegistryFinding(
                    "error",
                    claim.claim_id,
                    "rejected claim is allowed in a public use",
                )
            )
        if claim.superseded_by and claim.superseded_by not in known_ids:
            findings.append(
                RegistryFinding(
                    "error",
                    claim.claim_id,
                    f"unknown superseding claim {claim.superseded_by}",
                )
            )
        for prior_id in claim.supersedes:
            if prior_id not in known_ids:
                findings.append(
                    RegistryFinding(
                        "error",
                        claim.claim_id,
                        f"unknown superseded claim {prior_id}",
                    )
                )
        if claim.review_after and as_of > claim.review_after:
            findings.append(
                RegistryFinding(
                    "warning",
                    claim.claim_id,
                    f"review date passed on {claim.review_after.isoformat()}",
                )
            )
    return findings


def render_matrix(claims: list[RegistryClaim], as_of: date) -> str:
    lines = [
        "# ClinicOps claim registry",
        "",
        f"As of: {as_of.isoformat()}",
        "",
        "| ID | Status | Evidence | External readiness | Claim |",
        "| --- | --- | --- | --- | --- |",
    ]
    for claim in claims:
        external_reasons = claim.gate("research-note", as_of)
        readiness = "ready" if not external_reasons else "; ".join(external_reasons)
        text = claim.text.replace("|", "\\|")
        lines.append(
            f"| {claim.claim_id} | {claim.status.value} | "
            f"{claim.evidence_class.value} | {readiness} | {text} |"
        )
    return "\n".join(lines) + "\n"
