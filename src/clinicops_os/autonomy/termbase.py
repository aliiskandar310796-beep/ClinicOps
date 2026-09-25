"""EN↔DA regulatory termbase: CSV schema, validation, merge and QA.

Schema (one row per term pair, header exact and in this order)::

    id,en_term,da_term,domain,subdomain,source_ref,source_url,
    context_en,context_da,status,confidence,added_utc,job_run

* ``status``: ``verified`` (both terms quoted from the same aligned provision),
  ``candidate`` (aligned but ambiguous, or a synonym), ``unverified-seed``
  (not yet checked at source).
* ``confidence``: 0.0–1.0. An ``unverified-seed`` row may not exceed 0.5.
* A ``verified`` row must carry both contexts and a source URL.

Only public-source rows belong in ``data/termbase/termbase_public.csv``;
rows derived from the private corpus stay in Drive and the private project.
"""

from __future__ import annotations

import csv
import io
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

HEADER: tuple[str, ...] = (
    "id",
    "en_term",
    "da_term",
    "domain",
    "subdomain",
    "source_ref",
    "source_url",
    "context_en",
    "context_da",
    "status",
    "confidence",
    "added_utc",
    "job_run",
)
STATUSES = frozenset({"verified", "candidate", "unverified-seed"})
ID_RE = re.compile(r"^TB-(\d{4,})$")
ADDED_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SEED_MAX_CONFIDENCE = 0.5
LONG_TERM_CHARS = 80


class TermbaseError(ValueError):
    """Raised when a termbase file cannot be read as the expected schema."""


@dataclass(frozen=True)
class MergeResult:
    rows: list[dict[str, str]]
    added: int
    skipped: int
    reassigned_ids: dict[str, str] = field(default_factory=dict)


def dedupe_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (
        row["en_term"].strip().casefold(),
        row["da_term"].strip().casefold(),
        row["source_ref"].strip().casefold(),
    )


def read_rows(path: str | Path) -> list[dict[str, str]]:
    """Read a termbase CSV; raise :class:`TermbaseError` on a wrong header."""
    target = Path(path)
    try:
        text = target.read_text(encoding="utf-8-sig")
    except FileNotFoundError as exc:
        raise TermbaseError(f"termbase file not found: {target}") from exc
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration as exc:
        raise TermbaseError(f"{target}: empty file, expected header {','.join(HEADER)}") from exc
    if tuple(header) != HEADER:
        raise TermbaseError(
            f"{target}: header mismatch\n  expected: {','.join(HEADER)}\n"
            f"  found:    {','.join(header)}"
        )
    rows: list[dict[str, str]] = []
    for line_number, values in enumerate(reader, start=2):
        if not values or all(not cell.strip() for cell in values):
            continue
        if len(values) != len(HEADER):
            raise TermbaseError(
                f"{target}: line {line_number}: expected {len(HEADER)} columns, "
                f"found {len(values)}"
            )
        rows.append(dict(zip(HEADER, values, strict=True)))
    return rows


def write_rows(path: str | Path, rows: list[dict[str, str]]) -> None:
    Path(path).write_text(render_csv(rows), encoding="utf-8")


