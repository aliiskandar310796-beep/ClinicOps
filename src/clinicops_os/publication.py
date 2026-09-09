from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .claim_registry import RegistryClaim


@dataclass(frozen=True)
class PublicationPack:
    title: str
    use: str
    as_of: date
    claims: tuple[RegistryClaim, ...]


def build_publication_pack(
    registry: list[RegistryClaim],
    claim_ids: list[str],
    *,
    title: str,
    use: str,
    as_of: date,
) -> PublicationPack:
    by_id = {claim.claim_id: claim for claim in registry}
    selected: list[RegistryClaim] = []
    problems: list[str] = []

    for claim_id in claim_ids:
        claim = by_id.get(claim_id)
        if claim is None:
            problems.append(f"{claim_id}: not found in registry")
            continue
        reasons = claim.gate(use, as_of)
        if reasons:
            problems.append(f"{claim_id}: " + "; ".join(reasons))
            continue
        selected.append(claim)

    if problems:
        raise ValueError("publication gate blocked:\n- " + "\n- ".join(problems))
    if not selected:
        raise ValueError("publication gate blocked: no claims selected")

    return PublicationPack(
        title=title,
        use=use,
        as_of=as_of,
        claims=tuple(selected),
    )


def render_publication_pack(pack: PublicationPack) -> str:
    lines = [
        f"# {pack.title}",
        "",
        f"Use: {pack.use}",
        f"Evidence checked through: {pack.as_of.isoformat()}",
        "",
        "## Approved claims",
    ]
    for claim in pack.claims:
        lines.extend([f"### {claim.claim_id}", claim.text, ""])

    lines.append("## Required limitations")
    for claim in pack.claims:
        for limitation in claim.limitations:
            lines.append(f"- **{claim.claim_id}:** {limitation}")

    lines.extend(["", "## Source ledger"])
    for claim in pack.claims:
        for source in claim.sources:
            lines.append(f"- **{claim.claim_id}:** {source}")

    lines.extend(
        [
            "",
            "## Editorial gate",
            "- Preserve duty-holder and actor-role context.",
            "- Do not convert observations into population rates.",
            "- Do not convert derived operational rules into quoted law.",
            "- Re-run the claim guard after editing the final copy.",
        ]
    )
    return "\n".join(lines) + "\n"
