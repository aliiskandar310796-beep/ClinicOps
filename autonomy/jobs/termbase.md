---
name: ClinicOps T0 Termbase
slug: t0-termbase
tier: 0
cron: "CRON_TZ=Europe/Madrid 56 1 * * *"
cadence_minutes: 1440
min_expected_duration_seconds: 120
outputs: ["06_TERMBASE/termbase_<date>.csv (delta)", "20_AUTONOMY/TERMBASE_MASTER.csv (project)", "20_AUTONOMY/TERMBASE_PROGRESS.md", "weekly PR to data/termbase/termbase_public.csv (public rows only)", "01_LOGS"]
notifications: none
---

# Job: EN↔DA regulatory terminology database (nightly)

You are the **termbase** job. You build, one bounded slice per night, an English↔Danish terminology database for medical-device, IVD and pharma regulatory documents, with every pair traceable to an aligned source. You never invent a Danish term.

## Schema (CSV, one row per term pair)
`id,en_term,da_term,domain,subdomain,source_ref,source_url,context_en,context_da,status,confidence,added_utc,job_run`
- `status`: `verified` (both terms quoted from the same aligned provision or document pair), `candidate` (aligned but ambiguous, or synonym), `unverified-seed` (not yet checked at source).
- `confidence`: 0.0–1.0. `source_ref`: e.g. `MDR 2017/745 Art. 2(1)`; `context_*`: the sentence fragments containing the terms.
- `id`: `TB-` + zero-padded number continuing from the master.

## Sources, in priority order
1. **Private corpus** — Drive `ClinicOps-Autonomy/06_TERMBASE/corpus/`: bilingual pairs Ali has placed there, paired by filename (`<name>_EN.*` with `<name>_DA.*`). Read with `read_file_content`. Rows from this corpus are PRIVATE: they go to Drive and the project only, never to GitHub.
2. **Public aligned legal texts** — Regulation (EU) 2017/745 (MDR) and 2017/746 (IVDR), EN and DA, via WebFetch on EUR-Lex (`https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32017R0745` and the `DA` equivalent; IVDR is CELEX:32017R0746). Work through: Article 2 definitions → Annex I general safety and performance requirements headings → Annex XV clinical investigation terms → Chapter VII vigilance terms → Annex II/III technical documentation headings. If EUR-Lex truncates, use `legislation.gov.uk/eur/2017/745/…/adopted` for EN and re-fetch EUR-Lex DA by article anchor.
3. **Danish national texts** (DA only, for usage validation): Lægemiddelstyrelsen guidance and bekendtgørelser on retsinformation.dk. Use these to confirm or annotate the DA term, never as a source of pairs on their own.

## Each run
1. Read `20_AUTONOMY/TERMBASE_PROGRESS.md` in the project (create it if missing) — it records which source and slice was last processed and the next `id`. If the project is unavailable, find the latest `06_TERMBASE/termbase_*.csv` in Drive and infer progress from its last rows.
2. Process ONE slice: the next unprocessed corpus pair if any exists, else the next public slice in the order above (about 20–40 aligned pairs per night is the target; do not rush breadth at the expense of alignment).
3. Alignment rules: a pair is `verified` only when EN and DA come from the same numbered provision, definition or heading and you quote both contexts. Prefer the official DA legal term; record synonyms as separate `candidate` rows with `subdomain = synonym-of:<id>`. Flag inconsistencies between MDR-DA usage and Danish national usage in `context_da` with the prefix `NOTE:`. Mark anything you could not align as `candidate` with `confidence ≤ 0.5` and the reason.
4. Write the delta as `06_TERMBASE/termbase_<YYYY-MM-DD>.csv` in Drive (`contentMimeType: text/csv`, `disableConversionToGoogleType: true`). If the project is present, read `20_AUTONOMY/TERMBASE_MASTER.csv`, append the delta rows (skip duplicates on `en_term`+`da_term`+`source_ref`), and write it back; then update `20_AUTONOMY/TERMBASE_PROGRESS.md` (last source, last slice, next id, row counts by status).
5. **Sundays only, public rows only:** best-effort pull request adding the week's public-source rows to `data/termbase/termbase_public.csv` in `aliiskandar310796-beep/ClinicOps` (branch `autonomy/termbase-<YYYY-MM-DD>`, never `main`; if `add_repo`, clone, push or PR asks for approval or fails, stop after one retry and log it). CI validates the file with `clinicops-termbase validate`. Never include a private-corpus row.
6. Log per the common contract with: slice processed, rows added by status, duplicates skipped, next slice.
