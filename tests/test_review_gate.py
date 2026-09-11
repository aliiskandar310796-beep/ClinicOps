import json
from datetime import date
from pathlib import Path

from clinicops_os.bundle import build_pilot_bundle
from clinicops_os.review_gate import (
    REQUIRED_REVIEW_ATTESTATIONS,
    evaluate_review_gate,
    prepare_review_record,
)

ROOT = Path(__file__).resolve().parents[1]


def _activation() -> dict[str, object]:
    return json.loads(
        (ROOT / "examples" / "standard_pilot_preflight.example.json").read_text(
            encoding="utf-8"
        )
    )


def _approved_review(record: dict[str, object]) -> dict[str, object]:
    approved = dict(record)
    approved["review_completed_on"] = "2026-09-11"
    for key in REQUIRED_REVIEW_ATTESTATIONS:
        approved[key] = True
    return approved


def _bundle(tmp_path: Path) -> Path:
    output = tmp_path / "bundle"
    build_pilot_bundle(
        ROOT / "examples" / "portfolio.csv",
        output,
        as_of=date(2026, 9, 9),
    )
    return output


def test_prepare_review_record_is_bound_and_fail_closed(tmp_path):
    activation = _activation()
    output = _bundle(tmp_path)

    record = prepare_review_record(activation, output)

    assert record["human_reviewer"] == activation["human_reviewer"]
    assert record["reviewed_as_of"] == "2026-09-09"
    assert len(str(record["bundle_manifest_sha256"])) == 64
    assert len(str(record["source_sha256"])) == 64
    assert record["review_completed_on"] == ""
    assert all(record[key] is False for key in REQUIRED_REVIEW_ATTESTATIONS)

    result = evaluate_review_gate(activation, record, output)
    assert result.approved is False
    assert result.reasons


def test_review_gate_approves_explicit_review_for_exact_bundle(tmp_path):
    activation = _activation()
    output = _bundle(tmp_path)
    review = _approved_review(prepare_review_record(activation, output))

    result = evaluate_review_gate(activation, review, output)

    assert result.approved is True
    assert result.reasons == ()


def test_review_gate_rejects_bundle_regeneration_after_review(tmp_path):
    activation = _activation()
    output = _bundle(tmp_path)
    review = _approved_review(prepare_review_record(activation, output))

    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["interpretation"] = "changed after recorded review"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    result = evaluate_review_gate(activation, review, output)

    assert result.approved is False
    assert "bundle_manifest_sha256 does not match the final manifest" in result.reasons


def test_review_gate_rejects_reviewer_mismatch(tmp_path):
    activation = _activation()
    output = _bundle(tmp_path)
    review = _approved_review(prepare_review_record(activation, output))
    review["human_reviewer"] = "Different Reviewer"

    result = evaluate_review_gate(activation, review, output)

    assert result.approved is False
    assert "human_reviewer must match the activated pilot reviewer" in result.reasons


def test_review_gate_rejects_founder_or_unplanned_exception(tmp_path):
    activation = _activation()
    output = _bundle(tmp_path)
    review = _approved_review(prepare_review_record(activation, output))
    review["founder_transaction_decision_required"] = True
    review["unplanned_exception"] = True

    result = evaluate_review_gate(activation, review, output)

    assert result.approved is False
    assert any("founder_transaction_decision_required" in reason for reason in result.reasons)
    assert any("unplanned_exception" in reason for reason in result.reasons)


def test_review_prepare_rejects_nonactivated_pilot(tmp_path):
    activation = _activation()
    activation["activation_condition_satisfied"] = False
    output = _bundle(tmp_path)

    try:
        prepare_review_record(activation, output)
    except ValueError as exc:
        assert "pilot activation is not valid" in str(exc)
    else:
        raise AssertionError("non-activated pilot should not prepare a review record")
