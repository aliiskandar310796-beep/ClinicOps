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

RISK_CATEGORIES = {
    "commercial",
    "financial",
    "regulatory",
    "legal",
    "privacy",
    "security",
    "delivery",
    "reputation",
    "dependency",
    "model",
    "operational",
}

RISK_STATUSES = {"open", "mitigated", "accepted", "closed"}
CRITICAL_SCORE = 16
HIGH_SCORE = 10


def _required_string(row: dict[str, object], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _required_bool(row: dict[str, object], key: str) -> bool:
    value = row.get(key)
    if not isinstance(value, bool):
        raise TypeError(f"{key} must be a boolean")
    return value


def _required_score(row: dict[str, object], key: str) -> int:
    value = row.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{key} must be an integer")
    if value < 1 or value > 5:
        raise ValueError(f"{key} must be between 1 and 5")
    return value


def _string_tuple(row: dict[str, object], key: str) -> tuple[str, ...]:
    value = row.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"{key} must be a list of strings")
    return tuple(item.strip() for item in value if item.strip())


@dataclass(frozen=True)
class Risk:
    risk_id: str
    category: str
    description: str
    likelihood: int
    impact: int
    owner_agent: str
    status: str
    mitigation: str
    trigger: str
    evidence_refs: tuple[str, ...]
    review_point: str
    reserved_human_decision: bool

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> Risk:
        if not isinstance(row, dict):
            raise TypeError("risk must be a JSON object")

        category = _required_string(row, "category")
        if category not in RISK_CATEGORIES:
            known = ", ".join(sorted(RISK_CATEGORIES))
            raise ValueError(f"unknown category '{category}'; expected one of: {known}")

        owner_agent = _required_string(row, "owner_agent")
        if owner_agent not in CANONICAL_AGENTS:
            known = ", ".join(sorted(CANONICAL_AGENTS))
            raise ValueError(f"unknown owner_agent '{owner_agent}'; expected one of: {known}")

        status = _required_string(row, "status")
        if status not in RISK_STATUSES:
            known = ", ".join(sorted(RISK_STATUSES))
            raise ValueError(f"unknown status '{status}'; expected one of: {known}")

        return cls(
            risk_id=_required_string(row, "risk_id"),
            category=category,
            description=_required_string(row, "description"),
            likelihood=_required_score(row, "likelihood"),
            impact=_required_score(row, "impact"),
            owner_agent=owner_agent,
            status=status,
            mitigation=_required_string(row, "mitigation"),
            trigger=_required_string(row, "trigger"),
            evidence_refs=_string_tuple(row, "evidence_refs"),
            review_point=_required_string(row, "review_point"),
            reserved_human_decision=_required_bool(row, "reserved_human_decision"),
        )

    @property
    def score(self) -> int:
        return self.likelihood * self.impact


@dataclass(frozen=True)
class RiskRegister:
    schema_version: str
    mission_id: str
    risks: tuple[Risk, ...]

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> RiskRegister:
        if not isinstance(row, dict):
            raise TypeError("risk register must be a JSON object")
        schema_version = _required_string(row, "schema_version")
        if schema_version != "1.0":
            raise ValueError("schema_version must be 1.0")
        raw_risks = row.get("risks")
        if not isinstance(raw_risks, list):
            raise TypeError("risks must be a list")
        risks = tuple(Risk.from_dict(item) for item in raw_risks)
        risk_ids = [risk.risk_id for risk in risks]
        if len(risk_ids) != len(set(risk_ids)):
            raise ValueError("risk_id values must be unique within a register")
        return cls(
            schema_version=schema_version,
            mission_id=_required_string(row, "mission_id"),
            risks=risks,
        )


@dataclass(frozen=True)
class RiskFinding:
    risk_id: str
    severity: str
    message: str


@dataclass(frozen=True)
class RiskEvaluation:
    mission_id: str
    control_pass: bool
    open_risks: int
    critical_open_risks: int
    highest_score: int
    findings: tuple[RiskFinding, ...]


def evaluate_risk_register(register: RiskRegister) -> RiskEvaluation:
    findings: list[RiskFinding] = []
    for risk in register.risks:
        if risk.status == "open" and risk.score >= CRITICAL_SCORE:
            findings.append(
                RiskFinding(
                    risk.risk_id,
                    "error",
                    f"critical risk remains open at score {risk.score}",
                )
            )

        if risk.status in {"mitigated", "closed"} and not risk.evidence_refs:
            findings.append(
                RiskFinding(
                    risk.risk_id,
                    "error",
                    f"{risk.status} risk requires evidence of the changed state",
                )
            )

        if risk.status == "accepted" and risk.score >= HIGH_SCORE and not risk.evidence_refs:
            findings.append(
                RiskFinding(
                    risk.risk_id,
                    "error",
                    "accepted high/critical risk requires a decision/evidence reference",
                )
            )

        if risk.reserved_human_decision and risk.status == "accepted" and not risk.evidence_refs:
            findings.append(
                RiskFinding(
                    risk.risk_id,
                    "error",
                    "reserved-human risk acceptance requires a human decision reference",
                )
            )

    open_risks = [risk for risk in register.risks if risk.status == "open"]
    critical_open = [risk for risk in open_risks if risk.score >= CRITICAL_SCORE]
    highest_score = max((risk.score for risk in register.risks), default=0)
    control_pass = not any(item.severity == "error" for item in findings)

    return RiskEvaluation(
        mission_id=register.mission_id,
        control_pass=control_pass,
        open_risks=len(open_risks),
        critical_open_risks=len(critical_open),
        highest_score=highest_score,
        findings=tuple(findings),
    )


def load_risk_register(path: str | Path) -> RiskRegister:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return RiskRegister.from_dict(raw)


def render_evaluation(evaluation: RiskEvaluation) -> str:
    payload = {
        "schema_version": "1.0",
        "mission_id": evaluation.mission_id,
        "control_pass": evaluation.control_pass,
        "metrics": {
            "open_risks": evaluation.open_risks,
            "critical_open_risks": evaluation.critical_open_risks,
            "highest_score": evaluation.highest_score,
        },
        "findings": [
            {
                "risk_id": item.risk_id,
                "severity": item.severity,
                "message": item.message,
            }
            for item in evaluation.findings
        ],
        "interpretation": (
            "Risk scores are operational prioritisation only. A clean control pass means "
            "the register obeys the risk contract; it does not prove the risks are gone."
        ),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
