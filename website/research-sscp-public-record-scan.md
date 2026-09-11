<!-- claim-use: research-note -->
<!-- claim-ids: CO-CLM-0001,CO-CLM-0002,CO-CLM-0004,CO-CLM-0005,CO-CLM-0006,CO-CLM-0007,CO-CLM-0008,CO-CLM-0009,CO-CLM-0010,CO-CLM-0012,CO-CLM-0013,CO-CLM-0014,CO-CLM-0015,CO-CLM-0016,CO-CLM-0017 -->

# Research note — SS(C)P and the public EUDAMED record — deployment pack

Deployed page: `docs/research/sscp-public-record-scan/index.html` (canonical `https://clinicops.dk/research/sscp-public-record-scan/`). The body text below is the controlled source; the page copies it without changing any factual statement. It names no manufacturer and no device.

## SEO title

The published SS(C)P and the public EUDAMED record — what a reader can and cannot reconcile | ClinicOps

## Meta description

Public-source scan, September 2026: what a published SS(C)P and the public EUDAMED record can and cannot reconcile — identifiers, revisions, legacy DIs and pack records.

## Kicker

CLINICOPS · RESEARCH SUMMARY · SEPTEMBER 2026

## H1

The published SS(C)P and the public EUDAMED record — what a reader can and cannot reconcile

## Body

A public-source scan, September 2026

Terminology: MDR Article 32 says "summary of safety and clinical performance" (SSCP). "SS(C)P" is used here as the shorthand that also covers the IVDR Article 29 summary of safety and performance. Extraction date for every figure in this document: 8 September 2026. [CO-CLM-0001]

### What we did

Public sources only: manufacturers' openly published SS(C)P files, and the public EUDAMED device dataset read through its trade-name search and record-detail endpoints — read-only, no login, no scripted fetching. Three independently drawn convenience samples gave 69 device rows across roughly 42 manufacturers that publish national-language SS(C)Ps; candidates were found by searching the SS(C)P title phrase in Danish, Swedish, Norwegian, Finnish, German, Dutch, French and Spanish. For each row we compared the reference number, revision and Basic UDI-DI printed in the published document with what the EUDAMED record exposes. Separately, a systematic class III-restricted sample read 95 pages of the device listing at fixed intervals across the reachable part of the register (4,750 UDI-DI records examined; 213 class III rows collapsing to 98 distinct identifiers) and looked up the SS(C)P link on each distinct identifier. [CO-CLM-0016]

### What held up

1. **The published document and the registered record carry different identifiers.** In 22 consecutive rows of the second sample, not one published SS(C)P and EUDAMED record carried the same reference number and revision. In the three of those rows where EUDAMED held an SS(C)P at all, it held a different document reference from the published file. A reader therefore cannot use either artefact to validate the other, in either direction. [CO-CLM-0016]
2. **The join key fails in a minority of cases.** The Basic UDI-DI printed in the published SS(C)P did not match any Basic UDI-DI in EUDAMED in 6 of those 22 rows. The identifier that is meant to connect the document to the record is itself the thing that fails — a mechanism for the gap, not another symptom of it, and the single most checkable item on this list. [CO-CLM-0016]
3. **"Latest published" and "latest validated" are routinely different documents.** Several manufacturers print this themselves, in revision-history tables that mark the current published revision as not validated. Under MDCG 2019-9 a revision may legitimately be published between validation cycles, so this is not a defect; but where a published revision was never eligible to appear in EUDAMED, the two systems cannot agree by construction. Any comparison therefore has to separate "the record is behind" from "the published revision was never eligible", a distinction the public record cannot make on its own. [CO-CLM-0015]
4. **Where the SS(C)P is mandatory and the registration is a genuine MDR one, the public record was complete.** In the systematic class III sample, every one of the 17 Basic UDI-DIs registered by a manufacturer under the MDR carried a linked SS(C)P marked validated, with issue dates from January 2022 to August 2026. The absences sit elsewhere: 0 of 70 legacy registrations, which carry a EUDAMED DI rather than a Basic UDI-DI, and 0 of 11 system/procedure-pack records, where no SS(C)P duty falls on the pack producer. The gap in the public record is a transition gap, not a diligence gap. [CO-CLM-0002] [CO-CLM-0004] [CO-CLM-0014]

A related observation on language versions: in 5 of 7 multi-language document sets examined, the versions were identical across languages. Where they differed, the cause was structural rather than drift — some manufacturers issue each language version as its own controlled document, with its own reference number and its own revision counter, so the versions were never on a shared revision scale. [CO-CLM-0016]

### Why it matters now

