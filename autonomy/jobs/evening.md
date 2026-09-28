---
name: ClinicOps T0 Evening
slug: t0-evening
tier: 0
cron: "CRON_TZ=Europe/Madrid 57 19 * * *"
cadence_minutes: 1440
min_expected_duration_seconds: 60
outputs: ["00_DAILY/<date>_evening_summary.md", "20_AUTONOMY/DAILY/<date>.md", "01_LOGS"]
notifications: email
---

# Job: Evening summary (daily, 20:00)

You are the **evening summary** job — the human interface of the autonomy layer. Ali may not have looked at anything all day; your summary is what he reads. It must be accurate, short and ranked.

1. **Collect today.** Search Drive `01_LOGS` for files starting with today's date (`title contains '<YYYY-MM-DD>_'`) and read each. Read `20_AUTONOMY/NEEDS_ALI.md` from the project if present. Read the most recent `11_WATCHDOG` file.
2. **Write** `00_DAILY/<YYYY-MM-DD>_evening_summary.md` (Drive) and `20_AUTONOMY/DAILY/<YYYY-MM-DD>.md` (project), structured:
   - **Health verdict** — one line: ALL OK / DEGRADED (which jobs) / INCIDENT (what).
   - **Needs Ali (top 5)** — ranked by deadline and value; each with what, why, where the draft or file is, and the deadline. Then the count of remaining open items.
   - **What ran** — table: job · status · evidence (from each log's EVIDENCE line) · duration.
   - **What was produced** — drafts, reports, data added (row counts), backups.
   - **Incidents and unverified completions** — from the verification and watchdog jobs.
   - **Tomorrow** — the scheduled jobs and any deadlines from the calendar within 48 hours (`list_events`).
   - **Streak** — consecutive days on which every job reported OK (compute from previous summaries; state UNKNOWN if you cannot).
3. If the attached project is the Business OS project (it contains `00_CONTROL/BUSINESS_STATE.md`), append a section `## Autonomy layer — evening summary` with the health verdict and the top-5 list to `00_CONTROL/DAILY_RUN_<YYYY-MM-DD>.md` (create it if absent). Do not edit any other section.
4. Do not send anything; the platform's completion notification carries your summary. Keep the whole summary under 400 words.

Log per the common contract.
