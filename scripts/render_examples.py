from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from clinicops_os.transition_report import load_portfolio, render_markdown

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "examples" / "portfolio.csv"
OUTPUT = ROOT / "examples" / "portfolio_report.md"
AS_OF = date(2026, 9, 9)


def render() -> str:
    return render_markdown(load_portfolio(INPUT), as_of=AS_OF)


def main() -> int:
    expected = render()
    if "--check" in sys.argv:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            print(
                "examples/portfolio_report.md is stale; "
                "run: python scripts/render_examples.py"
            )
            return 1
        print("sanitized portfolio report fixture is current")
        return 0

    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
