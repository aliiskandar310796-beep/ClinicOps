from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from .claim_registry import audit_registry, load_registry, render_matrix
from .fleet import FleetRegistry
from .intake import render_intake_findings, validate_portfolio
from .publication import build_publication_pack, render_publication_pack
from .scoring import Idea, rank_ideas
from .transition_report import load_portfolio, render_markdown


def fleet_status() -> None:
    root = Path(__file__).resolve().parents[2]
    fleet = FleetRegistry.load(root / "agents" / "fleet.json")
    print(f"ClinicOps fleet: {len(fleet.agents)} specialized loops")
    for agent in fleet.by_min_leverage(0):
        print(
            f"{agent.leverage:>2}/10  {agent.name:<28} "
            f"{agent.cadence:<15} {agent.mission}"
        )


def rank_opportunities() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: clinicops-rank-opportunities <ideas.json>")
    path = Path(sys.argv[1])
    raw = json.loads(path.read_text(encoding="utf-8"))
    rows = raw.get("ideas", raw) if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        raise SystemExit("input must be a JSON list or an object with an 'ideas' list")

    ranked = rank_ideas([Idea.from_dict(row) for row in rows])
    print(f"{'#':>2}  {'Score':>5}  {'Decision':<10}  Opportunity")
    print("--  -----  ----------  -----------")
    for idx, idea in enumerate(ranked, start=1):
        print(f"{idx:>2}  {idea.score:>5.2f}  {idea.decision:<10}  {idea.name}")


def portfolio_report() -> None:
    if len(sys.argv) not in {2, 3}:
        raise SystemExit(
            "usage: clinicops-portfolio-report <portfolio.csv> [YYYY-MM-DD]"
        )
    as_of = (
        date.fromisoformat(sys.argv[2])
        if len(sys.argv) == 3
        else date.today()  # noqa: DTZ011 — report semantics intentionally use local calendar date.
    )
    rows = load_portfolio(sys.argv[1])
    print(render_markdown(rows, as_of=as_of), end="")


def portfolio_validate() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: clinicops-portfolio-validate <portfolio.csv>")
    rows = load_portfolio(sys.argv[1])
    findings = validate_portfolio(rows)
    print(render_intake_findings(findings), end="")
    if any(item.severity == "error" for item in findings):
        raise SystemExit(2)


def claims_status() -> None:
    if len(sys.argv) not in {1, 2, 3}:
        raise SystemExit("usage: clinicops-claims [registry.jsonl] [YYYY-MM-DD]")
    root = Path(__file__).resolve().parents[2]
    path = Path(sys.argv[1]) if len(sys.argv) >= 2 else root / "research" / "claims.jsonl"
    as_of = (
        date.fromisoformat(sys.argv[2])
        if len(sys.argv) == 3
        else date.today()  # noqa: DTZ011 — operator-facing status uses local calendar date.
    )
    claims = load_registry(path)
    findings = audit_registry(claims, as_of=as_of)
    print(render_matrix(claims, as_of=as_of), end="")
    if findings:
        print("\n## Registry audit")
        for item in findings:
            print(f"- [{item.severity}] {item.claim_id}: {item.message}")


def publication_pack() -> None:
    if len(sys.argv) not in {3, 4, 5}:
        raise SystemExit(
            "usage: clinicops-publication-pack <title> <claim-id,...> "
            "[use] [YYYY-MM-DD]"
        )
    root = Path(__file__).resolve().parents[2]
    title = sys.argv[1]
    claim_ids = [item.strip() for item in sys.argv[2].split(",") if item.strip()]
    use = sys.argv[3] if len(sys.argv) >= 4 else "research-note"
    as_of = (
        date.fromisoformat(sys.argv[4])
        if len(sys.argv) == 5
        else date.today()  # noqa: DTZ011 — operator-facing pack uses local calendar date.
    )
    claims = load_registry(root / "research" / "claims.jsonl")
    pack = build_publication_pack(
        claims,
        claim_ids,
        title=title,
        use=use,
        as_of=as_of,
    )
    print(render_publication_pack(pack), end="")
