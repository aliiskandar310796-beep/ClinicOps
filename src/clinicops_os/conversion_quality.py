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
        (
            "assessment-intake.html",
            "transition-map-sample/",
            "assessment-intake.html?workstream=integrity-review",
            "specimen-register/",
        ),
    ),
    ConversionRequirement(
        "tools.html",
        (
            "transition-map-sample/",
            "specimen-register/",
            "assessment-intake.html?workstream=integrity-review",
        ),
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
        ("transition-map-sample/", "readiness-score.html", "specimen-register/"),
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
            "../assessment-intake.html?workstream=integrity-review",
        ),
    ),
)


def _validate_specimen_pdf(docs_root: Path) -> list[str]:
    path = docs_root / SPECIMEN_PDF
    if not path.is_file():
        return []

    data = path.read_bytes()
    errors: list[str] = []
    if len(data) < 5_000:
        errors.append("specimen PDF is unexpectedly small")
    if not data.startswith(b"%PDF-"):
        errors.append("specimen PDF is missing the PDF file signature")
    if b"%%EOF" not in data[-1_024:]:
        errors.append("specimen PDF is missing a terminal PDF EOF marker")
    return errors


def validate_conversion_paths(docs_root: Path) -> list[str]:
    """Return broken high-intent conversion and externally shared path contracts.

    The contract is additive: new commercial journeys may be introduced without
    silently removing established entry routes that have already been published
    or distributed. It intentionally does not enforce pricing, analytics, or
    third-party integrations.
    """

    errors: list[str] = []

    for required_file in REQUIRED_FILES:
        if not (docs_root / required_file).is_file():
            errors.append(f"missing required public artifact: {required_file}")

    errors.extend(_validate_specimen_pdf(docs_root))

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
