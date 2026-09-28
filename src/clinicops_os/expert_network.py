from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

NETWORK_STATUSES = {
    "SOURCED",
    "SCREENING",
    "VERIFIED",
    "AVAILABLE",
    "LIMITED",
    "PAUSED",
    "DO_NOT_ASSIGN",
}
ASSIGNABLE_STATUSES = {"AVAILABLE", "LIMITED"}
ROLE_TYPES = {"ADVISORY", "REVIEWER", "DECISION_OWNER"}
SENSITIVE_DATA_LEVELS = {"NONE", "PSEUDONYMISED", "SPECIAL_CATEGORY"}
READY_CONTRACT_STATES = {"READY", "SIGNED", "FRAMEWORK_SIGNED"}
SIGNED_NDA_STATES = {"SIGNED", "IN_FORCE"}
INSURANCE_OK_STATES = {"VERIFIED", "NOT_REQUIRED"}


@dataclass(frozen=True)
class Finding:
    severity: str
    record_id: str
    field: str
    message: str

    def render(self) -> str:
        return f"[{self.severity}] {self.record_id} :: {self.field} :: {self.message}"


def _as_date(value: Any, *, field: str, findings: list[Finding], record_id: str) -> date | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        findings.append(Finding("error", record_id, field, "must be an ISO date string"))
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        findings.append(Finding("error", record_id, field, "must be YYYY-MM-DD"))
        return None


