"""Registry schema: risk class, last_verified, verified_method, fact_key/value, stamp fields.

Lens 29 (accuracy governance): cadence follows rate of change times cost of being
wrong, a verified claim never has review_after null, and two live claims that
share a fact_key must agree on its value.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from clinicops_os.claim_registry import (
    RISK_CLASS_INTERVAL_DAYS,
    RegistryClaim,
    audit_registry,
    load_registry,
)
from clinicops_os.evidence import EvidenceClass, VerificationStatus

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 11, 16)


def _claim(**overrides) -> RegistryClaim:
    values = {
        "claim_id": "CO-CLM-9999",
        "text": "A test claim.",
        "evidence_class": EvidenceClass.PRIMARY,
        "status": VerificationStatus.QUALIFIED,
        "sources": ("https://example.com/source",),
        "limitations": ("Scope is narrow.",),
        "allowed_uses": ("website", "research-note"),
        "review_after": date(2026, 12, 16),
        "supersedes": (),
        "superseded_by": None,
        "risk_class": "A",
        "last_verified": date(2026, 11, 16),
        "verified_method": "read-primary",
        "source_date": "undated",
        "not_established": ("Nothing beyond the quoted text.",),
        "label": "Test claim",
    }
    values.update(overrides)
    return RegistryClaim(**values)


def _errors(*claims: RegistryClaim) -> list[str]:
    return [
        f"{item.claim_id}: {item.message}"
        for item in audit_registry(list(claims), as_of=AS_OF)
        if item.severity == "error"
    ]


def test_a_complete_claim_has_no_errors() -> None:
    assert _errors(_claim()) == []


def test_class_intervals_follow_lens_29() -> None:
    assert RISK_CLASS_INTERVAL_DAYS == {"A": 30, "B": 45, "C": 90, "D": 120, "E": 180}


@pytest.mark.parametrize("value", [None, "F", "a", ""])
def test_risk_class_is_required_and_bounded(value) -> None:
    errors = _errors(_claim(risk_class=value))
    assert any("risk_class" in message for message in errors)


@pytest.mark.parametrize("status", [VerificationStatus.VERIFIED, VerificationStatus.QUALIFIED])
def test_live_claim_cannot_have_null_review_after(status) -> None:
    errors = _errors(_claim(status=status, review_after=None))
    assert any("review_after" in message for message in errors)


def test_rejected_claim_may_have_null_review_after() -> None:
    claim = _claim(
        status=VerificationStatus.REJECTED,
        evidence_class=EvidenceClass.HYPOTHESIS,
        allowed_uses=("internal-learning",),
        review_after=None,
        last_verified=None,
        verified_method=None,
        source_date=None,
        not_established=(),
        label=None,
    )
    assert _errors(claim) == []


def test_review_after_cannot_exceed_the_class_interval() -> None:
    claim = _claim(risk_class="A", review_after=date(2026, 11, 16) + timedelta(days=31))
    assert any("longer than" in message for message in _errors(claim))
    ok = _claim(risk_class="E", review_after=date(2026, 11, 16) + timedelta(days=180))
    assert _errors(ok) == []


def test_live_claim_needs_last_verified_and_method() -> None:
    assert any("last_verified" in m for m in _errors(_claim(last_verified=None)))
    assert any("verified_method" in m for m in _errors(_claim(verified_method=None)))
    assert any("verified_method" in m for m in _errors(_claim(verified_method="vibes")))


def test_verified_status_requires_a_primary_read() -> None:
    claim = _claim(status=VerificationStatus.VERIFIED, verified_method="carried-forward")
    assert any("read-primary" in message for message in _errors(claim))


def test_stamp_fields_are_required_for_public_claims() -> None:
    assert any("source_date" in m for m in _errors(_claim(source_date=None)))
    assert any("not_established" in m for m in _errors(_claim(not_established=())))
    assert any("label" in m for m in _errors(_claim(label=None)))


def test_internal_only_claim_does_not_need_stamp_fields() -> None:
    claim = _claim(allowed_uses=("internal",), source_date=None, not_established=(), label=None)
    assert _errors(claim) == []


def test_fact_key_and_value_travel_together() -> None:
    assert any("fact_key" in m for m in _errors(_claim(fact_key="a.b", value=None)))
    assert any("fact_key" in m for m in _errors(_claim(fact_key=None, value="x")))


def test_two_live_claims_with_one_fact_key_must_agree() -> None:
    one = _claim(claim_id="CO-CLM-9001", fact_key="eudamed.deadline", value="2026-11-28")
    two = _claim(claim_id="CO-CLM-9002", fact_key="eudamed.deadline", value="2026-11-27")
    errors = _errors(one, two)
    assert any("fact_key eudamed.deadline" in message for message in errors)
    agree = _claim(claim_id="CO-CLM-9002", fact_key="eudamed.deadline", value="2026-11-28")
    assert _errors(one, agree) == []


def test_a_superseded_claim_may_disagree_and_never_warns_about_expiry() -> None:
    old = _claim(
        claim_id="CO-CLM-9001",
        fact_key="eudamed.deadline",
        value="2026-11-27",
        superseded_by="CO-CLM-9002",
        review_after=date(2026, 1, 1),
    )
    new = _claim(claim_id="CO-CLM-9002", fact_key="eudamed.deadline", value="2026-11-28")
    findings = audit_registry([old, new], as_of=AS_OF)
    assert [i for i in findings if i.severity == "error"] == []
    assert not [i for i in findings if i.claim_id == "CO-CLM-9001" and "review" in i.message]


def test_review_due_soon_is_a_warning_not_an_error() -> None:
    claim = _claim(review_after=AS_OF + timedelta(days=10))
    findings = audit_registry([claim], as_of=AS_OF)
    assert [i for i in findings if i.severity == "error"] == []
    assert any(i.severity == "warning" and "due in 10 days" in i.message for i in findings)


# ---- the real registry ----------------------------------------------------


def _registry() -> list[RegistryClaim]:
    return load_registry(ROOT / "research" / "claims.jsonl")


def test_real_registry_passes_the_schema_audit() -> None:
    errors = [
        f"{i.claim_id}: {i.message}"
        for i in audit_registry(_registry(), as_of=AS_OF)
        if i.severity == "error"
    ]
    assert errors == []


def test_no_verified_claim_has_a_null_review_date() -> None:
    for claim in _registry():
        if claim.status == VerificationStatus.VERIFIED:
            assert claim.review_after is not None, claim.claim_id


def test_the_legacy_deadline_claims_share_one_fact_and_one_value() -> None:
    by_id = {c.claim_id: c for c in _registry()}
    for claim_id in ("CO-CLM-0013", "CO-CLM-0020"):
        assert by_id[claim_id].fact_key == "eudamed.legacy_registration_deadline"
        assert by_id[claim_id].value == "2026-11-28"
        assert "28 November 2026" in by_id[claim_id].text
        assert "27 or 28" not in by_id[claim_id].text
        assert "Friday 27 November 2026" in by_id[claim_id].text
        assert "no calendar date" in by_id[claim_id].text


def test_audit_script_reports_classes_and_exits_clean() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_claim_registry.py"), "--as-of", "2026-11-16"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": ""},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Live claims by risk class: A=4, B=5, C=3, D=6, E=6" in result.stdout
    assert "0 errors" in result.stdout


def test_audit_script_exits_2_on_a_schema_error(tmp_path: Path) -> None:
    import subprocess
    import sys

    bad = tmp_path / "claims.jsonl"
    bad.write_text(
        '{"id":"CO-CLM-0001","claim":"x","evidence_class":"primary","status":"verified",'
        '"sources":["https://e.com"],"limitations":[],"allowed_uses":["internal"],'
        '"review_after":null,"supersedes":[],"superseded_by":null}\n',
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_claim_registry.py"), "--registry", str(bad)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": ""},
    )
    assert result.returncode == 2
    assert "risk_class" in result.stdout and "review_after" in result.stdout
