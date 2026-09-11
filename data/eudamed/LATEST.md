# EUDAMED watch — latest snapshot (aggregate)

- Snapshot date: 2026-09-11
- Extracted at (UTC): 2026-09-11T21:32:34+00:00
- Tool: eudamed_watch 1.0.0 (mode: live)
- Snapshot sha256: `3e90f54fa7b32cff3941d2cebb80c8ea06b7e690ae764f748e9a5e1572c23ab2`
- Anonymisation: aggregate+keyed
- Recorded failures: 0
- Diff against previous snapshot: none (first snapshot)

Committed outputs are aggregate-level only and are designed to contain no string identifying a manufacturer, device, trade name, identifier or SS(C)P reference. Per-device rows, where present, are keyed by a truncated HMAC-SHA256 of the Basic UDI-DI under a private key and carry only classification-level fields.

## Totals

| Measure | Value |
|---|---|
| Watchlist entries queried | 14 |
| Search pages fetched | 35 |
| Search pages failed | 0 |
| Rows seen (all entries) | 1235 |
| Rows filtered out client-side | 521 |
| Distinct devices (deduped) | 147 |
| Entries truncated by page cap | 0 |
| Entries with zero rows | 2 |

## Classification counts (all entries combined)

- legacy_no_sscp_possible: 97
- pr_no_sscp_duty: 1
- sscp_expected_but_absent: 9
- sscp_link_absent: 28
- sscp_linked: 12

## Standing limits

- Extraction date: 2026-09-11.
- This is a snapshot of what the public EUDAMED record showed at the extraction date. It is not a compliance, conformity or diligence statement about any named company, and must not be quoted as one.
- Trade-name search is a case-insensitive, unanchored substring match. Results can include unrelated devices; rows are filtered client-side by manufacturer_contains where configured.
- Zero results means 'not findable under that search string at that time', not 'not registered'.
- totalElements counts returned by the API are unstable and are reported as approximate; they are for display only.
- pageSize is capped at 50 by the API; page coverage is bounded by --max-pages, so long result lists may be truncated (flagged per entry).
- riskClass/legislation query parameters are ignored by the API; risk class is taken from each row and filtering is client-side.
- No Basic UDI-DI lookup endpoint exists; detail lookups go through a UDI-DI uuid. Only identifiers and link metadata are retrievable; SS(C)P content is never retrievable through this API.
- A basicUdi starting with 'B-' is a legacy (MDD/AIMDD) EUDAMED-generated DI that structurally cannot carry an SS(C)P link (ClinicOps derived screening logic, not quoted Commission law).
- SRN role PR (system/procedure pack producer) records carry no SS(C)P duty and are not looked up.
- Committed snapshots, diffs and LATEST.md are aggregate-level only: they name no manufacturer, device, trade name, identifier or SS(C)P reference. Per-device rows, where present, use pseudonymous HMAC keys.
- sscp_expected is ClinicOps derived screening logic (class III or implantable, MDR, not legacy, not PR). 'sscp_expected_but_absent' means no SS(C)P link was visible in the public record at extraction; it is not a finding that any obligation is unmet.
- Failed pages and lookups are recorded explicitly; a device 'no longer seen' next to a recorded failure may be an extraction artefact, not a registry change.
