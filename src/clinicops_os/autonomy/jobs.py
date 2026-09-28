"""Job specifications: front-matter parsing and prompt assembly.

Each ``autonomy/jobs/<job>.md`` starts with a YAML front matter block that the
scheduler settings are read from, followed by the job body. The full prompt
of a scheduled task is ``_COMMON_HEADER.md`` (everything below its H1 title)
followed by the job body (everything below the front matter).

The front matter is parsed without PyYAML (``requests`` is the only runtime
dependency of this package). Supported: ``key: value`` scalars (quoted or
bare, integers, floats, booleans, null), JSON-style inline lists and YAML
block lists (``- item`` lines under an empty ``key:``).
"""

from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .rules import JOBS_RELATIVE_DIR, RulesError, find_repo_root

COMMON_HEADER_NAME = "_COMMON_HEADER.md"
REQUIRED_KEYS = (
    "name",
    "slug",
    "tier",
    "cron",
    "cadence_minutes",
    "min_expected_duration_seconds",
    "outputs",
    "notifications",
)
_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$")


class JobSpecError(ValueError):
    """Raised when a job file cannot be parsed or is missing required metadata."""


@dataclass(frozen=True)
class JobSpec:
    slug: str
    name: str
    path: Path
    tier: int
    cron: str
    cadence_minutes: int
    min_expected_duration_seconds: int
    outputs: tuple[str, ...]
    notifications: str
    meta: dict[str, Any]
    body: str


def _scalar(raw: str) -> Any:
    text = raw.strip()
    if not text:
        return ""
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text[1:-1]
    if len(text) >= 2 and text[0] == "'" and text[-1] == "'":
        return text[1:-1].replace("''", "'")
    # Strip a trailing YAML comment from an unquoted scalar.
    comment = re.search(r"\s#", text)
    if comment:
        text = text[: comment.start()].rstrip()
    low = text.lower()
    if low in {"true", "yes", "on"}:
        return True
    if low in {"false", "no", "off"}:
        return False
    if low in {"null", "~"}:
        return None
    if _INT_RE.match(text):
        return int(text)
    if _FLOAT_RE.match(text):
        return float(text)
    return text


