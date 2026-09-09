from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

VALID_SEGMENTS = {
    "manufacturer",
    "authorised_representative",
    "consultancy",
    "distributor",
    "other",
}

SCORE_WEIGHTS = {
    "urgency": 0.22,
    "offer_fit": 0.20,
    "evidence_strength": 0.18,
    "partner_leverage": 0.15,
    "access_strength": 0.10,
    "budget_signal": 0.10,
    "reuse_potential": 0.05,
}


def _parse_optional_score(value: str | float | None) -> float | None:
    if value is None or value == "":
        return None
    score = float(value)
    if not 0.0 <= score <= 5.0:
        raise ValueError("commercial signal scores must be between 0 and 5")
    return score


@dataclass(frozen=True)
class AccountIntelligence:
    """Evidence-aware commercial account record for prioritising learning and pilots.

    Scores are commercial operating signals, never regulatory/compliance risk scores.
    Unknown values stay ``None`` and are excluded from the weighted score.
    """

    company: str
    segment: str
    geography: str = ""
    trigger: str = ""
    source_url: str = ""
    evidence_note: str = ""
    experiment_id: str = ""
    urgency: float | None = None
    offer_fit: float | None = None
    evidence_strength: float | None = None
    partner_leverage: float | None = None
    access_strength: float | None = None
    budget_signal: float | None = None
    reuse_potential: float | None = None

    def __post_init__(self) -> None:
        if not self.company.strip():
            raise ValueError("company must not be empty")
        if self.segment not in VALID_SEGMENTS:
            raise ValueError(
                f"segment must be one of: {', '.join(sorted(VALID_SEGMENTS))}"
            )
        for field in SCORE_WEIGHTS:
            value = getattr(self, field)
            if value is not None and not 0.0 <= float(value) <= 5.0:
                raise ValueError(f"{field} must be between 0 and 5 when supplied")

    @property
    def score_coverage(self) -> float:
        known_weight = sum(
            weight
            for field, weight in SCORE_WEIGHTS.items()
            if getattr(self, field) is not None
        )
        return known_weight * 100.0

    @property
    def priority_score(self) -> float:
        weighted = 0.0
        known_weight = 0.0
        for field, weight in SCORE_WEIGHTS.items():
            value = getattr(self, field)
            if value is None:
                continue
            weighted += (float(value) / 5.0) * weight
            known_weight += weight
        if known_weight == 0:
            return 0.0
        return (weighted / known_weight) * 100.0

    @property
    def priority_band(self) -> str:
        # Weakly observed accounts remain learning targets regardless of apparent score.
        if self.score_coverage < 40.0:
            return "LEARN"
        if self.priority_score >= 75.0:
            return "HOT"
        if self.priority_score >= 55.0:
            return "WARM"
        if self.priority_score >= 35.0:
            return "LEARN"
        return "PARK"

    @property
    def next_experiment(self) -> str:
        evidence = self.evidence_strength
        offer_fit = self.offer_fit
        urgency = self.urgency
        access = self.access_strength
        budget = self.budget_signal
        leverage = self.partner_leverage

        if evidence is None or evidence < 2.0:
            return "RESEARCH"
        if offer_fit is None or offer_fit < 2.0:
            return "DISCOVERY"
        if (
            self.segment in {"authorised_representative", "consultancy"}
            and leverage is not None
            and leverage >= 4.0
            and urgency is not None
            and urgency >= 3.0
        ):
            return "PARTNER CONVERSATION"
        if (
            urgency is not None
            and urgency >= 4.0
            and budget is not None
            and budget >= 3.0
            and access is not None
            and access >= 2.0
        ):
            return "PILOT"
        if access is None or access < 2.0:
            return "WARM INTRO / DISCOVERY"
        return "DISCOVERY"

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = asdict(self)
        data.update(
            {
                "priority_score": round(self.priority_score, 2),
                "score_coverage": round(self.score_coverage, 2),
                "priority_band": self.priority_band,
                "next_experiment": self.next_experiment,
            }
        )
        return data


def account_from_dict(data: dict[str, str]) -> AccountIntelligence:
    allowed = {field.name for field in AccountIntelligence.__dataclass_fields__.values()}
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"unknown account fields: {', '.join(sorted(unknown))}")

    values: dict[str, object] = dict(data)
    for field in SCORE_WEIGHTS:
        values[field] = _parse_optional_score(data.get(field))
    return AccountIntelligence(**values)


def load_accounts(path: str | Path) -> list[AccountIntelligence]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("revenue CSV must include a header row")
        rows = [account_from_dict(dict(row)) for row in reader]
    if not rows:
        raise ValueError("revenue CSV must include at least one account")
    return rows


def rank_accounts(accounts: list[AccountIntelligence]) -> list[AccountIntelligence]:
    band_order = {"HOT": 0, "WARM": 1, "LEARN": 2, "PARK": 3}
    return sorted(
        accounts,
        key=lambda account: (
            band_order[account.priority_band],
            -account.priority_score,
            -account.score_coverage,
            account.company.lower(),
        ),
    )


def revenue_payload(accounts: list[AccountIntelligence]) -> dict[str, object]:
    ranked = rank_accounts(accounts)
    counts = {band: 0 for band in ("HOT", "WARM", "LEARN", "PARK")}
    for account in ranked:
        counts[account.priority_band] += 1
    return {
        "schema_version": "1.0",
        "interpretation": (
            "Commercial prioritisation for learning and pilot selection only; "
            "not a regulatory, compliance, legal, or enforcement-risk score."
        ),
        "summary": {"accounts": len(ranked), "bands": counts},
        "accounts": [account.to_dict() for account in ranked],
    }


def render_revenue_json(accounts: list[AccountIntelligence]) -> str:
    return json.dumps(revenue_payload(accounts), indent=2, ensure_ascii=False) + "\n"
