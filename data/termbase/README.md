# Public EN↔DA regulatory termbase

`termbase_public.csv` is the public slice of the ClinicOps English↔Danish terminology database for medical-device, IVD and pharma regulatory documents. It is built one bounded slice per night by the `t0-termbase` job (`autonomy/jobs/termbase.md`) and reaches this repository only through pull requests on Sundays. Every row must be traceable to an aligned public source; nothing here is invented.

## Schema

One row per term pair, header exact and in this order:

| Column | Meaning |
|---|---|
| `id` | `TB-` plus a zero-padded number (at least four digits), unique, continuing from the master |
| `en_term` | English term as used in the source |
| `da_term` | Danish term as used in the aligned source |
| `domain` | e.g. `regulatory`, `clinical`, `vigilance`, `technical-documentation` |
| `subdomain` | e.g. `MDR definitions`, `Annex I GSPR`, `synonym-of:TB-0001` |
| `source_ref` | the provision or document pair, e.g. `MDR 2017/745 Art. 2(1)` |
| `source_url` | public URL of the source (required for `verified` rows) |
| `context_en` / `context_da` | the sentence fragments containing the terms (both required for `verified` rows) |
| `status` | `verified` (both terms quoted from the same aligned provision), `candidate` (aligned but ambiguous, or a synonym), `unverified-seed` (not yet checked at source) |
| `confidence` | 0.0–1.0; an `unverified-seed` row may not exceed 0.5 |
| `added_utc` | ISO 8601 UTC timestamp, e.g. `2026-09-25T00:00:00Z` |
| `job_run` | the run that added the row (`seed-…` for hand-seeded rows) |

## Provenance rules

- A pair is `verified` only when EN and DA come from the same numbered provision, definition or heading and both contexts are quoted.
- The official Danish legal term is preferred; synonyms are separate `candidate` rows with `subdomain = synonym-of:<id>`.
- Sources, in priority order for public rows: Regulation (EU) 2017/745 and 2017/746 on EUR-Lex (EN and DA), then Danish national texts (DA only, for usage validation, never as a source of pairs on their own).
- The 22 seed rows dated 2026-09-25 are deliberately `unverified-seed` at confidence 0.4: they are common MDR Article 2 pairs recorded from working knowledge, not yet quoted from the source. The termbase job re-verifies them at EUR-Lex before promoting them.
- Duplicates are detected on (`en_term`, `da_term`, `source_ref`), case-insensitive.

## Public rows only

Rows derived from the private bilingual corpus in Drive (`ClinicOps-Autonomy/06_TERMBASE/corpus/`) are private: they live in Drive and the private project (`20_AUTONOMY/TERMBASE_MASTER.csv`) and never appear in this file. Client names, document titles or any text that could identify a client's file do not belong here.

## How CI validates

`.github/workflows/autonomy-gate.yml` runs on every change to `data/termbase/**`:

```bash
clinicops-termbase validate data/termbase/termbase_public.csv   # schema, ids, statuses, confidence, contexts, URLs
clinicops-termbase qa data/termbase/termbase_public.csv         # counts by status/domain, duplicates, suspicious rows
```

`clinicops-termbase merge MASTER DELTA --out MERGED` appends a nightly delta to a master file, skipping duplicates and reassigning colliding ids. Implementation: `src/clinicops_os/autonomy/termbase.py`; tests: `tests/test_termbase.py`.
