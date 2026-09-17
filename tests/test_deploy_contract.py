"""Contract tests for the production deployment pipeline.

These pin the invariant that production only ever contains CI-validated
source (incident 2026-09-17: a red main deployed to production because the
Pages workflow triggered on push, independent of CI). If someone edits
.github/workflows/pages.yml in a way that reopens that hole, these tests
fail before the change can merge.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / ".github" / "workflows" / "pages.yml"
CI = ROOT / ".github" / "workflows" / "ci.yml"


def _pages() -> dict:
    return yaml.safe_load(PAGES.read_text(encoding="utf-8"))


def test_pages_deploy_triggers_from_ci_completion_not_push() -> None:
    workflow = _pages()
    # PyYAML parses the bare key `on:` as boolean True.
    triggers = workflow.get("on") or workflow.get(True)
    assert "push" not in triggers, "push-triggered deploy bypasses CI validation"
    workflow_run = triggers.get("workflow_run")
    assert workflow_run is not None, "deploy must be driven by CI completion"
    assert "CI" in workflow_run.get("workflows", [])
    assert "main" in workflow_run.get("branches", [])


def test_pages_deploy_job_requires_ci_success() -> None:
    deploy = _pages()["jobs"]["deploy"]
    condition = deploy.get("if", "")
    assert "workflow_run.conclusion == 'success'" in condition


def test_pages_deploy_checks_out_the_exact_ci_validated_sha() -> None:
    deploy = _pages()["jobs"]["deploy"]
    checkout_refs = [
        str(step.get("with", {}).get("ref", ""))
        for step in deploy["steps"]
        if str(step.get("uses", "")).startswith("actions/checkout")
    ]
    assert any("workflow_run.head_sha" in ref for ref in checkout_refs), (
        "deploy must check out the exact SHA CI validated, never the moving tip"
    )


def test_manual_dispatch_is_guarded_by_ci_conclusion_check() -> None:
    deploy = _pages()["jobs"]["deploy"]
    guard_steps = [
        step
        for step in deploy["steps"]
        if "workflow_dispatch" in str(step.get("if", ""))
        and "conclusion" in str(step.get("run", ""))
    ]
    assert guard_steps, (
        "manual dispatch must verify a successful CI run for the exact SHA "
        "before deploying"
    )
    assert any("exit 1" in str(step.get("run", "")) for step in guard_steps)


def test_deploy_ends_with_post_deploy_live_smoke() -> None:
    deploy = _pages()["jobs"]["deploy"]
    assert "check_live_site" in str(deploy["steps"][-1].get("run", ""))


def test_ci_asserts_synthetic_example_produces_no_commercial_proof() -> None:
    ci_text = CI.read_text(encoding="utf-8")
    assert '"end_to_end_commercial_proof": false' in ci_text
    assert '"real_highest_commercial_stage": "E0"' in ci_text
    assert '"simulated_end_to_end_traversal": true' in ci_text