def _require_string(record: dict[str, Any], field: str, findings: list[Finding], record_id: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        findings.append(Finding("error", record_id, field, "required non-empty string"))
        return ""
    return value.strip()


def _require_list(record: dict[str, Any], field: str, findings: list[Finding], record_id: str) -> list[str]:
    value = record.get(field)
    if not isinstance(value, list) or not value:
        findings.append(Finding("error", record_id, field, "required non-empty list"))
        return []
    out: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            findings.append(Finding("error", record_id, field, "list values must be non-empty strings"))
            continue
        out.append(item.strip())
    return out


def _days_old(value: date | None, as_of: date) -> int | None:
    if value is None:
        return None
    return (as_of - value).days


def validate_expert(record: dict[str, Any], *, as_of: date | None = None) -> list[Finding]:
    as_of = as_of or date.today()
    findings: list[Finding] = []
    expert_id = _require_string(record, "expert_id", findings, "<unknown>") or "<unknown>"

    _require_string(record, "preferred_name", findings, expert_id)
    _require_string(record, "contact_route", findings, expert_id)
    _require_string(record, "country", findings, expert_id)
    _require_string(record, "professional_role", findings, expert_id)

    jurisdictions = _require_list(record, "jurisdictions", findings, expert_id)
    languages = _require_list(record, "languages", findings, expert_id)
    work_types = _require_list(record, "permitted_work_types", findings, expert_id)
    _require_list(record, "competency_domains", findings, expert_id)

    status = _require_string(record, "network_status", findings, expert_id)
    if status and status not in NETWORK_STATUSES:
        findings.append(Finding("error", expert_id, "network_status", f"unsupported value {status!r}"))

    verified_on = _as_date(record.get("credentials_verified_on"), field="credentials_verified_on", findings=findings, record_id=expert_id)
    conflict_on = _as_date(record.get("conflict_checked_on"), field="conflict_checked_on", findings=findings, record_id=expert_id)
    reviewed_on = _as_date(record.get("last_reviewed_on"), field="last_reviewed_on", findings=findings, record_id=expert_id)

    nda = str(record.get("nda_status", "")).upper()
    contract = str(record.get("contract_status", "")).upper()
    insurance = str(record.get("insurance_status", "")).upper()

    public_consent = record.get("public_profile_consent")
    public_wording = record.get("public_wording", "")
    if not isinstance(public_consent, bool):
        findings.append(Finding("error", expert_id, "public_profile_consent", "must be true or false"))
    if public_consent is False and isinstance(public_wording, str) and public_wording.strip():
        findings.append(Finding("error", expert_id, "public_wording", "must be blank when public consent is false"))
    if public_consent is True and (not isinstance(public_wording, str) or not public_wording.strip()):
        findings.append(Finding("error", expert_id, "public_wording", "required when public consent is true"))

    if status in ASSIGNABLE_STATUSES:
        if verified_on is None:
            findings.append(Finding("error", expert_id, "credentials_verified_on", "required before an expert is assignable"))
        elif (_days_old(verified_on, as_of) or 0) > 365:
            findings.append(Finding("error", expert_id, "credentials_verified_on", "credential verification is older than 365 days"))

        if conflict_on is None:
            findings.append(Finding("error", expert_id, "conflict_checked_on", "required before an expert is assignable"))
        elif (_days_old(conflict_on, as_of) or 0) > 180:
            findings.append(Finding("warning", expert_id, "conflict_checked_on", "network-level conflict check is older than 180 days; re-check before assignment"))

        if reviewed_on is None:
            findings.append(Finding("error", expert_id, "last_reviewed_on", "required before an expert is assignable"))
        elif (_days_old(reviewed_on, as_of) or 0) > 180:
            findings.append(Finding("warning", expert_id, "last_reviewed_on", "expert record review is older than 180 days"))

        if nda not in SIGNED_NDA_STATES:
            findings.append(Finding("error", expert_id, "nda_status", "must be SIGNED or IN_FORCE before assignment"))
        if contract not in READY_CONTRACT_STATES:
            findings.append(Finding("error", expert_id, "contract_status", "must be READY, SIGNED or FRAMEWORK_SIGNED before assignment"))
        if insurance not in INSURANCE_OK_STATES:
            findings.append(Finding("error", expert_id, "insurance_status", "must be VERIFIED or NOT_REQUIRED before assignment"))

    if status == "DO_NOT_ASSIGN" and record.get("availability_note"):
        findings.append(Finding("info", expert_id, "availability_note", "retain only the minimum note necessary to prevent reassignment"))

    if jurisdictions and len(set(jurisdictions)) != len(jurisdictions):
        findings.append(Finding("warning", expert_id, "jurisdictions", "contains duplicates"))
    if languages and len(set(languages)) != len(languages):
        findings.append(Finding("warning", expert_id, "languages", "contains duplicates"))
    if work_types and len(set(work_types)) != len(work_types):
        findings.append(Finding("warning", expert_id, "permitted_work_types", "contains duplicates"))

    return findings


def validate_assignment(
    assignment: dict[str, Any],
    expert: dict[str, Any],
    *,
    as_of: date | None = None,
) -> list[Finding]:
    as_of = as_of or date.today()
    findings: list[Finding] = []
    assignment_id = _require_string(assignment, "assignment_id", findings, "<unknown-assignment>") or "<unknown-assignment>"
    expert_id = _require_string(assignment, "expert_id", findings, assignment_id)
    expected_id = str(expert.get("expert_id", ""))
    if expert_id and expected_id and expert_id != expected_id:
        findings.append(Finding("error", assignment_id, "expert_id", "does not match the selected expert record"))

    _require_string(assignment, "engagement_id", findings, assignment_id)
    _require_string(assignment, "scoped_question", findings, assignment_id)
    work_type = _require_string(assignment, "work_type", findings, assignment_id)
    _require_string(assignment, "accountable_owner", findings, assignment_id)
    markets = _require_list(assignment, "markets", findings, assignment_id)
    languages = _require_list(assignment, "languages", findings, assignment_id)

    role = _require_string(assignment, "role_type", findings, assignment_id)
    if role and role not in ROLE_TYPES:
        findings.append(Finding("error", assignment_id, "role_type", f"unsupported value {role!r}"))

    status = str(expert.get("network_status", ""))
    if status not in ASSIGNABLE_STATUSES:
        findings.append(Finding("error", assignment_id, "expert_id", f"expert status {status!r} is not assignable"))

    permitted = set(expert.get("permitted_work_types", []))
    if work_type and work_type not in permitted:
        findings.append(Finding("error", assignment_id, "work_type", "not in expert's permitted work types"))

    expert_markets = set(expert.get("jurisdictions", []))
    for market in markets:
        if market not in expert_markets and "EU" not in expert_markets and "GLOBAL" not in expert_markets:
            findings.append(Finding("error", assignment_id, "markets", f"{market} is outside the expert's verified jurisdictions"))

    expert_languages = set(expert.get("languages", []))
    for language in languages:
        if language not in expert_languages:
            findings.append(Finding("error", assignment_id, "languages", f"{language} is outside the expert's recorded language capability"))

    credentials_on = _as_date(assignment.get("credentials_checked_on"), field="credentials_checked_on", findings=findings, record_id=assignment_id)
    conflict_on = _as_date(assignment.get("conflict_checked_on"), field="conflict_checked_on", findings=findings, record_id=assignment_id)
    insurance_on = _as_date(assignment.get("insurance_checked_on"), field="insurance_checked_on", findings=findings, record_id=assignment_id)

    if credentials_on is None or (_days_old(credentials_on, as_of) or 0) > 365:
        findings.append(Finding("error", assignment_id, "credentials_checked_on", "must be current within 365 days"))
    if conflict_on is None or (_days_old(conflict_on, as_of) or 0) > 30:
        findings.append(Finding("error", assignment_id, "conflict_checked_on", "assignment-specific conflict check must be within 30 days"))
    if insurance_on is None or (_days_old(insurance_on, as_of) or 0) > 365:
        findings.append(Finding("error", assignment_id, "insurance_checked_on", "insurance/not-required determination must be current within 365 days"))

    for field in ("confidentiality_confirmed", "contract_confirmed", "compensation_confirmed"):
        if assignment.get(field) is not True:
            findings.append(Finding("error", assignment_id, field, "must be confirmed before activation"))

    sensitive = _require_string(assignment, "sensitive_data_access", findings, assignment_id)
    if sensitive and sensitive not in SENSITIVE_DATA_LEVELS:
        findings.append(Finding("error", assignment_id, "sensitive_data_access", f"unsupported value {sensitive!r}"))
    if sensitive and sensitive != "NONE":
        if assignment.get("data_terms_confirmed") is not True:
            findings.append(Finding("error", assignment_id, "data_terms_confirmed", "required when specialist receives personal/special-category data"))
        if not str(assignment.get("data_minimisation_note", "")).strip():
            findings.append(Finding("error", assignment_id, "data_minimisation_note", "required when specialist receives personal/special-category data"))

    if role == "DECISION_OWNER":
        if not str(assignment.get("authority_basis", "")).strip():
            findings.append(Finding("error", assignment_id, "authority_basis", "required for a reserved decision role"))
        if not str(assignment.get("governance_approval_id", "")).strip():
            findings.append(Finding("error", assignment_id, "governance_approval_id", "required for a reserved decision role"))

    return findings


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _collect_experts(raw: Any) -> list[dict[str, Any]]:
    rows = raw.get("experts") if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        raise ValueError("expert roster must be a JSON list or an object with an 'experts' list")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("every expert record must be a JSON object")
    return rows


def _collect_assignments(raw: Any) -> list[dict[str, Any]]:
    rows = raw.get("assignments") if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        raise ValueError("assignments must be a JSON list or an object with an 'assignments' list")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("every assignment record must be a JSON object")
    return rows


def render_findings(findings: Iterable[Finding]) -> str:
    rows = list(findings)
    if not rows:
        return "OK — no expert-network gate findings.\n"
    return "\n".join(item.render() for item in rows) + "\n"


def expert_network_validate() -> None:
    if len(sys.argv) not in {2, 3, 4}:
        raise SystemExit(
            "usage: clinicops-expert-network-validate <roster.json> "
            "[assignments.json] [YYYY-MM-DD]"
        )
    as_of = date.fromisoformat(sys.argv[3]) if len(sys.argv) == 4 else date.today()
    try:
        experts = _collect_experts(_load_json(sys.argv[1]))
        findings: list[Finding] = []
        by_id: dict[str, dict[str, Any]] = {}
        for expert in experts:
            findings.extend(validate_expert(expert, as_of=as_of))
            expert_id = str(expert.get("expert_id", ""))
            if expert_id:
                if expert_id in by_id:
                    findings.append(Finding("error", expert_id, "expert_id", "duplicate expert_id"))
                by_id[expert_id] = expert

        if len(sys.argv) >= 3:
            assignments = _collect_assignments(_load_json(sys.argv[2]))
            for assignment in assignments:
                expert_id = str(assignment.get("expert_id", ""))
                expert = by_id.get(expert_id)
                assignment_id = str(assignment.get("assignment_id", "<unknown-assignment>"))
                if expert is None:
                    findings.append(Finding("error", assignment_id, "expert_id", "expert not found in roster"))
                    continue
                findings.extend(validate_assignment(assignment, expert, as_of=as_of))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc

    print(render_findings(findings), end="")
    if any(item.severity == "error" for item in findings):
        raise SystemExit(2)
