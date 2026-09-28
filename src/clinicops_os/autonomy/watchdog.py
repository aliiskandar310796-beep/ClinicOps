"""Offline fleet watchdog: evaluate a scheduler export against the job registry.

Input records are shaped like the claude.ai ``list_triggers`` output::

    {"name": "ClinicOps T0 Monitor", "enabled": true,
     "cron_expression": "...", "next_run_at": "2026-09-25T09:03:00Z",
     "last_run": {"status": "SUCCEEDED", "fired_at": "...", "finished_at": "..."}}

Rules (thresholds from ``autonomy/rules.json``):

* ``last_run.status`` FAILED — ALERT ``failed``.
* an expected job missing from the export — ALERT ``missing``.
* an expected job that is disabled — ALERT ``disabled``.
* no run within ``missed_multiplier`` × cadence — ALERT ``missed``.
* ``next_run_at`` more than ``scheduler_stall_hours`` in the past — ALERT ``scheduler_stall``.
* a run shorter than the job's minimum expected duration — WARN ``short_run``.
* an expected job with no recorded run yet — WARN ``no_run``.

This module is pure evaluation: it never changes, disables or fires a task.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .rules import JobEntry, RulesError, job_registry, load_rules, watchdog_thresholds

DEFAULT_THRESHOLDS: dict[str, float] = {
    "missed_multiplier": 2.0,
    "scheduler_stall_hours": 2.0,
    "stale_needs_ali_days": 7.0,
}


@dataclass(frozen=True)
class Finding:
    level: str
    job: str
    code: str
    message: str

    def render(self) -> str:
        return f"{self.level} {self.job}: {self.message}"


@dataclass(frozen=True)
class WatchdogReport:
    verdict: str
    alerts: tuple[Finding, ...]
    warnings: tuple[Finding, ...]
    now: str
    checked: int

    @property
    def red(self) -> bool:
        return bool(self.alerts)

    def render(self) -> str:
        lines = [f"FLEET: {self.verdict} — {len(self.alerts)} alerts, {len(self.warnings)} warnings"]
        lines.append(f"now: {self.now} · tasks checked: {self.checked}")
        for finding in self.alerts:
            lines.append(finding.render())
        for finding in self.warnings:
            lines.append(finding.render())
        return "\n".join(lines) + "\n"

    def to_dict(self) -> dict[str, object]:
        return {
            "verdict": self.verdict,
            "now": self.now,
            "checked": self.checked,
            "alerts": [finding.__dict__ for finding in self.alerts],
            "warnings": [finding.__dict__ for finding in self.warnings],
        }


def parse_timestamp(value: object) -> datetime | None:
    """Parse an ISO 8601 timestamp; naive values are taken as UTC."""
    if value is None:
        return None
    if isinstance(value, datetime):
        stamp = value
    else:
        text = str(value).strip()
        if not text:
            return None
        if text.endswith(("Z", "z")):
            text = text[:-1] + "+00:00"
        try:
            stamp = datetime.fromisoformat(text)
        except ValueError:
            return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=UTC)
    return stamp.astimezone(UTC)


def _match_trigger(job: JobEntry, triggers: list[dict[str, Any]]) -> dict[str, Any] | None:
    wanted = job.name.casefold()
    for trigger in triggers:
        if str(trigger.get("name", "")).strip().casefold() == wanted:
            return trigger
    for trigger in triggers:
        if job.slug in str(trigger.get("name", "")).casefold():
            return trigger
    return None


def _duration_seconds(last_run: dict[str, Any]) -> float | None:
    fired = parse_timestamp(last_run.get("fired_at"))
    finished = parse_timestamp(last_run.get("finished_at"))
    if fired is None or finished is None:
        return None
    return (finished - fired).total_seconds()


def evaluate(
    triggers: list[dict[str, Any]],
    registry: dict[str, JobEntry],
    now: datetime | str,
    thresholds: dict[str, float] | None = None,
) -> WatchdogReport:
    limits = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    moment = parse_timestamp(now)
    if moment is None:
        raise ValueError(f"cannot parse 'now' timestamp: {now!r}")
    stall_after = timedelta(hours=limits["scheduler_stall_hours"])

    alerts: list[Finding] = []
    warnings: list[Finding] = []
    matched_ids: set[int] = set()

    for job in registry.values():
        trigger = _match_trigger(job, triggers)
        if trigger is None:
            alerts.append(
                Finding("ALERT", job.name, "missing", "expected job is not in the scheduler export")
            )
            continue
        matched_ids.add(id(trigger))
        _evaluate_expected(job, trigger, moment, limits, stall_after, alerts, warnings)

    for trigger in triggers:
        if id(trigger) in matched_ids:
            continue
        _evaluate_health_only(trigger, moment, stall_after, alerts)

    if alerts:
        verdict = "RED"
    elif warnings:
        verdict = "AMBER"
    else:
        verdict = "GREEN"
    return WatchdogReport(
        verdict=verdict,
        alerts=tuple(alerts),
        warnings=tuple(warnings),
        now=moment.strftime("%Y-%m-%dT%H:%M:%SZ"),
        checked=len(triggers),
    )


def _evaluate_expected(
    job: JobEntry,
    trigger: dict[str, Any],
    now: datetime,
    limits: dict[str, float],
    stall_after: timedelta,
    alerts: list[Finding],
    warnings: list[Finding],
) -> None:
    name = job.name
    enabled = bool(trigger.get("enabled", False))
    if not enabled:
        reason = trigger.get("ended_reason") or trigger.get("suspension_reason") or "paused"
        alerts.append(Finding("ALERT", name, "disabled", f"expected job is disabled ({reason})"))
        return

    last_run = trigger.get("last_run") or {}
    status = str(last_run.get("status", "")).upper()
    fired_at = parse_timestamp(last_run.get("fired_at"))
    missed_after = timedelta(minutes=job.cadence_minutes * limits["missed_multiplier"])

    if status == "FAILED":
        alerts.append(
            Finding("ALERT", name, "failed", f"last run FAILED (fired {last_run.get('fired_at')})")
        )

    if fired_at is None:
        created = parse_timestamp(trigger.get("created_at"))
        if created is not None and now - created > missed_after:
            alerts.append(
                Finding(
                    "ALERT",
                    name,
                    "missed",
                    f"no recorded run since creation {trigger.get('created_at')} "
                    f"(> {missed_after} = {limits['missed_multiplier']:g}x cadence)",
                )
            )
        else:
            warnings.append(Finding("WARN", name, "no_run", "no recorded run yet"))
    elif now - fired_at > missed_after:
        alerts.append(
            Finding(
                "ALERT",
                name,
                "missed",
                f"last fired {fired_at.strftime('%Y-%m-%dT%H:%M:%SZ')}, more than "
                f"{limits['missed_multiplier']:g}x cadence ({job.cadence_minutes} min) ago",
            )
        )

    duration = _duration_seconds(last_run)
    if duration is not None and status != "FAILED" and duration < job.min_expected_duration_seconds:
        warnings.append(
            Finding(
                "WARN",
                name,
                "short_run",
                f"suspiciously short run — probable fail-fast: {duration:.0f}s "
                f"(minimum {job.min_expected_duration_seconds}s)",
            )
        )

    next_run = parse_timestamp(trigger.get("next_run_at"))
    if next_run is not None and now - next_run > stall_after:
        alerts.append(
            Finding(
                "ALERT",
                name,
                "scheduler_stall",
                f"next_run_at {next_run.strftime('%Y-%m-%dT%H:%M:%SZ')} is more than "
                f"{stall_after} in the past",
            )
        )


def _evaluate_health_only(
    trigger: dict[str, Any],
    now: datetime,
    stall_after: timedelta,
    alerts: list[Finding],
) -> None:
    if not bool(trigger.get("enabled", False)):
        return
    name = str(trigger.get("name", "<unnamed task>"))
    last_run = trigger.get("last_run") or {}
    if str(last_run.get("status", "")).upper() == "FAILED":
        alerts.append(
            Finding("ALERT", name, "failed", f"last run FAILED (fired {last_run.get('fired_at')})")
        )
    next_run = parse_timestamp(trigger.get("next_run_at"))
    if next_run is not None and now - next_run > stall_after:
        alerts.append(
            Finding(
                "ALERT",
                name,
                "scheduler_stall",
                f"next_run_at {next_run.strftime('%Y-%m-%dT%H:%M:%SZ')} is more than "
                f"{stall_after} in the past",
            )
        )


def load_triggers(path: str | Path) -> list[dict[str, Any]]:
    """Read a ``list_triggers`` export: a list, or an object holding one."""
    try:
        parsed = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"triggers file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"triggers file is not valid JSON: {path}: {exc}") from exc
    if isinstance(parsed, list):
        records = parsed
    elif isinstance(parsed, dict):
        records = None
        for key in ("triggers", "items", "data", "results"):
            if isinstance(parsed.get(key), list):
                records = parsed[key]
                break
        if records is None:
            raise ValueError("triggers file must be a list or an object with a 'triggers' list")
    else:
        raise TypeError("triggers file must be a list or an object with a 'triggers' list")
    if not all(isinstance(item, dict) for item in records):
        raise TypeError("every trigger record must be an object")
    return records


USAGE = (
    "usage: clinicops-autonomy-watchdog TRIGGERS.json [--now ISO8601] [--rules PATH] [--json]\n"
    "exit 2 when the fleet verdict is RED (any alert)"
)


def _take_option(args: list[str], flag: str) -> tuple[list[str], str | None]:
    if flag not in args:
        return args, None
    index = args.index(flag)
    if index + 1 >= len(args):
        raise SystemExit(f"{flag} requires a value")
    return args[:index] + args[index + 2 :], args[index + 1]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    args, now_arg = _take_option(args, "--now")
    args, rules_arg = _take_option(args, "--rules")
    as_json = "--json" in args
    args = [item for item in args if item != "--json"]
    if len(args) != 1:
        print(USAGE)
        return 2
    try:
        rules = load_rules(rules_arg)
        triggers = load_triggers(args[0])
        report = evaluate(
            triggers,
            job_registry(rules),
            now_arg or datetime.now(UTC),
            watchdog_thresholds(rules),
        )
    except (RulesError, TypeError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    if as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        sys.stdout.write(report.render())
    return 2 if report.red else 0


def watchdog_cli() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
