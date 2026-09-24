#!/usr/bin/env python3
"""Honest pipeline counts by evidence-ladder level (stdlib only).

Reads the discovery ledger and the pipeline CSV. Rows marked simulated are
refused. Rows claiming E4+ without genuine human interaction or a private
evidence reference are refused. Prints ``NO EVIDENCE YET`` when nothing valid.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "sales" / "discovery" / "discovery_ledger.csv"
PIPELINE = ROOT / "revenue" / "pipeline" / "pipeline.csv"

LEVELS = [f"E{i}" for i in range(10)]
_TRUE = {"true", "yes", "y", "1", "x"}
_LEVEL_RE = re.compile(r"^\s*E?([0-9])\s*$", re.IGNORECASE)


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in _TRUE


def parse_level(value: str | None) -> str | None:
    match = _LEVEL_RE.match(value or "")
    return f"E{match.group(1)}" if match else None


def read_rows(path: Path) -> list[dict[str, str]]:
    """Return rows as dicts; a missing or header-only file yields []."""
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def classify(rows: list[dict[str, str]]) -> tuple[Counter, list[str]]:
    """Count valid rows by level; return (counts, refusal messages)."""
    counts: Counter = Counter()
    refused: list[str] = []
    for index, row in enumerate(rows, start=2):  # line 1 is the header
        row = {(k or "").strip().lower(): v for k, v in row.items()}
        if not any((v or "").strip() for v in row.values()):
            continue
        if _truthy(row.get("simulated")) or _truthy(row.get("is_simulated")):
            refused.append(f"line {index}: simulated row refused")
            continue
        level = parse_level(row.get("evidence_level") or row.get("level"))
        if level is None:
            refused.append(f"line {index}: missing or invalid evidence level")
            continue
        if int(level[1]) >= 4:
            human = row.get("human_interaction")
            if human is not None and not _truthy(human):
                refused.append(f"line {index}: {level} without human interaction")
                continue
            ref = row.get("evidence_ref")
            if ref is not None and not ref.strip():
                refused.append(f"line {index}: {level} without private evidence_ref")
                continue
        counts[level] += 1
    return counts, refused


def render(name: str, counts: Counter, refused: list[str]) -> list[str]:
    lines = [f"== {name} =="]
    if not counts:
        lines.append("NO EVIDENCE YET")
    else:
        for level in LEVELS:
            if counts[level]:
                lines.append(f"{level}: {counts[level]}")
        buyer = sum(counts[lv] for lv in LEVELS[4:])
        lines.append(f"Buyer evidence (E4+): {buyer}")
    for message in refused:
        lines.append(f"REFUSED {message}")
    return lines


def build_report(ledger: Path = LEDGER, pipeline: Path = PIPELINE) -> str:
    out: list[str] = []
    for name, path in (("discovery ledger", ledger), ("pipeline", pipeline)):
        counts, refused = classify(read_rows(path))
        out.extend(render(name, counts, refused))
    return "\n".join(out)


def main() -> int:
    print(build_report())
    return 0


if __name__ == "__main__":
    sys.exit(main())
