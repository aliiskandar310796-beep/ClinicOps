from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CANONICAL_AGENTS = {
    "customer-discovery",
    "opportunity-architect",
    "portfolio-operator",
    "regulatory-evidence-steward",
    "release-sentinel",
    "visibility-architect",
}

OUTCOME_CLASSES = {
    "commercial-evidence",
    "revenue",
    "buyer-learning",
    "visibility-discovery",
    "delivery-quality",
    "resilience",
    "evidence-quality",
    "cycle-time",
}

WORKER_SPECIALTIES = {
    "market-scout",
    "regulatory-source-analyst",
    "account-researcher",
    "buyer-signal-analyst",
    "offer-scope-designer",
    "distribution-operator",
    "integrity-case-builder",
    "delivery-reconciler",
    "adversarial-qa",
    "automation-engineer",
    "metrics-auditor",
    "coordination-runner",
}

MISSION_STATUSES = {"active", "waiting", "blocked", "completed", "failed", "killed"}
WORKER_STATUSES = {
    "queued",
    "working",
    "waiting",
    "blocked",
    "completed",
    "failed",
    "killed",
}
METRIC_DIRECTIONS = {"increase", "decrease"}
COMMERCIAL_STAGES = tuple(f"E{index}" for index in range(10))
ACTIVE_WORKER_STATUSES = {"queued", "working"}
MAX_ACTIVE_WORKERS = 5
REAL_COMMERCIAL_STAGE_MIN = 4


def _required_string(row: dict[str, object], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _optional_string(row: dict[str, object], key: str) -> str | None:
    value = row.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string or null")
    value = value.strip()
    return value or None


def _required_bool(row: dict[str, object], key: str) -> bool:
    value = row.get(key)
    if not isinstance(value, bool):
        raise TypeError(f"{key} must be a boolean")
    return value


def _required_number(row: dict[str, object], key: str) -> float:
    value = row.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{key} must be a number")
    return float(value)


def _string_tuple(row: dict[str, object], key: str) -> tuple[str, ...]:
    value = row.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"{key} must be a list of strings")
    return tuple(item.strip() for item in value if item.strip())


@dataclass(frozen=True)
class Worker:
    worker_id: str
    specialty: str
    parent_agent: str
    objective: str
    status: str
    success_criteria: tuple[str, ...]
    stop_condition: str
    evidence_refs: tuple[str, ...]
    artifact_refs: tuple[str, ...]
    handoff_to: str | None
    handoff_completed: bool
    reserved_human_action: bool
    control_violation: bool
    violation_resolved: bool
    notes: str | None = None

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> Worker:
        if not isinstance(row, dict):
            raise TypeError("worker must be a JSON object")

        specialty = _required_string(row, "specialty")
        if specialty not in WORKER_SPECIALTIES:
            known = ", ".join(sorted(WORKER_SPECIALTIES))
            raise ValueError(f"unknown specialty '{specialty}'; expected one of: {known}")

        parent_agent = _required_string(row, "parent_agent")
        if parent_agent not in CANONICAL_AGENTS:
            known = ", ".join(sorted(CANONICAL_AGENTS))
            raise ValueError(
                f"unknown parent_agent '{parent_agent}'; expected one of: {known}"
            )

        status = _required_string(row, "status")
        if status not in WORKER_STATUSES:
            known = ", ".join(sorted(WORKER_STATUSES))
            raise ValueError(f"unknown worker status '{status}'; expected one of: {known}")

        handoff_to = _optional_string(row, "handoff_to")
        if handoff_to is not None and handoff_to not in CANONICAL_AGENTS:
            known = ", ".join(sorted(CANONICAL_AGENTS))
            raise ValueError(f"unknown handoff_to '{handoff_to}'; expected one of: {known}")

        criteria = _string_tuple(row, "success_criteria")
        if not criteria:
            raise ValueError("success_criteria must contain at least one item")
        if len(criteria) > 5:
            raise ValueError("success_criteria may contain at most five items")

        return cls(
            worker_id=_required_string(row, "worker_id"),
            specialty=specialty,
            parent_agent=parent_agent,
            objective=_required_string(row, "objective"),
            status=status,
            success_criteria=criteria,
            stop_condition=_required_string(row, "stop_condition"),
            evidence_refs=_string_tuple(row, "evidence_refs"),
            artifact_refs=_string_tuple(row, "artifact_refs"),
            handoff_to=handoff_to,
            handoff_completed=_required_bool(row, "handoff_completed"),
            reserved_human_action=_required_bool(row, "reserved_human_action"),
            control_violation=_required_bool(row, "control_violation"),
            violation_resolved=_required_bool(row, "violation_resolved"),
            notes=_optional_string(row, "notes"),
        )


