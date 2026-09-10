import csv
import json
from datetime import date
from pathlib import Path

from clinicops_os.bundle import build_pilot_bundle
from clinicops_os.bundle_verify import verify_pilot_bundle

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


def _write_portfolio(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow(
            {
                "company": "Example Co",
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


def _build(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "portfolio.csv"
    output = tmp_path / "bundle"
    _write_portfolio(source)
    build_pilot_bundle(source, output, as_of=date(2026, 9, 11))
    return source, output


def test_generated_bundle_verifies_against_source_and_manifest(tmp_path: Path) -> None:
    source, output = _build(tmp_path)

    result = verify_pilot_bundle(output, source)

    assert result.valid is True
    assert result.errors == ()
    assert result.as_dict()["status"] == "VERIFIED"


def test_modified_output_fails_verification(tmp_path: Path) -> None:
    source, output = _build(tmp_path)
    report = output / "portfolio_report.md"
    report.write_text(report.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")

    result = verify_pilot_bundle(output, source)

    assert result.valid is False
    assert "output hash mismatch: portfolio_report.md" in result.errors


def test_changed_source_fails_verification(tmp_path: Path) -> None:
    source, output = _build(tmp_path)
    source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    result = verify_pilot_bundle(output, source)

    assert result.valid is False
    assert "source_sha256 does not match the supplied source file" in result.errors


def test_manifest_output_key_mismatch_fails_verification(tmp_path: Path) -> None:
    source, output = _build(tmp_path)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    del manifest["output_sha256"]["client_report.html"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = verify_pilot_bundle(output, source)

    assert result.valid is False
    assert "outputs and output_sha256 keys do not match" in result.errors
    assert "output hash mismatch: client_report.html" in result.errors


def test_manifest_cannot_omit_controlled_output_even_if_hash_is_removed(tmp_path: Path) -> None:
    source, output = _build(tmp_path)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["outputs"].remove("client_report.html")
    del manifest["output_sha256"]["client_report.html"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = verify_pilot_bundle(output, source)

    assert result.valid is False
    assert "outputs do not match the schema-1.1 controlled output set" in result.errors


def test_manifest_cannot_escape_bundle_directory(tmp_path: Path) -> None:
    source, output = _build(tmp_path)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["outputs"].append("../portfolio.csv")
    manifest["output_sha256"]["../portfolio.csv"] = manifest["source_sha256"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = verify_pilot_bundle(output, source)

    assert result.valid is False
    assert "invalid output filename in manifest: ../portfolio.csv" in result.errors
