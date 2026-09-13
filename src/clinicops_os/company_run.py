from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEPARTMENTS = {
    "executive-orchestration",
    "market-regulatory-intelligence",
    "revenue-opportunity",
    "customer-discovery-partnerships",
    "growth-distribution",
    "client-delivery",
    "quality-engineering-resilience",
    "commercial-control",
    "human-governance",
}

STATUSES = {"completed", "blocked", "failed", "waiting"}
COMMERCIAL_STAGES = tuple(f"E{index}" for index in range(10))
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


def _string_tuple(row: dict[str, object], key: str) -> tuple[str, ...]:
    value = row.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"{key} must be a list of strings")
    return tuple(item.strip() for item in value if item.strip())


@dataclass(frozen=True)
class CompanyEvent:
    event_id: str
    department: str
    objective: str
    status: str
    ai_led: bool
    founder_intervention: bool
    reserved_human_decision: bool
    commercial_stage: str
    evidence_refs: tuple[str, ...]
    artifact_refs: tuple[str, ...]
    handoff_to: str | None
    handoff_completed: bool
    safety_violation: bool
    notes: str | None = None

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> CompanyEvent:
        if not isinstance(row, dict):
            raise TypeError("company event must be a JSON object")

        department = _required_string(row, "department")
        if department not in DEPARTMENTS:
            known = ", ".join(sorted(DEPARTMENTS))
            raise ValueError(f"unknown department '{department}'; expected one of: {known}")

        status = _required_string(row, "status")
        if status not in STATUSES:
            known = ", ".join(sorted(STATUSES))
            raise ValueError(f"unknown status '{status}'; expected one of: {known}")

        commercial_stage = _required_string(row, "commercial_stage").upper()
        if commercial_stage not in COMMERCIAL_STAGES:
            known = ", ".join(COMMERCIAL_STAGES)
            raise ValueError(
                f"unknown commercial_stage '{commercial_stage}'; expected one of: {known}"
            )

        handoff_to = _optional_string(row, "handoff_to")
        if handoff_to is not None and handoff_to not in DEPARTMENTS:
            known = ", ".join(sorted(DEPARTMENTS))
            raise ValueError(f"unknown handoff_to '{handoff_to}'; expected one of: {known}")

        return cls(
            event_id=_required_string(row, "event_id"),
            department=department,
            objective=_required_string(row, "objective"),
            status=status,
            ai_led=_required_bool(row, "ai_led"),
            founder_intervention=_required_bool(row, "founder_intervention"),
            reserved_human_decision=_required_bool(row, "reserved_human_decision"),
            commercial_stage=commercial_stage,
            evidence_refs=_string_tuple(row, "evidence_refs"),
            artifact_refs=_string_tuple(row, "artifact_refs"),
            handoff_to=handoff_to,
            handoff_completed=_required_bool(row, "handoff_completed"),
            safety_violation=_required_bool(row, "safety_violation"),
            notes=_optional_string(row, "notes"),
        )

    @property
    def stage_number(self) -> int:
        return int(self.commercial_stage[1:])


@dataclass(frozen=True)
class CompanyRun:
    run_id: str
    period_start: str
    period_end: str
    events: tuple[CompanyEvent, ...]

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> CompanyRun:
        if not isinstance(row, dict):
            raise TypeError("company run must be a JSON object")
        raw_events = row.get("events")
        if not isinstance(raw_events, list):
            raise TypeError("events must be a list")
        events = tuple(CompanyEvent.from_dict(item) for item in raw_events)
        event_ids = [item.event_id for item in events]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("event_id values must be unique within a run")
        return cls(
            run_id=_required_string(row, "run_id"),
            period_start=_required_string(row, "period_start"),
            period_end=_required_string(row, "period_end"),
            events=events,
        )


@dataclass(frozen=True)
class RunFinding:
    event_id: str
    severity: str
    message: str


@dataclass(frozen=True)
class CompanyRunEvaluation:
    run_id: str
    operational_pass: bool
    commercial_signal: bool
    activated_commercial_loop: bool
    end_to_end_commercial_proof: bool
    autonomy_rate: float
    handoff_closure_rate: float
    eligible_completed_events: int
    autonomous_completed_events: int
    non_reserved_founder_interventions: int
    reserved_human_decisions: int
    handoffs: int
    completed_handoffs: int
    highest_commercial_stage: str
    real_commercial_evidence_events: int
    findings: tuple[RunFinding, ...]