@dataclass(frozen=True)
class OutcomeMission:
    schema_version: str
    mission_id: str
    owner_agent: str
    outcome_class: str
    objective: str
    status: str
    metric_name: str
    metric_direction: str
    baseline: float
    target: float
    current: float
    unit: str
    commercial_stage: str
    evidence_refs: tuple[str, ...]
    artifact_refs: tuple[str, ...]
    review_point: str
    stop_condition: str
    workers: tuple[Worker, ...]

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> OutcomeMission:
        if not isinstance(row, dict):
            raise TypeError("outcome mission must be a JSON object")

        schema_version = _required_string(row, "schema_version")
        if schema_version != "1.0":
            raise ValueError("schema_version must be 1.0")

        owner_agent = _required_string(row, "owner_agent")
        if owner_agent not in CANONICAL_AGENTS:
            known = ", ".join(sorted(CANONICAL_AGENTS))
            raise ValueError(f"unknown owner_agent '{owner_agent}'; expected one of: {known}")

        outcome_class = _required_string(row, "outcome_class")
        if outcome_class not in OUTCOME_CLASSES:
            known = ", ".join(sorted(OUTCOME_CLASSES))
            raise ValueError(
                f"unknown outcome_class '{outcome_class}'; expected one of: {known}"
            )

        status = _required_string(row, "status")
        if status not in MISSION_STATUSES:
            known = ", ".join(sorted(MISSION_STATUSES))
            raise ValueError(f"unknown mission status '{status}'; expected one of: {known}")

        metric_direction = _required_string(row, "metric_direction")
        if metric_direction not in METRIC_DIRECTIONS:
            known = ", ".join(sorted(METRIC_DIRECTIONS))
            raise ValueError(
                f"unknown metric_direction '{metric_direction}'; expected one of: {known}"
            )

        commercial_stage = _required_string(row, "commercial_stage").upper()
        if commercial_stage not in COMMERCIAL_STAGES:
            known = ", ".join(COMMERCIAL_STAGES)
            raise ValueError(
                f"unknown commercial_stage '{commercial_stage}'; expected one of: {known}"
            )

        raw_workers = row.get("workers", [])
        if not isinstance(raw_workers, list):
            raise TypeError("workers must be a list")
        workers = tuple(Worker.from_dict(item) for item in raw_workers)
        worker_ids = [worker.worker_id for worker in workers]
        if len(worker_ids) != len(set(worker_ids)):
            raise ValueError("worker_id values must be unique within a mission")

        baseline = _required_number(row, "baseline")
        target = _required_number(row, "target")
        current = _required_number(row, "current")
        if metric_direction == "increase" and target <= baseline:
            raise ValueError("increase metrics require target > baseline")
        if metric_direction == "decrease" and target >= baseline:
            raise ValueError("decrease metrics require target < baseline")

        return cls(
            schema_version=schema_version,
            mission_id=_required_string(row, "mission_id"),
            owner_agent=owner_agent,
            outcome_class=outcome_class,
            objective=_required_string(row, "objective"),
            status=status,
            metric_name=_required_string(row, "metric_name"),
            metric_direction=metric_direction,
            baseline=baseline,
            target=target,
            current=current,
            unit=_required_string(row, "unit"),
            commercial_stage=commercial_stage,
            evidence_refs=_string_tuple(row, "evidence_refs"),
            artifact_refs=_string_tuple(row, "artifact_refs"),
            review_point=_required_string(row, "review_point"),
            stop_condition=_required_string(row, "stop_condition"),
            workers=workers,
        )

    @property
    def stage_number(self) -> int:
        return int(self.commercial_stage[1:])

    @property
    def outcome_achieved(self) -> bool:
        if self.metric_direction == "increase":
            return self.current >= self.target
        return self.current <= self.target

    @property
    def progress_ratio(self) -> float:
        if self.metric_direction == "increase":
            raw = (self.current - self.baseline) / (self.target - self.baseline)
        else:
            raw = (self.baseline - self.current) / (self.baseline - self.target)
        return max(0.0, min(1.0, raw))


@dataclass(frozen=True)
class OutcomeFinding:
    scope: str
    severity: str
    message: str


@dataclass(frozen=True)
class OutcomeEvaluation:
    mission_id: str
    control_pass: bool
    outcome_achieved: bool
    progress_ratio: float
    active_workers: int
    total_workers: int
    completed_workers: int
    completed_workers_with_refs: int
    handoffs: int
    completed_handoffs: int
    handoff_closure_rate: float
    highest_commercial_stage: str
    findings: tuple[OutcomeFinding, ...]


