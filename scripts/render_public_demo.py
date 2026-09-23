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
# Fictional records must not carry fake evidence URLs. A sanitized fixture row
# either has a real, reachable source or a blank source_url rendered as "—".
FORBIDDEN_PLACEHOLDER_DOMAINS = ("example.com", "example.org", "example.net", "test.invalid")

# Shared public shell: same stylesheet, fonts and navigation as every other docs/ page.
SHELL_HEAD = (
    '<link rel="preload" href="../assets/fonts/geist-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>'
    '<link rel="preload" href="../assets/fonts/geist-mono-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>'
    '<link rel="stylesheet" href="../site.css">\n'
    '<meta name="color-scheme" content="light dark">'
    '<meta name="theme-color" content="#f6f7f5" media="(prefers-color-scheme: light)">'
    '<meta name="theme-color" content="#0d1211" media="(prefers-color-scheme: dark)">'
)
SHELL_HEADER = (
    '<a class="skip-link" href="#main">Skip to content</a>'
    '<header class="site"><div class="site-inner"><a class="brand" href="../index.html">Clinic<span>Ops</span></a>'
    '<nav class="primary" aria-label="Primary"><a href="../index.html">Home</a><a href="../services.html">Solution</a>'
    '<a href="../use-cases.html">Use cases</a><a href="../research.html">Research</a>'
    '<a href="../tools.html" aria-current="page">Tools</a><a href="../about.html">About</a>'
    '<a href="../contact.html">Contact</a></nav></div></header>'
    '<script>(function(){var n=document.querySelector("nav.primary"),a=n&&n.querySelector("[aria-current]");'
    'if(a&&n.scrollWidth>n.clientWidth)n.scrollLeft=Math.max(0,a.offsetLeft-32)})()</script>\n'
)


def render_public_demo() -> str:
    rows = load_portfolio(SOURCE)
    html = render_client_html(rows, as_of=DEMO_DATE, title=TITLE, site_shell=True)

    metadata = f'''<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/assets/favicon-32.png" sizes="32x32" type="image/png"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="canonical" href="{CANONICAL}">
<meta name="description" content="{DESCRIPTION}">
<meta property="og:title" content="Class III Transition Map Sample | ClinicOps">
<meta property="og:description" content="{DESCRIPTION}">
<meta property="og:type" content="website">
<meta property="og:url" content="{CANONICAL}">
<meta property="og:site_name" content="ClinicOps">
<meta property="og:image" content="https://clinicops.dk/assets/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="https://clinicops.dk/assets/og-image.png">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"Class III Transition Map Sample | ClinicOps","description":"{DESCRIPTION}","url":"{CANONICAL}","isPartOf":{{"@type":"WebSite","name":"ClinicOps","url":"https://clinicops.dk/"}},"publisher":{{"@type":"Organization","name":"ClinicOps","url":"https://clinicops.dk/"}}}}</script>
'''
    html = html.replace("<style>", metadata + "<style>", 1)
    html = html.replace("</style>\n</head>", "</style>\n" + SHELL_HEAD + "</head>", 1)
    html = html.replace(
        '<main id="main" tabindex="-1" class="wrap">\n',
        '<main id="main" tabindex="-1" class="wrap">\n<div class="notice"><strong>Sanitized fictional sample.</strong> '
        "This page illustrates the ClinicOps portfolio transition work-plan format. "
        "It is not a compliance determination, legal conclusion, or full-register audit."
        "</div>",
        1,
    )
    html = html.replace("<body>\n", "<body>\n" + SHELL_HEADER, 1)
    html = html.replace(
        "</main>",
        '''<section class="notice"><h2>Want this applied to a real portfolio?</h2><p><strong>What to bring:</strong> start with a small portfolio export or agreed record set. Known identifiers, certificate timing and target-market context help; missing evidence can stay explicit rather than being guessed.</p><p><strong>What a scoped pilot produces:</strong> a prioritised work plan, evidence-gap queue and human-reviewed next steps grounded in the supplied or reachable evidence. The responsible regulatory team retains final judgement.</p><p><a href="/assessment-intake.html"><strong>Build an assessment brief</strong></a> · <a href="mailto:info@clinicops.dk?subject=Class%20III%20Transition%20Map%20Assessment">Email ClinicOps directly</a> · <a href="/readiness-score.html">Use the free readiness score</a> · <a href="/privacy-notice/">Privacy</a> · <a href="/">Back to ClinicOps</a></p></section>
</main>''',
        1,
    )
    for domain in FORBIDDEN_PLACEHOLDER_DOMAINS:
        if domain in html:
            raise SystemExit(
                f"public Transition Map sample contains placeholder domain "
                f"'{domain}'; fix examples/portfolio.csv (blank source_url for "
                "fictional records) instead of publishing fake evidence links"
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
