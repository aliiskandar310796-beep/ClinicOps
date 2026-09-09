from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "readiness-score.html"


def test_readiness_page_is_local_and_actionable() -> None:
    text = PAGE.read_text(encoding="utf-8")
    assert "Nothing is sent to ClinicOps" in text
    assert "Request a Regulatory Intelligence Assessment" in text
    assert "fetch(" not in text
    assert "XMLHttpRequest" not in text


def test_readiness_page_links_back_to_identifier_check() -> None:
    text = PAGE.read_text(encoding="utf-8")
    assert 'href="index.html"' in text
