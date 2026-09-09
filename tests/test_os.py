from datetime import date
import pytest

from clinicops_eudamed.claim_guard import check_claim
from clinicops_eudamed.identifier import classify_identifier
from clinicops_os.evidence import Claim, EvidenceClass, VerificationStatus, publication_gate
from clinicops_os.prospect import ProspectSignal
from clinicops_os.resilience import Dependency, resilience_backlog
from clinicops_os.scoring import Idea, rank_ideas
from clinicops_os.transition_report import PortfolioRow


def test_publication_gate_blocks_unchecked():
    ok, reasons = publication_gate([Claim("x", EvidenceClass.HYPOTHESIS, VerificationStatus.UNCHECKED)])
    assert not ok and reasons


def test_derivation_requires_limitation():
    ok, reasons = publication_gate([Claim("x", EvidenceClass.DERIVATION, VerificationStatus.VERIFIED)])
    assert not ok and "limitation" in reasons[0].lower()


def test_transition_prospect_priority():
    strong = ProspectSignal("A", True, True, True, True, 5).score
    weak = ProspectSignal("B", False, True, False, False, 2).score
    assert strong > weak


def test_idea_ranking_rewards_evidence_and_reuse():
    durable = Idea("durable", 8, 8, 8, 8, 8, 4, 2, evidence=9, defensibility=9, reuse=10, urgency=7, maintenance=2)
    noisy = Idea("noisy", 8, 8, 8, 8, 8, 4, 2, evidence=2, defensibility=2, reuse=2, urgency=7, maintenance=8)
    assert rank_ideas([noisy, durable])[0].name == "durable"


def test_high_risk_low_reversibility_escalates():
    idea = Idea("risky", 10, 8, 10, 3, 8, 2, 9, evidence=8)
    assert idea.decision == "ESCALATE"


def test_invalid_scale_rejected():
    with pytest.raises(ValueError):
        Idea("bad", 11, 5, 5, 5, 5, 2)


def test_resilience_prioritizes_no_fallback():
    ranked = resilience_backlog([Dependency("x", 5, True, 10), Dependency("y", 5, False, 10)])
    assert ranked[0].name == "y"


def test_transition_report_separates_pack_and_legacy():
    legacy = PortfolioRow("A", "D", "MF", "legacy", certificate_expiry="2026-12-01")
    pack = PortfolioRow("B", "P", "PR", "MDR")
    assert "transition" in legacy.workstream(date(2026, 9, 9)).lower()
    assert "pack" in pack.workstream(date(2026, 9, 9)).lower()


def test_null_sscp_is_not_compliance_finding():
    row = PortfolioRow("A", "D", "MF", "legacy", linked_sscp="null")
    assert "not treated as non-compliance" in row.evidence_note()


def test_claim_guard_blocks_discarded_headline():
    assert any(f.severity == "high" for f in check_claim("Manufacturers are failing to link SS(C)Ps"))


def test_b_prefix_is_qualified_derivation():
    result = classify_identifier("B-123")
    assert result.legacy_screen
    assert "Derived" in result.note
