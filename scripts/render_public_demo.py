from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from clinicops_os.client_report import render_client_html
from clinicops_os.transition_report import load_portfolio

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "portfolio.csv"
OUTPUT = ROOT / "docs" / "transition-map-sample" / "index.html"
DEMO_DATE = date(2026, 9, 10)
TITLE = "ClinicOps Class III Transition Map — Sanitized Sample"
CANONICAL = "https://clinicops.dk/transition-map-sample/"
DESCRIPTION = (
    "Sanitized fictional sample of the ClinicOps Class III Transition Map "
    "work-plan format."
)


def render_public_demo() -> str:
    rows = load_portfolio(SOURCE)
    html = render_client_html(rows, as_of=DEMO_DATE, title=TITLE)

    metadata = f'''<link rel="canonical" href="{CANONICAL}">
<meta name="description" content="{DESCRIPTION}">
<meta property="og:title" content="Class III Transition Map Sample | ClinicOps">
<meta property="og:description" content="{DESCRIPTION}">
<meta property="og:type" content="website">
<meta property="og:url" content="{CANONICAL}">
<meta property="og:site_name" content="ClinicOps">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"Class III Transition Map Sample | ClinicOps","description":"{DESCRIPTION}","url":"{CANONICAL}","isPartOf":{{"@type":"WebSite","name":"ClinicOps","url":"https://clinicops.dk/"}},"publisher":{{"@type":"Organization","name":"ClinicOps","url":"https://clinicops.dk/"}}}}</script>
'''
    html = html.replace("<style>", metadata + "<style>", 1)
    html = html.replace(
        "<body>",
        '<body>\n<div class="notice"><strong>Sanitized fictional sample.</strong> '
        "This page illustrates the ClinicOps portfolio transition work-plan format. "
        "It is not a compliance determination, legal conclusion, or full-register audit."
        "</div>",
        1,
    )
    html = html.replace(
        "</body>",
        '''<section class="notice"><h2>Want this applied to a real portfolio?</h2><p><strong>What to bring:</strong> start with a small portfolio export or agreed record set. Known identifiers, certificate timing and target-market context help; missing evidence can stay explicit rather than being guessed.</p><p><strong>What a scoped pilot produces:</strong> a prioritised work plan, evidence-gap queue and human-reviewed next steps grounded in the supplied or reachable evidence. The responsible regulatory team retains final judgement.</p><p><a href="/assessment-intake.html"><strong>Build an assessment brief</strong></a> · <a href="mailto:info@clinicops.dk?subject=Class%20III%20Transition%20Map%20Assessment">Email ClinicOps directly</a> · <a href="/readiness-score.html">Use the free readiness score</a> · <a href="/">Back to ClinicOps</a></p></section>
</body>''',
        1,
    )
    return html


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = render_public_demo()
    if args.check:
        existing = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if existing != rendered:
            raise SystemExit(
                "public Transition Map sample is stale; "
                "run `python scripts/render_public_demo.py`"
            )
        print("public Transition Map sample: OK")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
