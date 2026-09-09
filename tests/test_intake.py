import sys

import pytest

from clinicops_os.cli import portfolio_report
from clinicops_os.intake import validate_portfolio
from clinicops_os.transition_report import PortfolioRow


def test_intake_flags_b_prefix_mdr_conflict_and_missing_evidence():
    row = PortfolioRow(
        "Example",
        "Device",
        "MF",
        "MDR",
        basic_udi_di="B-123",
        danish_market="unknown",
    )
    findings = validate_portfolio([row])
    messages = "\n".join(item.message for item in findings)
    assert "conflicts with B-prefix" in messages
    assert "Danish-market relevance is unresolved" in messages
    assert "no evidence URL" in messages


def test_intake_flags_legacy_timing_gap():
    row = PortfolioRow(
        "Example",
        "Device",
        "MF",
        "legacy",
        source_url="https://example.test/source",
    )
    findings = validate_portfolio([row])
    assert any(item.field == "certificate_expiry" for item in findings)


def test_intake_clean_row_has_no_findings():
    row = PortfolioRow(
        "Example",
        "Device",
        "MF",
        "MDR",
        basic_udi_di="1234567890",
        certificate_expiry="2027-12-31",
        danish_market="yes",
        linked_sscp="true",
        source_url="https://example.test/source",
    )
    assert validate_portfolio([row]) == []


def test_intake_flags_invalid_date_without_crashing_report_prep():
    row = PortfolioRow(
        "Example",
        "Device",
        "MF",
        "legacy",
        certificate_expiry="31/12/2027",
        danish_market="yes",
        source_url="https://example.test/source",
    )
    findings = validate_portfolio([row])
    assert any(
        item.severity == "error"
        and item.field == "certificate_expiry"
        and "YYYY-MM-DD" in item.message
        for item in findings
    )


def test_intake_flags_duplicate_rows_before_counting():
    rows = [
        PortfolioRow(
            "Example",
            "Device",
            "MF",
            "MDR",
            basic_udi_di="123",
            certificate_expiry="2027-12-31",
            danish_market="yes",
            source_url="https://example.test/source",
        ),
        PortfolioRow(
            " example ",
            "DEVICE",
            "mf",
            "MDR",
            basic_udi_di="123",
            certificate_expiry="2027-12-31",
            danish_market="yes",
            source_url="https://example.test/source",
        ),
    ]
    findings = validate_portfolio(rows)
    assert any("possible duplicate of CSV row 2" in item.message for item in findings)


def test_report_cli_blocks_structural_errors(tmp_path, monkeypatch, capsys):
    portfolio = tmp_path / "bad.csv"
    portfolio.write_text(
        "company,device,actor_role,registration_type,certificate_expiry,danish_market,source_url\n"
        "Example,Device,MF,legacy,31/12/2027,yes,https://example.test/source\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", ["clinicops-portfolio-report", str(portfolio)])

    with pytest.raises(SystemExit) as exc:
        portfolio_report()

    assert exc.value.code == 2
    output = capsys.readouterr().out
    assert "Portfolio intake diagnostics" in output
    assert "YYYY-MM-DD" in output
