from __future__ import annotations

from dataclasses import dataclass

from .transition_report import PortfolioRow

KNOWN_ROLES = {"MF", "AR", "IM", "PR"}
KNOWN_REGISTRATIONS = {"legacy", "mdr", "unknown", ""}


@dataclass(frozen=True)
class IntakeFinding:
    row_number: int
    severity: str
    field: str
    message: str


def validate_portfolio(rows: list[PortfolioRow]) -> list[IntakeFinding]:
    """Validate evidence completeness/consistency without making compliance conclusions."""
    findings: list[IntakeFinding] = []
    for index, row in enumerate(rows, start=2):  # CSV header is row 1.
        if not row.company.strip():
            findings.append(IntakeFinding(index, "error", "company", "company is required"))
        if not row.device.strip():
            findings.append(IntakeFinding(index, "error", "device", "device is required"))

        role = row.actor_role.strip().upper()
        if role not in KNOWN_ROLES:
            findings.append(
                IntakeFinding(
                    index,
                    "warning",
                    "actor_role",
                    f"unrecognised actor role '{row.actor_role or 'blank'}'; resolve before role-aware interpretation",
                )
            )

        registration = row.registration_type.strip().lower()
        if registration not in KNOWN_REGISTRATIONS:
            findings.append(
                IntakeFinding(
                    index,
                    "warning",
                    "registration_type",
                    f"unrecognised registration type '{row.registration_type}'",
                )
            )

        b_prefix = row.basic_udi_di.strip().upper().startswith("B-")
        if b_prefix and registration == "mdr":
            findings.append(
                IntakeFinding(
                    index,
                    "warning",
                    "registration_type",
                    "MDR label conflicts with B-prefix legacy screening signal; verify source data",
                )
            )

        if row.is_manufacturer and row.is_legacy and not row.certificate_expiry.strip():
            findings.append(
                IntakeFinding(
                    index,
                    "warning",
                    "certificate_expiry",
                    "legacy manufacturer row has no certificate/transition date; timing cannot be prioritised",
                )
            )

        if row.danish_market.strip().lower() in {"", "unknown"}:
            findings.append(
                IntakeFinding(
                    index,
                    "info",
                    "danish_market",
                    "Danish-market relevance is unresolved",
                )
            )

        if not row.source_url.strip():
            findings.append(
                IntakeFinding(
                    index,
                    "warning",
                    "source_url",
                    "no evidence URL recorded for this row",
                )
            )
    return findings


def render_intake_findings(findings: list[IntakeFinding]) -> str:
    if not findings:
        return "Portfolio intake: no structural/evidence findings.\n"
    counts = {
        severity: sum(item.severity == severity for item in findings)
        for severity in ("error", "warning", "info")
    }
    lines = [
        "# Portfolio intake diagnostics",
        "",
        f"- Errors: **{counts['error']}**",
        f"- Warnings: **{counts['warning']}**",
        f"- Information gaps: **{counts['info']}**",
        "",
        "> These are evidence-quality and structural diagnostics, not compliance findings.",
        "",
    ]
    for item in findings:
        lines.append(
            f"- Row {item.row_number} [{item.severity}] `{item.field}` — {item.message}"
        )
    return "\n".join(lines) + "\n"