def render_csv(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(HEADER)
    for row in rows:
        writer.writerow([row.get(column, "") for column in HEADER])
    return buffer.getvalue()


def _parse_confidence(value: str) -> float | None:
    try:
        number = float(value)
    except ValueError:
        return None
    if math.isnan(number):
        return None
    return number


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    """Return validation errors for parsed rows (empty list means valid)."""
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=2):
        row_id = row["id"].strip()
        label = f"line {index} ({row_id or 'no id'})"
        if not ID_RE.match(row_id):
            errors.append(f"{label}: id must match TB-#### (at least four digits)")
        elif row_id in seen_ids:
            errors.append(f"{label}: duplicate id")
        seen_ids.add(row_id)

        for column in ("en_term", "da_term", "source_ref", "domain", "job_run"):
            if not row[column].strip():
                errors.append(f"{label}: {column} must not be empty")

        status = row["status"].strip()
        if status not in STATUSES:
            errors.append(
                f"{label}: status {status!r} not in {', '.join(sorted(STATUSES))}"
            )

        confidence = _parse_confidence(row["confidence"].strip())
        if confidence is None or not 0.0 <= confidence <= 1.0:
            errors.append(f"{label}: confidence must be a number between 0 and 1")
        elif status == "unverified-seed" and confidence > SEED_MAX_CONFIDENCE:
            errors.append(
                f"{label}: unverified-seed confidence must be <= {SEED_MAX_CONFIDENCE}"
            )

        url = row["source_url"].strip()
        if url and not url.startswith(("https://", "http://")):
            errors.append(f"{label}: source_url must start with http:// or https://")

        if status == "verified":
            if not row["context_en"].strip() or not row["context_da"].strip():
                errors.append(f"{label}: verified rows need both context_en and context_da")
            if not url:
                errors.append(f"{label}: verified rows need a source_url")

        if not ADDED_UTC_RE.match(row["added_utc"].strip()):
            errors.append(f"{label}: added_utc must be ISO 8601 UTC like 2026-09-25T00:00:00Z")
    return errors


def validate(path: str | Path) -> list[str]:
    """Validate a termbase CSV file; header errors are returned, not raised."""
    try:
        rows = read_rows(path)
    except TermbaseError as exc:
        return [str(exc)]
    return validate_rows(rows)


def _id_number(row_id: str) -> int:
    match = ID_RE.match(row_id.strip())
    return int(match.group(1)) if match else 0


def _format_id(number: int, width: int) -> str:
    return f"TB-{number:0{width}d}"


def merge(master: list[dict[str, str]], delta: list[dict[str, str]]) -> MergeResult:
    """Append delta rows to master, skipping duplicates on (en, da, source_ref).

    Matching is case-insensitive and whitespace-trimmed. A delta row whose id
    collides with an existing id (but is a new pair) receives the next free id.
    """
    rows = [dict(row) for row in master]
    seen_keys = {dedupe_key(row) for row in rows}
    used_ids = {row["id"].strip() for row in rows}
    highest = max((_id_number(row["id"]) for row in rows), default=0)
    width = max((len(row["id"].strip()) - 3 for row in rows), default=4)
    width = max(width, 4)

    added = 0
    skipped = 0
    reassigned: dict[str, str] = {}
    for original in delta:
        row = dict(original)
        key = dedupe_key(row)
        if key in seen_keys:
            skipped += 1
            continue
        row_id = row["id"].strip()
        if not ID_RE.match(row_id) or row_id in used_ids:
            highest += 1
            new_id = _format_id(highest, width)
            reassigned[row_id or f"<row {added + skipped + 1}>"] = new_id
            row["id"] = new_id
        else:
            highest = max(highest, _id_number(row_id))
        used_ids.add(row["id"])
        seen_keys.add(key)
        rows.append(row)
        added += 1
    return MergeResult(rows=rows, added=added, skipped=skipped, reassigned_ids=reassigned)


def qa_report(path: str | Path) -> dict[str, object]:
    """Counts by status and domain, duplicate pairs and suspicious rows."""
    rows = read_rows(path)
    by_status = Counter(row["status"].strip() for row in rows)
    by_domain = Counter(row["domain"].strip() for row in rows)

    groups: dict[tuple[str, str, str], list[str]] = {}
    for row in rows:
        groups.setdefault(dedupe_key(row), []).append(row["id"])
    duplicates = [
        {"en_term": key[0], "da_term": key[1], "source_ref": key[2], "ids": ids}
        for key, ids in groups.items()
        if len(ids) > 1
    ]

    suspicious: list[dict[str, str]] = []
    for row in rows:
        en = row["en_term"].strip()
        da = row["da_term"].strip()
        reasons: list[str] = []
        if en.casefold() == da.casefold():
            reasons.append("identical en_term and da_term")
        if len(en) > LONG_TERM_CHARS or len(da) > LONG_TERM_CHARS:
            reasons.append(f"term longer than {LONG_TERM_CHARS} characters")
        if en.isdigit() or da.isdigit():
            reasons.append("term consists of digits only")
        if row["status"].strip() == "verified" and not row["source_url"].strip():
            reasons.append("verified row without source_url")
        for reason in reasons:
            suspicious.append({"id": row["id"], "reason": reason})

    return {
        "path": str(path),
        "rows": len(rows),
        "by_status": dict(sorted(by_status.items())),
        "by_domain": dict(sorted(by_domain.items())),
        "duplicates": duplicates,
        "suspicious": suspicious,
        "counts": {"duplicates": len(duplicates), "suspicious": len(suspicious)},
    }


