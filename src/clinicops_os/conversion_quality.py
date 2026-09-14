from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConversionRequirement:
    page: str
    required_targets: tuple[str, ...]


SPECIMEN_PDF = "specimen-register/ClinicOps_Regulatory_Integrity_Specimen_Register_v1.5.pdf"
REQUIRED_FILES = (
    "specimen-register/index.html",
    SPECIMEN_PDF,
)

REQUIREMENTS = (
    ConversionRequirement(
        "index.html",
        ("assessment-intake.html?workstream=integrity-review", "specimen-register/"),
    ),
    ConversionRequirement(
        "tools.html",
        ("specimen-register/", "assessment-intake.html?workstream=integrity-review"),
    ),
    ConversionRequirement(
        "integrity-gate.html",
        ("specimen-register/", "assessment-intake.html?workstream=integrity-review"),
    ),
    ConversionRequirement(
        "eu-mdr-regulatory-integrity.html",
        ("specimen-register/", "assessment-intake.html?workstream=integrity-review"),
    ),
    ConversionRequirement(
        "assessment-intake.html",
        ("specimen-register/", "readiness-score.html"),
    ),
    ConversionRequirement(
        "readiness-score.html",
        ("assessment-intake.html",),
    ),
    ConversionRequirement(
        "class-iii-transition.html",
        ("assessment-intake.html", "transition-map-sample/"),
    ),
    ConversionRequirement(
        "transition-map-sample/index.html",
        ("/assessment-intake.html",),
    ),
    ConversionRequirement(
        "specimen-register/index.html",
        (
            "ClinicOps_Regulatory_Integrity_Specimen_Register_v1.5.pdf",
            "../assessment-intake.html?workstream=integrity-gate",
        ),
    ),
)


def validate_conversion_paths(docs_root: Path) -> list[str]:
    """Return broken high-intent conversion and externally shared path contracts.

    This checks durable buyer-navigation and specimen availability invariants.
    It intentionally does not enforce pricing, analytics, or third-party integrations.
    """

    errors: list[str] = []

    for required_file in REQUIRED_FILES:
        if not (docs_root / required_file).is_file():
            errors.append(f"missing required public artifact: {required_file}")

    for requirement in REQUIREMENTS:
        path = docs_root / requirement.page
        if not path.exists():
            errors.append(f"missing conversion page: {requirement.page}")
            continue
        text = path.read_text(encoding="utf-8")
        for target in requirement.required_targets:
            if f'href="{target}"' not in text:
                errors.append(
                    f"{requirement.page}: missing high-intent path to {target}"
                )
    return errors
