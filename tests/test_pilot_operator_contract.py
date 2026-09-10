from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATOR_DOCS = (
    ROOT / "sales" / "buyer-conversation-to-pilot-playbook.md",
    ROOT / "sales" / "first-pilot-scope-template.md",
)


def test_canonical_pilot_playbooks_require_preflight_before_bundle() -> None:
    for path in OPERATOR_DOCS:
        text = path.read_text(encoding="utf-8")
        preflight = text.index("clinicops-pilot-preflight")
        bundle = text.index("clinicops-pilot-bundle")

        assert preflight < bundle, f"{path.name} must require preflight before bundle generation"
        assert '"status": "ACTIVATED"' in text
        assert "NON-STANDARD — NOT ACTIVATED" in text


def test_canonical_pilot_playbooks_require_integrity_verification_before_release() -> None:
    for path in OPERATOR_DOCS:
        text = path.read_text(encoding="utf-8")

        assert "clinicops-pilot-verify" in text
        assert '"status": "VERIFIED"' in text
        assert "human review" in text.lower() or "human-review" in text.lower()


def test_operator_docs_do_not_treat_ci_as_delegation_proof() -> None:
    playbook = OPERATOR_DOCS[0].read_text(encoding="utf-8")
    preflight_note = (ROOT / "sales" / "standard-pilot-preflight.md").read_text(
        encoding="utf-8"
    )

    assert "does **not** prove founder-independent execution" in playbook
    assert "is **not** a delegation proof run" in preflight_note
