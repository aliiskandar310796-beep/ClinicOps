from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConversionRequirement:
    page: str
    required_targets: tuple[str, ...]


REQUIREMENTS = (
    ConversionRequirement(
        "index.html",
        ("assessment-intake.html", "transition-map-sample/"),
    ),
    ConversionRequirement(
        "tools.html",
        ("transition-map-sample/",),
    ),
    ConversionRequirement(
        "assessment-intake.html",
        ("transition-map-sample/", "readiness-score.html"),
    ),
    ConversionRequirement(
        "readiness-score.html",
        ("assessment-intake.html",),
    ),
    ConversionRequirement(
        "transition-map-sample/index.html",
        ("/assessment-intake.html",),
    ),
)


def validate_conversion_paths(docs_root: Path) -> list[str]:
    """Return broken high-intent conversion-path requirements.

    This deliberately checks only durable navigation contracts. It does not
    enforce marketing copy, pricing, analytics, or third-party integrations.
    """

    errors: list[str] = []
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
