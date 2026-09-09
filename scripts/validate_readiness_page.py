from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "readiness-score.html"
CONFIG_RE = re.compile(
    r'<script type="application/json" id="score-config">\s*(.*?)\s*</script>',
    re.DOTALL,
)


def main() -> None:
    text = PAGE.read_text(encoding="utf-8")
    match = CONFIG_RE.search(text)
    if not match:
        raise SystemExit("readiness-score.html is missing score-config JSON")

    config = json.loads(match.group(1))
    questions = config.get("questions")
    if not isinstance(questions, list) or not 5 <= len(questions) <= 8:
        raise SystemExit("readiness score must contain 5-8 questions")

    weights = [question.get("weight") for question in questions]
    if any(not isinstance(weight, int) or weight <= 0 for weight in weights):
        raise SystemExit("every readiness question needs a positive integer weight")
    if sum(weights) != 100:
        raise SystemExit(f"readiness weights must total 100, got {sum(weights)}")

    ids = [question.get("id") for question in questions]
    if len(ids) != len(set(ids)):
        raise SystemExit("readiness question IDs must be unique")

    for question in questions:
        options = question.get("options")
        if not isinstance(options, dict) or len(options) < 2:
            raise SystemExit(f"{question.get('id')} needs at least two options")
        for option in options.values():
            factor = option.get("factor")
            if not isinstance(factor, (int, float)) or not 0 <= factor <= 1:
                raise SystemExit("readiness option factor must be between 0 and 1")
            if factor < 1 and not str(option.get("gap", "")).strip():
                raise SystemExit(
                    "non-full-score readiness options require a gap message"
                )

    bands = config.get("bands")
    if not isinstance(bands, list) or not bands:
        raise SystemExit("readiness score needs output bands")
    covered: set[int] = set()
    for band in bands:
        low = band.get("min")
        high = band.get("max")
        if not isinstance(low, int) or not isinstance(high, int) or low > high:
            raise SystemExit("invalid readiness band")
        covered.update(range(low, high + 1))
    if covered != set(range(101)):
        raise SystemExit("readiness bands must cover every score from 0 through 100")

    required_copy = (
        "Nothing is sent to ClinicOps",
        "not a regulatory determination",
        "Request a Regulatory Intelligence Assessment",
        "Resolve unresolved points against EUDAMED and your RA/QA team",
    )
    for phrase in required_copy:
        if phrase not in text:
            raise SystemExit(f"readiness page missing required copy: {phrase}")

    forbidden_network = ("fetch(", "XMLHttpRequest", "sendBeacon(", "WebSocket(")
    for token in forbidden_network:
        if token in text:
            raise SystemExit(f"readiness page must stay local-only; found {token}")

    print("readiness page contract: OK")


if __name__ == "__main__":
    main()
