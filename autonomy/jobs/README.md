# Tier-0 job specifications

Each file here is the **complete prompt** of one scheduled Claude task, split into two parts:

1. `_COMMON_HEADER.md` — the hard limits, the kill switch, and the logging/evidence contract. It is prepended verbatim to every job.
2. `<job>.md` — the job body. The YAML front matter records the task name, slug, cron (Europe/Madrid, minutes jittered away from :00/:30), cadence, the minimum sane run duration the watchdog uses, expected outputs and notification channels.

The scheduled tasks themselves run on claude.ai (fresh session per firing, with Ali's connectors: Microsoft 365, Gmail, Google Drive, Google Calendar, HubSpot, GitHub via Claude Code Remote). They are **not** GitHub Actions: GitHub Actions in this repository stay low-frequency, bounded and compute-only. The two systems meet through the repository: jobs read `autonomy/HALT.md` (kill switch), `research/claims.jsonl`, `data/eudamed/LATEST.md` and the positioning documents from `main`, and open **pull requests** (never pushes to `main`) for public-safe artefacts — claim re-verification patches, public termbase rows, content drafts — so that CI's existing gates validate them.

To recreate a task: concatenate `_COMMON_HEADER.md` + `<job>.md` body (everything below the front matter) as the prompt; use the cron and notification settings from the front matter; enable automatic approval so unattended runs do not stall. `python -m clinicops_os.autonomy.jobs render <slug>` prints the assembled prompt.

Private material — client names, prospect lists, mailbox content, watchlists, vendor identifiers — never appears in these files and never leaves Drive or the private project.
