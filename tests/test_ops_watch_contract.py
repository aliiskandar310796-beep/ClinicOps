from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ops_watch_keeps_scheduled_live_site_check() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ops-watch.yml").read_text(
        encoding="utf-8"
    )

    assert "schedule:" in workflow
    assert "cron: '13 6 * * 1'" in workflow
    assert "python scripts/check_live_site.py" in workflow
    assert "Live site health" in workflow


def test_live_site_watch_covers_public_research_pages() -> None:
    checker = (ROOT / "scripts" / "check_live_site.py").read_text(encoding="utf-8")

    assert 'Target(\n        "/research/sscp-public-record-scan/"' in checker
    assert '"The published SS(C)P and the public EUDAMED record"' in checker
    assert 'Target(\n        "/research/eudamed-watch/"' in checker
    assert '"Continuous monitoring of the public EUDAMED record"' in checker
