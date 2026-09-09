from __future__ import annotations

import json
from pathlib import Path
import sys
from datetime import date

from .fleet import FleetRegistry
from .scoring import Idea, rank_ideas
from .transition_report import load_portfolio, render_markdown


def fleet_status() -> None:
    root = Path(__file__).resolve().parents[2]
    fleet = FleetRegistry.load(root / "agents" / "fleet.json")
    print(f"ClinicOps fleet: {len(fleet.agents)} specialized loops")
    for agent in fleet.by_min_leverage(0):
        print(f"{agent.leverage:>2}/10  {agent.name:<28} {agent.cadence:<15} {agent.mission}")


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
        raise SystemExit("usage: clinicops-portfolio-report <portfolio.csv> [YYYY-MM-DD]")
    as_of = date.fromisoformat(sys.argv[2]) if len(sys.argv) == 3 else date.today()
    rows = load_portfolio(sys.argv[1])
    print(render_markdown(rows, as_of=as_of), end="")
