from datetime import date

from clinicops_os.transition_report import PortfolioRow, load_portfolio, render_markdown


def test_priority_rewards_urgent_danish_legacy_row():
    urgent = PortfolioRow(
        "A",
        "Legacy device",
        "MF",
        "legacy",
        certificate_expiry="2026-10-01",
        danish_market="yes",
        source_url="https://example.test/a",
    )
    routine = PortfolioRow("B", "MDR device", "MF", "MDR", danish_market="no")
    as_of = date(2026, 9, 9)
    assert urgent.priority_score(as_of) > routine.priority_score(as_of)

    report = render_markdown([routine, urgent], as_of=as_of)
    assert report.index("Legacy device") < report.index("MDR device")
    assert "not a regulatory risk" in report.lower()


def test_load_portfolio_ignores_extra_columns(tmp_path):
    csv_path = tmp_path / "portfolio.csv"
    csv_path.write_text(
        "company,device,actor_role,registration_type,unknown_export_field\n"
        "A,Device A,MF,legacy,keep-but-ignore\n",
        encoding="utf-8",
    )
    rows = load_portfolio(csv_path)
    assert len(rows) == 1
    assert rows[0].company == "A"
    assert rows[0].is_legacy
