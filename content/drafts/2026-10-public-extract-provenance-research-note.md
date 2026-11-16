DRAFT — requires user confirmation before publishing.
<!-- claim-use: research-note -->
<!-- claim-ids: CO-CLM-0017, CO-CLM-0016, CO-CLM-0006, CO-CLM-0011, CO-CLM-0007 -->

# Reading EUDAMED's public device data as evidence: a provenance minimum

## Why this note

Manufacturers, authorised representatives, importers, notified bodies and reviewers all check portfolios against EUDAMED's public data. An extract from a public interface is an observation made at a time, through a route, under that route's behaviour on that day. Without that context, gaps in the extract look like gaps in the register.

## What was observed (September 2026)

On the public EUDAMED device API in September 2026, the `riskClass=` and `legislation=` query parameters were ignored (totals unchanged); the same unfiltered query returned different `totalElements` values minutes apart; trade-name search was an unanchored substring match; no "has an SS(C)P" filter and no Basic UDI-DI lookup existed; and a systematic sample reached only the lower roughly 47% of the listing because offset pages beyond roughly 30,000 timed out [1]. The `udiDiData` route returned at most 50 records per page even when a larger page size was requested [2].

Reachability itself moved. On 8 September, probes around page 30,000 were consistently served while probes around page 32,000 consistently failed [3]. On 9 September, a single canary run served pages 0, 30,000 and 32,000 with HTTP 200 and 50 items each, so the apparent boundary did not reproduce [4]. Neither establishes full-register reachability.

Within the frame that was reached, the systematic class III sample read 95 listing pages (4,750 UDI-DI records), and 103 of 103 detail lookups cross-checked clean against the identifier and risk class they were fetched for [5].

## Four failure modes

1. **Silent filters.** A query that looks scoped to class III returns everything.
2. **Moving totals.** Two runs of "the same" query report different totals, and neither recorded the time.
3. **Partial reach presented as census.** An extract that stops where pages stop being served is called "the register".
4. **Absence read as a finding.** A device not found by substring search, or an SS(C)P not seen in the reachable data, is treated as non-compliance. Missing public metadata is never, by itself, a finding.

## A provenance minimum

Every extract should carry: the route and the full query as sent; the timestamp (UTC); the total the interface reported and the number of records actually retrieved; the deepest page reached and every page that failed; any filter applied after retrieval rather than trusted to the query; a cross-check sample of detail lookups with its result; and a plain statement of what the extract cannot show.

A reviewer can then tell "not in our extract" from "not in the register"; an extract can only establish the first.

## Boundaries

Sample design: one systematic sample of listing pages within the reachable frame, plus convenience samples; aggregates only; no manufacturer or device named. Unresolved: the upper part of the listing was not reached in the systematic sample. These are dated observations of public interfaces, not service guarantees; re-test before reliance. They say nothing about any named party's compliance, conformity or CE marking.

---
Footnotes (source verification)

[1] CO-CLM-0017 (qualified, observation). Read at source on `main` (6edb5b2), `website/research-sscp-public-record-scan.md` l.57: "The `riskClass=` and `legislation=` query parameters are ignored by the public API (totals unchanged), so no filtered census is possi[ble]…" and "EUDAMED has no \"has an SS(C)P\" filter and no Basic UDI-DI lookup". Limitations carried: point-in-time behaviour, not a service contract; the deep-offset boundary did not reproduce on 9 Sep 2026 and is not stated as stable; counts approximate; no full-register coverage implied.
[2] CO-CLM-0007 (qualified, observation). Source: `research/corrections/2026-09-08-headline-reversal.md`; corroborated by `research/corrections/2026-09-09-api-reachability-update.md` l.35: "50 records were returned at each requested page size of 50". Limitation carried: observed behaviour; re-test before operational reliance.
[3] CO-CLM-0006 (qualified, observation). Read at source, `research/corrections/2026-09-09-api-reachability-update.md` l.7: "On 8 September 2026, ClinicOps repeatedly observed the public `udiDiData` route serving around page 30,000 while probes around page 32,000 failed." Limitation carried: must not be treated as stable (l.28, l.40: "Do not publish a fixed statement such as `the public API becomes inaccessible above page 30,000`").
[4] CO-CLM-0011 (qualified, observation). Read at source, same file, table l.22–24 (pages 0 / 30,000 / 32,000: HTTP 200, 50 items each); run https://github.com/aliiskandar310796-beep/ClinicOps/actions/runs/34352492799. Limitation carried: a single bounded run from one network context.
[5] CO-CLM-0016 (qualified, observation). Read at source, `website/research-sscp-public-record-scan.md` l.65: "every detail lookup cross-checked against the identifier and risk class it was fetched for (103 of 103 clean). Residual extraction error cannot be excluded." Also `research/corrections/2026-09-08-headline-reversal.md` l.7: "95 pages, 4,750 UDI-DI records". Limitations carried: convenience and reachable-frame samples, not population rates; extraction by language-model agents.

The four failure modes and the provenance minimum are an editorial method derived from these observations and CLAIM_RULES rules 5, 7 and 8; they are not a Commission position.
