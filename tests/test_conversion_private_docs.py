"""Conversion path: the private auto-reply document matches the public commitment.

Split out of tests/test_conversion_path_contract.py at integration so that the one test that
reads a private path (03_OPERATIONS/) moves with the private set in the planned repository
split (scripts/private_split_manifest.py, MOVES_WITH_PRIVATE_TESTS), while the public contract
stays fully testable in a public-only copy.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_auto_reply_document_exists_and_matches_the_site_commitment() -> None:
    doc = (ROOT / "03_OPERATIONS" / "MAILBOX_AUTO_REPLY_AND_RESPONSE_TIME.md").read_text(encoding="utf-8")
    assert "within three working days" in doc
    assert "tre arbejdsdage" in doc
    assert "CM-01" in doc and "CM-05" in doc
    assert "Please do not send patient-identifiable data or confidential files by email" in doc
