<!-- claim-use: research-note -->
<!-- claim-ids: CO-CLM-0001,CO-CLM-0004,CO-CLM-0005,CO-CLM-0008,CO-CLM-0009,CO-CLM-0010,CO-CLM-0013,CO-CLM-0017 -->

# Method page — continuous monitoring of the public EUDAMED record — deployment pack

Deployed page: `docs/research/eudamed-watch/index.html` (canonical `https://clinicops.dk/research/eudamed-watch/`). The page copies the body below; it names no manufacturer and no device, and describes the method only at the level of "automated, read-only, polite to the public API".

## SEO title

Continuous monitoring of the public EUDAMED record | ClinicOps

## Meta description

How ClinicOps continuously monitors the public EUDAMED record: monthly versioned snapshots of SS(C)P linkage for a private watchlist, diffed, aggregates only.

## Body

### What it does

ClinicOps runs a monthly automated snapshot of what the public EUDAMED record shows for a private watchlist of devices: whether each registration carries a linked SS(C)P, its validation flag and issue year, and how each record is classified — a genuine MDR registration, a legacy registration identified by its `B-` EUDAMED DI, or a system/procedure-pack record. [CO-CLM-0004] Each snapshot is versioned and diffed against the previous one, so what changed in the public record between runs — a link appearing, a revision moving, a registration vanishing from search — is recorded rather than remembered. Published results are aggregate-level only: counts and changes, never names, identifiers or document references.

### Why now

MDCG 2026-4 describes a revised EUDAMED operating model in which the manufacturer uploads the SS(C)P master and translations, while the notified body indicates the validated SS(C)P against the relevant Basic UDI-DI(s) — with production deployment planned for October 2026 and uploads recommended no later than 27 February 2027 for devices placed on the market before mandatory use. [CO-CLM-0008] [CO-CLM-0009] [CO-CLM-0010] Separately, following Commission Decision (EU) 2025/2371, legacy devices still on the market must be registered in EUDAMED by 28 November 2026. [CO-CLM-0013] Many more SS(C)Ps and Basic UDI-DIs will attach to public records in a short window, and the public record will move under any portfolio that is not watching it. Under MDR Article 32(1) the manufacturer is the duty holder for drawing up the SSCP for applicable implantable and class III devices, subject to the Article 32 exclusions — the monitoring watches the public trace of that work, not the work itself. [CO-CLM-0001]

### Method

Automated, read-only, and polite to the public API: bounded page counts, spaced requests, an identifying agent string, no login, no scraping of anything beyond the public JSON record. Records are deduplicated by Basic UDI-DI; legacy `B-` identifiers are treated as structurally unable to carry an SS(C)P link, as ClinicOps derived screening logic rather than quoted Commission law. [CO-CLM-0005] Every failed request is recorded, never silently skipped, so a record "no longer seen" next to a failure is flagged as a possible extraction artefact rather than a registry change.

### Standing limits

- This monitors the public record only. It is never a compliance, conformity or diligence statement about any named company, and its outputs must not be quoted as one.
- Trade-name search on the public API is a case-insensitive, unanchored substring match; zero results means "not findable under that string at that time", not "not registered". [CO-CLM-0017]
- Counts returned by the public API are unstable and are treated as approximate, display-only figures; the API's risk-class and legislation query filters are ignored server-side, so classification is done client-side. [CO-CLM-0017]
- SS(C)P content is never retrievable through the public API — only a reference number, revision, issue date and validation flag. A "link" is metadata, not text.
- A null SS(C)P link means "no SS(C)P visible in the public record", never "no SS(C)P exists".

### Portfolio monitoring as a service

The same monitoring can run against a manufacturer's or authorised representative's own portfolio, with the named detail delivered privately and reviewed by an accountable regulatory professional. Contact info@clinicops.dk.
