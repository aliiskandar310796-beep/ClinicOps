from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

MAX_CASE_BYTES = 5_000_000
MAX_SOURCES = 50
MAX_SURFACES = 100
MAX_RULES = 250
MAX_CHANGES = 250
MAX_FIELDS_PER_RECORD = 250
MAX_TEXT_LENGTH = 10_000


def _fail(message: str) -> None:
    raise ValueError(message)


def _strict_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        _fail("case file does not exist")
    if p.stat().st_size > MAX_CASE_BYTES:
        _fail(f"case file exceeds {MAX_CASE_BYTES} bytes")

    def reject_constant(value: str) -> None:
        _fail(f"non-finite JSON number is not allowed: {value}")

    raw = json.loads(p.read_text(encoding="utf-8"), parse_constant=reject_constant)
    if not isinstance(raw, dict):
        _fail("integrity case must be a JSON object")
    return raw


def _check_scalar(value: object, *, label: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        _fail(f"{label} contains a non-finite number")
    if isinstance(value, str) and len(value) > MAX_TEXT_LENGTH:
        _fail(f"{label} exceeds {MAX_TEXT_LENGTH} characters")
    if value is not None and not isinstance(value, (str, int, float, bool)):
        _fail(f"{label} must be a JSON scalar")


def _typed_key(value: object) -> tuple[str, str]:
    return type(value).__name__, json.dumps(value, ensure_ascii=False, sort_keys=True)


def preflight_case_safety(path: str | Path) -> dict[str, Any]:
    """Fail closed on oversized, ambiguous or disallowed live-pilot inputs.

    This is intentionally stricter than the underlying reconciliation engine. The public/operator
    CLI calls this before bundle generation so unsafe cases do not enter the delivery workflow.
    """

    case = _strict_json(path)

    governance = case.get("data_governance")
    if not isinstance(governance, dict):
        _fail("data_governance must be a JSON object")
    if governance.get("contains_patient_identifiable_data") is not False:
        _fail("contains_patient_identifiable_data must be explicitly false")
    if governance.get("processing_authorized") is not True:
        _fail("processing_authorized must be explicitly true")
    if governance.get("source_population_approved") is not True:
        _fail("source_population_approved must be explicitly true")

    sources = case.get("controlled_sources")
    surfaces = case.get("surfaces")
    rules = case.get("rules")
    changes = case.get("changes", [])
    if not isinstance(sources, list) or len(sources) > MAX_SOURCES:
        _fail(f"controlled_sources must contain at most {MAX_SOURCES} items")
    if not isinstance(surfaces, list) or len(surfaces) > MAX_SURFACES:
        _fail(f"surfaces must contain at most {MAX_SURFACES} items")
    if not isinstance(rules, list) or len(rules) > MAX_RULES:
        _fail(f"rules must contain at most {MAX_RULES} items")
    if not isinstance(changes, list) or len(changes) > MAX_CHANGES:
        _fail(f"changes must contain at most {MAX_CHANGES} items")

    source_ids: set[str] = set()
    surface_ids: set[str] = set()
    for collection_name, collection, id_key, id_set in (
        ("controlled_sources", sources, "source_id", source_ids),
        ("surfaces", surfaces, "surface_id", surface_ids),
    ):
        for index, item in enumerate(collection):
            if not isinstance(item, dict):
                _fail(f"{collection_name}[{index}] must be a JSON object")
            item_id = item.get(id_key)
            if not isinstance(item_id, str) or not item_id.strip():
                _fail(f"{collection_name}[{index}].{id_key} must be a non-empty string")
            if len(item_id) > 200:
                _fail(f"{collection_name}[{index}].{id_key} is too long")
            id_set.add(item_id)
            evidence_ref = item.get("evidence_ref")
            if not isinstance(evidence_ref, str) or not evidence_ref.strip():
                _fail(f"{collection_name}[{index}].evidence_ref must be a non-empty string")
            if len(evidence_ref) > 1_000:
                _fail(f"{collection_name}[{index}].evidence_ref is too long")
            fields = item.get("fields")
            if not isinstance(fields, dict):
                _fail(f"{collection_name}[{index}].fields must be a JSON object")
            if len(fields) > MAX_FIELDS_PER_RECORD:
                _fail(
                    f"{collection_name}[{index}].fields exceeds {MAX_FIELDS_PER_RECORD} fields"
                )
            for field, value in fields.items():
                if not isinstance(field, str) or not field.strip() or len(field) > 200:
                    _fail(f"{collection_name}[{index}] contains an invalid field name")
                _check_scalar(value, label=f"{collection_name}[{index}].fields[{field!r}]")

    overlap = source_ids.intersection(surface_ids)
    if overlap:
        _fail(f"source_id and surface_id values must not overlap: {sorted(overlap)}")

    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            _fail(f"rules[{index}] must be a JSON object")
        targets = rule.get("targets")
        if not isinstance(targets, list):
            _fail(f"rules[{index}].targets must be a list")
        for target in targets:
            if not isinstance(target, str) or not target.strip():
                _fail(f"rules[{index}].targets must contain only non-empty strings")

    for index, change in enumerate(changes):
        if not isinstance(change, dict):
            _fail(f"changes[{index}] must be a JSON object")
        old_value = change.get("old_value")
        new_value = change.get("new_value")
        _check_scalar(old_value, label=f"changes[{index}].old_value")
        _check_scalar(new_value, label=f"changes[{index}].new_value")
        if _typed_key(old_value) == _typed_key(new_value):
            _fail(f"changes[{index}] old_value and new_value must differ")
        expected = change.get("expected_surfaces")
        if not isinstance(expected, list):
            _fail(f"changes[{index}].expected_surfaces must be a list")
        for target in expected:
            if not isinstance(target, str) or not target.strip():
                _fail(
                    f"changes[{index}].expected_surfaces must contain only non-empty strings"
                )

    return case
