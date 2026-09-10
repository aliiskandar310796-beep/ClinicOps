from __future__ import annotations

import json
from pathlib import Path

from clinicops_os.scoring import Idea, rank_ideas

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "examples" / "service_entry_ideas.json"


def _load_ranked() -> list[Idea]:
    raw = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = raw["ideas"]
    return rank_ideas([Idea.from_dict(row) for row in rows])


def test_service_entry_example_is_valid_unique_and_rankable() -> None:
    ranked = _load_ranked()
    names = [idea.name for idea in ranked]

    assert len(ranked) == 14
    assert len(names) == len(set(names))
    assert ranked[0].name == "Class III Transition Map Pilot"


def test_only_flagship_is_default_do_now() -> None:
    ranked = _load_ranked()
    do_now = [idea.name for idea in ranked if idea.decision == "DO NOW"]

    assert do_now == ["Class III Transition Map Pilot"]


def test_adjacent_entries_require_validation_before_activation() -> None:
    decisions = {idea.name: idea.decision for idea in _load_ranked()}

    assert decisions["Portfolio Evidence Triage"] == "TEST"
    assert decisions["Identifier + Certificate Reconciliation Sprint"] == "TEST"
    assert decisions["AR / Consultancy White-Label Portfolio Desk"] == "TEST"
    assert decisions["Productized Operator Packs"] == "BACKLOG"


def test_emerging_entries_stay_in_test_not_do_now() -> None:
    decisions = {idea.name: idea.decision for idea in _load_ranked()}

    assert decisions["IVDR Transition Evidence Triage (watchlist)"] == "TEST"
    assert decisions["EUDAMED Vigilance/PMS Readiness (watchlist)"] == "TEST"
