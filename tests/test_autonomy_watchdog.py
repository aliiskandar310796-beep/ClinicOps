from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from clinicops_os.autonomy import watchdog
from clinicops_os.autonomy.rules import job_registry, load_rules, watchdog_thresholds
from clinicops_os.autonomy.watchdog import evaluate, load_triggers, parse_timestamp

ROOT = Path(__file__).resolve().parents[1]
RULES = load_rules(ROOT / "autonomy" / "rules.json")
REGISTRY = job_registry(RULES)
THRESHOLDS = watchdog_thresholds(RULES)
NOW = datetime(2026, 9, 25, 7, 0, tzinfo=UTC)


def iso(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def healthy_trigger(slug: str, now: datetime = NOW) -> dict:
    job = REGISTRY[slug]
    fired = now - timedelta(minutes=min(job.cadence_minutes, 60))
    finished = fired + timedelta(seconds=job.min_expected_duration_seconds + 30)
    return {
        "id": f"trig_{slug}",
        "name": job.name,
        "enabled": True,
        "cron_expression": job.cron,
        "created_at": iso(now - timedelta(days=30)),
        "next_run_at": iso(now + timedelta(minutes=job.cadence_minutes)),
        "last_run": {"status": "SUCCEEDED", "fired_at": iso(fired), "finished_at": iso(finished)},
    }


def healthy_fleet(now: datetime = NOW) -> list[dict]:
    return [healthy_trigger(slug, now) for slug in REGISTRY]


def codes(findings) -> set[str]:
    return {finding.code for finding in findings}


def test_healthy_fleet_is_green() -> None:
    report = evaluate(healthy_fleet(), REGISTRY, NOW, THRESHOLDS)
    assert report.verdict == "GREEN"
    assert report.alerts == () and report.warnings == ()
    assert report.checked == 11
    assert report.render().startswith("FLEET: GREEN — 0 alerts, 0 warnings")


def test_failed_run_is_an_alert() -> None:
    fleet = healthy_fleet()
    fleet[0]["last_run"]["status"] = "FAILED"
    report = evaluate(fleet, REGISTRY, NOW, THRESHOLDS)
    assert report.verdict == "RED"
    assert codes(report.alerts) == {"failed"}
    assert report.alerts[0].job == fleet[0]["name"]


def test_missed_job_beyond_twice_cadence_is_an_alert() -> None:
    fleet = healthy_fleet()
    monitor = next(t for t in fleet if t["name"] == "ClinicOps T0 Monitor")
    # cadence 180 min -> missed after 360 min; 361 minutes ago is missed
    monitor["last_run"]["fired_at"] = iso(NOW - timedelta(minutes=361))
    monitor["last_run"]["finished_at"] = iso(NOW - timedelta(minutes=359))
    report = evaluate(fleet, REGISTRY, NOW, THRESHOLDS)
    assert codes(report.alerts) == {"missed"}

    monitor["last_run"]["fired_at"] = iso(NOW - timedelta(minutes=359))
    monitor["last_run"]["finished_at"] = iso(NOW - timedelta(minutes=357))
    assert evaluate(fleet, REGISTRY, NOW, THRESHOLDS).verdict == "GREEN"


def test_scheduler_stall_when_next_run_is_over_two_hours_past() -> None:
    fleet = healthy_fleet()
    fleet[3]["next_run_at"] = iso(NOW - timedelta(hours=2, minutes=1))
    report = evaluate(fleet, REGISTRY, NOW, THRESHOLDS)
    assert codes(report.alerts) == {"scheduler_stall"}
    fleet[3]["next_run_at"] = iso(NOW - timedelta(hours=1, minutes=59))
    assert evaluate(fleet, REGISTRY, NOW, THRESHOLDS).verdict == "GREEN"


def test_short_run_below_minimum_duration_is_a_warning() -> None:
    fleet = healthy_fleet()
    research = next(t for t in fleet if t["name"] == "ClinicOps T0 Research")
    fired = parse_timestamp(research["last_run"]["fired_at"])
    research["last_run"]["finished_at"] = iso(fired + timedelta(seconds=20))
    report = evaluate(fleet, REGISTRY, NOW, THRESHOLDS)
    assert report.verdict == "AMBER"
    assert codes(report.warnings) == {"short_run"}
    assert "20s" in report.warnings[0].message and "120s" in report.warnings[0].message


def test_short_failed_run_reports_only_the_failure() -> None:
    fleet = healthy_fleet()
    fired = parse_timestamp(fleet[0]["last_run"]["fired_at"])
    fleet[0]["last_run"].update({"status": "FAILED", "finished_at": iso(fired + timedelta(seconds=3))})
    report = evaluate(fleet, REGISTRY, NOW, THRESHOLDS)
    assert codes(report.alerts) == {"failed"} and report.warnings == ()


def test_disabled_expected_job_is_an_alert() -> None:
    fleet = healthy_fleet()
    fleet[5]["enabled"] = False
    fleet[5]["ended_reason"] = "user_paused"
    report = evaluate(fleet, REGISTRY, NOW, THRESHOLDS)
    assert codes(report.alerts) == {"disabled"}
    assert "user_paused" in report.alerts[0].message


def test_missing_expected_job_is_an_alert() -> None:
    fleet = [t for t in healthy_fleet() if t["name"] != "ClinicOps T0 Backup"]
    report = evaluate(fleet, REGISTRY, NOW, THRESHOLDS)
    assert codes(report.alerts) == {"missing"}
    assert report.alerts[0].job == "ClinicOps T0 Backup"


def test_never_fired_job_warns_when_young_and_alerts_when_old() -> None:
    fleet = healthy_fleet()
    fleet[2].pop("last_run")
    fleet[2]["created_at"] = iso(NOW - timedelta(hours=1))
    report = evaluate(fleet, REGISTRY, NOW, THRESHOLDS)
    assert codes(report.warnings) == {"no_run"} and report.verdict == "AMBER"

    fleet[2]["created_at"] = iso(NOW - timedelta(days=5))
    report = evaluate(fleet, REGISTRY, NOW, THRESHOLDS)
    assert codes(report.alerts) == {"missed"}


def test_non_registry_tasks_are_judged_for_health_only() -> None:
    fleet = healthy_fleet()
    fleet.append(
        {
            "name": "Daily Command Center",
            "enabled": True,
            "next_run_at": iso(NOW + timedelta(hours=1)),
            "last_run": {
                "status": "SUCCEEDED",
                "fired_at": iso(NOW - timedelta(days=9)),
                "finished_at": iso(NOW - timedelta(days=9) + timedelta(seconds=2)),
            },
        }
    )
    assert evaluate(fleet, REGISTRY, NOW, THRESHOLDS).verdict == "GREEN"
    fleet[-1]["last_run"]["status"] = "FAILED"
    fleet[-1]["next_run_at"] = iso(NOW - timedelta(hours=3))
    report = evaluate(fleet, REGISTRY, NOW, THRESHOLDS)
    assert codes(report.alerts) == {"failed", "scheduler_stall"}
    fleet[-1]["enabled"] = False
    assert evaluate(fleet, REGISTRY, NOW, THRESHOLDS).verdict == "GREEN"


def test_triggers_match_by_exact_name_or_slug_fallback() -> None:
    fleet = healthy_fleet()
    fleet[0]["name"] = fleet[0]["name"].upper()
    assert evaluate(fleet, REGISTRY, NOW, THRESHOLDS).verdict == "GREEN"
    fleet[0]["name"] = "renamed task (t0-monitor)"
    assert evaluate(fleet, REGISTRY, NOW, THRESHOLDS).verdict == "GREEN"


def test_timestamp_parsing_accepts_z_offsets_and_naive() -> None:
    assert parse_timestamp("2026-09-25T07:00:00Z") == NOW
    assert parse_timestamp("2026-09-25T09:00:00+02:00") == NOW
    assert parse_timestamp("2026-09-25T07:00:00") == NOW
    assert parse_timestamp("2026-09-25T07:00:00.250Z") == NOW + timedelta(milliseconds=250)
    assert parse_timestamp("") is None
    assert parse_timestamp("not a date") is None
    with pytest.raises(ValueError, match="cannot parse 'now'"):
        evaluate([], REGISTRY, "yesterday", THRESHOLDS)


def test_cli_reads_export_shapes_and_exits_two_on_alert(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    export = tmp_path / "triggers.json"
    export.write_text(json.dumps({"triggers": healthy_fleet()}), encoding="utf-8")
    rules_arg = ["--rules", str(ROOT / "autonomy" / "rules.json")]
    assert watchdog.main([str(export), "--now", iso(NOW), *rules_arg]) == 0
    assert "FLEET: GREEN" in capsys.readouterr().out

    fleet = healthy_fleet()
    fleet[0]["last_run"]["status"] = "FAILED"
    export.write_text(json.dumps(fleet), encoding="utf-8")
    assert watchdog.main([str(export), "--now", iso(NOW), "--json", *rules_arg]) == 2
    assert json.loads(capsys.readouterr().out)["verdict"] == "RED"

    export.write_text('{"nothing": 1}', encoding="utf-8")
    with pytest.raises(ValueError, match="triggers file must be a list"):
        load_triggers(export)
    assert watchdog.main([str(export), *rules_arg]) == 2
    assert watchdog.main([]) == 2
