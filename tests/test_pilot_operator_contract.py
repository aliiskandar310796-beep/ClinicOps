from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATOR_DOCS = (
    ROOT / "sales" / "buyer-conversation-to-pilot-playbook.md",
    ROOT / "sales" / "first-pilot-scope-template.md",
)


def test_canonical_pilot_playbooks_require_full_controlled_release_order() -> None:
    for path in OPERATOR_DOCS:
        text = path.read_text(encoding="utf-8")
        preflight = text.index("clinicops-pilot-preflight")
        bundle = text.index("clinicops-pilot-bundle")
        review_prepare = text.index("clinicops-pilot-review-prepare")
        review_gate = text.index("clinicops-pilot-review-gate")
        verify = text.index("clinicops-pilot-verify")

        assert preflight < bundle < review_prepare < review_gate < verify, (
            f"{path.name} must preserve preflight → bundle → recorded human review → "
            "integrity verification"
        )
        assert '"status": "ACTIVATED"' in text
        assert "NON-STANDARD — NOT ACTIVATED" in text
        assert '"status": "REVIEW APPROVED"' in text
        assert '"status": "VERIFIED"' in text


def test_canonical_pilot_playbooks_keep_human_review_responsible() -> None:
    for path in OPERATOR_DOCS:
        text = path.read_text(encoding="utf-8").lower()

        assert "human review" in text or "human-review" in text
        assert "cannot" in text and "review" in text
        assert "professional" in text or "responsible" in text


def test_operator_docs_do_not_treat_ci_as_delegation_proof() -> None:
    playbook = OPERATOR_DOCS[0].read_text(encoding="utf-8")
    preflight_note = (ROOT / "sales" / "standard-pilot-preflight.md").read_text(
        encoding="utf-8"
    )

    assert "does **not** prove founder-independent execution" in playbook
    assert "is **not** a delegation proof run" in preflight_note
