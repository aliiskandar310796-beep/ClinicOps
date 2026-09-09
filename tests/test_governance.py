from datetime import date
from pathlib import Path

import pytest

from clinicops_os.claim_registry import audit_registry, load_registry
from clinicops_os.publication import build_publication_pack, render_publication_pack

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "research" / "claims.jsonl"


def registry():
    return load_registry(REGISTRY_PATH)


def test_claim_registry_has_no_structural_errors_on_current_baseline():
    findings = audit_registry(registry(), as_of=date(2026, 9, 9))
    assert not [item for item in findings if item.severity == "error"]


def test_rejected_claim_cannot_enter_publication_pack():
    with pytest.raises(ValueError, match="status is rejected"):
        build_publication_pack(
            registry(),
            ["CO-CLM-0003"],
            title="Blocked",
            use="research-note",
            as_of=date(2026, 9, 9),
        )


def test_context_gate_blocks_research_only_claim_from_website():
    with pytest.raises(ValueError, match="use 'website' is not allowed"):
        build_publication_pack(
            registry(),
            ["CO-CLM-0002"],
            title="Wrong context",
            use="website",
            as_of=date(2026, 9, 9),
        )


def test_review_expiry_blocks_stale_public_claim():
    with pytest.raises(ValueError, match="review expired"):
        build_publication_pack(
            registry(),
            ["CO-CLM-0008"],
            title="Stale timing",
            use="research-note",
            as_of=date(2026, 11, 1),
        )


def test_publication_pack_inherits_limitations_and_sources():
    pack = build_publication_pack(
        registry(),
        ["CO-CLM-0002", "CO-CLM-0010"],
        title="Transition evidence pack",
        use="research-note",
        as_of=date(2026, 9, 9),
    )
    rendered = render_publication_pack(pack)
    assert "not a population rate or full-register audit" in rendered
    assert "27 February 2027" in rendered
    assert "mdcg_2026-4_en.pdf" in rendered
    assert "Re-run the claim guard" in rendered


def test_unknown_claim_id_is_blocked():
    with pytest.raises(ValueError, match="not found in registry"):
        build_publication_pack(
            registry(),
            ["CO-CLM-9999"],
            title="Unknown",
            use="internal",
            as_of=date(2026, 9, 9),
        )
