from datetime import date

import pytest

from clinicops_os.claim_registry import RegistryClaim
from clinicops_os.evidence import EvidenceClass, VerificationStatus
from clinicops_os.publication import build_publication_pack, render_publication_pack


def _claim(
    claim_id: str,
    *,
    status: VerificationStatus = VerificationStatus.VERIFIED,
    allowed_uses: tuple[str, ...] = ("research-note",),
    review_after: date | None = None,
) -> RegistryClaim:
    return RegistryClaim(
        claim_id=claim_id,
        text=f"Claim {claim_id}",
        evidence_class=EvidenceClass.PRIMARY,
        status=status,
        sources=("https://example.com/source",),
        limitations=("Keep the scope narrow.",),
        allowed_uses=allowed_uses,
        review_after=review_after,
        supersedes=(),
        superseded_by=None,
    )


def test_publication_pack_renders_sources_and_limitations() -> None:
    pack = build_publication_pack(
        [_claim("CO-CLM-0001")],
        ["CO-CLM-0001"],
        title="Test note",
        use="research-note",
        as_of=date(2026, 9, 9),
    )
    rendered = render_publication_pack(pack)
    assert "CO-CLM-0001" in rendered
    assert "Keep the scope narrow." in rendered
    assert "https://example.com/source" in rendered


def test_publication_pack_blocks_rejected_claim() -> None:
    with pytest.raises(ValueError, match="status is rejected"):
        build_publication_pack(
            [_claim("CO-CLM-0002", status=VerificationStatus.REJECTED)],
            ["CO-CLM-0002"],
            title="Blocked note",
            use="research-note",
            as_of=date(2026, 9, 9),
        )


def test_publication_pack_blocks_stale_external_claim() -> None:
    with pytest.raises(ValueError, match="review expired"):
        build_publication_pack(
            [_claim("CO-CLM-0003", review_after=date(2026, 9, 1))],
            ["CO-CLM-0003"],
            title="Stale note",
            use="research-note",
            as_of=date(2026, 9, 9),
        )
