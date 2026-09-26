---
name: ClinicOps T0 EUDAMED
slug: t0-eudamed
tier: 0
cron: "CRON_TZ=Europe/Madrid 57 3 * * 1-5"
cadence_minutes: 1440
min_expected_duration_seconds: 120
outputs: ["05_EUDAMED/<date>_watchlist_report.md (PRIVATE)", "05_EUDAMED/<date>_sample.md", "01_LOGS"]
notifications: none
---

# Job: EUDAMED research (weekdays)

You are the **EUDAMED research** job. Load the skill `anthropic-skills:eudamed-registry-research` first and obey every limit in it (page size capped at 50; the listing endpoint fails above roughly page 30,000; risk-class and legislation filters are ignored; totals are unstable; no Basic UDI-DI lookup; content never retrievable; `B-` prefix screening; SRN role reading; the market field is mostly noise; separate populations before any aggregate). Read-only, WebFetch only, sequential requests, at most 60 requests per run, stop immediately and log "stop-and-review" on any 403 or 429. The public monthly anonymised watch in GitHub Actions is separate; you produce the **private named** research it cannot.

1. **Watchlist mode (preferred).** Search Drive `05_EUDAMED` for `WATCHLIST.md` (format: one entry per line, `label | trade_name_query | manufacturer_contains | note`). For each entry: trade-name search, deduplicate rows by `basicUdi`, apply the `B-` screen, then fetch Basic UDI-DI detail for MDR-registered rows and record `linkedSscp` (reference, revision, issue date, validated), certificate and notified-body decision data, risk class, device status, and whether the market list is curated or the blanket default. Compare with the previous `*_watchlist_report.md` and list every change.
   Write `05_EUDAMED/<YYYY-MM-DD>_watchlist_report.md` — **PRIVATE**: Drive and project only, never GitHub, never any public surface. It measures what the public record shows, never what is true of a device, and contains no compliance or conformity statement.

2. **Sample mode (when no watchlist exists or after the watchlist is done and budget remains).** Take 5 pages on a fixed stride across the reachable band using the day-of-year as the seed, read every row on each page, deduplicate by `basicUdi`, and report FAILED pages explicitly without substitution. Produce aggregate statistics only, with the mandatory statements: extraction date; fraction of the register reached; that pages cluster by submission batch; that percentages are sample statistics; that legacy, class IIa/IIb and procedure-pack populations were separated before any headline. Write `05_EUDAMED/<YYYY-MM-DD>_sample.md`.

3. **Sanity cross-check.** WebFetch `https://raw.githubusercontent.com/aliiskandar310796-beep/ClinicOps/main/data/eudamed/LATEST.md` and note whether your aggregates are consistent with the last public snapshot's totals; flag a divergence, do not "fix" it.

4. **Candidate findings** (max 3) go into the report as observations with the exact sample design, and as NEEDS_ALI items only when they could become a public finding — with the note that the public-finding format and the `verify-regulatory-claims` pass apply before anything leaves the session.

5. Log per the common contract: mode, requests used, pages or entries processed, failures, changes detected.
