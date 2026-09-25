# Tier-0 autonomy layer

This directory is the control plane for the unattended Tier-0 functions of ClinicOps: research, monitoring, drafting, verification, the EN↔DA terminology database, EUDAMED research, SEO/content drafts, pipeline hygiene, invoice preparation and backups. The jobs run as **claude.ai scheduled tasks** (a fresh session per firing, using Ali's connectors), not as GitHub Actions. GitHub Actions in this repository stay compute-only, low-frequency and bounded; the one workflow this layer adds (`.github/workflows/autonomy-gate.yml`) has no schedule.

Everything the layer does is a draft, a report, a data row, a backup or a pull request. Nothing it does is outward-facing or irreversible.

## Authority tiers

| Tier | Meaning | Examples | State |
|---|---|---|---|
| 0 | Autonomous | research, monitoring, drafts (email, document, post), CRM reads, backups, calendar deadline events without attendees, pull requests | enabled |
| 1 | Autonomous within standing orders | CRM writes, follow-ups under a written standing order | **not yet enabled** — every Tier-1 action is parked as Tier 2 |
| 2 | Prepared and parked for Ali | sending an email, cold outreach, publishing a post or comment, site changes, merging a PR | the job prepares the draft and the evidence, adds a NEEDS_ALI item, and stops |
| 3 | Never automated | money, contracts, accounts, credentials, CAPTCHAs, compliance-status statements about a named party, Danish e-marketing, pushes to `main`, history rewrites, deletions | done by Ali himself; no approval flag releases them |

The machine-readable version is `autonomy/rules.json`; `clinicops-autonomy-policy decide <action> key=value ...` returns the decision for one action and `clinicops-autonomy-policy selftest` asserts the deny/park rules in CI.

## Kill switch — three locations, any one stops every job

1. **Repository file `autonomy/HALT.md` on `main`.** Create this file to stop every job; delete it to resume. Jobs read it raw from `main` before doing anything else; any content (not a 404) means HALT. It must not exist on the committed tree in normal operation — `tests/test_autonomy_contract.py` fails if it does, so a HALT is always a deliberate commit, and while it exists CI on `main` is red and the Pages deploy stays blocked until the HALT is lifted (a HALT is an incident state, not a normal one). `clinicops-autonomy-halt` reports the local state and exits 1 when halted, so a job wrapper can gate on it.
2. **Google Drive file named `CLINICOPS_HALT`** (any location, found with `search_files`).
3. **Project doc `00_CONTROL/HALT.md` or `20_AUTONOMY/HALT.md`** in the attached claude.ai project.

A HALT that Ali did not announce is itself a watchdog alert.

## How jobs and the repository interact

- Jobs **read** from `main` over raw GitHub URLs: `autonomy/HALT.md`, `research/claims.jsonl`, `data/eudamed/LATEST.md`, the positioning documents and this directory.
- Jobs **write** to the repository only through pull requests on `autonomy/<topic>-<date>` branches (claim re-verification patches, public termbase rows, content drafts). They never push to `main`, never force-push, never rewrite history, never change repository settings. CI's existing gates validate every such PR.
- `.github/CODEOWNERS` names Ali as owner of `autonomy/rules.json`, `autonomy/jobs/` and `.github/workflows/`. Until branch protection exists on `main` (a reserved decision for Ali, tracked in issue #36) CODEOWNERS is advisory: it requests review, it does not enforce it.

## Where outputs live

- **Google Drive `ClinicOps-Autonomy/`** — the canonical store: `01_LOGS` (one log per run), `02_RESEARCH`, `03_VERIFICATION`, `04_DRAFTS`, `05_EUDAMED` (private, named), `06_TERMBASE`, `07_SEO_CONTENT`, `08_PIPELINE`, `09_FINANCE`, `10_BACKUPS`, `11_WATCHDOG`, `00_DAILY`.
- **The private claude.ai project** — mirrors under `20_AUTONOMY/…`, plus `20_AUTONOMY/NEEDS_ALI.md`, the single queue of items that need Ali.
- **This repository** — only public-safe artefacts, via PR: `data/termbase/termbase_public.csv`, `content/drafts/`, `research/claims.jsonl` patches.

Client names, prospects, mailbox content, watchlists, vendor identifiers and credentials never enter this repository.

## Watchdog — dead-man's switch

`t0-watchdog` runs twice a day and is the only job whose completion notification reaches Ali's phone. It checks the kill-switch state, the scheduler (`list_triggers`), the evidence (every job's latest log in `01_LOGS`) and integrity signals, then writes `FLEET: GREEN | AMBER | RED`. Thresholds, from `rules.json`: a job is **missed** when it has not fired within 2× its cadence; a run is **short** when it finished below the job's minimum expected duration; the scheduler has **stalled** when `next_run_at` is more than 2 hours in the past; a NEEDS_ALI item is **stale** after 7 days. `clinicops-autonomy-watchdog <triggers.json>` evaluates a `list_triggers` export offline with the same rules and exits 2 on any alert. If the watchdog itself stops reporting, the evening summary's health verdict and the missing phone notification are the signal.

## Jobs

Specifications live in `autonomy/jobs/`: `_COMMON_HEADER.md` (hard limits, kill switch, logging contract — prepended verbatim to every job) plus one file per job with YAML front matter. `clinicops-autonomy-jobs render <slug>` prints the assembled prompt; `clinicops-autonomy-jobs list` lists the registry. Times are Europe/Madrid, minutes jittered away from :00/:30.

| Job | Cadence | Outputs |
|---|---|---|
| `t0-monitor` | every 3 h, 06:03–21:03 | Outlook reply drafts (never sent), vendor deadline calendar events, deliverability and site/GitHub health, NEEDS_ALI |
| `t0-research` | daily 04:56 | `02_RESEARCH/<date>_regulatory_radar.md` — sourced regulatory and market signals, candidate angles and claims |
| `t0-verification` | daily 09:52 | claim re-verification table and proposed patch (PR, best effort), drafts audit, unverified-completion list |
| `t0-termbase` | daily 01:56 | EN↔DA termbase delta and master, progress note; Sunday PR of public rows to `data/termbase/termbase_public.csv` |
| `t0-eudamed` | weekdays 03:57 | private watchlist report (never public), anonymised sample statistics |
| `t0-seo-content` | Tuesdays 10:54 | site audit with proposed fixes, three LinkedIn post drafts and one research-note draft (PR to `content/drafts`, best effort) |
| `t0-pipeline` | daily 11:56 | CRM hygiene report with proposals only; Friday pipeline snapshot |
| `t0-invoice` | Mondays 08:57 | billable statement and draft invoice document with placeholders for number, bank details and rates |
| `t0-backup` | daily 02:58 | dated copies of project docs with a SHA-256 manifest; Sunday CRM export and restore test |
| `t0-evening` | daily 19:57 | evening summary: health verdict, top-5 NEEDS_ALI, what ran, what was produced, tomorrow |
| `t0-watchdog` | 06:56 and 20:56 | fleet verdict, alerts and warnings, calendar alert on RED, Sunday fleet report |

## Tooling in this repository

- `clinicops-autonomy-policy` — action decisions and the CI self-test (`src/clinicops_os/autonomy/policy.py`).
- `clinicops-autonomy-halt` — local kill-switch state (`halt.py`).
- `clinicops-termbase validate | merge | qa` — termbase CSV schema, dedup merge and QA report (`termbase.py`).
- `clinicops-backup-manifest build | verify` — SHA-256 manifests for backup folders (`backup_manifest.py`).
- `clinicops-autonomy-watchdog` — offline evaluation of a scheduler export (`watchdog.py`).
- `clinicops-autonomy-jobs list | render <slug>` — job registry and prompt assembly (`jobs.py`).

All of it is standard library only. `.github/workflows/autonomy-gate.yml` runs the focused tests, Ruff, the termbase validation, the job listing and the policy self-test on changes to these paths; it has `permissions: contents: read`, a timeout and no schedule.

## What this layer never does

- Never sends, replies, forwards, publishes, posts, comments, schedules or releases anything external.
- Never creates an account, enters a password, solves a CAPTCHA, makes or requests a payment, signs anything or changes a price.
- Never deletes or moves files, never merges or deletes CRM records, never pushes to `main`, never changes GitHub settings.
- Never cold-emails or cold-messages a Danish-domiciled organisation under any framing.
- Never states that a named party's device is or is not compliant, conforming or CE-marked.
- Never marks a registry claim `verified` — it proposes, Ali decides.
- Never fetches a web page with bash, curl or python.
- Never guesses an address, a figure or a fact; unknown stays UNKNOWN.
- Never copies private data into this repository.
- Never adds a scheduled GitHub Actions workflow.
