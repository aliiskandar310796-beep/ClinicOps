"""Read-only manifest for the private/public repository split.

This script NEVER changes the repository, its history, its visibility or any
remote. It only:

  * classifies every tracked path as ``private`` (sales, prospect, strategy,
    operations material under AGENTS.md non-negotiable "keep client/prospect
    data out of the public repo" and copilot-instructions rules 8 and 15) or
    ``public`` (site, research, tests, scripts, source that must stay public);
  * lists the references that public files make to private paths (the
    dependencies that must be handled before the split);
  * with ``--verify-public-build``, copies only the public set into a temporary
    directory and runs the build and test steps there, proving the public repo
    still builds and passes tests once the private set is gone.

Usage:
    python scripts/private_split_manifest.py                  # summary
    python scripts/private_split_manifest.py --list private   # one path per line
    python scripts/private_split_manifest.py --deps           # public -> private references
    python scripts/private_split_manifest.py --json
    python scripts/private_split_manifest.py --verify-public-build

``--list private`` output is suitable for ``git filter-repo --paths-from-file``
(see 07_RESILIENCE/PRIVATE_SPLIT_RUNBOOK.md). Classification is a first-match
rule table below; the founder reviews every ``judgement`` row before anything
is executed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PRIVATE = "private"
PUBLIC = "public"
CERTAIN = "certain"
JUDGEMENT = "judgement"


@dataclass(frozen=True)
class Rule:
    match: str  # "dir/" prefix or exact path
    klass: str
    confidence: str
    reason: str


# First match wins. A rule ending in "/" is a directory prefix.
RULES: tuple[Rule, ...] = (
    # --- private: sales / prospects (AGENTS.md rule 8, rule 15) ---------------
    Rule("sales/", PRIVATE, CERTAIN, "named target accounts, outreach drafts, discovery ledger, pilot sales packs"),
    Rule("revenue/", PRIVATE, CERTAIN, "pipeline, customer-discovery state, revenue handoff"),
    Rule("05_CLIENT_DELIVERY/", PRIVATE, CERTAIN, "client delivery runbooks, SOW, invoice and terms checklists"),
    Rule("research/economic-validation/", PRIVATE, CERTAIN, "buyer budget signals"),
    Rule("research/market/", PRIVATE, JUDGEMENT, "market positioning and expert-network sourcing evidence"),
    Rule("research/drafts/", PRIVATE, JUDGEMENT, "unpublished research and note-pack drafts (public once published)"),
    Rule("offers/", PRIVATE, JUDGEMENT, "service ladder, pricing and funnel plans"),
    Rule("content/drafts/", PRIVATE, CERTAIN, "unpublished LinkedIn and outreach drafts"),
    # --- private: strategy ---------------------------------------------------
    Rule("01_STRATEGY/", PRIVATE, CERTAIN, "company strategy, positioning source, project PIDs"),
    Rule("04_GROWTH/", PRIVATE, CERTAIN, "growth plans, client acquisition engine, expansion lanes"),
    Rule("02_PRODUCTS/", PRIVATE, JUDGEMENT, "product registry and extraction ledger"),
    Rule("01_PRODUCT/", PRIVATE, JUDGEMENT, "unbuilt product specs"),
    Rule("05_INTELLIGENCE/", PRIVATE, JUDGEMENT, "knowledge-graph schema (internal)"),
    Rule("website/visibility-plan.md", PRIVATE, JUDGEMENT, "growth plan, not site copy"),
    Rule("website/CLINICOPS_DK_DEPLOYMENT_PLAN.md", PRIVATE, JUDGEMENT, "deployment plan, not site copy"),
    Rule("website/denmark-medtech-language-review.md", PRIVATE, JUDGEMENT, "internal language review"),
    # --- public exceptions inside private directories (checked before them) ----
    Rule("03_OPERATIONS/expert_network/roster.example.json", PUBLIC, JUDGEMENT, "synthetic roster read by tests/test_expert_network.py (propose moving to examples/)"),
    Rule("03_OPERATIONS/expert_network/assignment.example.json", PUBLIC, JUDGEMENT, "synthetic assignment example (propose moving to examples/)"),
    # --- private: operations / agent fleet / resilience -----------------------
    Rule("00_STATE/", PRIVATE, JUDGEMENT, "operating state shards (fleet status, next work, private-state rules)"),
    Rule("03_OPERATIONS/", PRIVATE, JUDGEMENT, "internal operating engines, discovery ledger, expert-network governance"),
    Rule("06_AGENTS/", PRIVATE, JUDGEMENT, "agent operating model and protocols"),
    Rule("07_RESILIENCE/", PRIVATE, CERTAIN, "survival plan, revenue bootstrap, handover (lens 30: must not be public)"),
    Rule("BUILD_NOTES/", PRIVATE, JUDGEMENT, "internal build and handoff notes"),
    Rule("experiments/", PRIVATE, JUDGEMENT, "commercial experiment ledger"),
    Rule("AGENT_STATE.md", PRIVATE, JUDGEMENT, "shared operating state index"),
    Rule("AGENT_STATE_NEW.md", PRIVATE, JUDGEMENT, "historic draft of the agent state index (no longer tracked)"),
    Rule("COLLABORATION.md", PRIVATE, JUDGEMENT, "internal collaboration protocol"),
    Rule("VALIDATION_AND_SCALABILITY_GATES.md", PRIVATE, JUDGEMENT, "internal validation gates for commercial assets"),
    # --- public: must stay ---------------------------------------------------
    Rule("docs/", PUBLIC, CERTAIN, "the served site (GitHub Pages)"),
    Rule("website/", PUBLIC, CERTAIN, "governed site copy sources checked by validate_content_claims.py"),
    Rule("research/", PUBLIC, CERTAIN, "claims registry, corrections, primary-source reviews, canary baseline"),
    Rule("data/", PUBLIC, CERTAIN, "anonymised watch outputs, public termbase, public proof wordings"),
    Rule("src/", PUBLIC, CERTAIN, "source"),
    Rule("tests/", PUBLIC, CERTAIN, "tests"),
    Rule("scripts/", PUBLIC, CERTAIN, "scripts"),
    Rule("e2e/", PUBLIC, CERTAIN, "browser journeys"),
    Rule("qa/", PUBLIC, CERTAIN, "QA harness"),
    Rule("examples/", PUBLIC, CERTAIN, "sanitized fixtures"),
    Rule("skills/", PUBLIC, CERTAIN, "skill validation"),
    Rule("design/", PUBLIC, CERTAIN, "design tokens"),
    Rule("agents/", PUBLIC, JUDGEMENT, "fleet registry read by src/clinicops_os/cli.py; content is generic"),
    Rule("autonomy/", PUBLIC, JUDGEMENT, "policy + job specs read by code, tests, CODEOWNERS and a workflow; no names"),
    Rule(".github/", PUBLIC, CERTAIN, "workflows, CODEOWNERS, issue templates, agent profiles"),
    Rule(".claude/", PUBLIC, CERTAIN, "tooling skills"),
    Rule("content/", PUBLIC, CERTAIN, "published content (drafts are matched earlier)"),
    Rule("AGENTS.md", PUBLIC, CERTAIN, "agent instructions"),
    Rule("CLAIM_RULES.md", PUBLIC, CERTAIN, "claim rules"),
    Rule("README.md", PUBLIC, CERTAIN, "readme"),
    Rule("PRIMARY_SOURCES.md", PUBLIC, CERTAIN, "primary sources"),
    Rule("CHANGELOG.md", PUBLIC, CERTAIN, "changelog"),
    Rule("pyproject.toml", PUBLIC, CERTAIN, "packaging"),
    Rule("requirements-lock.txt", PUBLIC, CERTAIN, "packaging"),
    Rule(".gitignore", PUBLIC, CERTAIN, "git"),
)

# Name patterns that should never sit in the public set. Used as a tripwire by
# the tests: a path that is classified public (or not classified) but looks
# like prospect, pipeline or pricing material fails loudly.
SENSITIVE_NAME = re.compile(
    r"(target_accounts|prospect|pipeline|discovery_ledger|outreach|invoice|pricing|"
    r"customer_discovery|mailbox|credential|secret|(^|/)\.env)",
    re.IGNORECASE,
)
# Only data-like files trip the wire (source code and job specs legitimately use
# words like "prospect" and "invoice"; sanitized fixtures live under examples/).
SENSITIVE_SUFFIXES = {".csv", ".xlsx", ".xls", ".docx", ".pdf", ".json", ".jsonl", ".env", ""}
SENSITIVE_EXEMPT_PREFIXES = ("examples/", "tests/fixtures/", "docs/", "src/", "scripts/", "e2e/", "qa/")

# Public-side tests that assert the CONTENT of private documents. When those
# documents leave the public repo, these tests move with them (or become
# fixture-backed). Verified by test_private_split_manifest.py: each listed test
# really does read a private path, and the verify run deselects exactly these.
MOVES_WITH_PRIVATE_TESTS: tuple[str, ...] = (
    "tests/test_commercial_activation_gate.py",  # asserts content of sales/commercial-activation-gate.md
    "tests/test_delegation_proof_contract.py",  # asserts content of sales/ delegation docs
    "tests/test_pilot_operator_contract.py",  # asserts content of sales/ pilot playbooks
    "tests/test_expansion_lane_contract.py",  # asserts content of 04_GROWTH/expansion_lanes.json
)

TEXT_SUFFIXES = {
    ".py", ".yml", ".yaml", ".json", ".jsonl", ".md", ".cjs", ".mjs", ".js", ".html",
    ".toml", ".sh", ".txt", ".csv", ".xml", ".css",
}  # fmt: skip

SKIP_DEP_SCAN_DIRS = ("node_modules/", ".git/")


def classify(path: str) -> Rule | None:
    for rule in RULES:
        if rule.match.endswith("/"):
            if path.startswith(rule.match):
                return rule
        elif path == rule.match:
            return rule
    return None


def tracked_files(root: Path) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=True, capture_output=True,
        ).stdout.decode("utf-8")  # fmt: skip
        files = [p for p in out.split("\0") if p]
        if files:
            return sorted(files)
    except (OSError, subprocess.CalledProcessError):
        pass
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache")]
        for name in filenames:
            found.append(str((Path(dirpath) / name).relative_to(root)).replace(os.sep, "/"))
    return sorted(found)


def history_paths(root: Path) -> list[str]:
    """Every path that has ever existed on any ref (read-only ``git log``).

    ``git filter-repo`` needs historical locations too: a file that was renamed
    or deleted earlier still carries its content in old commits.
    """
    out = subprocess.run(
        ["git", "-C", str(root), "log", "--all", "--name-only", "--format=", "-z"],
        check=True, capture_output=True,
    ).stdout.decode("utf-8", "replace")  # fmt: skip
    return sorted({p for p in out.replace("\n", "\0").split("\0") if p})


def build_manifest(paths: list[str]) -> dict:
    rows = []
    unclassified = []
    for path in paths:
        rule = classify(path)
        if rule is None:
            unclassified.append(path)
            continue
        rows.append({"path": path, "class": rule.klass, "confidence": rule.confidence, "rule": rule.match, "reason": rule.reason})
    return {"rows": rows, "unclassified": unclassified}


def paths_of(manifest: dict, klass: str) -> list[str]:
    return [r["path"] for r in manifest["rows"] if r["class"] == klass]


def sensitive_in_public(manifest: dict) -> list[str]:
    """Public or unclassified paths whose NAME looks like private material."""
    candidates = paths_of(manifest, PUBLIC) + manifest["unclassified"]
    return [
        p
        for p in candidates
        if SENSITIVE_NAME.search(p)
        and Path(p).suffix.lower() in SENSITIVE_SUFFIXES
        and not p.startswith(SENSITIVE_EXEMPT_PREFIXES)
    ]


# ---------------------------------------------------------------------------
# Dependencies: which public files mention private paths
# ---------------------------------------------------------------------------


def _private_patterns(manifest: dict) -> re.Pattern[str]:
    private = paths_of(manifest, PRIVATE)
    prefixes = sorted({r["rule"] for r in manifest["rows"] if r["class"] == PRIVATE and r["rule"].endswith("/")})
    exact = sorted({p for p in private if not any(p.startswith(x) for x in prefixes)})
    alts = [re.escape(x) for x in prefixes + exact]
    # Also catch pathlib joins such as ROOT / "sales" / "file.md" (quoted dir name).
    quoted = [re.escape(x.rstrip("/")) for x in prefixes]
    return re.compile(
        r"(?<![A-Za-z0-9_.-])(" + "|".join(alts) + r")"
        r"|[\"'](" + "|".join(quoted) + r")[\"']\s*[,/)]"
    )


def _area(path: str) -> str:
    if path.startswith(".github/workflows/"):
        return "workflow"
    if path.startswith(".github/"):
        return "github-config"
    for top, name in (("tests/", "test"), ("src/", "src"), ("scripts/", "script"), ("e2e/", "e2e"), ("qa/", "qa"), ("docs/", "site"), ("examples/", "example"), ("website/", "site-source")):
        if path.startswith(top):
            return name
    return "other"


def find_dependencies(root: Path, manifest: dict) -> list[dict]:
    pattern = _private_patterns(manifest)
    deps: list[dict] = []
    for path in paths_of(manifest, PUBLIC):
        if Path(path).suffix not in TEXT_SUFFIXES and Path(path).name not in {"CODEOWNERS", ".gitignore"}:
            continue
        full = root / path
        if not full.is_file():
            continue
        try:
            text = full.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for match in pattern.finditer(line):
                target = match.group(1) or match.group(2) + "/ (pathlib join)"
                deps.append({"file": path, "line": lineno, "target": target, "area": _area(path), "text": line.strip()[:160]})
    return deps


# ---------------------------------------------------------------------------
# Verify: build and test the public set alone, in a temporary copy
# ---------------------------------------------------------------------------

VERIFY_ENV_GUARD = "CLINICOPS_SPLIT_VERIFY"

# Steps mirror the self-contained part of .github/workflows/ci.yml. Steps that
# name a private path in ci.yml are listed separately in the runbook, not run.
PUBLIC_BUILD_STEPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("sitemap contract", ("python", "scripts/render_sitemap.py", "--check")),
    ("public shell drift", ("python", "scripts/harmonize_public_shell.py", "--check")),
    ("llms.txt contract", ("python", "scripts/render_llms_txt.py", "--check")),
    ("internal links", ("python", "scripts/validate_internal_links.py")),
    ("site metadata", ("python", "scripts/validate_site_metadata.py")),
    ("professional claims", ("python", "scripts/validate_professional_claims.py")),
    ("public transition map sample", ("python", "scripts/render_public_demo.py", "--check")),
    ("claim registry audit", ("python", "scripts/audit_claim_registry.py")),
    ("claim reference integrity", ("python", "scripts/audit_claim_references.py")),
    ("governed content claims", ("python", "scripts/validate_content_claims.py", "website")),
    ("public-copy claim gate", ("python", "scripts/claim_gate.py", "README.md", "PRIMARY_SOURCES.md", "docs", "website", "examples/portfolio_report.md", "research")),
    ("ruff", ("python", "-m", "ruff", "check", "src", "tests", "scripts")),
    (
        "browser reconciliation rules (node)",
        (
            "node", "--test", "tests/reconciliation.test.cjs", "tests/ecoa_workbench.test.cjs",
            "tests/coa_finder.test.cjs", "tests/coa_leadtime.test.cjs", "tests/coa_burden.test.cjs",
        ),
    ),
    (
        "pytest",
        (
            "python", "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider",
            *(f"--ignore={t}" for t in MOVES_WITH_PRIVATE_TESTS),
        ),
    ),
)  # fmt: skip


def copy_public_set(root: Path, manifest: dict, dest: Path) -> int:
    count = 0
    for path in paths_of(manifest, PUBLIC):
        src = root / path
        if not src.is_file():
            continue
        target = dest / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        count += 1
    return count


def verify_public_build(root: Path, manifest: dict, steps=PUBLIC_BUILD_STEPS, keep: bool = False) -> list[dict]:
    """Run ``steps`` inside a temp copy holding only the public set. Returns per-step results."""
    results: list[dict] = []
    tmp = Path(tempfile.mkdtemp(prefix="clinicops-public-only-"))
    try:
        copied = copy_public_set(root, manifest, tmp)
        for private in paths_of(manifest, PRIVATE):
            if (tmp / private).exists():  # defence in depth: the copy must be private-free
                raise RuntimeError(f"private path leaked into public copy: {private}")
        node_modules = root / "node_modules"
        if node_modules.exists():
            (tmp / "node_modules").symlink_to(node_modules)
        env = {**os.environ, VERIFY_ENV_GUARD: "1", "PYTHONPATH": str(tmp / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
        results.append({"step": "copy public set", "ok": True, "detail": f"{copied} files, 0 private"})
        for name, argv in steps:
            if argv[0] == "node" and not shutil.which("node"):
                results.append({"step": name, "ok": True, "detail": "skipped: node not installed"})
                continue
            argv = tuple(sys.executable if a == "python" else a for a in argv)
            proc = subprocess.run(argv, cwd=tmp, env=env, capture_output=True, text=True, check=False)
            tail = (proc.stdout + proc.stderr).strip().splitlines()[-6:]
            results.append({"step": name, "ok": proc.returncode == 0, "detail": "\n".join(tail)})
            if proc.returncode != 0:
                break
        return results
    finally:
        if keep:
            print(f"kept temp copy: {tmp}", file=sys.stderr)
        else:
            shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def summary(manifest: dict) -> str:
    counts = Counter((r["class"], r["confidence"]) for r in manifest["rows"])
    by_dir: dict[str, Counter] = defaultdict(Counter)
    for r in manifest["rows"]:
        by_dir[r["path"].split("/", 1)[0] if "/" in r["path"] else "(root)"][r["class"]] += 1
    lines = [
        f"tracked paths: {len(manifest['rows']) + len(manifest['unclassified'])}",
        f"private: {counts[(PRIVATE, CERTAIN)]} certain + {counts[(PRIVATE, JUDGEMENT)]} judgement (founder to confirm)",
        f"public: {counts[(PUBLIC, CERTAIN)] + counts[(PUBLIC, JUDGEMENT)]}",
        f"unclassified: {len(manifest['unclassified'])}",
        "",
        "by top-level directory (private/public):",
    ]
    for name in sorted(by_dir):
        lines.append(f"  {name:24} {by_dir[name][PRIVATE]:4} / {by_dir[name][PUBLIC]:4}")
    if manifest["unclassified"]:
        lines += ["", "UNCLASSIFIED (add a rule before the split):"] + [f"  {p}" for p in manifest["unclassified"]]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument(
        "--list",
        choices=(PRIVATE, PUBLIC, "judgement", "private-history"),
        help="print paths of one class, one per line ('private-history': every private path ever on any ref, "
        "for git filter-repo; paths that match no rule are printed to stderr for review)",
    )
    parser.add_argument("--deps", action="store_true", help="list public files that reference private paths")
    parser.add_argument("--json", action="store_true", help="full machine-readable manifest")
    parser.add_argument("--strict", action="store_true", help="exit 1 if any path is unclassified or a sensitive name is public")
    parser.add_argument("--verify-public-build", action="store_true", help="run build and tests in a temp copy without the private set")
    parser.add_argument("--keep", action="store_true", help="keep the temp copy (with --verify-public-build)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    manifest = build_manifest(tracked_files(root))

    if args.list == "private-history":
        hist = build_manifest(history_paths(root))
        print("\n".join(paths_of(hist, PRIVATE)))
        if hist["unclassified"]:
            print("historic paths matching no rule (review):", *hist["unclassified"], sep="\n  ", file=sys.stderr)
    elif args.list == "judgement":
        print("\n".join(r["path"] for r in manifest["rows"] if r["class"] == PRIVATE and r["confidence"] == JUDGEMENT))
    elif args.list:
        print("\n".join(paths_of(manifest, args.list)))
    elif args.deps:
        for d in find_dependencies(root, manifest):
            print(f"{d['area']:12} {d['file']}:{d['line']}  ->  {d['target']}")
    elif args.json:
        print(json.dumps({**manifest, "rules": [asdict(r) for r in RULES]}, indent=1))
    elif args.verify_public_build:
        if os.environ.get(VERIFY_ENV_GUARD):
            print("already inside a verify run; refusing to recurse")
            return 0
        results = verify_public_build(root, manifest, keep=args.keep)
        for r in results:
            print(f"[{'ok' if r['ok'] else 'FAIL'}] {r['step']}" + ("" if r["ok"] else "\n" + r["detail"]))
        return 0 if all(r["ok"] for r in results) else 1
    else:
        print(summary(manifest))

    bad = manifest["unclassified"] + sensitive_in_public(manifest)
    if args.strict and bad:
        print("strict: unclassified or sensitive-looking public paths:", *bad, sep="\n  ", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:  # e.g. piped into head
        raise SystemExit(0) from None
