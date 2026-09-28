"""Load and validate ``autonomy/rules.json``.

The rules file is the single machine-readable policy of the Tier-0 autonomy
layer. Loading is strict: a missing file, invalid JSON or a structurally wrong
document raises :class:`RulesError` with a message that names the problem.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

RULES_RELATIVE_PATH = Path("autonomy") / "rules.json"
JOBS_RELATIVE_DIR = Path("autonomy") / "jobs"
REPO_ROOT_ENV = "CLINICOPS_REPO_ROOT"
SUPPORTED_SCHEMA_VERSIONS = {"1.0"}

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CRON_TZ_RE = re.compile(r"^CRON_TZ=[A-Za-z_]+(?:/[A-Za-z_+-]+)*\s+(.+)$")
CRON_FIELD_RE = re.compile(r"^[0-9*,/-]+$")

REQUIRED_TOP_LEVEL = (
    "schema_version",
    "generated_from",
    "tiers",
    "standing_caps",
    "jurisdictions",
    "post_gate",
    "do_not_contact",
    "kill_switch",
    "jobs",
    "watchdog",
    "claim_freshness",
)
REQUIRED_JOB_KEYS = (
    "slug",
    "name",
    "file",
    "tier",
    "cron",
    "cadence_minutes",
    "min_expected_duration_seconds",
    "outputs",
    "notifications",
)
REQUIRED_WATCHDOG_KEYS = (
    "missed_multiplier",
    "scheduler_stall_hours",
    "stale_needs_ali_days",
)


class RulesError(ValueError):
    """Raised when the rules file is missing, unreadable or malformed."""


@dataclass(frozen=True)
class JobEntry:
    slug: str
    name: str
    file: str
    tier: int
    cron: str
    cadence_minutes: int
    min_expected_duration_seconds: int
    outputs: tuple[str, ...]
    notifications: str

    @classmethod
    def from_dict(cls, row: dict[str, object]) -> JobEntry:
        return cls(
            slug=str(row["slug"]),
            name=str(row["name"]),
            file=str(row["file"]),
            tier=int(row["tier"]),
            cron=str(row["cron"]),
            cadence_minutes=int(row["cadence_minutes"]),
            min_expected_duration_seconds=int(row["min_expected_duration_seconds"]),
            outputs=tuple(str(item) for item in row["outputs"]),
            notifications=str(row["notifications"]),
        )


def find_repo_root(start: str | Path | None = None) -> Path:
    """Locate the repository root: the nearest ancestor holding ``autonomy/rules.json``.

    With an explicit ``start`` only its ancestors are searched. Otherwise the
    ``CLINICOPS_REPO_ROOT`` environment variable, the current working directory
    and the directory tree above this module (an editable install) are tried
    in that order.
    """
    candidates: list[Path] = []
    if start is not None:
        candidates.append(Path(start))
    else:
        env_root = os.environ.get(REPO_ROOT_ENV)
        if env_root:
            candidates.append(Path(env_root))
        candidates.append(Path.cwd())
        candidates.append(Path(__file__).resolve())

    for candidate in candidates:
        base = candidate.resolve()
        for directory in (base, *base.parents):
            if (directory / RULES_RELATIVE_PATH).is_file():
                return directory
    raise RulesError(
        "repository root not found: no ancestor of "
        f"{', '.join(str(c) for c in candidates)} contains {RULES_RELATIVE_PATH}"
    )


def rules_path(repo_root: str | Path | None = None) -> Path:
    root = Path(repo_root) if repo_root is not None else find_repo_root()
    return root / RULES_RELATIVE_PATH


def _validate_cron(slug: str, cron: str) -> None:
    match = CRON_TZ_RE.match(cron)
    fields = (match.group(1) if match else cron).split()
    if len(fields) != 5:
        raise RulesError(
            f"job {slug}: cron must have 5 fields after an optional CRON_TZ prefix, "
            f"got {cron!r}"
        )
    for field in fields:
        if not CRON_FIELD_RE.match(field):
            raise RulesError(f"job {slug}: invalid cron field {field!r} in {cron!r}")


def _validate_job(row: object, seen_slugs: set[str], seen_names: set[str]) -> None:
    if not isinstance(row, dict):
        raise RulesError("jobs entries must be objects")
    missing = [key for key in REQUIRED_JOB_KEYS if key not in row]
    if missing:
        raise RulesError(
            f"job {row.get('slug', '<no slug>')}: missing keys {', '.join(missing)}"
        )
    slug = str(row["slug"])
    if not SLUG_RE.match(slug):
        raise RulesError(f"job slug {slug!r} is not a lowercase kebab-case slug")
    if slug in seen_slugs:
        raise RulesError(f"duplicate job slug {slug!r}")
    seen_slugs.add(slug)
    name = str(row["name"])
    if name in seen_names:
        raise RulesError(f"duplicate job name {name!r}")
    seen_names.add(name)
    if not isinstance(row["tier"], int) or row["tier"] != 0:
        raise RulesError(f"job {slug}: tier must be the integer 0 for a Tier-0 job")
    for key in ("cadence_minutes", "min_expected_duration_seconds"):
        value = row[key]
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise RulesError(f"job {slug}: {key} must be a positive integer")
    if not isinstance(row["outputs"], list) or not row["outputs"]:
        raise RulesError(f"job {slug}: outputs must be a non-empty list")
    if not str(row["file"]).startswith("autonomy/jobs/"):
        raise RulesError(f"job {slug}: file must live under autonomy/jobs/")
    _validate_cron(slug, str(row["cron"]))


def validate_rules(rules: object) -> dict[str, object]:
    """Validate the parsed rules document and return it."""
    if not isinstance(rules, dict):
        raise RulesError("rules document must be a JSON object")
    missing = [key for key in REQUIRED_TOP_LEVEL if key not in rules]
    if missing:
        raise RulesError(f"rules missing top-level keys: {', '.join(missing)}")

    version = str(rules["schema_version"])
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise RulesError(
            f"unsupported schema_version {version!r}; "
            f"supported: {', '.join(sorted(SUPPORTED_SCHEMA_VERSIONS))}"
        )

    tiers = rules["tiers"]
    if not isinstance(tiers, dict) or set(tiers) != {"0", "1", "2", "3"}:
        raise RulesError("tiers must be an object with exactly the keys 0, 1, 2 and 3")
    for tier_key, tier in tiers.items():
        if not isinstance(tier, dict) or "label" not in tier:
            raise RulesError(f"tier {tier_key}: must be an object with a label")
        for list_key in ("allow", "deny", "park"):
            if list_key in tier and not isinstance(tier[list_key], list):
                raise RulesError(f"tier {tier_key}: {list_key} must be a list")

    seen_actions: dict[str, str] = {}
    for tier_key, tier in tiers.items():
        for list_key in ("allow", "deny", "park"):
            for action in tier.get(list_key, []):
                if action in seen_actions:
                    raise RulesError(
                        f"action {action!r} appears in tier {seen_actions[action]} "
                        f"and tier {tier_key}; an action belongs to exactly one tier"
                    )
                seen_actions[action] = tier_key

    jobs = rules["jobs"]
    if not isinstance(jobs, list) or not jobs:
        raise RulesError("jobs must be a non-empty list")
    seen_slugs: set[str] = set()
    seen_names: set[str] = set()
    for row in jobs:
        _validate_job(row, seen_slugs, seen_names)

    watchdog = rules["watchdog"]
    if not isinstance(watchdog, dict):
        raise RulesError("watchdog must be an object")
    for key in REQUIRED_WATCHDOG_KEYS:
        value = watchdog.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            raise RulesError(f"watchdog.{key} must be a positive number")

    freshness = rules["claim_freshness"]
    if not isinstance(freshness, dict):
        raise RulesError("claim_freshness must be an object")
    days = freshness.get("reverify_days_before_review_after")
    if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
        raise RulesError(
            "claim_freshness.reverify_days_before_review_after must be a positive integer"
        )

    post_gate = rules["post_gate"]
    if not isinstance(post_gate, list) or len(post_gate) != 5:
        raise RulesError("post_gate must list exactly 5 items")

    kill_switch = rules["kill_switch"]
    locations = kill_switch.get("locations") if isinstance(kill_switch, dict) else None
    if not isinstance(locations, list) or len(locations) != 3:
        raise RulesError("kill_switch.locations must list exactly 3 locations")

    return rules


def load_rules(path: str | Path | None = None) -> dict[str, object]:
    """Read, parse and validate the rules file.

    ``path`` may be the rules file itself or a repository root. When omitted
    the repository root is resolved with :func:`find_repo_root`.
    """
    if path is None:
        target = rules_path()
    else:
        candidate = Path(path)
        target = candidate / RULES_RELATIVE_PATH if candidate.is_dir() else candidate
    try:
        text = target.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RulesError(f"rules file not found: {target}") from exc
    except OSError as exc:
        raise RulesError(f"rules file unreadable: {target}: {exc}") from exc
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RulesError(f"rules file is not valid JSON: {target}: {exc}") from exc
    return validate_rules(parsed)


def job_registry(rules: dict[str, object] | None = None) -> dict[str, JobEntry]:
    """Return the job registry keyed by slug, in file order."""
    document = rules if rules is not None else load_rules()
    registry: dict[str, JobEntry] = {}
    for row in document["jobs"]:
        entry = JobEntry.from_dict(row)
        registry[entry.slug] = entry
    return registry


def watchdog_thresholds(rules: dict[str, object] | None = None) -> dict[str, float]:
    document = rules if rules is not None else load_rules()
    watchdog = document["watchdog"]
    return {
        "missed_multiplier": float(watchdog["missed_multiplier"]),
        "scheduler_stall_hours": float(watchdog["scheduler_stall_hours"]),
        "stale_needs_ali_days": float(watchdog["stale_needs_ali_days"]),
    }
