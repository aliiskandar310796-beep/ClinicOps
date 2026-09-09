from __future__ import annotations

from dataclasses import dataclass
import math


SCALE_MIN = 0.0
SCALE_MAX = 10.0


def _check_scale(name: str, value: float) -> None:
    if not SCALE_MIN <= value <= SCALE_MAX:
        raise ValueError(f"{name} must be between {SCALE_MIN:g} and {SCALE_MAX:g}")


@dataclass(frozen=True)
class Idea:
    """A ClinicOps opportunity scored on a 0-10 scale.

    Rewards evidence, leverage and durable reuse; penalizes regulatory/reputation
    risk plus ongoing maintenance burden. Effort is divided by sqrt(effort) so
    tiny low-value tasks do not automatically dominate meaningful projects.
    """

    name: str
    impact: float
    confidence: float
    leverage: float
    reversibility: float
    learning_value: float
    effort: float
    risk: float = 0.0
    evidence: float = 5.0
    defensibility: float = 5.0
    reuse: float = 5.0
    urgency: float = 5.0
    maintenance: float = 0.0

    def __post_init__(self) -> None:
        for field in (
            "impact", "confidence", "leverage", "reversibility", "learning_value",
            "risk", "evidence", "defensibility", "reuse", "urgency", "maintenance",
        ):
            _check_scale(field, float(getattr(self, field)))
        if self.effort <= 0:
            raise ValueError("effort must be > 0")
        if not self.name.strip():
            raise ValueError("name must not be empty")

    @property
    def raw_value(self) -> float:
        positive = (
            self.impact * 0.19 + self.evidence * 0.14 + self.leverage * 0.14
            + self.defensibility * 0.11 + self.reuse * 0.11 + self.urgency * 0.09
            + self.learning_value * 0.08 + self.confidence * 0.07
            + self.reversibility * 0.07
        )
        penalty = self.risk * 0.18 + self.maintenance * 0.12
        return max(0.0, positive - penalty)

    @property
    def score(self) -> float:
        return self.raw_value / math.sqrt(self.effort)

    @property
    def decision(self) -> str:
        if self.risk >= 8 and self.reversibility <= 4:
            return "ESCALATE"
        if self.score >= 3.2:
            return "DO NOW"
        if self.score >= 2.1:
            return "TEST"
        if self.score >= 1.3:
            return "BACKLOG"
        return "KILL/PARK"

    @classmethod
    def from_dict(cls, data: dict) -> "Idea":
        allowed = {f.name for f in cls.__dataclass_fields__.values()}
        unknown = set(data) - allowed
        if unknown:
            raise ValueError(f"unknown idea fields: {', '.join(sorted(unknown))}")
        return cls(**data)


def rank_ideas(ideas: list[Idea]) -> list[Idea]:
    return sorted(ideas, key=lambda i: (-i.score, i.risk, i.effort, i.name.lower()))
