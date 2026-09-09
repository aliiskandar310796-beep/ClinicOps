from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class AgentSpec:
    name: str
    mission: str
    cadence: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    guardrails: tuple[str, ...]
    escalation: str
    leverage: int


class FleetRegistry:
    def __init__(self, agents: list[AgentSpec]):
        names = [a.name for a in agents]
        if len(names) != len(set(names)):
            raise ValueError("Agent names must be unique")
        self.agents = agents

    @classmethod
    def load(cls, path: str | Path) -> "FleetRegistry":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        agents = []
        for item in raw["agents"]:
            agents.append(
                AgentSpec(
                    name=item["name"],
                    mission=item["mission"],
                    cadence=item["cadence"],
                    inputs=tuple(item.get("inputs", [])),
                    outputs=tuple(item.get("outputs", [])),
                    guardrails=tuple(item.get("guardrails", [])),
                    escalation=item.get("escalation", "Escalate material ambiguity."),
                    leverage=int(item.get("leverage", 5)),
                )
            )
        return cls(agents)

    def by_min_leverage(self, threshold: int) -> list[AgentSpec]:
        return sorted(
            [a for a in self.agents if a.leverage >= threshold],
            key=lambda a: (-a.leverage, a.name),
        )

    def to_json(self) -> str:
        return json.dumps({"agents": [asdict(a) for a in self.agents]}, indent=2)
