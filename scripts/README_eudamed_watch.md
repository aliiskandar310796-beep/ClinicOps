# eudamed_watch — operator notes

`scripts/eudamed_watch.py` monitors the public EUDAMED JSON API for a private
watchlist of trade names, writes a dated **anonymised, aggregate-only** snapshot
of what the public record shows, and diffs it against the previous snapshot.
Standard library only (no `requests`, no PyYAML); the watchlist is JSON for
that reason.

## Standing rules

- Nothing this tool produces is a compliance, conformity or diligence statement
  about any named company. Outputs record what the *public record showed* at
  the extraction date and nothing more.
- **This repository is public, and ClinicOps' anonymisation rule applies:
  nothing committed here (snapshots, diffs, LATEST.md) and nothing printed to
  CI logs may contain a string identifying a manufacturer, device, trade name,
  identifier or SS(C)P reference.** The watchlist itself is private (a
  repository secret), and named detail exists only in local `--full-out`
  reports, which are gitignored.

## Public-aggregates design

Committed outputs carry:

- **Totals only**: entries queried, pages fetched/failed, rows seen, rows
  filtered client-side, distinct devices after dedupe, entries truncated by the
  page cap, entries with zero rows, and combined classification counts
  (`legacy_no_sscp_possible`, `pr_no_sscp_duty`, `sscp_linked`,
  `sscp_expected_but_absent`, `sscp_link_absent`, `lookup_failed`). Failures
  are recorded as counts per kind — never with the entry label or URL, since
  search URLs embed trade names.
- **Optional pseudonymous per-device rows**, present only when the
  `EUDAMED_HMAC_KEY` environment variable is set: each device is keyed by
  `HMAC-SHA256(key, basicUdi)` truncated to 16 hex chars, and carries only
  `classification`, `risk_class`, `sscp_expected`, `linked`, `validated` and
  the SS(C)P `issue_year`. The same key across runs gives stable keys, so the
  diff can report per-device classification/link changes without identifying
  anything. Without the key, snapshots are aggregate-only and the diff reports
  count deltas only.

The fully-named report (per-entry table, Basic UDI-DIs, manufacturer names,
SS(C)P references, named failures) is written **only** when you pass
`--full-out DIR` locally. `data/eudamed/full/` is gitignored for that purpose;
never publish these files or paste them into public issues/logs.

## Secrets Ali must create (repository → Settings → Secrets → Actions)

1. `EUDAMED_WATCHLIST` — the private watchlist JSON, same shape as
   `data/eudamed/watchlist.example.json` (that file contains only fictional
   entries). The workflow writes it to a temp file at runtime and fails with a
   clear error if the secret is missing or not valid JSON.
2. `EUDAMED_HMAC_KEY` — any long random string (for example
   `openssl rand -hex 32`). Optional but recommended; keep it stable, because
   changing it changes every device key and breaks per-device diff continuity.

## What it does per entry

For each watchlist entry (`label`, `trade_name_query`, optional
`manufacturer_contains`, `expected_srn`, `note`):

1. Pages through `GET /api/devices/udiDiData?tradeName=<query>` (page size 50,
   at most `--max-pages` pages, default 5, `--sleep` seconds between calls,
   default 1.0, User-Agent `ClinicOps-eudamed-watch/1.0 (+https://clinicops.dk)`).
2. Filters rows client-side by `manufacturer_contains` (case-insensitive
   substring of `manufacturerName`), because trade-name search is unanchored.
3. Dedupes rows by `basicUdi` and classifies each distinct device:
   `legacy_no_sscp_possible` (`B-` prefix; no detail lookup), `pr_no_sscp_duty`
   (SRN role `PR`; no detail lookup), otherwise one detail lookup per distinct
   `basicUdi` → `sscp_linked`, `sscp_expected_but_absent` (class III or
   implantable, MDR, not legacy, not PR — derived screening logic, not a
   compliance finding) or `sscp_link_absent`; a failed lookup is
   `lookup_failed`.
