"""Professional-claims gate (Proof & Credibility Directive, 2026-09-18).

Every founder/professional assertion on a public page must stay inside the
approved wordings in data/proof_public.json (the sanitized subset of the
private Professional Proof Register). This validator fails CI when:

- a page uses a credential/designation that is never claimable (RAC,
  cand.med., physician/licensure language, certification claims);
- "QPPV" appears outside the appointed-only boundary framing;
- an agency end-client name from the restricted lists appears on any page
  (client names live on the founder's own CV/LinkedIn, never on ClinicOps
  surfaces — RULES §28);
- the proof data file itself is malformed, or a proof entry is used while
  not marked verified;
- the About page drops the verified credential line or the boundary.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PROOF = ROOT / "data" / "proof_public.json"

# Never claimable on any ClinicOps surface (VERIFIED_PROFILE_FACTS §A0).
# Acronyms are matched on word boundaries so "RAC" never hits "practice".
FORBIDDEN_PHRASES = (
    "cand.med",
    "kandidatgrad i medicin",
    "board-certified",
    "specialist physician",
    "licensed physician",
    "medical doctor",
    "notified-body expert",
    "ISO-certified",
    "ISO certified",
    # Specialist Expertise directive §2/§5: the capability is public, the
    # network is not — no roster-shaped or recruitment language anywhere.
    "growing bench",
    "join our network",
)
FORBIDDEN_ACRONYMS = (re.compile(r"\bRAC\b"), re.compile(r"\bCCRA\b"))

# Agency end-client names: CV/LinkedIn-only, never on ClinicOps pages.
RESTRICTED_CLIENT_NAMES = (
    "Stryker",
    "Zimmer Biomet",
    "DePuy",
    "Smith+Nephew",
    "Smith & Nephew",
    "Cook Medical",
    "Medela",
    "AirLife",
    "Teleflex",
    "ConvaTec",
    "Coloplast",
    "Exactech",
    "Merit Medical",
    "Fisher & Paykel",
    "Galderma",
    "Wright Medical",
    "Brasseler",
    "Riverpoint",
    "Osteotec",
    "Straumann",
    "ClearCorrect",
    "Aiforia",
    "Tecomet",
    "Fillmed",
    "Heartcor",
    "Novo Nordisk",
    "Novartis",
    "Sanofi",
    "TransPerfect",
    "Welocalize",
)


def pages() -> list[Path]:
    return [
        p
        for p in DOCS.rglob("*.html")
        if p.name not in {"404.html", "clinical-operations.html"}
    ]


def main() -> int:
    errors: list[str] = []

    try:
        proof = json.loads(PROOF.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report and fail closed
        print(f"proof data unreadable: {exc}")
        return 1

    wordings = {p["id"]: p for p in proof.get("proofs", [])}
    for pid, entry in wordings.items():
        if entry.get("status") != "verified":
            errors.append(f"proof_public.json: {pid} is not marked verified")
        if not entry.get("public_wording", "").strip():
            errors.append(f"proof_public.json: {pid} has empty public wording")
        if entry.get("named_client_allowed"):
            errors.append(
                f"proof_public.json: {pid} allows named clients — not permitted "
                "on ClinicOps surfaces (RULES §28)"
            )

    for page in pages():
        html = page.read_text(encoding="utf-8")
        rel = page.relative_to(DOCS)
        for token in FORBIDDEN_PHRASES:
            if token.lower() in html.lower():
                errors.append(f"{rel}: forbidden professional claim token {token!r}")
        for pattern in FORBIDDEN_ACRONYMS:
            if pattern.search(html):
                errors.append(f"{rel}: forbidden credential acronym {pattern.pattern!r}")
        for name in RESTRICTED_CLIENT_NAMES:
            if name.lower() in html.lower():
                errors.append(f"{rel}: restricted client name {name!r} on a public page")
        if "QPPV" in html and "explicitly appointed" not in html:
            errors.append(
                f"{rel}: 'QPPV' outside the appointed-only boundary framing"
            )

    about = (DOCS / "about.html").read_text(encoding="utf-8")
    if "MSc in Medicine (Translational Medicine), Aalborg University" not in about:
        errors.append("about.html: verified credential line missing")
    if "explicitly appointed" not in about:
        errors.append("about.html: professional boundary statement missing")

    if errors:
        print("professional-claims contract FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"professional-claims contract: OK ({len(wordings)} approved wordings, {len(pages())} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
