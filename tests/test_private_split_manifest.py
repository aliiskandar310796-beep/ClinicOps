"""Tests for scripts/private_split_manifest.py (read-only private/public split preparation).

The heavy test builds a temporary copy that contains ONLY the public set and
runs the site checks, ruff and the test suite inside it. It proves the public
repository stands on its own once the private set is removed. Nothing here
changes the real repository, its history or any remote.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "private_split_manifest.py"
RUNBOOK = ROOT / "07_RESILIENCE" / "PRIVATE_SPLIT_RUNBOOK.md"

_spec = importlib.util.spec_from_file_location("private_split_manifest", SCRIPT)
psm = importlib.util.module_from_spec(_spec)
sys.modules["private_split_manifest"] = psm
assert _spec.loader is not None
_spec.loader.exec_module(psm)


# Repo-level tooling for the pre-split repository. Inside the public-only copy
# (and in the real public repo after the split) the private files are gone, so
# these tests skip there; delete this file and the script once the split is done.
pytestmark = pytest.mark.skipif(
    bool(os.environ.get(psm.VERIFY_ENV_GUARD)),
    reason="inside a public-only verify run (the private set is intentionally absent)",
)


@pytest.fixture(scope="module")
def manifest() -> dict:
    return psm.build_manifest(psm.tracked_files(ROOT))


def test_classify_known_paths():
    cases = {
        "sales/target_accounts_2026-09-23.csv": psm.PRIVATE,
        "revenue/pipeline/pipeline.csv": psm.PRIVATE,
        "01_STRATEGY/CLINICOPS_2030_OPERATING_SYSTEM.md": psm.PRIVATE,
        "07_RESILIENCE/RESILIENCE_OPERATING_SYSTEM.md": psm.PRIVATE,
        "AGENT_STATE.md": psm.PRIVATE,
        "docs/index.html": psm.PUBLIC,
        "research/claims.jsonl": psm.PUBLIC,
        "research/market/anything.md": psm.PRIVATE,  # more specific than research/
        "tests/test_os.py": psm.PUBLIC,
        "scripts/render_sitemap.py": psm.PUBLIC,
        "AGENTS.md": psm.PUBLIC,
        "03_OPERATIONS/expert_network/roster.example.json": psm.PUBLIC,  # exception inside a private dir
        "03_OPERATIONS/REVENUE_OS.md": psm.PRIVATE,
    }
    for path, klass in cases.items():
        rule = psm.classify(path)
        assert rule is not None and rule.klass == klass, path


def test_every_tracked_path_is_classified(manifest):
    assert manifest["unclassified"] == [], (
        "New tracked paths match no rule in scripts/private_split_manifest.py: "
        f"{manifest['unclassified']}. Add a rule (private or public) before merging."
    )


def test_no_sensitive_looking_data_file_sits_in_the_public_set(manifest):
    assert psm.sensitive_in_public(manifest) == []


def test_sensitive_tripwire_catches_a_misplaced_prospect_file():
    fake = {"rows": [{"path": "data/prospect_list.csv", "class": psm.PUBLIC, "confidence": "certain", "rule": "data/", "reason": ""}], "unclassified": []}
    assert psm.sensitive_in_public(fake) == ["data/prospect_list.csv"]
    ok = {"rows": [{"path": "src/clinicops_os/prospect.py", "class": psm.PUBLIC, "confidence": "certain", "rule": "src/", "reason": ""}], "unclassified": []}
    assert psm.sensitive_in_public(ok) == []


def test_classes_partition_the_tracked_files(manifest):
    private, public = set(psm.paths_of(manifest, psm.PRIVATE)), set(psm.paths_of(manifest, psm.PUBLIC))
    assert private and public and not (private & public)
    assert len(private) + len(public) == len(manifest["rows"])


def test_must_stay_public_areas_are_never_private(manifest):
    private = psm.paths_of(manifest, psm.PRIVATE)
    for forbidden in ("docs/", "src/", "tests/", "scripts/", ".github/", "research/claims.jsonl", "pyproject.toml", "AGENTS.md", "CLAIM_RULES.md"):
        assert not [p for p in private if p.startswith(forbidden)], forbidden


def test_named_prospect_and_strategy_material_is_private(manifest):
    private = set(psm.paths_of(manifest, psm.PRIVATE))
    for path in ("sales/target_accounts_2026-09-23.csv", "sales/outreach-operating-pack.md", "offers/cash-entry-service-ladder.md", "revenue/pipeline/pipeline.csv"):
        assert path in private, path


def test_dependency_scan_finds_the_known_hard_dependencies(manifest):
    deps = psm.find_dependencies(ROOT, manifest)
    by_file = {d["file"] for d in deps}
    assert ".github/workflows/ci.yml" in by_file  # clinicops-sales-swarm sales/global-sales-swarm.json
    assert "tests/test_delegation_proof_contract.py" in by_file  # pathlib join: ROOT / "sales" / ...
    assert "scripts/pipeline_report.py" in by_file


def test_tests_that_move_with_the_private_set_really_depend_on_it(manifest):
    deps = psm.find_dependencies(ROOT, manifest)
    reading = {d["file"] for d in deps if d["area"] == "test"}
    for test in psm.MOVES_WITH_PRIVATE_TESTS:
        assert (ROOT / test).is_file(), f"stale entry: {test}"
        assert test in reading, f"{test} no longer references a private path; remove it from MOVES_WITH_PRIVATE_TESTS"


def test_no_other_public_test_depends_on_private_paths(manifest):
    """Ratchet: a NEW test that reads a private path must be listed (or fixture-backed)."""
    deps = psm.find_dependencies(ROOT, manifest)
    tests = {d["file"] for d in deps if d["area"] == "test"}
    # Docstring-only mentions of 01_STRATEGY are allowed; the heavy verify test below
    # is the real proof. This keeps the list reviewable.
    allowed_mentions = {"tests/test_positioning_contract.py", "tests/test_strategic_invariants.py", "tests/test_expert_network.py"}
    unexpected = tests - set(psm.MOVES_WITH_PRIVATE_TESTS) - allowed_mentions
    assert unexpected == set(), f"public tests referencing private paths: {sorted(unexpected)}"


def test_history_paths_lists_deleted_and_renamed_private_files(tmp_path):
    def git(*args):
        subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@example.test", *args], check=True, capture_output=True)

    git("init", "-q")
    (tmp_path / "sales").mkdir()
    (tmp_path / "sales" / "old.csv").write_text("a\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.html").write_text("x\n")
    git("add", ".")
    git("commit", "-qm", "one")
    git("rm", "-q", "sales/old.csv")
    git("commit", "-qm", "two")
    hist = psm.build_manifest(psm.history_paths(tmp_path))
    assert "sales/old.csv" in psm.paths_of(hist, psm.PRIVATE)  # gone from HEAD, still in history
    assert "docs/index.html" in psm.paths_of(hist, psm.PUBLIC)
    assert "sales/old.csv" not in psm.tracked_files(tmp_path)


def test_copy_of_public_set_contains_no_private_path(manifest, tmp_path):
    count = psm.copy_public_set(ROOT, manifest, tmp_path)
    assert count > 100
    for private in psm.paths_of(manifest, psm.PRIVATE):
        assert not (tmp_path / private).exists(), private


def test_script_is_read_only_it_never_calls_a_mutating_git_command():
    text = SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("filter-repo", "push", "reset", "checkout", "rm ", "gh api", "visibility"):
        for line in text.splitlines():
            code = line.split("#", 1)[0]
            if '["git"' in code or "subprocess" in code:
                assert forbidden not in code, f"{forbidden!r} in: {line.strip()}"


def test_runbook_exists_with_the_required_sections():
    text = RUNBOOK.read_text(encoding="utf-8")
    for needle in (
        "Option A",
        "Option B",
        "git filter-repo",
        "--invert-paths",
        "GitHub Support",
        "forks",
        "CODEOWNERS",
        "Actions minutes",
        "Pages",
        "Nothing in this runbook has been executed",
    ):
        assert needle in text, needle


def test_public_set_builds_and_passes_tests_without_the_private_set(manifest):
    """The public-only copy builds the site and passes ruff and pytest."""
    results = psm.verify_public_build(ROOT, manifest)
    failed = [r for r in results if not r["ok"]]
    assert not failed, "\n".join(f"{r['step']}: {r['detail']}" for r in failed)
    assert results[-1]["step"] == "pytest"
