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
    assert ranked[0].name == "Portfolio Evidence Triage"
    assert ranked[0].decision == "DO NOW"


def test_emerging_entries_stay_in_test_not_do_now() -> None:
    decisions = {idea.name: idea.decision for idea in _load_ranked()}

    assert decisions["IVDR Transition Evidence Triage (watchlist)"] == "TEST"
    assert decisions["EUDAMED Vigilance/PMS Readiness (watchlist)"] == "TEST"
