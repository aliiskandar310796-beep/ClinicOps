import csv
import json
from datetime import date
from pathlib import Path

import pytest

from clinicops_os.bundle import build_pilot_bundle


FIELDNAMES = [
    "company",
    "device",
    "actor_role",
    "registration_type",
    "basic_udi_di",
    "certificate_expiry",
    "danish_market",
    "linked_sscp",
    "source_url",
    "notes",
]


def _write_portfolio(path: Path, *, company: str = "Example Co") -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow(
            {
                "company": company,
                "device": "Example device",
                "actor_role": "MF",
                "registration_type": "legacy",
                "basic_udi_di": "B-123",
                "certificate_expiry": "2026-12-01",
                "danish_market": "confirmed",
                "linked_sscp": "null",
                "source_url": "https://example.test",
                "notes": "fictional",
            }
        )


def test_bundle_builds_reproducible_deliverable_set(tmp_path):
    source = tmp_path / "portfolio.csv"
    output = tmp_path / "bundle"
    _write_portfolio(source)

    result = build_pilot_bundle(source, output, as_of=date(2026, 9, 9))

    assert result.manifest["bundle_schema_version"] == "1.0"
    assert result.manifest["records_reviewed"] == 1
    assert len(result.manifest["source_sha256"]) == 64
    for name in ("portfolio_report.md", "portfolio_report.json", "intake_diagnostics.md", "manifest.json"):
        assert (output / name).exists()

    payload = json.loads((output / "portfolio_report.json").read_text(encoding="utf-8"))
    assert payload["rows"][0]["company"] == "Example Co"
    assert "not a compliance" in (output / "portfolio_report.md").read_text(encoding="utf-8")


def test_bundle_blocks_structurally_invalid_input(tmp_path):
    source = tmp_path / "portfolio.csv"
    output = tmp_path / "bundle"
    _write_portfolio(source, company="")

    with pytest.raises(ValueError, match="portfolio intake blocked"):
        build_pilot_bundle(source, output, as_of=date(2026, 9, 9))
    assert not output.exists()
