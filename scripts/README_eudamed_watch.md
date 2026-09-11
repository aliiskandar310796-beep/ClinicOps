# eudamed_watch — operator notes

`scripts/eudamed_watch.py` monitors the public EUDAMED JSON API for a watchlist
of trade names, writes a dated snapshot of what the public record shows, and
diffs it against the previous snapshot. Standard library only (no `requests`,
no PyYAML); the watchlist is JSON for that reason.

## Standing rule

Nothing this tool produces is a compliance, conformity or diligence statement
about any named company. Outputs record what the *public record showed* at the
extraction date and nothing more. Do not quote a snapshot, a diff or
`LATEST.md` as evidence that a manufacturer has, or has not, met an obligation.

## What it does

For each entry in `data/eudamed/watchlist.json`
(`label`, `trade_name_query`, optional `manufacturer_contains`, `expected_srn`, `note`):

1. Pages through `GET /api/devices/udiDiData?tradeName=<query>` (page size 50,
   at most `--max-pages` pages, default 5, with `--sleep` seconds between calls,
   default 1.0, User-Agent `ClinicOps-eudamed-watch/1.0 (+https://clinicops.dk)`).
2. Filters rows client-side by `manufacturer_contains` (case-insensitive
   substring of `manufacturerName`), because trade-name search is unanchored.
3. Dedupes rows by `basicUdi` (one family can occupy dozens of rows).
4. Classifies each distinct device:
   - `legacy_no_sscp_possible` — `basicUdi` starts with `B-` (legacy MDD/AIMDD
     EUDAMED-generated DI); no detail lookup.
   - `pr_no_sscp_duty` — SRN role `PR` (system/procedure pack producer); no
     detail lookup.
   - otherwise one detail lookup per distinct `basicUdi` via
     `GET /api/devices/basicUdiData/udiDiData/<uuid>` → `sscp_linked`
     (records `referenceNumber`, `revisionNumber`, `issueDate`, `validated`,
     `inactive`), `sscp_expected_but_absent` (see below) or `sscp_link_absent`;
     a failed lookup is `lookup_failed`. The detail also yields `legislation`
     (+ `legacyDirective`), `implantable`, NB decision reason/date and the
     first `deviceCertificateInfoList` entry's type and number.
   - `sscp_expected` (ClinicOps derived screening logic, MDR Art. 32
     population): (class III or implantable) and MDR (not a legacy directive)
     and not `B-` and not PR. Expected-but-absent means no link was *visible in
     the public record* at extraction; it is not a finding that an obligation
     is unmet.

API code values (`riskClass`, `deviceStatusType`, `legislation`, …) arrive as
`{"code": "refdata.<group>.<value>"}` objects; the tool records the raw code
and a normalised form with the prefix stripped (`class-iii`, `on-the-market`,
`mdr`). In the detail response `basicUdi` is an object; `basicUdi.code` is used
(string fallback kept).
5. Writes `data/eudamed/snapshots/<YYYY-MM-DD>.json` (UTC timestamp, tool
   version, per-entry results, approximate `totalElements`, explicit failure
   list, sha256 of the canonical payload), then
   `data/eudamed/diffs/<YYYY-MM-DD>.md` against the most recent earlier
   snapshot (new devices, devices no longer seen, SS(C)P link changes, status
   changes, classification changes) and refreshes `data/eudamed/LATEST.md`.

Failures are never skipped silently: every failed page or lookup is recorded in
the snapshot, `LATEST.md` and the run output. The exit code stays 0 unless
`--strict` is passed. A device "no longer seen" next to a recorded failure is
flagged as a possible extraction artefact.

## How to run

```bash
# live (read-only, polite)
python scripts/eudamed_watch.py run --watchlist data/eudamed/watchlist.json --out data/eudamed/

# useful flags
python scripts/eudamed_watch.py run ... --max-pages 5 --sleep 1.0 --timeout 30 --date 2026-09-11 --strict

# offline dry run against the committed fixture (no network)
python scripts/eudamed_watch.py run --watchlist data/eudamed/watchlist.json --out /tmp/eudamed \
  --fetch-fixture tests/fixtures/eudamed_fixture.json --sleep 0

# diff two snapshots
python scripts/eudamed_watch.py diff data/eudamed/snapshots/2026-09-01.json data/eudamed/snapshots/2026-10-01.json

# tests
python -m pytest tests/test_eudamed_watch.py -q
```

`--fetch-fixture` reads a JSON file shaped `{"responses": {"<url>": <body>}}`;
`{"__error__": "..."}` or a missing URL simulates a failed call.

Shape caveat: the listing and detail parsers were verified against two real
public responses on 2026-09-11 (one `tradeName=PALACOS` listing page and one
Basic UDI-DI detail for a PALACOS R+G row), plus one `tradeName=CERAMENT` page
that returned zero rows. Only a handful of rows were seen; other risk-class,
status and legislation code values, the `implantable` encoding on other
devices, and certificate entries with non-null numbers are extrapolated from
that sample. The parser tolerates missing keys, so an unrecognised shape shows
up as `sscp_link_absent` / null fields rather than an error — check the first
live snapshot by hand.

The monthly GitHub Actions workflow is `.github/workflows/eudamed-watch.yml`
(cron `17 6 1 * *`, also `workflow_dispatch`). It commits changed files under
`data/eudamed/` with a bot identity. Open item: confirm the EUDAMED public-data
reuse terms before relying on scheduled live runs.

## Limits block (written into every snapshot and markdown)

- Extraction date is stated on every output.
- Snapshot of what the public record shows; never a compliance/conformity
  statement about any named company.
- Trade-name search is a case-insensitive, unanchored substring match;
  unrelated devices are expected and filtered client-side by manufacturer.
- Zero results means "not findable under that string at that time", not
  "not registered".
- `totalElements` is unstable; counts are approximate and for display only.
- `pageSize` is capped at 50; coverage is bounded by `--max-pages` and
  truncation is flagged per entry.
- `riskClass` / `legislation` query parameters are ignored by the API; risk
  class is taken from rows and filtered client-side.
- No Basic UDI-DI lookup endpoint exists; lookups go via a UDI-DI uuid; only
  identifiers and link metadata are retrievable, never SS(C)P content.
- `B-` basicUdi = legacy DI that structurally cannot carry an SS(C)P link
  (ClinicOps derived screening logic, not quoted Commission law).
- SRN role `PR` records carry no SS(C)P duty and are not looked up.
- Failures are recorded explicitly; "no longer seen" next to a failure may be
  an extraction artefact.
