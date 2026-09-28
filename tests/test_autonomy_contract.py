"""Contract tests for the Tier-0 autonomy layer control plane.

These pin the governance invariants of the layer: the kill switch is never
committed by accident, the gate workflow stays compute-only and unscheduled,
and the layer README documents every kill-switch location.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
AUTONOMY = ROOT / "autonomy"
WORKFLOW = ROOT / ".github" / "workflows" / "autonomy-gate.yml"
CODEOWNERS = ROOT / ".github" / "CODEOWNERS"


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def test_kill_switch_is_not_committed() -> None:
    halt = AUTONOMY / "HALT.md"
    assert not halt.exists(), (
        "autonomy/HALT.md exists on the committed tree. Creating it stops every Tier-0 "
        "job, so a HALT must be a deliberate, announced commit on main — never a stray "
        "file. If this HALT is intended, this red test is the expected signal; delete the "
        "file to resume the jobs."
    )


def test_gate_workflow_is_read_only_bounded_and_unscheduled() -> None:
    workflow = _workflow()
    assert workflow["name"] == "Autonomy Gate"
    assert workflow["permissions"] == {"contents": "read"}
    triggers = workflow.get("on") or workflow.get(True)
    assert "schedule" not in triggers, "the autonomy gate must never add a cron"
    assert "workflow_dispatch" in triggers
    for event in ("push", "pull_request"):
        paths = triggers[event]["paths"]
        assert "autonomy/**" in paths
        assert "src/clinicops_os/autonomy/**" in paths
        assert "data/termbase/**" in paths
    assert workflow["concurrency"]["group"] == "clinicops-autonomy-gate"
    job = workflow["jobs"]["autonomy-gate"]
    assert job["timeout-minutes"] == 8
    runs = " ".join(str(step.get("run", "")) for step in job["steps"])
    assert "clinicops-autonomy-policy selftest" in runs
    assert "clinicops-termbase validate data/termbase/termbase_public.csv" in runs
    assert "clinicops-termbase qa data/termbase/termbase_public.csv" in runs
    assert "clinicops-autonomy-jobs list" in runs
    assert "ruff check src tests" in runs
    assert "tests/test_autonomy_contract.py" in runs


def test_no_workflow_in_the_repository_schedules_the_autonomy_layer() -> None:
    for path in (ROOT / ".github" / "workflows").glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        if "autonomy" in text and path.name != "autonomy-gate.yml":
            raise AssertionError(f"{path.name} references the autonomy layer")


def test_readme_names_all_three_kill_switch_locations_and_the_never_list() -> None:
    readme = (AUTONOMY / "README.md").read_text(encoding="utf-8")
    assert "`autonomy/HALT.md`" in readme
    assert "Create this file to stop every job; delete it to resume" in readme
    assert "`CLINICOPS_HALT`" in readme
    assert "`00_CONTROL/HALT.md`" in readme and "`20_AUTONOMY/HALT.md`" in readme
    assert "## What this layer never does" in readme
    assert "never push to `main`" in readme
    assert "claude.ai scheduled tasks" in readme
    assert "CODEOWNERS" in readme and "advisory" in readme


def test_codeowners_covers_the_control_plane() -> None:
    text = CODEOWNERS.read_text(encoding="utf-8")
    assert "/autonomy/rules.json @aliiskandar310796-beep" in text
    assert "/autonomy/jobs/ @aliiskandar310796-beep" in text
    assert "/.github/workflows/ @aliiskandar310796-beep" in text


def test_common_header_keeps_the_hard_limits() -> None:
    header = (AUTONOMY / "jobs" / "_COMMON_HEADER.md").read_text(encoding="utf-8")
    for phrase in (
        "Never send, reply, forward, publish, post, comment, schedule or release anything external",
        "never push to the `main` branch",
        "Danish-domiciled organisations are never cold-emailed under any framing",
        "Never fetch a web page with bash, curl or python",
        "## Kill switch — check FIRST, before any other work",
    ):
        assert phrase in header, phrase
