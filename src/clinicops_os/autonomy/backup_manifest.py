"""SHA-256 manifests for backup folders.

``build(directory)`` lists every regular file under a directory with its size
and SHA-256; ``verify(manifest, directory)`` recomputes and reports every
mismatch (missing, changed size, changed hash, extra file). Both sides are
plain JSON so the nightly backup job and Ali can use the same format.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

MANIFEST_SCHEMA_VERSION = "1.0"
DEFAULT_MANIFEST_NAME = "MANIFEST.json"
_CHUNK = 1 << 20


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_files(directory: Path, exclude_names: set[str]) -> list[Path]:
    files = [
        path
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name not in exclude_names
    ]
    return files


def build(
    directory: str | Path,
    origin: str = "local",
    exclude_names: set[str] | None = None,
    generated_utc: str | None = None,
) -> dict[str, object]:
    """Build a manifest for every regular file under ``directory``."""
    base = Path(directory)
    if not base.is_dir():
        raise ValueError(f"not a directory: {base}")
    excluded = set(exclude_names or set()) | {DEFAULT_MANIFEST_NAME}
    entries = []
    total = 0
    for path in _iter_files(base, excluded):
        size = path.stat().st_size
        total += size
        entries.append(
            {
                "name": path.relative_to(base).as_posix(),
                "bytes": size,
                "sha256": sha256_of(path),
                "origin": origin,
            }
        )
    stamp = generated_utc or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "generated_utc": stamp,
        "directory": base.name,
        "files": entries,
        "counts": {"files": len(entries), "bytes": total},
    }


def verify(
    manifest: dict[str, object],
    directory: str | Path,
    exclude_names: set[str] | None = None,
) -> list[str]:
    """Return mismatches between ``manifest`` and the files under ``directory``."""
    base = Path(directory)
    if not base.is_dir():
        return [f"not a directory: {base}"]
    files = manifest.get("files")
    if not isinstance(files, list):
        return ["manifest has no 'files' list"]

    mismatches: list[str] = []
    expected: dict[str, dict[str, object]] = {}
    for entry in files:
        if not isinstance(entry, dict) or "name" not in entry:
            mismatches.append(f"malformed manifest entry: {entry!r}")
            continue
        expected[str(entry["name"])] = entry

    excluded = set(exclude_names or set()) | {DEFAULT_MANIFEST_NAME}
    present = {path.relative_to(base).as_posix(): path for path in _iter_files(base, excluded)}

    for name, entry in sorted(expected.items()):
        path = present.get(name)
        if path is None:
            mismatches.append(f"missing: {name}")
            continue
        size = path.stat().st_size
        if "bytes" in entry and int(entry["bytes"]) != size:
            mismatches.append(f"size mismatch: {name} manifest={entry['bytes']} actual={size}")
        digest = sha256_of(path)
        if str(entry.get("sha256", "")).lower() != digest:
            mismatches.append(
                f"sha256 mismatch: {name} manifest={entry.get('sha256')} actual={digest}"
            )
    for name in sorted(set(present) - set(expected)):
        mismatches.append(f"extra file not in manifest: {name}")
    return mismatches


def load_manifest(path: str | Path) -> dict[str, object]:
    try:
        parsed = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"manifest is not valid JSON: {path}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise TypeError(f"manifest must be a JSON object: {path}")
    return parsed


USAGE = (
    "usage:\n"
    "  clinicops-backup-manifest build DIR [--origin NAME] [--out FILE]\n"
    "  clinicops-backup-manifest verify MANIFEST DIR\n"
    "verify exits 2 when any file is missing, changed or unexpected"
)


def _take_option(args: list[str], flag: str) -> tuple[list[str], str | None]:
    if flag not in args:
        return args, None
    index = args.index(flag)
    if index + 1 >= len(args):
        raise SystemExit(f"{flag} requires a value")
    return args[:index] + args[index + 2 :], args[index + 1]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(USAGE)
        return 2
    command, rest = args[0], args[1:]

    if command == "build":
        rest, origin = _take_option(rest, "--origin")
        rest, out = _take_option(rest, "--out")
        if len(rest) != 1:
            print(USAGE)
            return 2
        try:
            manifest = build(rest[0], origin=origin or "local")
        except (OSError, ValueError) as exc:
            print(f"error: {exc}")
            return 2
        text = json.dumps(manifest, indent=2) + "\n"
        if out:
            Path(out).write_text(text, encoding="utf-8")
            print(
                f"manifest written: {out} ({manifest['counts']['files']} files, "  # type: ignore[index]
                f"{manifest['counts']['bytes']} bytes)"  # type: ignore[index]
            )
        else:
            sys.stdout.write(text)
        return 0

    if command == "verify":
        if len(rest) != 2:
            print(USAGE)
            return 2
        try:
            manifest = load_manifest(rest[0])
        except (TypeError, ValueError) as exc:
            print(f"error: {exc}")
            return 2
        mismatches = verify(manifest, rest[1])
        if mismatches:
            print(f"manifest verify FAILED: {len(mismatches)} mismatch(es)")
            for item in mismatches:
                print(f"  {item}")
            return 2
        count = len(manifest.get("files", []))  # type: ignore[arg-type]
        print(f"manifest verify OK: {count} files match")
        return 0

    print(USAGE)
    return 2


def backup_manifest_cli() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
