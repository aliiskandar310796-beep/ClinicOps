from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from clinicops_os.autonomy import jobs as jobs_module
from clinicops_os.autonomy.rules import (
    RulesError,
    find_repo_root,
    job_registry,
    load_rules,
    validate_rules,
    watchdog_thresholds,
)

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "autonomy" / "rules.json"


def rules() -> dict:
    return load_rules(RULES)


def test_rules_file_loads_and_declares_provenance() -> None:
    document = rules()
    assert document["schema_version"] == "1.0"
    assert document["generated_from"] == "autonomy/jobs/*.md front matter"


def test_repo_root_resolves_from_module_and_from_explicit_start(tmp_path: Path) -> None:
    assert find_repo_root() == ROOT
    assert find_repo_root(ROOT / "tests") == ROOT
    with pytest.raises(RulesError, match="repository root not found"):
        find_repo_root(tmp_path)


def test_load_rules_accepts_repo_root_or_file_path() -> None:
    assert load_rules(ROOT)["schema_version"] == load_rules(RULES)["schema_version"]


def test_missing_and_malformed_rules_raise_explicit_errors(tmp_path: Path) -> None:
    with pytest.raises(RulesError, match="rules file not found"):
        load_rules(tmp_path / "nope.json")
    broken = tmp_path / "rules.json"
    broken.write_text("{not json", encoding="utf-8")
    with pytest.raises(RulesError, match="not valid JSON"):
        load_rules(broken)


def test_registry_matches_every_job_front_matter_exactly() -> None:
    registry = job_registry(rules())
    specs = {spec.slug: spec for spec in jobs_module.list_jobs(ROOT / "autonomy" / "jobs")}

    assert set(registry) == set(specs), (
        "every job file needs a registry entry and every registry entry a job file"
    )
    for slug, entry in registry.items():
        spec = specs[slug]
        assert entry.name == spec.name
        assert entry.cron == spec.cron, f"{slug}: cron drift between rules.json and front matter"
        assert entry.cadence_minutes == spec.cadence_minutes
        assert entry.min_expected_duration_seconds == spec.min_expected_duration_seconds
        assert entry.outputs == spec.outputs
        assert entry.notifications == spec.notifications
        assert entry.tier == spec.tier == 0
        assert entry.file == f"autonomy/jobs/{spec.path.name}"


def test_registry_holds_the_eleven_tier0_jobs() -> None:
    registry = job_registry(rules())
    assert len(registry) == 11
    assert "t0-watchdog" in registry
    assert registry["t0-watchdog"].cadence_minutes == 720


def test_watchdog_thresholds_and_freshness_match_the_documented_policy() -> None:
    document = rules()
    thresholds = watchdog_thresholds(document)
    assert thresholds["missed_multiplier"] == 2
    assert thresholds["scheduler_stall_hours"] == 2
    assert thresholds["stale_needs_ali_days"] == 7
    assert document["claim_freshness"]["reverify_days_before_review_after"] == 21


def test_standing_caps_and_jurisdictions_are_encoded() -> None:
    document = rules()
    cold = document["standing_caps"]["cold_email"]
    assert cold["daily_cap"] == 50
    assert cold["cap_is_ceiling_not_target"] is True
    assert cold["sub_batch_size"] == 5
    assert cold["opt_out_line_required"] is True
    linkedin = document["standing_caps"]["linkedin"]
    assert linkedin["posts_per_week_max"] == 3
    assert linkedin["post_time_local"] == "08:30"
    assert document["jurisdictions"]["DK"]["cold_email"] == "deny"
    assert "UWG" in document["jurisdictions"]["DE"]["legal_basis"]
    assert "TKG" in document["jurisdictions"]["AT"]["legal_basis"]
    assert len(document["post_gate"]) == 5
    assert set(document["do_not_contact"]["public_permanent_exclusions"]) == {
        "Ergomed Group",
        "PrimeVigilance",
    }


def test_every_action_belongs_to_exactly_one_tier() -> None:
    document = copy.deepcopy(rules())
    document["tiers"]["0"]["allow"].append("payment")
    with pytest.raises(RulesError, match="exactly one tier"):
        validate_rules(document)


def test_duplicate_slug_and_bad_cron_are_rejected() -> None:
    document = copy.deepcopy(rules())
    document["jobs"].append(dict(document["jobs"][0]))
    with pytest.raises(RulesError, match="duplicate job slug"):
        validate_rules(document)

    document = copy.deepcopy(rules())
    document["jobs"][0]["cron"] = "CRON_TZ=Europe/Madrid 3 6 * *"
    with pytest.raises(RulesError, match="5 fields"):
        validate_rules(document)


def test_missing_top_level_key_is_named() -> None:
    document = copy.deepcopy(rules())
    del document["watchdog"]
    with pytest.raises(RulesError, match="watchdog"):
        validate_rules(document)


def test_rules_file_is_canonical_json() -> None:
    text = RULES.read_text(encoding="utf-8")
    assert text == json.dumps(json.loads(text), indent=2, ensure_ascii=False) + "\n"