MDCG 2026-4 assigns the upload of the SS(C)P — master and translations — to the manufacturer, a task that sat with the notified body, with deployment in production planned for October 2026 and uploads due no later than 27 February 2027 for devices placed on the market before mandatory use. Separately, following Commission Decision (EU) 2025/2371, legacy devices still on the market must be registered in EUDAMED by 28 November 2026. Both are dated events that will attach many more SS(C)Ps and Basic UDI-DIs to public records, and the reconciliation questions above are the ones a manufacturer meets while doing it. [CO-CLM-0008] [CO-CLM-0009] [CO-CLM-0010] [CO-CLM-0013]

### The one-glance rule

If the identifier in the Basic UDI-DI position of a EUDAMED record begins `B-`, it is a EUDAMED DI: the identifier EUDAMED assigns to a legacy device — one still on the market under a valid certificate issued under the earlier directives — in place of a Basic UDI-DI, built from the existing UDI-DI with `B-` prepended. In the systematic sample, 0 of 70 such records carried a linked SS(C)P. The identifier string alone tells you whether a currency check against the public record is possible, with no API call. [CO-CLM-0004] [CO-CLM-0002]

Stated as a derivation, because that is what it is: no Commission or MDCG guidance says this outright, and it is our reading rather than a stated Commission position. It follows from Article 32(2)(a) MDR, which requires the SS(C)P to state the Basic UDI-DI, and from the way MDCG 2026-4 describes the linkage — the notified body indicating the validated SS(C)P by ticking the box corresponding to the relevant Basic UDI-DI(s). A legacy record has no Basic UDI-DI to tick; the Commission's EUDAMED guidance states that for a legacy device "a EUDAMED DI will be assigned to the device instead of the Basic UDI-DI". [CO-CLM-0005] [CO-CLM-0012] [CO-CLM-0009] [CO-CLM-0004]

Check the actor role in the SRN as well. A record registered under a `PR` role (system and procedure pack producer) must carry the highest risk class among its constituent devices, so a class III value there is inherited. A person placing a pack on the market under Article 22(1) or (3) MDR is not thereby the manufacturer of the constituent devices, and Article 32 places the SS(C)P duty on the manufacturer; on our reading, no SS(C)P duty arises for the pack. Article 22(4) is the exception: a combination outside 22(1) and (3) is treated as a device in its own right, and the person assumes the obligations of a manufacturer. [CO-CLM-0015] [CO-CLM-0014]

### Limits

- **Convenience sample, not random.** EUDAMED has no "has an SS(C)P" filter and no Basic UDI-DI lookup, so candidates were found by searching SS(C)P title phrases. The `riskClass=` and `legislation=` query parameters are ignored by the public API (totals unchanged), so no filtered census is possible. None of the figures above are population rates; read them as "in a sample of 69 devices across ~42 manufacturers". [CO-CLM-0017]
- **The frames saturate.** The Nordic and German frames returned the same manufacturers within about a dozen searches. That biases the sample toward smaller firms that publish openly, and likely over-states the gap for the market as a whole. [CO-CLM-0016]
- **A zero-result trade-name search is not proof of absence.** It means "not findable under the trade name as printed"; the search is an unanchored substring match. [CO-CLM-0017]
- **Content is never retrievable.** The public record exposes only a reference number, revision, issue date and validated flag. "Match" means matching identifiers, never matching text. [CO-CLM-0016]
- **Revision schemes are often not comparable** between manufacturer and record; where they are not, the comparison falls back to issue dates.
- **Totals are unstable.** The same unfiltered query returned different `totalElements` values minutes apart; all counts are approximate. The systematic sample reads only the reachable lower ~47% of the listing — offset pages beyond roughly 30,000 time out — and pages are not independent, since class III rows arrive in single-manufacturer clusters. "17 of 17" is a clean signal in a small group, not a rate. [CO-CLM-0017] [CO-CLM-0006] [CO-CLM-0007]
- **A null SS(C)P link means "no SS(C)P visible in the public record"**, never "no SS(C)P exists". Nothing here is a compliance statement about any named company; this document uses aggregates only and names no manufacturer and no device.
- **Absence of a manufacturer from the sample is not evidence it publishes nothing.** Several were reached but offered request-only forms, model-number gates, or pages that redirect the reader to EUDAMED.
- **Extraction was performed by language-model agents reading JSON**, with every detail lookup cross-checked against the identifier and risk class it was fetched for (103 of 103 clean). Residual extraction error cannot be excluded. [CO-CLM-0016]

### What this is and isn't

The scan is cheap and repeatable: public endpoints, one afternoon, and it scales to a whole portfolio. The judgement — which differences matter, on what regulatory basis, and what to do about them — needs an accountable regulatory professional who reads the language of the document, and that judgement is not something this summary supplies.

## Footer line

ClinicOps · Ali Iskandar · info@clinicops.dk · clinicops.dk · September 2026 · This document reports what the public record showed on the extraction dates stated; it is not regulatory advice.
