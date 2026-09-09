from __future__ import annotations

from datetime import date
from pathlib import Path

from clinicops_os.agents import AgentTask, evaluate_agent_task, resolve_role
from clinicops_os.claim_registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = load_registry(ROOT / "research" / "claims.jsonl")
AS_OF = date(2026, 9, 9)


def task(**overrides: object) -> AgentTask:
    row: dict[str, object] = {
        "task_id": "AGT-TEST",
        "role": "evidence-guardian",
        "objective": "Review a governed internal claim",
        "output_text": (
            "B-prefixed EUDAMED DI structure is used for legacy-device identification."
        ),
        "evidence_refs": ["research/claims.jsonl#CO-CLM-0004"],
        "claim_ids": ["CO-CLM-0004"],
        "intended_use": "internal",
        "business_value": (
            "Prevent an unsupported statement from entering downstream copy."
        ),
        "next_action": "Record the gate result in the work item.",
        "reproduction_steps": ["Run the agent gate against the same task JSON."],
        "artifacts": ["examples/agent_tasks.json"],
        "external_publish": False,
        "human_reviewed": False,
    }
    row.update(overrides)
    return AgentTask.from_dict(row)


def test_aliases_resolve_to_existing_profiles() -> None:
    assert resolve_role("Evidence Guardian") == "regulatory-evidence-steward"
    assert resolve_role("Research Scout") == "regulatory-evidence-steward"
    assert resolve_role("Content Engine") == "visibility-architect"
    assert resolve_role("Revenue Agent") == "opportunity-architect"
    assert resolve_role("Resilience Agent") == "release-sentinel"


def test_valid_internal_task_passes() -> None:
    result = evaluate_agent_task(task(), registry=REGISTRY, as_of=AS_OF)
    assert result.passed
    assert result.profile_path.endswith("regulatory-evidence-steward.agent.md")


def test_external_publication_requires_human_review() -> None:
    result = evaluate_agent_task(
        task(
            intended_use="website",
            external_publish=True,
            human_reviewed=False,
        ),
        registry=REGISTRY,
        as_of=AS_OF,
    )
    assert not result.passed
    assert any(item.gate == "human-review" for item in result.findings)


def test_claim_use_is_checked_against_registry() -> None:
    result = evaluate_agent_task(
        task(
            claim_ids=["CO-CLM-0005"],
            intended_use="website",
            external_publish=True,
            human_reviewed=True,
        ),
        registry=REGISTRY,
        as_of=AS_OF,
    )
    assert not result.passed
    assert any("CO-CLM-0005" in item.message for item in result.findings)


def test_missing_evidence_and_reproducibility_fail() -> None:
    result = evaluate_agent_task(
        task(evidence_refs=[], reproduction_steps=[], artifacts=[]),
        registry=REGISTRY,
        as_of=AS_OF,
    )
    assert not result.passed
    gates = {item.gate for item in result.findings}
    assert {"evidence", "reproducibility"}.issubset(gates)
