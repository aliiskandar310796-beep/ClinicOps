from __future__ import annotations

from pathlib import Path

import pytest

from clinicops_os.experiments import (
    ExperimentRecord,
    experiment_payload,
    load_experiments,
)

ROOT = Path(__file__).resolve().parents[1]


def test_completed_experiment_requires_decision_result_and_learning() -> None:
    with pytest.raises(ValueError, match="completed experiments must record a decision"):
        ExperimentRecord(
            experiment_id="EXP-001",
            opportunity_id="REV-001",
            hypothesis="A buyer values the work plan.",
            target_buyer="authorised representative",
            smallest_test="Show one sanitized example.",
            metric="pilot requests",
            success_threshold="one pilot request",
            kill_condition="no expressed pain after five conversations",
            status="completed",
        )


def test_non_completed_experiment_cannot_scale() -> None:
    with pytest.raises(ValueError, match="non-completed experiments"):
        ExperimentRecord(
            experiment_id="EXP-002",
            opportunity_id="REV-002",
            hypothesis="Research content creates qualified conversations.",
            target_buyer="regulatory consultancy",
            smallest_test="Publish one evidence-approved note.",
            metric="qualified conversations",
            success_threshold="two conversations",
            kill_condition="zero qualified engagement after distribution",
            status="running",
            decision="scale",
        )


def test_sanitized_register_loads_and_summarizes() -> None:
    experiments = load_experiments(ROOT / "examples" / "experiments.json")
    payload = experiment_payload(experiments)

    assert payload["schema_version"] == "1.0"
    assert payload["summary"]["experiments"] == 2
    assert payload["summary"]["status"]["planned"] == 2
    assert payload["summary"]["decisions"]["pending"] == 2
    assert "not regulatory" in payload["interpretation"]


def test_duplicate_experiment_ids_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "experiments.json"
    path.write_text(
        """{"experiments":[
        {"experiment_id":"EXP-001","opportunity_id":"REV-001","hypothesis":"x","target_buyer":"AR","smallest_test":"x","metric":"x","success_threshold":"x","kill_condition":"x"},
        {"experiment_id":"EXP-001","opportunity_id":"REV-002","hypothesis":"y","target_buyer":"MF","smallest_test":"y","metric":"y","success_threshold":"y","kill_condition":"y"}
        ]}""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate experiment_id"):
        load_experiments(path)


def test_invalid_top_level_experiment_shape_is_type_error(tmp_path: Path) -> None:
    path = tmp_path / "experiments.json"
    path.write_text('{"experiments":"not-a-list"}', encoding="utf-8")

    with pytest.raises(TypeError, match="JSON list"):
        load_experiments(path)


def test_non_object_experiment_entry_is_type_error(tmp_path: Path) -> None:
    path = tmp_path / "experiments.json"
    path.write_text('{"experiments":["not-an-object"]}', encoding="utf-8")

    with pytest.raises(TypeError, match="JSON object"):
        load_experiments(path)
