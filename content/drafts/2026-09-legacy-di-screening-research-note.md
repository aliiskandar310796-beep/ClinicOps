DRAFT — requires user confirmation before publishing.
<!-- claim-use: research-note -->
<!-- claim-ids: CO-CLM-0004, CO-CLM-0005, CO-CLM-0013, CO-CLM-0017, CO-CLM-0011 -->

# The B-prefix as a screening signal, not a finding: reading legacy-device identifiers before 28 November 2026

## Why this note

The Commission's EUDAMED transition timeline gives 28 November 2026 as the deadline to register, in the UDI/Devices module, devices already on the market before mandatory use (following Commission Decision (EU) 2025/2371; the Decision itself does not print the date, and whether a device is a legacy device is the manufacturer's determination) [1]. Anyone reconciling a portfolio against the public record between now and then will meet identifiers that do not look like Basic UDI-DIs. This note records what such an identifier does and does not tell a reviewer.

## The structure (primary)

For EUDAMED legacy-device identification, an EUDAMED DI uses the `B-` prefix and stands in place of a Basic UDI-DI for the legacy registration model [2]. The prefix is an identifier convention documented by the Commission's EUDAMED Information Centre. It is not, on its own, a statement about the device's regulatory status, certificate, or documentation.

## The screening rule (derivation)

ClinicOps treats a B-prefixed EUDAMED DI as a screening signal that the legacy registration is not the MDR Basic UDI-DI linkage target described for SS(C)P handling [3]. This is a ClinicOps derivation from observed system behaviour, consistent with CLAIM_RULES.md rule 3: a B-prefix / legacy screening rule is a derivation unless a primary source states the exact consequence being claimed. The Commission pages document the identifier structure; they do not state the downstream SS(C)P consequence.

## What follows for a reviewer

1. A `B-` record is routed to "legacy registration — expected to be re-registered in the UDI/Devices module by the Commission's deadline", not to "missing SS(C)P" and not to "non-compliant". Missing public metadata is never, by itself, a compliance finding.
2. The comparison runs from the manufacturer's authoritative device list to the public record, one expected record per device. Rows with no match are "missing evidence" until a qualified person resolves them.
3. The public API cannot be used to establish coverage. In September 2026 ClinicOps observed that the `riskClass=` and `legislation=` parameters were ignored, totals changed minutes apart, trade-name search is an unanchored substring match, and no Basic UDI-DI lookup exists [4]. A bounded probe never supports a full-register statement.
4. Observed API behaviour is point-in-time. The deep-offset time-out seen on 8 September 2026 did not reproduce on 9 September, when pages 0, 30,000 and 32,000 of the `udiDiData` route all returned HTTP 200 with 50 items [5]. Record the date with every observation.

## Boundaries

Sample designs used by ClinicOps to date are convenience and reachable-frame samples, aggregates only, naming no manufacturer and no device. "Match" means identifiers align; document bodies were not compared. This note makes no statement about any named party's registration, conformity or CE marking.

---
Footnotes (source verification)

[1] CO-CLM-0013 (qualified, primary). Sources: https://eur-lex.europa.eu/eli/dec/2025/2371/oj · https://health.ec.europa.eu/medical-devices-eudamed/overview_en. Limitation honoured: Commission figure only; 27 November framing not cited alongside it.
[2] CO-CLM-0004 (verified, primary): "For EUDAMED legacy-device identification, an EUDAMED DI uses the B- prefix and stands in place of a Basic UDI-DI for the legacy registration model." Sources: Commission EUDAMED Information Centre legacy-device identification pages (see PRIMARY_SOURCES.md, "Legacy-device identifiers").
[3] CO-CLM-0005 (qualified, derivation): "ClinicOps treats a B-prefixed EUDAMED DI as a screening signal that the legacy registration is not the MDR Basic UDI-DI linkage target described for SS(C)P handling…" Labelled as derivation in the body, as required.
[4] CO-CLM-0017 (qualified, observation). Sources: website/research-sscp-public-record-scan.md; research/corrections/2026-09-08-headline-reversal.md; 2026-09-09-api-reachability-update.md.
[5] CO-CLM-0011 (qualified, observation): GitHub Actions canary run 34352492799 — raw job log re-verified 2026-09-26: `{"page": 0, "requested_page_size": 50, "ok": true, "status_code": 200, … "returned_items": 50, "total_elements": 3394504}` and identically for pages 30000 and 32000.

Verification note (2026-09-29 run): live re-fetch of EUR-Lex, health.ec.europa.eu and webgate.ec.europa.eu refused twice (PROVENANCE_REQUIRED). Registry claim texts quoted; last at-source checks: 2026-09-26 (CO-CLM-0011 raw log), 9 September 2026 (PRIMARY_SOURCES.md). Re-verify at source before publishing.
