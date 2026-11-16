"""WP-17: the machines-and-people statement is bounded and sourced."""
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def test_about_statement_is_bounded_and_registered() -> None:
    about = (ROOT / "docs" / "about.html").read_text(encoding="utf-8")
    assert 'id="machines-and-people"' in about
    assert "do not use a language model" in about
    assert "does not claim to comply" in about
    assert "not devices" in about
    assert "CO-CLM-0022" in about
    claims = [json.loads(x) for x in (ROOT / "research" / "claims.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    entry = next(c for c in claims if c["id"] == "CO-CLM-0022")
    assert entry["status"] == "qualified" and "website" in entry["allowed_uses"]
    assert any(urlparse(s).hostname == "www.fda.gov" for s in entry["sources"])