def evaluate_company_run(run: CompanyRun) -> CompanyRunEvaluation:
    findings: list[RunFinding] = []

    for event in run.events:
        if event.stage_number >= REAL_COMMERCIAL_STAGE_MIN and not event.evidence_refs:
            findings.append(
                RunFinding(
                    event.event_id,
                    "error",
                    f"{event.commercial_stage} requires at least one external/private evidence reference",
                )
            )

        if event.status == "completed" and not (event.artifact_refs or event.evidence_refs):
            findings.append(
                RunFinding(
                    event.event_id,
                    "error",
                    "completed event requires at least one artifact or evidence reference",
                )
            )

        if event.handoff_to is None and event.handoff_completed:
            findings.append(
                RunFinding(
                    event.event_id,
                    "error",
                    "handoff_completed cannot be true when handoff_to is null",
                )
            )

        if event.handoff_to is not None and not event.handoff_completed:
            findings.append(
                RunFinding(
                    event.event_id,
                    "warning",
                    f"handoff to {event.handoff_to} is still open",
                )
            )

        if event.safety_violation:
            findings.append(
                RunFinding(
                    event.event_id,
                    "error",
                    "safety/control violation recorded for this event",
                )
            )

        if event.founder_intervention and event.reserved_human_decision:
            findings.append(
                RunFinding(
                    event.event_id,
                    "info",
                    "human involvement is policy-reserved and excluded from the autonomy denominator",
                )
            )

        if event.founder_intervention and not event.reserved_human_decision:
            findings.append(
                RunFinding(
                    event.event_id,
                    "warning",
                    "non-reserved founder intervention reduced operational autonomy",
                )
            )

    eligible_completed = [
        event
        for event in run.events
        if event.status == "completed" and not event.reserved_human_decision
    ]
    autonomous_completed = [
        event
        for event in eligible_completed
        if event.ai_led and not event.founder_intervention
    ]
    autonomy_rate = (
        len(autonomous_completed) / len(eligible_completed) if eligible_completed else 0.0
    )

    handoffs = [event for event in run.events if event.handoff_to is not None]
    completed_handoffs = [event for event in handoffs if event.handoff_completed]
    handoff_closure_rate = len(completed_handoffs) / len(handoffs) if handoffs else 1.0

    highest_stage_number = max((event.stage_number for event in run.events), default=0)
    highest_stage = f"E{highest_stage_number}"
    real_commercial_evidence_events = sum(
        event.stage_number >= REAL_COMMERCIAL_STAGE_MIN for event in run.events
    )

    integrity_ok = not any(item.severity == "error" for item in findings)
    operational_pass = (
        integrity_ok and autonomy_rate >= 0.90 and handoff_closure_rate >= 0.95
    )

    return CompanyRunEvaluation(
        run_id=run.run_id,
        operational_pass=operational_pass,
        commercial_signal=highest_stage_number >= 6,
        activated_commercial_loop=highest_stage_number >= 7,
        end_to_end_commercial_proof=highest_stage_number >= 8,
        autonomy_rate=autonomy_rate,
        handoff_closure_rate=handoff_closure_rate,
        eligible_completed_events=len(eligible_completed),
        autonomous_completed_events=len(autonomous_completed),
        non_reserved_founder_interventions=sum(
            event.founder_intervention and not event.reserved_human_decision
            for event in run.events
        ),
        reserved_human_decisions=sum(event.reserved_human_decision for event in run.events),
        handoffs=len(handoffs),
        completed_handoffs=len(completed_handoffs),
        highest_commercial_stage=highest_stage,
        real_commercial_evidence_events=real_commercial_evidence_events,
        findings=tuple(findings),
    )


def load_company_run(path: str | Path) -> CompanyRun:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return CompanyRun.from_dict(raw)


def evaluation_payload(evaluation: CompanyRunEvaluation) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "run_id": evaluation.run_id,
        "operational_pass": evaluation.operational_pass,
        "commercial_signal": evaluation.commercial_signal,
        "activated_commercial_loop": evaluation.activated_commercial_loop,
        "end_to_end_commercial_proof": evaluation.end_to_end_commercial_proof,
        "metrics": {
            "autonomy_rate": round(evaluation.autonomy_rate, 4),
            "handoff_closure_rate": round(evaluation.handoff_closure_rate, 4),
            "eligible_completed_events": evaluation.eligible_completed_events,
            "autonomous_completed_events": evaluation.autonomous_completed_events,
            "non_reserved_founder_interventions": evaluation.non_reserved_founder_interventions,
            "reserved_human_decisions": evaluation.reserved_human_decisions,
            "handoffs": evaluation.handoffs,
            "completed_handoffs": evaluation.completed_handoffs,
            "highest_commercial_stage": evaluation.highest_commercial_stage,
            "real_commercial_evidence_events": evaluation.real_commercial_evidence_events,
        },
        "findings": [
            {
                "event_id": item.event_id,
                "severity": item.severity,
                "message": item.message,
            }
            for item in evaluation.findings
        ],
        "interpretation": (
            "Operational autonomy and commercial validation are separate. "
            "A clean AI operating pass does not prove product-market fit, revenue, "
            "founder independence or qualified professional review."
        ),
    }


def render_evaluation(evaluation: CompanyRunEvaluation) -> str:
    return json.dumps(evaluation_payload(evaluation), indent=2, ensure_ascii=False) + "\n"
