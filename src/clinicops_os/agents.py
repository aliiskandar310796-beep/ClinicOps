from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from clinicops_eudamed.claim_guard import check_claim

from .claim_registry import PUBLIC_USES, RegistryClaim, load_registry

CANONICAL_PROFILES = {
    "regulatory-evidence-steward": ".github/agents/regulatory-evidence-steward.agent.md",
    "portfolio-operator": ".github/agents/portfolio-operator.agent.md",
    "release-sentinel": ".github/agents/release-sentinel.agent.md",
    "opportunity-architect": ".github/agents/opportunity-architect.agent.md",
    "customer-discovery": ".github/agents/customer-discovery.agent.md",
    "visibility-architect": ".github/agents/visibility-architect.agent.md",
}

ROLE_ALIASES = {
    "evidence-guardian": "regulatory-evidence-steward",
    "intelligence-scout": "regulatory-evidence-steward",
    "research-scout": "regulatory-evidence-steward",
    "growth-agent": "visibility-architect",
    "content-engine": "visibility-architect",
    "opportunity-agent": "opportunity-architect",
    "revenue-agent": "opportunity-architect",
    "resilience-agent": "release-sentinel",
}


def _normalise_role(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def resolve_role(value: str) -> str:
    role = _normalise_role(value)
    canonical = ROLE_ALIASES.get(role, role)
    if canonical not in CANONICAL_PROFILES:
        known = ", ".join(sorted(CANONICAL_PROFILES))
        raise ValueError(f"unknown agent role '{value}'; expected one of: {known}")
    return canonical


def _required_string(row: dict[str, object], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _string_tuple(row: dict[str, object], key: str) -> tuple[str, ...]:
    value = row.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"{key} must be a list of strings")
    return tuple(item.strip() for item in value if item.strip())


@dataclass(frozen=True)
class AgentTask:
    task_id: str
    role: str
    objective: str
    output_text: str
    evidence_refs: tuple[str, ...]
    claim_ids: tuple[str, ...]
    intended_use: str
    business_value: str
    next_action: str
    reproduction_steps: tuple[str, ...]
    artifacts: tuple[str, ...]
    external_publish: bool = False
    human_reviewed: bool = False

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> AgentTask:
        if not isinstance(row, dict):
            raise TypeError("agent task must be a JSON object")
        external_publish = row.get("external_publish", False)
        human_reviewed = row.get("human_reviewed", False)
        if not isinstance(external_publish, bool):
            raise TypeError("external_publish must be a boolean")
        if not isinstance(human_reviewed, bool):
            raise TypeError("human_reviewed must be a boolean")
        return cls(
            task_id=_required_string(row, "task_id"),
            role=resolve_role(_required_string(row, "role")),
            objective=_required_string(row, "objective"),
            output_text=_required_string(row, "output_text"),
            evidence_refs=_string_tuple(row, "evidence_refs"),
            claim_ids=_string_tuple(row, "claim_ids"),
            intended_use=_required_string(row, "intended_use"),
            business_value=_required_string(row, "business_value"),
            next_action=_required_string(row, "next_action"),
            reproduction_steps=_string_tuple(row, "reproduction_steps"),
            artifacts=_string_tuple(row, "artifacts"),
            external_publish=external_publish,
            human_reviewed=human_reviewed,
        )


@dataclass(frozen=True)
class GateFinding:
    gate: str
    severity: str
    message: str


@dataclass(frozen=True)
class AgentEvaluation:
    task_id: str
    role: str
    profile_path: str
    passed: bool
    findings: tuple[GateFinding, ...]


def evaluate_agent_task(
    task: AgentTask,
    *,
    registry: list[RegistryClaim],
    as_of: date,
) -> AgentEvaluation:
    findings: list[GateFinding] = []

    if not task.evidence_refs:
        findings.append(
            GateFinding("evidence", "error", "at least one evidence reference is required")
        )

    registry_by_id = {claim.claim_id: claim for claim in registry}
    for flag in check_claim(task.output_text):
        findings.append(
            GateFinding(
                "claim-safety",
                "error",
                f"blocked phrase '{flag.pattern}': {flag.guidance}",
            )
        )

    if task.external_publish and not task.claim_ids:
        findings.append(
            GateFinding(
                "claim-safety",
                "error",
                "external publication requires explicit registered claim IDs",
            )
        )

    for claim_id in task.claim_ids:
        claim = registry_by_id.get(claim_id)
        if claim is None:
            findings.append(
                GateFinding("claim-safety", "error", f"unknown claim ID {claim_id}")
            )
            continue
        for reason in claim.gate(task.intended_use, as_of):
            findings.append(
                GateFinding(
                    "claim-safety",
                    "error",
                    f"{claim_id} blocked for {task.intended_use}: {reason}",
                )
            )

    if task.external_publish and task.intended_use not in PUBLIC_USES:
        findings.append(
            GateFinding(
                "claim-safety",
                "error",
                f"external publication cannot use internal-only use '{task.intended_use}'",
            )
        )

    if not task.business_value.strip() or not task.next_action.strip():
        findings.append(
            GateFinding(
                "business-value",
                "error",
                "business value and next action are both required",
            )
        )

    if not task.reproduction_steps or not task.artifacts:
        findings.append(
            GateFinding(
                "reproducibility",
                "error",
                "reproduction steps and at least one artifact are required",
            )
        )

    if task.external_publish and not task.human_reviewed:
        findings.append(
            GateFinding(
                "human-review",
                "error",
                "externally published output requires recorded human review",
            )
        )

    passed = not any(item.severity == "error" for item in findings)
    return AgentEvaluation(
        task_id=task.task_id,
        role=task.role,
        profile_path=CANONICAL_PROFILES[task.role],
        passed=passed,
        findings=tuple(findings),
    )


def load_agent_tasks(path: str | Path) -> list[AgentTask]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = raw.get("tasks", raw) if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        raise TypeError("input must be a JSON list or an object with a 'tasks' list")
    return [AgentTask.from_dict(row) for row in rows]


def gate_payload(
    tasks: list[AgentTask],
    *,
    registry_path: str | Path,
    as_of: date,
) -> dict[str, object]:
    registry = load_registry(registry_path)
    evaluations = [
        evaluate_agent_task(task, registry=registry, as_of=as_of) for task in tasks
    ]
    return {
        "schema_version": "1.0",
        "as_of": as_of.isoformat(),
        "summary": {
            "tasks": len(evaluations),
            "passed": sum(item.passed for item in evaluations),
            "failed": sum(not item.passed for item in evaluations),
        },
        "evaluations": [
            {
                "task_id": item.task_id,
                "role": item.role,
                "profile_path": item.profile_path,
                "passed": item.passed,
                "findings": [
                    {
                        "gate": finding.gate,
                        "severity": finding.severity,
                        "message": finding.message,
                    }
                    for finding in item.findings
                ],
            }
            for item in evaluations
        ],
        "interpretation": (
            "Agent gate validates evidence, claim safety, business value, "
            "reproducibility and human-review requirements. It does not replace "
            "regulatory judgement."
        ),
    }
