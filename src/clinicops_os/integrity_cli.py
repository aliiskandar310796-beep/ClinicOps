from __future__ import annotations

import json
import sys

from .integrity_gate import build_bundle, verify_bundle_integrity
from .integrity_review import (
    prepare_review_record,
    verify_review_gate,
    write_review_gate,
)


def integrity_gate() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: clinicops-integrity-gate <case.json> <output-dir>")
    try:
        report = build_bundle(sys.argv[1], sys.argv[2])
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(report, indent=2, ensure_ascii=False))


def integrity_review_prepare() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: clinicops-integrity-review-prepare <output-dir>")
    try:
        record = prepare_review_record(sys.argv[1])
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(record, indent=2, ensure_ascii=False))


def integrity_review_gate() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: clinicops-integrity-review-gate <review-record.json> <output-dir>"
        )
    try:
        result = write_review_gate(sys.argv[1], sys.argv[2])
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(result.as_dict(), indent=2, ensure_ascii=False))
    if not result.approved:
        raise SystemExit(2)


def integrity_verify() -> None:
    args = sys.argv[1:]
    require_review = False
    if "--require-review" in args:
        args.remove("--require-review")
        require_review = True
    if len(args) != 2:
        raise SystemExit(
            "usage: clinicops-integrity-verify <output-dir> <case.json> [--require-review]"
        )
    verified, reasons, manifest = verify_bundle_integrity(args[0], args[1])
    review_ok, review_reasons = verify_review_gate(args[0])
    if require_review and not review_ok:
        reasons = tuple(reasons) + tuple(
            f"review: {reason}" for reason in review_reasons
        )
        verified = False
    result = {
        "status": "VERIFIED" if verified else "NOT VERIFIED",
        "release_ready": verified and review_ok,
        "case_id": manifest.get("case_id") if manifest else None,
        "automated_gate_status": manifest.get("gate_status") if manifest else None,
        "review_status": "REVIEW APPROVED" if review_ok else "REVIEW REQUIRED",
        "reasons": list(reasons),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not verified:
        raise SystemExit(2)
