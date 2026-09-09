from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .intake import render_intake_findings, validate_portfolio
from .transition_report import load_portfolio, render_json, render_markdown


@dataclass(frozen=True)
class BundleResult:
    output_dir: Path
    manifest: dict[str, object]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_pilot_bundle(
    portfolio_path: str | Path,
    output_dir: str | Path,
    *,
    as_of: date,
) -> BundleResult:
    source = Path(portfolio_path)
    destination = Path(output_dir)
    rows = load_portfolio(source)
    findings = validate_portfolio(rows)
    errors = [item for item in findings if item.severity == "error"]
    if errors:
        detail = "; ".join(
            f"row {item.row_number} {item.field}: {item.message}" for item in errors
        )
        raise ValueError(f"portfolio intake blocked: {detail}")

    destination.mkdir(parents=True, exist_ok=True)
    markdown_path = destination / "portfolio_report.md"
    json_path = destination / "portfolio_report.json"
    intake_path = destination / "intake_diagnostics.md"
    manifest_path = destination / "manifest.json"

    markdown_path.write_text(render_markdown(rows, as_of=as_of), encoding="utf-8")
    json_path.write_text(render_json(rows, as_of=as_of), encoding="utf-8")
    intake_path.write_text(render_intake_findings(findings), encoding="utf-8")

    manifest: dict[str, object] = {
        "bundle_schema_version": "1.0",
        "as_of": as_of.isoformat(),
        "source_file": source.name,
        "source_sha256": _sha256(source),
        "records_reviewed": len(rows),
        "diagnostics": {
            "errors": 0,
            "warnings": sum(item.severity == "warning" for item in findings),
            "information_gaps": sum(item.severity == "info" for item in findings),
        },
        "outputs": [
            markdown_path.name,
            json_path.name,
            intake_path.name,
        ],
        "interpretation": (
            "Evidence-quality diagnostics and operator triage only; "
            "not a compliance determination or legal conclusion."
        ),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return BundleResult(destination, manifest)
