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


def test_public_degree_wording_uses_official_program_titles() -> None:
    docs = ROOT / "docs"
    public = "\n".join(
        path.read_text(encoding="utf-8")
        for path in docs.rglob("*.html")
        if path.name not in {"404.html", "clinical-operations.html"}
    )
    assert "MSc in Medicine (Translational Medicine)" not in public
    assert "Bachelor of Medicine, Aalborg University" not in public
    about = (docs / "about.html").read_text(encoding="utf-8")
    assert "Master of Science (MSc) in Medicine with Industrial Specialisation (Translational Medicine), Aalborg University" in about
    assert "Bachelor of Science (BSc) in Medicine with Industrial Specialisation, Aalborg University" in about
