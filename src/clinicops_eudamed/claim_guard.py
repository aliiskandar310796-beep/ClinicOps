from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimFlag:
    severity: str
    pattern: str
    guidance: str


RISKY = [
    (
        "high",
        "class iii devices are registered with no ss(c)p linked",
        "Discarded framing. The corrected 8 Sep 2026 census found linked, validated SS(C)Ps for all sampled MDR manufacturer class III registrations.",
    ),
    (
        "high",
        "manufacturers are failing to link",
        "Do not allege manufacturer diligence failure from the census. Reframe around legacy-to-MDR transition backlog.",
    ),
    (
        "high",
        "legacy registrations never carry",
        "Present this as ClinicOps reasoning/observed screening behavior, not as a directly stated regulatory rule.",
    ),
    (
        "high",
        "audit the public register end-to-end",
        "Public API reachability is incomplete; do not imply full-register audit coverage.",
    ),
    (
        "medium",
        "revision number proves",
        "Revision-number semantics can differ. Prefer issue dates unless numbering equivalence is established.",
    ),
    (
        "medium",
        "procedure pack is a class iii device",
        "Risk class on a system/procedure pack can be inherited from the highest-class constituent; qualify carefully.",
    ),
    (
        "medium",
        "pre-mdr means legacy",
        "Legacy device is narrower than all pre-MDR devices; preserve the distinction.",
    ),
]


def check_claim(text: str) -> list[ClaimFlag]:
    low = text.lower()
    out = []
    for severity, pattern, guidance in RISKY:
        if pattern in low:
            out.append(ClaimFlag(severity, pattern, guidance))
    return out