4. Aggregates everything into `data/eudamed/snapshots/<YYYY-MM-DD>.json`
   (sha256 of the canonical payload), writes
   `data/eudamed/diffs/<YYYY-MM-DD>.md` against the most recent earlier
   snapshot, and refreshes `data/eudamed/LATEST.md` — all aggregate-only.

API code values arrive as `{"code": "refdata.<group>.<value>"}` objects; the
tool normalises them (`class-iii`, `on-the-market`, `mdr`). Shapes were
verified against two real public responses on 2026-09-11; only a handful of
rows were seen, the parser tolerates missing keys, and an unrecognised shape
surfaces as null fields rather than an error.

## How to run

```bash
# live (read-only, polite); watchlist is a private, untracked local file
python scripts/eudamed_watch.py run --watchlist /path/to/private-watchlist.json --out data/eudamed/

# with stable pseudonymous device keys
EUDAMED_HMAC_KEY='<long random string>' python scripts/eudamed_watch.py run ...

# ALSO write the fully-named report locally (never commit; dir is gitignored)
python scripts/eudamed_watch.py run ... --full-out data/eudamed/full/

# offline dry run against the committed fixture (no network)
python scripts/eudamed_watch.py run --watchlist data/eudamed/watchlist.example.json \
  --out /tmp/eudamed --fetch-fixture tests/fixtures/eudamed_fixture.json --sleep 0

# diff two anonymised snapshots
python scripts/eudamed_watch.py diff data/eudamed/snapshots/A.json data/eudamed/snapshots/B.json

# tests
python -m pytest tests/test_eudamed_watch.py -q
```

Other flags: `--max-pages`, `--sleep`, `--timeout`, `--date YYYY-MM-DD`,
`--strict` (exit 1 on any recorded failure). `--fetch-fixture` reads
`{"responses": {"<url>": <body>}}`; `{"__error__": "..."}` or a missing URL
simulates a failed call.

The monthly workflow is `.github/workflows/eudamed-watch.yml` (cron
`17 6 1 * *`, plus `workflow_dispatch`). It writes the watchlist from the
secret, runs the tool with anonymised outputs, puts only the anonymised
LATEST.md in the job summary, and commits changes under `data/eudamed/` with a
bot identity. Open item: confirm the EUDAMED public-data reuse terms before
relying on scheduled live runs. Note: earlier git history contains named
outputs from the first live run; scrubbing history is a separate owner
decision.

## Limits block (written into every snapshot and markdown)

- Extraction date is stated on every output.
- Snapshot of what the public record shows; never a compliance/conformity
  statement about any named company.
- Committed outputs are aggregate-level and name no manufacturer, device,
  trade name, identifier or SS(C)P reference; per-device rows use pseudonymous
  HMAC keys.
- Trade-name search is a case-insensitive, unanchored substring match;
  unrelated devices are expected and filtered client-side by manufacturer.
- Zero results means "not findable under that string at that time", not
  "not registered".
- `totalElements` is unstable; counts are approximate and for display only.
- `pageSize` is capped at 50; coverage is bounded by `--max-pages` and
  truncation is flagged.
- `riskClass` / `legislation` query parameters are ignored by the API; risk
  class is taken from rows and filtered client-side.
- No Basic UDI-DI lookup endpoint exists; lookups go via a UDI-DI uuid; only
  identifiers and link metadata are retrievable, never SS(C)P content.
- `B-` basicUdi = legacy DI that structurally cannot carry an SS(C)P link
  (ClinicOps derived screening logic, not quoted Commission law).
- SRN role `PR` records carry no SS(C)P duty and are not looked up.
- `sscp_expected_but_absent` means no link was visible in the public record at
  extraction; it is not a finding that any obligation is unmet.
- Failures are recorded explicitly (as counts in public outputs); a device "no
  longer seen" next to recorded failures may be an extraction artefact.
