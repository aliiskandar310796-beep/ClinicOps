from __future__ import annotations

from pathlib import Path

import pytest

from clinicops_os.autonomy import halt

ROOT = Path(__file__).resolve().parents[1]


def _fake_repo(tmp_path: Path) -> Path:
    (tmp_path / "autonomy").mkdir()
    (tmp_path / "autonomy" / "rules.json").write_text("{}", encoding="utf-8")
    return tmp_path


def test_inactive_when_file_absent(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    state = halt.halt_state(repo)
    assert not state.halted
    assert state.first_line is None
    assert state.path == repo / "autonomy" / "HALT.md"
    assert "HALT inactive" in state.describe()


def test_active_with_first_non_empty_line(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    (repo / "autonomy" / "HALT.md").write_text(
        "\n\n# HALT — deliverability incident 2026-09-25\nDetails follow.\n", encoding="utf-8"
    )
    state = halt.halt_state(repo)
    assert state.halted
    assert state.first_line == "# HALT — deliverability incident 2026-09-25"
    assert "HALT active" in state.describe()


def test_empty_file_still_halts(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    (repo / "autonomy" / "HALT.md").write_text("", encoding="utf-8")
    state = halt.halt_state(repo)
    assert state.halted
    assert state.first_line is None
    assert "(empty file)" in state.describe()


def test_cli_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _fake_repo(tmp_path)
    assert halt.main([str(repo)]) == 0
    (repo / "autonomy" / "HALT.md").write_text("stop\n", encoding="utf-8")
    assert halt.main([str(repo)]) == 1
    assert halt.main(["a", "b"]) == 2
    assert halt.main([str(tmp_path / "missing")]) == 2
    out = capsys.readouterr().out
    assert "HALT active" in out


def test_committed_repository_is_not_halted() -> None:
    assert not halt.halt_state(ROOT).halted
