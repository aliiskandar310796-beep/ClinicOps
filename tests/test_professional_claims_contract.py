"""The professional-claims gate must stay green and stay wired into CI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_professional_claims_validator_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_professional_claims.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_ci_runs_the_professional_claims_gate() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "validate_professional_claims.py" in ci


def test_proof_data_keeps_qsr_unpublished() -> None:
    proof = json.loads((ROOT / "data" / "proof_public.json").read_text(encoding="utf-8"))
    pending = {p["id"] for p in proof.get("pending_verification", [])}
    assert "proof-pharma-qsr" in pending, "QSR must stay pending until the founder verifies its meaning and scope"
    assert all(p["id"] != "proof-pharma-qsr" for p in proof["proofs"])


def test_public_site_is_independent_of_any_individual() -> None:
    """Decision 2026-11-14 (owner): the public structure names no individual and
    carries no personal biography, degree, language list or personal profile link.

    Three places keep an identity because the law or a registry requires it: the
    privacy notice (GDPR controller identification), the registered-actor block on
    the EU authorised representative page, and the contact address. Nothing else may.
    """
    docs = ROOT / "docs"
    allowed = {"privacy-notice/index.html", "eu-authorised-representative.html"}
    forbidden = ("Iskandar", "Aalborg University", "Bachelor of Medicine", "linkedin.com/in/", "Industrial Specialisation")
    offenders = []
    for path in list(docs.rglob("*.html")) + [docs / "llms.txt"]:
        rel = path.relative_to(docs).as_posix()
        if rel in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        offenders += [f"{rel}: {tok}" for tok in forbidden if tok in text]
    assert not offenders, offenders
    about = (docs / "about.html").read_text(encoding="utf-8")
    assert "explicitly appointed" in about
