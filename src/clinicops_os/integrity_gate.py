from __future__ import annotations

import hashlib
import html
import json
from collections.abc import Mapping
from datetime import date
from pathlib import Path

CASE_SCHEMA_VERSION = "1.0"
BUNDLE_SCHEMA_VERSION = "1.0"

PASS = "PASS"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
UNRESOLVED_AUTHORITY = "UNRESOLVED_AUTHORITY"
HOLD_FOR_HUMAN_DECISION = "HOLD_FOR_HUMAN_DECISION"

_GATE_RANK = {
    PASS: 0,
    REVIEW_REQUIRED: 1,
    UNRESOLVED_AUTHORITY: 2,
    HOLD_FOR_HUMAN_DECISION: 3,
}

LIMITATIONS = (
    "This is an evidence-reconciliation and change-propagation screen, not a legal, "
    "regulatory or compliance determination.",
    "A PASS means the declared rules found no discrepancy in the supplied evidence; "
    "it does not establish overall device compliance or completeness.",
    "Authoritative values are never inferred when supplied controlled sources disagree.",
    "External release remains human-review gated even when the automated gate status is PASS.",
)


def _is_scalar(value: object) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _value_key(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _nonempty(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _json_object(path: str | Path, *, label: str) -> dict[str, object]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError(f"{label} must be a JSON object")
    return raw


def sha256_path(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_case(case: Mapping[str, object]) -> None:
    if case.get("schema_version") != CASE_SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {CASE_SCHEMA_VERSION}")
    _nonempty(case.get("case_id"), label="case_id")
    as_of = _nonempty(case.get("as_of"), label="as_of")
    try:
        date.fromisoformat(as_of)
    except ValueError as exc:
        raise ValueError("as_of must be an ISO date (YYYY-MM-DD)") from exc

    scope = case.get("scope")
    if not isinstance(scope, dict):
        raise TypeError("scope must be a JSON object")

    source_ids: set[str] = set()
    sources = case.get("controlled_sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("controlled_sources must be a non-empty list")
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise TypeError(f"controlled_sources[{index}] must be a JSON object")
        source_id = _nonempty(
            source.get("source_id"), label=f"controlled_sources[{index}].source_id"
        )
        if source_id in source_ids:
            raise ValueError(f"duplicate controlled source_id: {source_id}")
        source_ids.add(source_id)
        _nonempty(source.get("source_type"), label=f"{source_id}.source_type")
        _nonempty(source.get("evidence_ref"), label=f"{source_id}.evidence_ref")
        fields = source.get("fields")
        if not isinstance(fields, dict):
            raise TypeError(f"{source_id}.fields must be a JSON object")
        for field, value in fields.items():
            _nonempty(field, label=f"{source_id}.field")
            if not _is_scalar(value):
                raise TypeError(
                    f"{source_id}.fields[{field!r}] must be a JSON scalar"
                )

    surface_ids: set[str] = set()
    surfaces = case.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        raise ValueError("surfaces must be a non-empty list")
    for index, surface in enumerate(surfaces):
        if not isinstance(surface, dict):
            raise TypeError(f"surfaces[{index}] must be a JSON object")
        surface_id = _nonempty(
            surface.get("surface_id"), label=f"surfaces[{index}].surface_id"
        )
        if surface_id in surface_ids:
            raise ValueError(f"duplicate surface_id: {surface_id}")
        surface_ids.add(surface_id)
        _nonempty(surface.get("surface_type"), label=f"{surface_id}.surface_type")
        _nonempty(surface.get("evidence_ref"), label=f"{surface_id}.evidence_ref")
        fields = surface.get("fields")
        if not isinstance(fields, dict):
            raise TypeError(f"{surface_id}.fields must be a JSON object")
        for field, value in fields.items():
            _nonempty(field, label=f"{surface_id}.field")
            if not _is_scalar(value):
                raise TypeError(
                    f"{surface_id}.fields[{field!r}] must be a JSON scalar"
                )

    rule_ids: set[str] = set()
    rules = case.get("rules")
    if not isinstance(rules, list) or not rules:
        raise ValueError("rules must be a non-empty list")
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise TypeError(f"rules[{index}] must be a JSON object")
        rule_id = _nonempty(rule.get("rule_id"), label=f"rules[{index}].rule_id")
        if rule_id in rule_ids:
            raise ValueError(f"duplicate rule_id: {rule_id}")
        rule_ids.add(rule_id)
        _nonempty(rule.get("field"), label=f"{rule_id}.field")
        mode = rule.get("mode")
        if mode not in {"match_authority", "required_presence"}:
            raise ValueError(
                f"{rule_id}.mode must be match_authority or required_presence"
            )
        targets = rule.get("targets")
        if not isinstance(targets, list) or not targets:
            raise ValueError(f"{rule_id}.targets must be a non-empty list")
        unknown = [target for target in targets if target not in surface_ids]
        if unknown:
            raise ValueError(
                f"{rule_id}.targets contains unknown surfaces: {unknown}"
            )
        if len(targets) != len(set(targets)):
            raise ValueError(f"{rule_id}.targets contains duplicates")

    change_ids: set[str] = set()
    changes = case.get("changes", [])
    if not isinstance(changes, list):
        raise TypeError("changes must be a list")
    for index, change in enumerate(changes):
        if not isinstance(change, dict):
            raise TypeError(f"changes[{index}] must be a JSON object")
        change_id = _nonempty(
            change.get("change_id"), label=f"changes[{index}].change_id"
        )
        if change_id in change_ids:
            raise ValueError(f"duplicate change_id: {change_id}")
        change_ids.add(change_id)
        _nonempty(change.get("field"), label=f"{change_id}.field")
        approved_source_id = _nonempty(
            change.get("approved_source_id"),
            label=f"{change_id}.approved_source_id",
        )
        if approved_source_id not in source_ids:
            raise ValueError(
                f"{change_id}.approved_source_id is unknown: {approved_source_id}"
            )
        if not _is_scalar(change.get("old_value")) or not _is_scalar(
            change.get("new_value")
        ):
            raise TypeError(f"{change_id} old_value/new_value must be JSON scalars")
        expected = change.get("expected_surfaces")
        if not isinstance(expected, list) or not expected:
            raise ValueError(
                f"{change_id}.expected_surfaces must be a non-empty list"
            )
        unknown = [target for target in expected if target not in surface_ids]
        if unknown:
            raise ValueError(
                f"{change_id}.expected_surfaces contains unknown surfaces: {unknown}"
            )
        if len(expected) != len(set(expected)):
            raise ValueError(f"{change_id}.expected_surfaces contains duplicates")


def load_case(path: str | Path) -> dict[str, object]:
    case = _json_object(path, label="integrity case")
    validate_case(case)
    return case


def _source_authority(
    sources: list[dict[str, object]], field: str
) -> tuple[str, object | None, list[dict[str, object]]]:
    candidates: list[dict[str, object]] = []
    for source in sources:
        fields = source["fields"]
        assert isinstance(fields, dict)
        if field in fields and fields[field] not in ("", None):
            candidates.append(source)
    if not candidates:
        return "missing", None, []
    distinct = {
        _value_key(source["fields"][field])  # type: ignore[index]
        for source in candidates
    }
    if len(distinct) > 1:
        return "conflict", None, candidates
    return "resolved", candidates[0]["fields"][field], candidates  # type: ignore[index]


def evaluate_case(
    case: Mapping[str, object], *, input_sha256: str | None = None
) -> dict[str, object]:
    validate_case(case)
    sources = [dict(item) for item in case["controlled_sources"]]  # type: ignore[index]
    surfaces = [dict(item) for item in case["surfaces"]]  # type: ignore[index]
    surface_by_id = {surface["surface_id"]: surface for surface in surfaces}

    pending: list[dict[str, object]] = []
    rule_checks = 0
    change_checks = 0

    def add_finding(
        *,
        code: str,
        gate_status: str,
        field: str,
        message: str,
        surface_id: str | None = None,
        rule_id: str | None = None,
        change_id: str | None = None,
        observed_value: object = None,
        expected_value: object = None,
        evidence_refs: list[str] | None = None,
    ) -> None:
        pending.append(
            {
                "code": code,
                "gate_status": gate_status,
                "rule_id": rule_id,
                "change_id": change_id,
                "field": field,
                "surface_id": surface_id,
                "observed_value": observed_value,
                "expected_value": expected_value,
                "evidence_refs": evidence_refs or [],
                "message": message,
            }
        )

    for rule in sorted(
        case["rules"], key=lambda item: item["rule_id"]  # type: ignore[index]
    ):
        rule_id = rule["rule_id"]
        field = rule["field"]
        targets = rule["targets"]
        mode = rule["mode"]

        if mode == "required_presence":
            for target_id in targets:
                rule_checks += 1
                surface = surface_by_id[target_id]
                fields = surface["fields"]
                assert isinstance(fields, dict)
                observed = fields.get(field)
                if observed in ("", None):
                    add_finding(
                        code="MISSING_REQUIRED_FIELD",
                        gate_status=REVIEW_REQUIRED,
                        field=field,
                        surface_id=target_id,
                        rule_id=rule_id,
                        observed_value=observed,
                        evidence_refs=[str(surface["evidence_ref"])],
                        message=(
                            f"{target_id} has no supplied value for required field "
                            f"{field}."
                        ),
                    )
            continue

        authority_state, expected_value, authority_sources = _source_authority(
            sources, field
        )
        authority_refs = [
            str(source["evidence_ref"]) for source in authority_sources
        ]
        if authority_state == "missing":
            add_finding(
                code="AUTHORITY_MISSING",
                gate_status=UNRESOLVED_AUTHORITY,
                field=field,
                rule_id=rule_id,
                evidence_refs=[],
                message=(
                    f"No client-approved controlled source supplied an authoritative value "
                    f"for {field}; ClinicOps will not infer one."
                ),
            )
            rule_checks += len(targets)
            continue
        if authority_state == "conflict":
            values = {
                str(source["source_id"]): source["fields"][field]  # type: ignore[index]
                for source in authority_sources
            }
            add_finding(
                code="AUTHORITY_CONFLICT",
                gate_status=UNRESOLVED_AUTHORITY,
                field=field,
                rule_id=rule_id,
                observed_value=values,
                evidence_refs=authority_refs,
                message=(
                    f"Supplied controlled sources disagree on {field}; authoritative "
                    "source is unresolved and requires RA/QA decision."
                ),
            )
            rule_checks += len(targets)
            continue

        for target_id in targets:
            rule_checks += 1
            surface = surface_by_id[target_id]
            fields = surface["fields"]
            assert isinstance(fields, dict)
            observed = fields.get(field)
            if observed in ("", None):
                add_finding(
                    code="MISSING_FIELD",
                    gate_status=REVIEW_REQUIRED,
                    field=field,
                    surface_id=target_id,
                    rule_id=rule_id,
                    observed_value=observed,
                    expected_value=expected_value,
                    evidence_refs=authority_refs + [str(surface["evidence_ref"])],
                    message=f"{target_id} has no supplied {field} value to reconcile.",
                )
            elif observed != expected_value:
                add_finding(
                    code="VALUE_MISMATCH",
                    gate_status=REVIEW_REQUIRED,
                    field=field,
                    surface_id=target_id,
                    rule_id=rule_id,
                    observed_value=observed,
                    expected_value=expected_value,
                    evidence_refs=authority_refs + [str(surface["evidence_ref"])],
                    message=(
                        f"{target_id} does not match the single supplied client-approved "
                        f"controlled value for {field}."
                    ),
                )

    source_by_id = {source["source_id"]: source for source in sources}
    for change in sorted(
        case.get("changes", []), key=lambda item: item["change_id"]  # type: ignore[index]
    ):
        change_id = change["change_id"]
        field = change["field"]
        old_value = change.get("old_value")
        new_value = change.get("new_value")
        approved_source = source_by_id[change["approved_source_id"]]
        approved_fields = approved_source["fields"]
        assert isinstance(approved_fields, dict)
        source_value = approved_fields.get(field)

        if source_value in ("", None):
            add_finding(
                code="CHANGE_SOURCE_MISSING",
                gate_status=UNRESOLVED_AUTHORITY,
                field=field,
                change_id=change_id,
                observed_value=source_value,
                expected_value=new_value,
                evidence_refs=[str(approved_source["evidence_ref"])],
                message=(
                    f"The declared approved source has no supplied {field} value for "
                    f"change {change_id}; propagation cannot be evaluated safely."
                ),
            )
        elif source_value != new_value:
            add_finding(
                code="CHANGE_SOURCE_MISMATCH",
                gate_status=HOLD_FOR_HUMAN_DECISION,
                field=field,
                change_id=change_id,
                observed_value=source_value,
                expected_value=new_value,
                evidence_refs=[str(approved_source["evidence_ref"])],
                message=(
                    f"The declared approved source does not contain the declared new "
                    f"value for {field}; hold for human decision."
                ),
            )

        for target_id in change["expected_surfaces"]:
            change_checks += 1
            surface = surface_by_id[target_id]
            fields = surface["fields"]
            assert isinstance(fields, dict)
            observed = fields.get(field)
            refs = [
                str(approved_source["evidence_ref"]),
                str(surface["evidence_ref"]),
            ]
            if observed in ("", None):
                add_finding(
                    code="CHANGE_TARGET_MISSING",
                    gate_status=HOLD_FOR_HUMAN_DECISION,
                    field=field,
                    surface_id=target_id,
                    change_id=change_id,
                    observed_value=observed,
                    expected_value=new_value,
                    evidence_refs=refs,
                    message=(
                        f"{target_id} is declared in the change-propagation scope but "
                        f"has no supplied {field} value."
                    ),
                )
            elif observed == new_value:
                continue
            elif observed == old_value:
                add_finding(
                    code="CHANGE_NOT_PROPAGATED",
                    gate_status=HOLD_FOR_HUMAN_DECISION,
                    field=field,
                    surface_id=target_id,
                    change_id=change_id,
                    observed_value=observed,
                    expected_value=new_value,
                    evidence_refs=refs,
                    message=(
                        f"{target_id} still contains the declared old value for {field}; "
                        "change propagation is incomplete."
                    ),
                )
            else:
                add_finding(
                    code="CHANGE_VALUE_CONFLICT",
                    gate_status=HOLD_FOR_HUMAN_DECISION,
                    field=field,
                    surface_id=target_id,
                    change_id=change_id,
                    observed_value=observed,
                    expected_value=new_value,
                    evidence_refs=refs,
                    message=(
                        f"{target_id} contains a third value for {field}; hold for human "
                        "decision."
                    ),
                )

    hold_keys = {
        (finding.get("field"), finding.get("surface_id"))
        for finding in pending
        if finding.get("gate_status") == HOLD_FOR_HUMAN_DECISION
        and finding.get("surface_id") is not None
    }
    pending = [
        finding
        for finding in pending
        if not (
            finding.get("gate_status") == REVIEW_REQUIRED
            and (finding.get("field"), finding.get("surface_id")) in hold_keys
        )
    ]

    pending.sort(
        key=lambda finding: (
            -_GATE_RANK[str(finding["gate_status"])],
            str(finding.get("change_id") or ""),
            str(finding.get("rule_id") or ""),
            str(finding.get("surface_id") or ""),
            str(finding["field"]),
            str(finding["code"]),
        )
    )
    findings: list[dict[str, object]] = []
    for index, finding in enumerate(pending, start=1):
        enriched = {"finding_id": f"IGF-{index:03d}"}
        enriched.update(finding)
        findings.append(enriched)

    gate_status = PASS
    if findings:
        gate_status = max(
            (str(finding["gate_status"]) for finding in findings),
            key=lambda status: _GATE_RANK[status],
        )

    return {
        "analysis_schema_version": CASE_SCHEMA_VERSION,
        "case_id": case["case_id"],
        "as_of": case["as_of"],
        "scope": case["scope"],
        "input_sha256": input_sha256,
        "gate_status": gate_status,
        "human_review_required": True,
        "release_ready": False,
        "metrics": {
            "controlled_sources": len(sources),
            "surfaces": len(surfaces),
            "rule_checks": rule_checks,
            "change_checks": change_checks,
            "findings": len(findings),
            "hold_findings": sum(
                finding["gate_status"] == HOLD_FOR_HUMAN_DECISION
                for finding in findings
            ),
            "unresolved_authority_findings": sum(
                finding["gate_status"] == UNRESOLVED_AUTHORITY
                for finding in findings
            ),
            "review_findings": sum(
                finding["gate_status"] == REVIEW_REQUIRED for finding in findings
            ),
        },
        "findings": findings,
        "limitations": list(LIMITATIONS),
    }


def render_markdown(report: Mapping[str, object]) -> str:
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    lines = [
        f"# Integrity Gate — {report['case_id']}",
        "",
        f"**As of:** {report['as_of']}",
        f"**Automated gate status:** `{report['gate_status']}`",
        "**External release:** `HUMAN REVIEW REQUIRED`",
        "",
        "## Coverage",
        "",
        f"- controlled sources: {metrics['controlled_sources']}",
        f"- declared surfaces: {metrics['surfaces']}",
        f"- reconciliation checks: {metrics['rule_checks']}",
        f"- change-propagation checks: {metrics['change_checks']}",
        f"- findings: {metrics['findings']}",
        "",
        "## Findings",
        "",
    ]
    findings = report["findings"]
    assert isinstance(findings, list)
    if not findings:
        lines.append("No discrepancy was found by the declared automated checks.")
    else:
        for finding in findings:
            assert isinstance(finding, dict)
            lines.extend(
                [
                    f"### {finding['finding_id']} — {finding['code']}",
                    "",
                    f"- status: `{finding['gate_status']}`",
                    f"- field: `{finding['field']}`",
                    f"- surface: `{finding.get('surface_id') or 'n/a'}`",
                    f"- observed: `{finding.get('observed_value')}`",
                    f"- expected: `{finding.get('expected_value')}`",
                    f"- message: {finding['message']}",
                    "- evidence:",
                ]
            )
            refs = finding.get("evidence_refs", [])
            if refs:
                for ref in refs:
                    lines.append(f"  - `{ref}`")
            else:
                lines.append("  - none supplied")
            lines.append("")
    lines.extend(["## Limitations", ""])
    for limitation in report["limitations"]:  # type: ignore[index]
        lines.append(f"- {limitation}")
    lines.append("")
    return "\n".join(lines)


def render_html(report: Mapping[str, object]) -> str:
    findings = report["findings"]
    assert isinstance(findings, list)
    rows = []
    for finding in findings:
        assert isinstance(finding, dict)
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(finding['finding_id']))}</td>"
            f"<td>{html.escape(str(finding['gate_status']))}</td>"
            f"<td>{html.escape(str(finding['code']))}</td>"
            f"<td>{html.escape(str(finding['field']))}</td>"
            f"<td>{html.escape(str(finding.get('surface_id') or 'n/a'))}</td>"
            f"<td>{html.escape(str(finding.get('observed_value')))}</td>"
            f"<td>{html.escape(str(finding.get('expected_value')))}</td>"
            "</tr>"
        )
    if not rows:
        rows.append(
            "<tr><td colspan=\"7\">No discrepancy found by declared automated checks.</td></tr>"
        )
    limitations = "".join(
        f"<li>{html.escape(str(item))}</li>"
        for item in report["limitations"]  # type: ignore[index]
    )
    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>Integrity Gate — {html.escape(str(report['case_id']))}</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:1100px;margin:40px auto;padding:0 20px;line-height:1.5;color:#1c2430}}
.badge{{display:inline-block;padding:5px 10px;border:1px solid #9aa5b1;border-radius:999px;font-weight:700}}
.callout{{background:#f3f1ec;padding:14px 16px;border-radius:10px}}
table{{width:100%;border-collapse:collapse;margin:20px 0}}th,td{{border:1px solid #d8dee5;padding:8px;text-align:left;vertical-align:top;font-size:.92rem}}
code{{background:#f3f1ec;padding:2px 4px;border-radius:4px}}
</style>
</head>
<body>
<h1>ClinicOps Integrity Gate</h1>
<p><strong>Case:</strong> {html.escape(str(report['case_id']))} · <strong>As of:</strong> {html.escape(str(report['as_of']))}</p>
<p><span class=\"badge\">{html.escape(str(report['gate_status']))}</span></p>
<div class=\"callout\"><strong>DRAFT — HUMAN REVIEW REQUIRED.</strong> Automated output is not a compliance determination and is not externally release-ready.</div>
<h2>Findings</h2>
<table>
<thead><tr><th>ID</th><th>Status</th><th>Code</th><th>Field</th><th>Surface</th><th>Observed</th><th>Expected</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
<h2>Limitations</h2>
<ul>{limitations}</ul>
</body>
</html>
"""


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def build_bundle(case_path: str | Path, output_dir: str | Path) -> dict[str, object]:
    case_path = Path(case_path)
    case = load_case(case_path)
    input_hash = sha256_path(case_path)
    report = evaluate_case(case, input_sha256=input_hash)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for stale_name in ("review_gate.json", "review_record.json"):
        stale_path = out / stale_name
        if stale_path.exists():
            stale_path.unlink()

    report_json = out / "integrity_report.json"
    report_md = out / "integrity_report.md"
    report_html = out / "integrity_report.html"
    _write_text(
        report_json,
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
    )
    _write_text(report_md, render_markdown(report))
    _write_text(report_html, render_html(report))

    manifest = {
        "bundle_schema_version": BUNDLE_SCHEMA_VERSION,
        "case_id": case["case_id"],
        "as_of": case["as_of"],
        "gate_status": report["gate_status"],
        "release_status": "DRAFT — HUMAN REVIEW REQUIRED",
        "source_sha256": input_hash,
        "files": {
            "integrity_report.json": sha256_path(report_json),
            "integrity_report.md": sha256_path(report_md),
            "integrity_report.html": sha256_path(report_html),
        },
    }
    _write_text(
        out / "manifest.json",
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    )
    return report


def verify_bundle_integrity(
    output_dir: str | Path, case_path: str | Path | None = None
) -> tuple[bool, tuple[str, ...], dict[str, object]]:
    out = Path(output_dir)
    reasons: list[str] = []
    manifest_path = out / "manifest.json"
    if not manifest_path.is_file():
        return False, ("manifest.json is missing",), {}
    try:
        manifest = _json_object(manifest_path, label="manifest.json")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return False, (str(exc),), {}
    if manifest.get("bundle_schema_version") != BUNDLE_SCHEMA_VERSION:
        reasons.append(f"bundle_schema_version must be {BUNDLE_SCHEMA_VERSION}")
    files = manifest.get("files")
    if not isinstance(files, dict):
        reasons.append("manifest files must be a JSON object")
    else:
        for name, expected_hash in files.items():
            path = out / str(name)
            if not path.is_file():
                reasons.append(f"{name} is missing")
                continue
            if sha256_path(path) != expected_hash:
                reasons.append(f"{name} hash does not match manifest")
    if case_path is not None:
        source_hash = sha256_path(case_path)
        if source_hash != manifest.get("source_sha256"):
            reasons.append("source_sha256 does not match supplied case file")
    return not reasons, tuple(reasons), manifest