def evaluate_outcome_mission(mission: OutcomeMission) -> OutcomeEvaluation:
    findings: list[OutcomeFinding] = []

    if mission.stage_number >= REAL_COMMERCIAL_STAGE_MIN and not mission.evidence_refs:
        findings.append(
            OutcomeFinding(
                "mission",
                "error",
                f"{mission.commercial_stage} requires private external evidence refs",
            )
        )

    if mission.current != mission.baseline and not (
        mission.evidence_refs or mission.artifact_refs
    ):
        findings.append(
            OutcomeFinding(
                "mission",
                "error",
                "metric movement requires at least one evidence or artifact reference",
            )
        )

    if mission.status == "completed" and not mission.outcome_achieved:
        findings.append(
            OutcomeFinding(
                "mission",
                "error",
                "mission cannot be completed before its target outcome is achieved",
            )
        )

    if mission.status == "completed" and not (
        mission.evidence_refs or mission.artifact_refs
    ):
        findings.append(
            OutcomeFinding(
                "mission",
                "error",
                "completed mission requires evidence or artifact refs",
            )
        )

    active_workers = [
        worker for worker in mission.workers if worker.status in ACTIVE_WORKER_STATUSES
    ]
    if len(active_workers) > MAX_ACTIVE_WORKERS:
        findings.append(
            OutcomeFinding(
                "mission",
                "error",
                f"active worker cap exceeded: {len(active_workers)} > {MAX_ACTIVE_WORKERS}",
            )
        )

    for worker in mission.workers:
        scope = f"worker:{worker.worker_id}"
        if worker.status == "completed" and not (
            worker.evidence_refs or worker.artifact_refs
        ):
            findings.append(
                OutcomeFinding(
                    scope,
                    "error",
                    "completed worker requires at least one evidence or artifact reference",
                )
            )

        if worker.handoff_to is None and worker.handoff_completed:
            findings.append(
                OutcomeFinding(
                    scope,
                    "error",
                    "handoff_completed cannot be true when handoff_to is null",
                )
            )

        if worker.handoff_to is not None and not worker.handoff_completed:
            severity = "error" if mission.status == "completed" else "warning"
            findings.append(
                OutcomeFinding(
                    scope,
                    severity,
                    f"handoff to {worker.handoff_to} remains open",
                )
            )

        if worker.control_violation and not worker.violation_resolved:
            findings.append(
                OutcomeFinding(scope, "error", "unresolved control violation")
            )
        elif worker.control_violation and worker.violation_resolved:
            findings.append(
                OutcomeFinding(
                    scope,
                    "info",
                    "control incident is recorded and resolved",
                )
            )

        if worker.violation_resolved and not worker.control_violation:
            findings.append(
                OutcomeFinding(
                    scope,
                    "error",
                    "violation_resolved cannot be true without a recorded control_violation",
                )
            )

    completed_workers = [worker for worker in mission.workers if worker.status == "completed"]
    completed_workers_with_refs = [
        worker
        for worker in completed_workers
        if worker.evidence_refs or worker.artifact_refs
    ]
    handoffs = [worker for worker in mission.workers if worker.handoff_to is not None]
    completed_handoffs = [worker for worker in handoffs if worker.handoff_completed]
    handoff_rate = len(completed_handoffs) / len(handoffs) if handoffs else 1.0

    control_pass = not any(finding.severity == "error" for finding in findings)

    return OutcomeEvaluation(
        mission_id=mission.mission_id,
        control_pass=control_pass,
        outcome_achieved=mission.outcome_achieved,
        progress_ratio=mission.progress_ratio,
        active_workers=len(active_workers),
        total_workers=len(mission.workers),
        completed_workers=len(completed_workers),
        completed_workers_with_refs=len(completed_workers_with_refs),
        handoffs=len(handoffs),
        completed_handoffs=len(completed_handoffs),
        handoff_closure_rate=handoff_rate,
        highest_commercial_stage=mission.commercial_stage,
        findings=tuple(findings),
    )


def load_outcome_mission(path: str | Path) -> OutcomeMission:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return OutcomeMission.from_dict(raw)


def evaluation_payload(evaluation: OutcomeEvaluation) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "mission_id": evaluation.mission_id,
        "control_pass": evaluation.control_pass,
        "outcome_achieved": evaluation.outcome_achieved,
        "metrics": {
            "progress_ratio": round(evaluation.progress_ratio, 4),
            "active_workers": evaluation.active_workers,
            "active_worker_cap": MAX_ACTIVE_WORKERS,
            "total_workers": evaluation.total_workers,
            "completed_workers": evaluation.completed_workers,
            "completed_workers_with_refs": evaluation.completed_workers_with_refs,
            "handoffs": evaluation.handoffs,
            "completed_handoffs": evaluation.completed_handoffs,
            "handoff_closure_rate": round(evaluation.handoff_closure_rate, 4),
            "highest_commercial_stage": evaluation.highest_commercial_stage,
        },
        "findings": [
            {
                "scope": finding.scope,
                "severity": finding.severity,
                "message": finding.message,
            }
            for finding in evaluation.findings
        ],
        "interpretation": (
            "A control pass means the mission record obeys the ClinicOps outcome and "
            "worker-control contract. It does not prove demand, revenue, PMF, founder "
            "independence or qualified professional review."
        ),
    }


def render_evaluation(evaluation: OutcomeEvaluation) -> str:
    return json.dumps(evaluation_payload(evaluation), indent=2, ensure_ascii=False) + "\n"