def render_qa_report(report: dict[str, object]) -> str:
    lines = [f"termbase QA: {report['path']}", f"rows: {report['rows']}"]
    lines.append("by status:")
    for status, count in report["by_status"].items():  # type: ignore[union-attr]
        lines.append(f"  {status}: {count}")
    lines.append("by domain:")
    for domain, count in report["by_domain"].items():  # type: ignore[union-attr]
        lines.append(f"  {domain}: {count}")
    duplicates = report["duplicates"]
    suspicious = report["suspicious"]
    lines.append(f"duplicates: {len(duplicates)}")  # type: ignore[arg-type]
    for item in duplicates:  # type: ignore[union-attr]
        lines.append(f"  {', '.join(item['ids'])}: {item['en_term']} / {item['da_term']}")
    lines.append(f"suspicious: {len(suspicious)}")  # type: ignore[arg-type]
    for item in suspicious:  # type: ignore[union-attr]
        lines.append(f"  {item['id']}: {item['reason']}")
    return "\n".join(lines) + "\n"


USAGE = (
    "usage:\n"
    "  clinicops-termbase validate FILE\n"
    "  clinicops-termbase merge MASTER DELTA [--out FILE]\n"
    "  clinicops-termbase qa FILE [--json]"
)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(USAGE)
        return 2
    command, rest = args[0], args[1:]

    if command == "validate":
        if len(rest) != 1:
            print(USAGE)
            return 2
        errors = validate(rest[0])
        if errors:
            print(f"termbase INVALID: {rest[0]} ({len(errors)} error(s))")
            for error in errors:
                print(f"  {error}")
            return 2
        rows = read_rows(rest[0])
        print(f"termbase valid: {rest[0]} ({len(rows)} rows)")
        return 0

    if command == "merge":
        out: str | None = None
        if "--out" in rest:
            index = rest.index("--out")
            if index + 1 >= len(rest):
                print(USAGE)
                return 2
            out = rest[index + 1]
            rest = rest[:index] + rest[index + 2 :]
        if len(rest) != 2:
            print(USAGE)
            return 2
        for label, target in (("master", rest[0]), ("delta", rest[1])):
            errors = validate(target)
            if errors:
                print(f"{label} INVALID: {target}")
                for error in errors:
                    print(f"  {error}")
                return 2
        result = merge(read_rows(rest[0]), read_rows(rest[1]))
        if out:
            write_rows(out, result.rows)
            print(
                f"merged: {len(result.rows)} rows, added {result.added}, "
                f"skipped {result.skipped} duplicate(s), "
                f"reassigned {len(result.reassigned_ids)} id(s) -> {out}"
            )
        else:
            sys.stdout.write(render_csv(result.rows))
        return 0

    if command == "qa":
        as_json = "--json" in rest
        rest = [item for item in rest if item != "--json"]
        if len(rest) != 1:
            print(USAGE)
            return 2
        errors = validate(rest[0])
        if errors:
            print(f"termbase INVALID: {rest[0]} ({len(errors)} error(s))")
            for error in errors:
                print(f"  {error}")
            return 2
        report = qa_report(rest[0])
        if as_json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            sys.stdout.write(render_qa_report(report))
        return 0

    print(USAGE)
    return 2


def termbase_cli() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
