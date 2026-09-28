"""Repository kill switch: ``autonomy/HALT.md``.

Creating ``autonomy/HALT.md`` on ``main`` stops every Tier-0 job; deleting it
resumes them. This module reports the local state so a job wrapper can gate
on it (exit code 1 when halted). The scheduled jobs themselves read the file
raw from ``main`` and also check the Drive and project locations.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from .rules import RulesError, find_repo_root

HALT_RELATIVE_PATH = Path("autonomy") / "HALT.md"


@dataclass(frozen=True)
class HaltState:
    halted: bool
    path: Path
    first_line: str | None

    def describe(self) -> str:
        if not self.halted:
            return f"HALT inactive — {self.path} does not exist"
        headline = self.first_line or "(empty file)"
        return f"HALT active — {self.path}: {headline}"


def halt_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / HALT_RELATIVE_PATH


def halt_state(repo_root: str | Path | None = None) -> HaltState:
    """Return whether ``autonomy/HALT.md`` exists under ``repo_root`` and its first line."""
    root = Path(repo_root) if repo_root is not None else find_repo_root()
    if not root.is_dir():
        raise RulesError(f"repository root does not exist: {root}")
    path = halt_path(root)
    if not path.exists():
        return HaltState(False, path, None)
    if path.is_dir():
        return HaltState(True, path, "(HALT.md is a directory — treated as active)")
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return HaltState(True, path, f"(unreadable: {exc})")
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), None)
    return HaltState(True, path, first_line)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    repo_root: str | None = None
    if args and args[0] in {"-h", "--help"}:
        print("usage: clinicops-autonomy-halt [REPO_ROOT]\nexit 1 when autonomy/HALT.md exists")
        return 0
    if len(args) > 1:
        print("usage: clinicops-autonomy-halt [REPO_ROOT]")
        return 2
    if args:
        repo_root = args[0]
    try:
        state = halt_state(repo_root)
    except RulesError as exc:
        print(f"error: {exc}")
        return 2
    print(state.describe())
    return 1 if state.halted else 0


def halt_cli() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
