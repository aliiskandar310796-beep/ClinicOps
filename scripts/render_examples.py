from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from clinicops_os.transition_report import load_portfolio, render_json, render_markdown

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "examples" / "portfolio.csv"
MARKDOWN_OUTPUT = ROOT / "examples" / "portfolio_report.md"
JSON_OUTPUT = ROOT / "examples" / "portfolio_report.json"
AS_OF = date(2026, 9, 9)


def render() -> dict[Path, str]:
    rows = load_portfolio(INPUT)
    return {
        MARKDOWN_OUTPUT: render_markdown(rows, as_of=AS_OF),
        JSON_OUTPUT: render_json(rows, as_of=AS_OF),
    }


def main() -> int:
    expected = render()
    if "--check" in sys.argv:
        stale = [
            path
            for path, content in expected.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            for path in stale:
                print(
                    f"{path.relative_to(ROOT)} is stale; "
                    "run: python scripts/render_examples.py"
                )
            return 1
        print("sanitized portfolio report fixtures are current")
        return 0

    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
