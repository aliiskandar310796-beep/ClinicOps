from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from .evidence import EvidenceClass, VerificationStatus

CLAIM_ID_RE = re.compile(r"^CO-CLM-\d{4}$")
LANGUAGE_CODE_RE = re.compile(r"^[a-z]{2}$")
PUBLIC_USES = {
    "research-note",
    "website",
    "linkedin",
    "sales-copy",
    "client-deliverable",
}

# Lens 29: review cadence follows (rate of change) x (cost of being wrong).
# A dated duties and planning dates, B operating-model and guidance statements,
# C tool constants, D ClinicOps observations, E stable primary law text.
RISK_CLASS_INTERVAL_DAYS = {"A": 30, "B": 45, "C": 90, "D": 120, "E": 180}
VERIFIED_METHODS = {"read-primary", "read-secondary", "observation", "carried-forward"}
# Uses that put a claim in front of a reader, so the claim can be stamped.
STAMPED_USES = {"website", "research-note"}
LIVE_STATUSES = {"verified", "qualified"}
REVIEW_WARNING_DAYS = 14


def _opt_str(raw: object) -> str | None:
    return str(raw) if raw not in (None, "") else None


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
    risk_class: str | None = None
    last_verified: date | None = None
    verified_method: str | None = None
    fact_key: str | None = None
    value: str | None = None
    source_date: str | None = None
    not_established: tuple[str, ...] = ()
    label: str | None = None
    # Optional translations of `text`, as (language code, text) pairs. The English
    # `text` stays the single authoritative wording; a translation carries the
    # same limitations and allowed uses and never widens the claim.
    translations: tuple[tuple[str, str], ...] = ()

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> RegistryClaim:
        review_raw = row.get("review_after")
        review_after = date.fromisoformat(str(review_raw)) if review_raw else None
        verified_raw = row.get("last_verified")
        last_verified = date.fromisoformat(str(verified_raw)) if verified_raw else None
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
            risk_class=_opt_str(row.get("risk_class")),
            last_verified=last_verified,
            verified_method=_opt_str(row.get("verified_method")),
            fact_key=_opt_str(row.get("fact_key")),
            value=_opt_str(row.get("value")),
            source_date=_opt_str(row.get("source_date")),
            not_established=tuple(str(item) for item in row.get("not_established", [])),
            label=_opt_str(row.get("label")),
            translations=tuple(
                (str(language), str(text))
                for language, text in sorted(dict(row.get("translations") or {}).items())
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
            raise TypeError(f"line {line_number} must contain a JSON object")
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
        for language, translated in claim.translations:
            if not LANGUAGE_CODE_RE.fullmatch(language) or language == "en":
                findings.append(
                    RegistryFinding(
                        "error",
                        claim.claim_id,
                        f"translation language {language!r} must be a two-letter code other than 'en'",
                    )
                )
            if not translated.strip():
                findings.append(
                    RegistryFinding(
                        "error", claim.claim_id, f"{language} translation is empty"
                    )
                )
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
        findings.extend(_schema_findings(claim))
        # A superseded claim is history: it never warns about its own expiry.
        if claim.superseded_by:
            continue
        if claim.review_after and as_of > claim.review_after:
            findings.append(
                RegistryFinding(
                    "warning",
                    claim.claim_id,
                    f"review date passed on {claim.review_after.isoformat()}",
                )
            )
        elif claim.review_after and (claim.review_after - as_of).days <= REVIEW_WARNING_DAYS:
            days = (claim.review_after - as_of).days
            findings.append(
                RegistryFinding(
                    "warning",
                    claim.claim_id,
                    f"review due in {days} days ({claim.review_after.isoformat()}): "
                    "re-read the source; do not just move the date",
                )
            )
    findings.extend(_fact_key_findings(claims))
    return findings


def _schema_findings(claim: RegistryClaim) -> list[RegistryFinding]:
    """Lens 29 schema rules. Superseded and rejected claims are exempt from the
    freshness rules because no reader can be served by them."""
    out: list[RegistryFinding] = []

    def error(message: str) -> None:
        out.append(RegistryFinding("error", claim.claim_id, message))

    if claim.risk_class not in RISK_CLASS_INTERVAL_DAYS:
        error("risk_class must be one of A, B, C, D, E")
    if bool(claim.fact_key) != bool(claim.value):
        error("fact_key and value must be set together")

    live = claim.status.value in LIVE_STATUSES and not claim.superseded_by
    if not live:
        return out

    if claim.review_after is None:
        error("a verified or qualified claim must have a review_after date")
    if claim.last_verified is None:
        error("a verified or qualified claim must record last_verified")
    if claim.verified_method not in VERIFIED_METHODS:
        error(f"verified_method must be one of {', '.join(sorted(VERIFIED_METHODS))}")
    elif claim.status.value == "verified" and claim.verified_method != "read-primary":
        error("status verified requires verified_method read-primary")
    if claim.review_after and claim.last_verified and claim.risk_class in RISK_CLASS_INTERVAL_DAYS:
        limit = claim.last_verified + timedelta(days=RISK_CLASS_INTERVAL_DAYS[claim.risk_class])
        if claim.review_after > limit:
            error(
                f"review_after {claim.review_after.isoformat()} is longer than the "
                f"class {claim.risk_class} interval "
                f"({RISK_CLASS_INTERVAL_DAYS[claim.risk_class]} days from last_verified)"
            )
    if STAMPED_USES.intersection(claim.allowed_uses):
        if not claim.source_date:
            error("source_date is required for a claim that can appear on a page")
        if not claim.not_established:
            error("not_established is required for a claim that can appear on a page")
        if not claim.label:
            error("label is required for a claim that can appear on a page")
    return out


def _fact_key_findings(claims: list[RegistryClaim]) -> list[RegistryFinding]:
    """Two live claims that share a fact_key must agree on its value."""
    seen: dict[str, RegistryClaim] = {}
    out: list[RegistryFinding] = []
    for claim in claims:
        if not claim.fact_key or claim.superseded_by:
            continue
        if claim.status.value not in LIVE_STATUSES:
            continue
        first = seen.setdefault(claim.fact_key, claim)
        if first is not claim and first.value != claim.value:
            out.append(
                RegistryFinding(
                    "error",
                    claim.claim_id,
                    f"fact_key {claim.fact_key} has value {claim.value!r} here but "
                    f"{first.value!r} in {first.claim_id}",
                )
            )
    return out


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
