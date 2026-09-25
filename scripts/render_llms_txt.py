from __future__ import annotations

import argparse
from pathlib import Path
from xml.etree import ElementTree

from clinicops_os.site_quality import parse_metadata

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LLMS = DOCS / "llms.txt"
SITEMAP = DOCS / "sitemap.xml"
BASE = "https://clinicops.dk/"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

INTRO = """# ClinicOps

ClinicOps is a Danish-led, EU-wide evidence-controlled clinical and life-sciences operations company. Denmark is the local-market and localisation anchor; delivery is English-first and EU-wide, with Danish language, authority and professional expertise brought into scope when relevant.
"""

# Section title -> predicate on the path relative to the site root.
SECTIONS = (
    ("Core pages", lambda r: r in {"index.html", "services.html", "use-cases.html", "about.html", "contact.html", "assessment-intake.html"}),
    ("Solution and use cases", lambda r: r in {
        "integrity-gate.html", "evidence-change-control-pack.html", "denmark-market-access.html",
        "eu-mdr-regulatory-integrity.html", "eudamed-transition.html", "class-iii-transition.html",
        "sscp-operations.html", "authorised-representative-portfolio-intelligence.html",
        "medical-device-document-control.html", "regulatory-intelligence.html", "expert-network.html",
        "what-a-pilot-looks-like.html", "evidence-pack-checklist.html",
    }),
    ("Free browser-local tools and examples", lambda r: r in {
        "tools.html", "integrity-check.html", "integrity-scanner.html", "integrity-economics.html",
        "identifier-check.html", "readiness-score.html", "change-surface-mapper.html",
        "regulatory-change-impact.html", "technical-file-consistency.html",
        "specimen-register/index.html", "transition-map-sample/index.html",
        "danish-pv-literature-register.html", "sdea-clause-checker.html", "danish-dhpc-checker.html",
    }),
    ("Research and primary sources", lambda r: r in {"research.html", "primary-sources.html"} or r.startswith("research/")),
    ("Policies", lambda r: r.startswith("privacy-notice/")),
)

OUTRO = """Operating boundaries:
- ClinicOps structures evidence, reconciliation and operational change; it does not turn machine findings into legal, regulatory, clinical, safety, quality or compliance determinations.
- Missing public records or links do not by themselves establish non-compliance.
- Source authority, professional judgement and release decisions remain explicit human responsibilities.
- Public-source coverage is bounded by the declared method and evidence population.
- Independent experts are engaged only within a defined project scope after credential, availability and conflict checks; their participation does not transfer reserved professional authority to ClinicOps.

Contact: info@clinicops.dk
Canonical site: https://clinicops.dk/
"""


def _local_path(url: str) -> Path:
    relative = url[len(BASE):]
    if relative == "" or relative.endswith("/"):
        relative += "index.html"
    return DOCS / relative


def _clean(text: str) -> str:
    return " ".join(text.split())


def sitemap_urls() -> list[str]:
    root = ElementTree.parse(SITEMAP).getroot()
    return [el.text.strip() for el in root.findall("sm:url/sm:loc", NS) if el.text]


def render() -> str:
    entries: dict[str, list[tuple[str, str, str]]] = {title: [] for title, _ in SECTIONS}
    for url in sitemap_urls():
        path = _local_path(url)
        relative = path.relative_to(DOCS).as_posix()
        meta = parse_metadata(path.read_text(encoding="utf-8"))
        title = _clean(meta.title or relative)
        description = _clean(meta.meta.get("description", ""))
        for section, matches in SECTIONS:
            if matches(relative):
                entries[section].append((url, title, description))
                break
        else:
            raise SystemExit(f"{relative}: not assigned to an llms.txt section; update SECTIONS")
    lines = [INTRO.rstrip("\n"), ""]
    for section, _ in SECTIONS:
        rows = sorted(entries[section], key=lambda row: row[0])
        if not rows:
            continue
        lines.append(f"{section}:")
        for url, title, description in rows:
            lines.append(f"- {title}: {url}" + (f" - {description}" if description else ""))
        lines.append("")
    return "\n".join(lines) + "\n" + OUTRO


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render()
    if args.check:
        existing = LLMS.read_text(encoding="utf-8") if LLMS.exists() else ""
        if existing != rendered:
            raise SystemExit("docs/llms.txt is stale; run `python scripts/render_llms_txt.py`")
        print("llms.txt contract: OK")
        return
    LLMS.write_text(rendered, encoding="utf-8")
    print(f"wrote {LLMS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
