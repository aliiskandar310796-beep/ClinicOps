from __future__ import annotations

from dataclasses import dataclass
import re

ROLE_NAMES = {
    "MF": "Manufacturer",
    "AR": "Authorised representative",
    "IM": "Importer",
    "PR": "System and procedure pack producer",
}

SRN_RE = re.compile(r"^(?P<country>[A-Z]{2})-(?P<role>MF|AR|IM|PR)-(?P<number>\d{9})$")


@dataclass(frozen=True)
class SrnAssessment:
    raw: str
    normalized: str
    valid_shape: bool
    country: str | None
    role_code: str | None
    role_name: str | None
    number: str | None
    note: str


def decode_srn(value: str) -> SrnAssessment:
    normalized = value.strip().upper()
    match = SRN_RE.fullmatch(normalized)
    if not match:
        return SrnAssessment(
            raw=value,
            normalized=normalized,
            valid_shape=False,
            country=None,
            role_code=None,
            role_name=None,
            number=None,
            note=(
                "String does not match the common EUDAMED SRN shape "
                "CC-ROLE-#########. Resolve against EUDAMED before use."
            ),
        )

    role_code = match.group("role")
    return SrnAssessment(
        raw=value,
        normalized=normalized,
        valid_shape=True,
        country=match.group("country"),
        role_code=role_code,
        role_name=ROLE_NAMES[role_code],
        number=match.group("number"),
        note=(
            "Role decoding is structural only; it does not verify that the actor is "
            "currently registered, active, or responsible for a specific device."
        ),
    )
