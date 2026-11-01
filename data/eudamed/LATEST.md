# EUDAMED watch — latest snapshot (aggregate)

- Snapshot date: 2026-11-01
- Extracted at (UTC): 2026-11-01T13:24:50+00:00
- Tool: eudamed_watch 1.0.0 (mode: live)
- Snapshot sha256: `0cf22ab7f2259263c2ee71601800a57251ee7278409b681a8244887670e6a627`
- Anonymisation: aggregate+keyed
- Recorded failures: 24 (detail_lookup=15, search_page=9)
- Diff against previous snapshot: diffs/2026-11-01.md

Committed outputs are aggregate-level only and are designed to contain no string identifying a manufacturer, device, trade name, identifier or SS(C)P reference. Per-device rows, where present, are keyed by a truncated HMAC-SHA256 of the Basic UDI-DI under a private key and carry only classification-level fields.

## Totals

| Measure | Value |
|---|---|
| Watchlist entries queried | 14 |
| Search pages fetched | 25 |
| Search pages failed | 9 |
| Rows seen (all entries) | 1076 |
| Rows filtered out client-side | 161 |
| Distinct devices (deduped) | 255 |
| Entries truncated by page cap | 1 |
| Entries with zero rows | 8 |

## Classification counts (all entries combined)

- legacy_no_sscp_possible: 220
- lookup_failed: 15
- pr_no_sscp_duty: 5
- sscp_expected_but_absent: 2
- sscp_link_absent: 3
- sscp_linked: 10

## Standing limits

- Extraction date: 2026-11-01.
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
