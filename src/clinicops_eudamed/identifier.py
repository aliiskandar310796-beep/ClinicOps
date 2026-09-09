import re
from dataclasses import dataclass


@dataclass(frozen=True)
class IdentifierAssessment:
    raw: str
    normalized: str
    kind: str
    legacy_screen: bool
    gs1_valid: bool | None
    note: str


def gs1_mod10_valid(value: str) -> bool | None:
    digits = re.sub(r"\D", "", value)
    if len(digits) < 2:
        return None
    body, check = digits[:-1], int(digits[-1])
    total = 0
    for i, ch in enumerate(reversed(body)):
        total += int(ch) * (3 if i % 2 == 0 else 1)
    expected = (10 - total % 10) % 10
    return expected == check


def classify_identifier(value: str) -> IdentifierAssessment:
    raw = value
    normalized = value.strip()
    legacy = normalized.upper().startswith("B-")
    if legacy:
        return IdentifierAssessment(
            raw,
            normalized,
            "EUDAMED legacy registration identifier",
            True,
            None,
            "Derived ClinicOps screening rule: B-prefix indicates a legacy-style registration path. Do not present SS(C)P-link consequences as a directly quoted Commission rule.",
        )
    compact = re.sub(r"[\s-]", "", normalized)
    gs1 = gs1_mod10_valid(compact) if compact.isdigit() else None
    kind = "numeric UDI candidate" if compact.isdigit() else "identifier candidate"
    return IdentifierAssessment(
        raw,
        normalized,
        kind,
        False,
        gs1,
        "Resolve against EUDAMED before drawing regulatory conclusions.",
    )
