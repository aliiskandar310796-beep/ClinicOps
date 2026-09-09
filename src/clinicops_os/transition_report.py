from __future__ import annotations

import csv
from dataclasses import dataclass, fields
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class PortfolioRow:
    company: str
    device: str
    actor_role: str
    registration_type: str
    basic_udi_di: str = ""
    certificate_expiry: str = ""
    danish_market: str = "unknown"
    linked_sscp: str = "unknown"
    source_url: str = ""
    notes: str = ""

    @property
    def is_manufacturer(self) -> bool:
        return self.actor_role.strip().upper() == "MF"

    @property
    def is_pack_role(self) -> bool:
        return self.actor_role.strip().upper() == "PR"

    @property
    def is_legacy(self) -> bool:
        explicit = self.registration_type.strip().lower() == "legacy"
        b_prefix = self.basic_udi_di.strip().upper().startswith("B-")
        return explicit or b_prefix

    @property
    def is_danish_market(self) -> bool:
        return self.danish_market.strip().lower() in {"yes", "true", "1", "confirmed"}

    def expiry_date(self) -> date | None:
        if not self.certificate_expiry.strip():
            return None
        return datetime.strptime(  # noqa: DTZ007 — input is a date-only field by design.
            self.certificate_expiry.strip(),
            "%Y-%m-%d",
        ).date()

    def workstream(self, as_of: date) -> str:
        if self.is_pack_role:
            return "Separate PR/system-procedure-pack review"
        if not self.is_manufacturer:
            return "Role/scope review"
        if self.is_legacy:
            expiry = self.expiry_date()
            if expiry:
                days = (expiry - as_of).days
                if days < 0:
                    return "Legacy record — certificate date passed; verify transition status"
                if days <= 180:
                    return "Legacy → MDR transition: urgent work-plan review"
                if days <= 365:
                    return "Legacy → MDR transition: near-term work-plan review"
            return "Legacy → MDR transition: timing to establish"
        return "MDR manufacturer record — monitor document/market-language controls"

    def priority_score(self, as_of: date) -> int:
        """Operator triage score, not a regulatory risk or compliance score."""
        score = 0
        if self.is_manufacturer and self.is_legacy:
            score += 50
            expiry = self.expiry_date()
            if expiry:
                days = (expiry - as_of).days
                if days < 0:
                    score += 35
                elif days <= 90:
                    score += 30
                elif days <= 180:
                    score += 25
                elif days <= 365:
                    score += 15
            else:
                score += 10
        elif self.is_manufacturer:
            score += 10
        elif self.is_pack_role:
            score += 5

        if self.is_danish_market:
            score += 20
        if self.source_url.strip():
            score += 3
        return score

    def evidence_note(self) -> str:
        notes = []
        if self.basic_udi_di.strip().upper().startswith("B-"):
            notes.append("B-prefix used only as a derived legacy screening signal")
        if self.linked_sscp.strip().lower() in {"no", "false", "0", "null"}:
            notes.append("absence of linked SS(C)P is not treated as non-compliance")
        return "; ".join(notes)


def load_portfolio(path: str | Path) -> list[PortfolioRow]:
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"company", "device", "actor_role", "registration_type"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
        known = {field.name for field in fields(PortfolioRow)}
        return [
            PortfolioRow(
                **{
                    key: (value or "")
                    for key, value in row.items()
                    if key in known
                }
            )
            for row in reader
        ]


def render_markdown(
    rows: list[PortfolioRow],
    *,
    as_of: date,
    title: str = "ClinicOps Portfolio Transition Brief",
) -> str:
    legacy_mf = [r for r in rows if r.is_manufacturer and r.is_legacy]
    mdr_mf = [r for r in rows if r.is_manufacturer and not r.is_legacy]
    packs = [r for r in rows if r.is_pack_role]
    danish = [r for r in rows if r.is_danish_market]

    out = [
        f"# {title}",
        "",
        f"**As of:** {as_of.isoformat()}",
        "",
        "> Work-plan screening from supplied/public metadata. This is not a compliance determination or a full-register audit.",
        "",
        "## Portfolio snapshot",
        "",
        f"- Records reviewed: **{len(rows)}**",
        f"- Manufacturer-role legacy/legacy-screened records: **{len(legacy_mf)}**",
        f"- Manufacturer-role MDR/non-legacy records: **{len(mdr_mf)}**",
        f"- PR/system-procedure-pack records: **{len(packs)}**",
        f"- Confirmed Danish-market rows: **{len(danish)}**",
        "",
        "## Prioritised work plan",
        "",
        "> Priority is an operator triage score only; it is not a regulatory risk, compliance, or legal-conclusion score.",
        "",
        "| Priority | Company | Device | Role | Registration | Certificate expiry | Danish market | Workstream |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    ordered = sorted(
        rows,
        key=lambda row: (
            -row.priority_score(as_of),
            row.company.lower(),
            row.device.lower(),
        ),
    )
    for row in ordered:
        out.append(
            "| "
            + " | ".join(
                [
                    str(row.priority_score(as_of)),
                    row.company or "—",
                    row.device or "—",
                    row.actor_role or "—",
                    row.registration_type or "—",
                    row.certificate_expiry or "—",
                    row.danish_market or "unknown",
                    row.workstream(as_of),
                ]
            )
            + " |"
        )

    cautions = sorted({r.evidence_note() for r in rows if r.evidence_note()})
    out.extend(["", "## Interpretation constraints", ""])
    out.extend(
        [
            "- Separate manufacturer (MF) registrations from PR/system-procedure-pack records before interpreting class or SS(C)P fields.",
            "- A B-prefix is used here only as a ClinicOps-derived screening signal; do not quote it as a Commission rule.",
            "- No conclusion about SS(C)P compliance is drawn solely from a null/absent public link.",
            "- Certificate dates and Danish-market presence require source verification before external use.",
            "- Public API reachability limitations mean this report must not be described as an end-to-end audit of EUDAMED.",
        ]
    )
    if cautions:
        out.extend(
            ["", "### Row-level derived cautions", ""]
            + [f"- {c}" for c in cautions]
        )

    out.extend(
        [
            "",
            "## Recommended next questions",
            "",
            "1. Which legacy manufacturer-role devices have the earliest verified certificate/transition dates?",
            "2. Which of those devices are confirmed to be placed on the Danish market?",
            "3. For each transition, who owns Basic UDI-DI creation, SS(C)P validation/linkage, Danish-language availability and change control?",
            "4. Which evidence is already portfolio-controlled by the AR/manufacturer, and which must be obtained from the notified body or manufacturer?",
        ]
    )
    return "\n".join(out) + "\n"
