from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProspectSignal:
    company: str
    legacy_class_iii: bool = False
    danish_market: bool = False
    public_sscp: bool = False
    transition_date_known: bool = False
    evidence_strength: float = 0.0
    partner_multiplier: float = 1.0

    @property
    def score(self) -> float:
        base = 0.0
        base += 4.0 if self.legacy_class_iii else 0.0
        base += 3.0 if self.danish_market else 0.0
        base += 1.5 if self.public_sscp else 0.0
        base += 2.0 if self.transition_date_known else 0.0
        base += max(0.0, min(5.0, self.evidence_strength))
        return base * max(0.5, self.partner_multiplier)
