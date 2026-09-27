# Production Surface

Status: CURRENT as of 2026-09-27. This file records operating invariants and verified production architecture. Generated artifacts remain the source of truth for transient counts.

## Public production surface

`clinicops.dk` is served from `docs/**` via GitHub Pages. GoDaddy is DNS only. HTTPS is enforced.

Current production release: `b956b85def6b3bd6bbabb974e8fae4a1234c4567` (merged PR #82). Main CI, Integrity Gate, CodeQL and the Pages deployment all passed for this SHA. The post-deploy live smoke fetched the homepage, sitemap, robots and every critical production page through `https://clinicops.dk/` successfully.

The deterministic sitemap is the canonical list of indexable production URLs — derive it, do not hard-code it in operational logic. Source of truth: `docs/sitemap.xml`, generated and checked by `scripts/render_sitemap.py --check`. As of this reconciliation it contains 38 URLs.

Public architecture is now deliberately narrow:

- company identity: **EU MedTech Regulatory Data Integrity**;
- flagship: **Regulatory Change Integrity Review**;
- low-friction entry: **Portfolio Integrity Scan**;
- recurring extension: **Continuous Portfolio Integrity Monitoring** only as real recurrence warrants it;
- public utilities: Regulatory Integrity Scanner, Identifier Check and bounded supporting tools;
- secondary specialist lanes: Denmark market access / Danish localisation and Danish pharmacovigilance.

EUDAMED, UDI, certificates, SS(C)P, Class III/implantable transition, authorised-representative portfolios, controlled documents and language versions are use cases of one discipline, not separate company identities.

Broad clinical-operations lanes are archived from the public architecture. Do not reintroduce TrialOps, LabOps, Clinic Operations, Clinical AI Ops, generic QualityOps or a multi-lane services portfolio without new buyer evidence and explicit strategy change.

Do not mass-produce thin SEO pages while current production pages are still being discovered.

### Browser-local acquisition path

Current low-infrastructure path:

`public site / research / free tool / sanitized sample → browser-local assessment brief → user's email client → controlled private scope/intake`

`docs/assessment-intake.html` has no backend form action, analytics, tracking, `fetch`, XHR, `sendBeacon` or WebSocket submission. User input stays local until the user explicitly creates an email draft to `info@clinicops.dk`.

Optional `src`, `campaign` and `segment` URL parameters remain local and are included in the generated scope brief only when the visitor explicitly creates the draft. ClinicOps receives them only if the visitor chooses to send that email. Keep this attribution model privacy-preserving unless Ali explicitly approves a privacy-posture change.

The Readiness Score → assessment handoff may use one-shot tab-scoped `sessionStorage` containing bounded screening context only; do not use browser storage for client-confidential evidence.

Keep the EUDAMED Identifier Check and core integrity utilities free.

## Search / indexing

Canonical sitemap:

`https://clinicops.dk/sitemap.xml`

Robots:

`https://clinicops.dk/robots.txt`

Verified 2026-09-27 production facts:

- live `clinicops.dk` serves the current GitHub Pages build and passes post-deploy smoke;
- sitemap and robots both return HTTP 200 in the live smoke;
- external search/index caches can still surface the obsolete 2025 Danish clinic-compliance homepage and duplicate LinkedIn identities;
- therefore the current P0 discoverability problem is **stale/fragmented external indexing and entity resolution**, not the live origin;
- the canonical LinkedIn company identity referenced by website structured data is `https://www.linkedin.com/company/clinicops-dk/`;
- the older `clinicops-danish-regulatory` company page remains externally indexable and should be retired, redirected or made clearly non-canonical through LinkedIn account administration when access permits.

Search Console property access was previously verified, but the currently installed GSC Wizard connector is blocked behind its own expired subscription and is not authoritative evidence of present GSC state. Do not repeat old 7/16/19/29 URL counts or obsolete sitemap status as current facts.

Required next indexing work when direct Search Console access is available:

1. inspect the `https://clinicops.dk/` property;
2. verify `https://clinicops.dk/sitemap.xml` is the active submitted sitemap;
3. inspect indexed/non-indexed counts and reasons;
4. inspect canonical selection for priority URLs;
5. request recrawl/indexing only where appropriate;
6. remove obsolete sitemap submissions only after verifying the current sitemap is accepted.

Sitemap acceptance, crawlability, indexing, impressions and qualified commercial discovery are separate facts.

## EUDAMED Watch — PRs #39–#41

Workflow: `.github/workflows/eudamed-watch.yml`.

Trigger surface is intentionally narrow:

- manual `workflow_dispatch`;
- monthly schedule `17 6 1 * *`;
- **no push trigger**.

### Hard public anonymisation invariant

Nothing committed under watcher outputs, and nothing printed to public CI logs, may identify a manufacturer, device, trade name, Basic UDI-DI or SS(C)P reference.

Current design:

- real watchlist only in private `EUDAMED_WATCHLIST` secret;
- optional stable pseudonymous keys use truncated HMAC-SHA256 under `EUDAMED_HMAC_KEY`;
- committed outputs are aggregate-only or pseudonymous;
- named output only via local/private `--full-out DIR`;
- `--max-pages 8`;
- leak-assertion tests are governance controls: fix code, never loosen the test.

Zero rows means “not findable under the tested string at that time”, never “not registered”. Missing public SS(C)P links are not evidence of non-compliance.

Current Public API use remains bounded GET-only, identifying User-Agent, one-second spacing and finite page cap. Re-review on endpoint/term changes, repeated 403/429, materially increased request volume or publication of raw named records. Never evade restrictions with proxies/identity rotation.

### SS(C)P Playground workflow evidence — PR #44

Commission Playground/help v3.31.2 documents manufacturer-side SS(C)P workflow concepts including new records, Basic UDI-DI linking, versions/master documents and translations. Treat this as Playground/help evidence, **not proof that planned Production deployment has already occurred**.

## Privacy / claim governance

`https://clinicops.dk/privacy-notice/` is a production invariant.

Current posture:

- static GitHub Pages;
- no ClinicOps cookies;
- no analytics/tracking runtime;
- browser-local tools;
- sitemap-wide privacy-link visibility.

Do not add analytics/tracking or materially change privacy posture without Ali's explicit approval plus corresponding notice/contract updates.

Canonical claim controls include:

- `research/claims.jsonl`;
- `src/clinicops_eudamed/claim_guard.py`;
- `src/clinicops_os/claim_registry.py`;
- governed external-profile/claim records where present.

Preserve these boundaries:

- missing/null public SS(C)P link ≠ non-compliance;
- do not imply complete EUDAMED public-register/API coverage;
- B-prefix output is structural screening only;
- preserve MF / AR / IM / PR roles;
- do not present non-binding recommendations as statutory deadlines;
- deterministic scores are operator triage, not regulatory/compliance/legal/safety risk scores;
- nothing external introduces ungoverned factual claims outside verified claim/profile controls.

Corrected thesis: sampled MF-role MDR Class III registrations had linked validated SS(C)P metadata; the opportunity is transition/document-operations workload, evidence control and reconciliation—not a generic manufacturer diligence-failure allegation.

