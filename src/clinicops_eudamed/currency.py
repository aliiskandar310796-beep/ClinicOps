from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CurrencyResult:
    verdict: str
    website_date: date | None
    eudamed_date: date | None
    reason: str


def compare_issue_dates(
    website_date: date | None,
    eudamed_date: date | None,
) -> CurrencyResult:
    if website_date is None or eudamed_date is None:
        return CurrencyResult(
            "UNRESOLVED",
            website_date,
            eudamed_date,
            "Both issue dates are required for a defensible currency comparison.",
        )
    if website_date == eudamed_date:
        return CurrencyResult(
            "MATCH",
            website_date,
            eudamed_date,
            "Issue dates match. This does not prove textual identity.",
        )
    if website_date > eudamed_date:
        return CurrencyResult(
            "AHEAD",
            website_date,
            eudamed_date,
            "Manufacturer-published issue date is newer. This is not by itself an irregularity.",
        )
    return CurrencyResult(
        "LAG",
        website_date,
        eudamed_date,
        "EUDAMED-linked issue date is newer than the manufacturer-published issue date.",
    )
