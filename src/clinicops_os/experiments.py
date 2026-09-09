from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

VALID_STATUSES = {"planned", "running", "completed", "cancelled"}
VALID_DECISIONS = {"pending", "scale", "modify", "kill", "repeat"}


@dataclass(frozen=True)
class ExperimentRecord:
    """Commercial learning experiment, never a regulatory/compliance conclusion."""

    experiment_id: str
    opportunity_id: str
    hypothesis: str
    target_buyer: str
    smallest_test: str
    metric: str
    success_threshold: str
    kill_condition: str
    evidence: str = ""
    status: str = "planned"
    result: str = ""
    learning: str = ""
    decision: str = "pending"
    asset_path: str = ""

    def __post_init__(self) -> None:
        required = {
            "experiment_id": self.experiment_id,
            "opportunity_id": self.opportunity_id,
            "hypothesis": self.hypothesis,
            "target_buyer": self.target_buyer,
            "smallest_test": self.smallest_test,
            "metric": self.metric,
            "success_threshold": self.success_threshold,
            "kill_condition": self.kill_condition,
        }
        for field, value in required.items():
            if not value.strip():
                raise ValueError(f"{field} must not be empty")
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"status must be one of: {', '.join(sorted(VALID_STATUSES))}"
            )
        if self.decision not in VALID_DECISIONS:
            raise ValueError(
                f"decision must be one of: {', '.join(sorted(VALID_DECISIONS))}"
            )
        if self.status != "completed" and self.decision not in {"pending", "kill"}:
            raise ValueError(
                "non-completed experiments may only have decision 'pending' or 'kill'"
            )
        if self.status == "completed" and self.decision == "pending":
            raise ValueError("completed experiments must record a decision")
        if self.status == "completed" and not self.result.strip():
            raise ValueError("completed experiments must record a result")
        if self.status == "completed" and not self.learning.strip():
            raise ValueError("completed experiments must record learning")

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def experiment_from_dict(data: dict[str, object]) -> ExperimentRecord:
    allowed = set(ExperimentRecord.__dataclass_fields__)
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"unknown experiment fields: {', '.join(sorted(unknown))}")
    values = {key: "" if value is None else str(value) for key, value in data.items()}
    return ExperimentRecord(**values)


def load_experiments(path: str | Path) -> list[ExperimentRecord]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = raw.get("experiments", raw) if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        raise ValueError("experiment input must be a JSON list or object with 'experiments'")
    experiments = [experiment_from_dict(dict(row)) for row in rows]
    if not experiments:
        raise ValueError("experiment input must include at least one experiment")

    ids = [experiment.experiment_id for experiment in experiments]
    duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate experiment_id values: {', '.join(duplicates)}")
    return experiments


def experiment_payload(experiments: list[ExperimentRecord]) -> dict[str, object]:
    status_counts = Counter(experiment.status for experiment in experiments)
    decision_counts = Counter(experiment.decision for experiment in experiments)
    learning_complete = sum(
        1
        for experiment in experiments
        if experiment.status == "completed" and experiment.learning.strip()
    )
    return {
        "schema_version": "1.0",
        "interpretation": (
            "Commercial learning experiments only. Results guide product and market "
            "decisions; they are not regulatory, compliance, legal, or enforcement findings."
        ),
        "summary": {
            "experiments": len(experiments),
            "status": dict(sorted(status_counts.items())),
            "decisions": dict(sorted(decision_counts.items())),
            "completed_with_learning": learning_complete,
        },
        "experiments": [experiment.to_dict() for experiment in experiments],
    }


def render_experiment_json(experiments: list[ExperimentRecord]) -> str:
    return json.dumps(experiment_payload(experiments), indent=2, ensure_ascii=False) + "\n"
