from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Dependency:
    name: str
    criticality: int
    has_fallback: bool
    manual_recovery_minutes: int

    @property
    def fragility(self) -> float:
        fallback_penalty = 0 if self.has_fallback else 5
        recovery_penalty = min(5, self.manual_recovery_minutes / 30)
        return self.criticality + fallback_penalty + recovery_penalty


def resilience_backlog(dependencies: list[Dependency]) -> list[Dependency]:
    return sorted(dependencies, key=lambda d: (-d.fragility, d.name))
