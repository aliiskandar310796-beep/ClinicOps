from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from clinicops_os.autonomy import backup_manifest
from clinicops_os.autonomy.backup_manifest import build, load_manifest, verify


def _populate(directory: Path) -> None:
    (directory / "00_CONTROL__BUSINESS_STATE.md").write_text("state\n", encoding="utf-8")
    (directory / "nested").mkdir()
    (directory / "nested" / "20_AUTONOMY__NEEDS_ALI.md").write_bytes(b"- [ ] item\n")


def test_build_lists_every_file_with_hash_and_origin(tmp_path: Path) -> None:
    _populate(tmp_path)
    manifest = build(tmp_path, origin="project-docs", generated_utc="2026-09-25T02:58:00Z")
    assert manifest["schema_version"] == "1.0"
    assert manifest["generated_utc"] == "2026-09-25T02:58:00Z"
    assert manifest["directory"] == tmp_path.name
    names = [entry["name"] for entry in manifest["files"]]
    assert names == ["00_CONTROL__BUSINESS_STATE.md", "nested/20_AUTONOMY__NEEDS_ALI.md"]
    first = manifest["files"][0]
    assert first["bytes"] == 6
    assert first["sha256"] == hashlib.sha256(b"state\n").hexdigest()
    assert first["origin"] == "project-docs"
    assert manifest["counts"] == {"files": 2, "bytes": 6 + 11}


def test_manifest_file_itself_is_excluded(tmp_path: Path) -> None:
    _populate(tmp_path)
    (tmp_path / "MANIFEST.json").write_text("{}", encoding="utf-8")
    manifest = build(tmp_path)
    assert all(entry["name"] != "MANIFEST.json" for entry in manifest["files"])
    assert verify(manifest, tmp_path) == []


def test_verify_reports_every_kind_of_mismatch(tmp_path: Path) -> None:
    _populate(tmp_path)
    manifest = build(tmp_path)
    assert verify(manifest, tmp_path) == []

    (tmp_path / "00_CONTROL__BUSINESS_STATE.md").write_text("changed\n", encoding="utf-8")
    (tmp_path / "nested" / "20_AUTONOMY__NEEDS_ALI.md").unlink()
    (tmp_path / "extra.txt").write_text("x", encoding="utf-8")

    mismatches = verify(manifest, tmp_path)
    assert any(item.startswith("size mismatch: 00_CONTROL__BUSINESS_STATE.md") for item in mismatches)
    assert any(item.startswith("sha256 mismatch: 00_CONTROL__BUSINESS_STATE.md") for item in mismatches)
    assert "missing: nested/20_AUTONOMY__NEEDS_ALI.md" in mismatches
    assert "extra file not in manifest: extra.txt" in mismatches


def test_verify_detects_same_size_content_change(tmp_path: Path) -> None:
    _populate(tmp_path)
    manifest = build(tmp_path)
    (tmp_path / "00_CONTROL__BUSINESS_STATE.md").write_text("statf\n", encoding="utf-8")
    mismatches = verify(manifest, tmp_path)
    assert len(mismatches) == 1 and mismatches[0].startswith("sha256 mismatch")


def test_verify_rejects_malformed_manifest_and_missing_directory(tmp_path: Path) -> None:
    assert verify({"files": "nope"}, tmp_path) == ["manifest has no 'files' list"]
    assert verify({"files": []}, tmp_path / "absent")[0].startswith("not a directory")
    assert verify({"files": ["bad"]}, tmp_path) == ["malformed manifest entry: 'bad'"]
    with pytest.raises(ValueError, match="not a directory"):
        build(tmp_path / "absent")


def test_cli_build_then_verify_round_trip(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _populate(tmp_path)
    out = tmp_path / "MANIFEST.json"
    assert backup_manifest.main(["build", str(tmp_path), "--origin", "drive", "--out", str(out)]) == 0
    manifest = load_manifest(out)
    assert manifest["files"][0]["origin"] == "drive"
    assert backup_manifest.main(["verify", str(out), str(tmp_path)]) == 0

    (tmp_path / "00_CONTROL__BUSINESS_STATE.md").write_text("tampered\n", encoding="utf-8")
    assert backup_manifest.main(["verify", str(out), str(tmp_path)]) == 2
    printed = capsys.readouterr().out
    assert "manifest verify OK" in printed and "manifest verify FAILED" in printed

    assert backup_manifest.main(["build", str(tmp_path)]) == 0
    assert json.loads(capsys.readouterr().out)["schema_version"] == "1.0"

    assert backup_manifest.main([]) == 2
    assert backup_manifest.main(["verify", str(tmp_path / "none.json"), str(tmp_path)]) == 2
