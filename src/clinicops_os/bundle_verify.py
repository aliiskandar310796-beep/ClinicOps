from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

EXPECTED_BUNDLE_SCHEMA_VERSION = "1.1"
EXPECTED_OUTPUTS = {
    "client_report.html",
    "portfolio_report.md",
    "portfolio_report.json",
    "intake_diagnostics.md",
}


@dataclass(frozen=True)
class BundleVerificationResult:
    valid: bool
    errors: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "bundle_schema_version": EXPECTED_BUNDLE_SCHEMA_VERSION,
            "valid": self.valid,
            "status": "VERIFIED" if self.valid else "INVALID",
            "errors": list(self.errors),
        }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_pilot_bundle(
    output_dir: str | Path,
    source_path: str | Path,
) -> BundleVerificationResult:
    """Verify a generated schema-1.1 bundle against its manifest and source file."""

    destination = Path(output_dir)
    source = Path(source_path)
    manifest_path = destination / "manifest.json"
    errors: list[str] = []

    if not manifest_path.is_file():
        return BundleVerificationResult(False, ("manifest.json is missing",))

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return BundleVerificationResult(False, (f"manifest.json is unreadable: {exc}",))

    if not isinstance(manifest, dict):
        return BundleVerificationResult(False, ("manifest.json must contain a JSON object",))

    if manifest.get("bundle_schema_version") != EXPECTED_BUNDLE_SCHEMA_VERSION:
        errors.append(
            f"bundle_schema_version must be {EXPECTED_BUNDLE_SCHEMA_VERSION}"
        )

    if not source.is_file():
        errors.append("source file is missing")
    else:
        if manifest.get("source_file") != source.name:
            errors.append("source_file does not match the supplied source filename")
        expected_source_hash = manifest.get("source_sha256")
        if not isinstance(expected_source_hash, str) or _sha256(source) != expected_source_hash:
            errors.append("source_sha256 does not match the supplied source file")

    outputs = manifest.get("outputs")
    output_hashes = manifest.get("output_sha256")
    if not isinstance(outputs, list) or not all(isinstance(item, str) for item in outputs):
        errors.append("outputs must be a list of filenames")
        outputs = []
    if not isinstance(output_hashes, dict):
        errors.append("output_sha256 must be an object")
        output_hashes = {}

    output_names = set(outputs)
    if len(outputs) != len(output_names):
        errors.append("outputs contains duplicate filenames")
    if output_names != EXPECTED_OUTPUTS:
        errors.append("outputs do not match the schema-1.1 controlled output set")
    if output_names != set(output_hashes):
        errors.append("outputs and output_sha256 keys do not match")

    for name in outputs:
        if Path(name).name != name or name == "manifest.json":
            errors.append(f"invalid output filename in manifest: {name}")
            continue
        path = destination / name
        if not path.is_file():
            errors.append(f"declared output is missing: {name}")
            continue
        expected_hash = output_hashes.get(name)
        if not isinstance(expected_hash, str) or _sha256(path) != expected_hash:
            errors.append(f"output hash mismatch: {name}")

    return BundleVerificationResult(valid=not errors, errors=tuple(errors))


def render_bundle_verification(result: BundleVerificationResult) -> str:
    return json.dumps(result.as_dict(), indent=2, ensure_ascii=False) + "\n"