def _parse_inline_list(raw: str) -> list[Any]:
    text = raw.strip()
    if not (text.startswith("[") and text.endswith("]")):
        raise JobSpecError(f"unterminated inline list: {raw!r}")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, list):
        return parsed
    inner = text[1:-1].strip()
    if not inner:
        return []
    reader = csv.reader([inner], skipinitialspace=True, quotechar="'")
    return [_scalar(item) for item in next(reader)]


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Split a Markdown document into (front matter dict, body)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise JobSpecError("missing opening front matter delimiter '---' on line 1")
    closing = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if closing is None:
        raise JobSpecError("missing closing front matter delimiter '---'")

    data: dict[str, Any] = {}
    list_key: str | None = None
    for number, line in enumerate(lines[1:closing], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if list_key is not None and stripped.startswith("- "):
            data[list_key].append(_scalar(stripped[2:]))
            continue
        if list_key is not None and stripped == "-":
            data[list_key].append("")
            continue
        list_key = None
        if line.startswith((" ", "\t")):
            raise JobSpecError(f"line {number}: nested mappings are not supported: {line!r}")
        key, separator, raw = line.partition(":")
        if not separator or not key.strip():
            raise JobSpecError(f"line {number}: expected 'key: value', got {line!r}")
        key = key.strip()
        if key in data:
            raise JobSpecError(f"line {number}: duplicate key {key!r}")
        value = raw.strip()
        if value == "":
            data[key] = []
            list_key = key
        elif value.startswith("["):
            data[key] = _parse_inline_list(value)
        else:
            data[key] = _scalar(value)

    body = "\n".join(lines[closing + 1 :]).lstrip("\n")
    if body and not body.endswith("\n"):
        body += "\n"
    return data, body


def jobs_dir(repo_root: str | Path | None = None) -> Path:
    root = Path(repo_root) if repo_root is not None else find_repo_root()
    return root / JOBS_RELATIVE_DIR


def job_files(directory: str | Path | None = None) -> list[Path]:
    base = Path(directory) if directory is not None else jobs_dir()
    if not base.is_dir():
        raise JobSpecError(f"jobs directory not found: {base}")
    return sorted(
        path
        for path in base.glob("*.md")
        if not path.name.startswith("_") and path.name.lower() != "readme.md"
    )


def load_job(path: str | Path) -> JobSpec:
    target = Path(path)
    try:
        meta, body = parse_front_matter(target.read_text(encoding="utf-8"))
    except JobSpecError as exc:
        raise JobSpecError(f"{target.name}: {exc}") from exc
    missing = [key for key in REQUIRED_KEYS if key not in meta]
    if missing:
        raise JobSpecError(f"{target.name}: front matter missing {', '.join(missing)}")
    outputs = meta["outputs"]
    if not isinstance(outputs, list) or not outputs:
        raise JobSpecError(f"{target.name}: outputs must be a non-empty list")
    for key in ("cadence_minutes", "min_expected_duration_seconds", "tier"):
        if not isinstance(meta[key], int) or isinstance(meta[key], bool):
            raise JobSpecError(f"{target.name}: {key} must be an integer")
    if not body.strip():
        raise JobSpecError(f"{target.name}: job body is empty")
    return JobSpec(
        slug=str(meta["slug"]),
        name=str(meta["name"]),
        path=target,
        tier=int(meta["tier"]),
        cron=str(meta["cron"]),
        cadence_minutes=int(meta["cadence_minutes"]),
        min_expected_duration_seconds=int(meta["min_expected_duration_seconds"]),
        outputs=tuple(str(item) for item in outputs),
        notifications=str(meta["notifications"]),
        meta=meta,
        body=body,
    )


def list_jobs(directory: str | Path | None = None) -> list[JobSpec]:
    """Parse every job file; slugs and names must be unique."""
    specs = [load_job(path) for path in job_files(directory)]
    seen: dict[str, str] = {}
    for spec in specs:
        if spec.slug in seen:
            raise JobSpecError(
                f"duplicate slug {spec.slug!r} in {spec.path.name} and {seen[spec.slug]}"
            )
        seen[spec.slug] = spec.path.name
    names = [spec.name for spec in specs]
    if len(names) != len(set(names)):
        raise JobSpecError("job names must be unique")
    return specs


def get_job(slug: str, directory: str | Path | None = None) -> JobSpec:
    for spec in list_jobs(directory):
        if spec.slug == slug:
            return spec
    raise JobSpecError(f"unknown job slug {slug!r}")


def common_header(directory: str | Path | None = None) -> str:
    """The shared header without its H1 title line."""
    base = Path(directory) if directory is not None else jobs_dir()
    path = base / COMMON_HEADER_NAME
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise JobSpecError(f"common header not found: {path}") from exc
    lines = text.splitlines()
    title = next((index for index, line in enumerate(lines) if line.startswith("# ")), None)
    if title is None:
        raise JobSpecError(f"{COMMON_HEADER_NAME}: no H1 title line found")
    header = "\n".join(lines[title + 1 :]).strip("\n")
    if not header:
        raise JobSpecError(f"{COMMON_HEADER_NAME}: nothing below the title line")
    return header + "\n"


def render(slug: str, directory: str | Path | None = None) -> str:
    """Assemble the full prompt: common header + job body."""
    spec = get_job(slug, directory)
    return common_header(directory) + "\n" + spec.body


def render_table(specs: list[JobSpec]) -> str:
    lines = [f"{'slug':<16} {'cadence':>8} {'min s':>6} {'notify':<11} cron"]
    for spec in specs:
        lines.append(
            f"{spec.slug:<16} {spec.cadence_minutes:>8} "
            f"{spec.min_expected_duration_seconds:>6} {spec.notifications:<11} {spec.cron}"
        )
    lines.append(f"{len(specs)} job specifications")
    return "\n".join(lines) + "\n"


USAGE = (
    "usage:\n"
    "  clinicops-autonomy-jobs list [--jobs-dir DIR]\n"
    "  clinicops-autonomy-jobs render <slug> [--jobs-dir DIR]"
)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    directory: str | None = None
    if "--jobs-dir" in args:
        index = args.index("--jobs-dir")
        if index + 1 >= len(args):
            print(USAGE)
            return 2
        directory = args[index + 1]
        args = args[:index] + args[index + 2 :]
    if not args:
        print(USAGE)
        return 2
    try:
        if args[0] == "list" and len(args) == 1:
            sys.stdout.write(render_table(list_jobs(directory)))
            return 0
        if args[0] == "render" and len(args) == 2:
            sys.stdout.write(render(args[1], directory))
            return 0
    except (JobSpecError, RulesError, OSError) as exc:
        print(f"error: {exc}")
        return 2
    print(USAGE)
    return 2


def jobs_cli() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
