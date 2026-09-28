# Production Surface

Status: CURRENT as of 2026-09-28. This file records operating invariants; generated artifacts remain the source of truth for transient counts.

## Public production surface

`clinicops.dk` is served from `docs/**` via GitHub Pages. GoDaddy is DNS only. HTTPS is enforced.

Current production before this indexing release: `4059bdaae1721eb3517b095064b636fd818db917`, with CI, Integrity Gate, CodeQL and Pages deployment green.

Public identity is deliberately narrow:

- **ClinicOps — EU MedTech Regulatory Data Integrity**
- flagship: **Regulatory Change Integrity Review**
- low-friction entry: **Portfolio Integrity Scan**
- recurring extension: monitoring only where repeated real drift warrants it
- secondary specialist capabilities: Denmark market access / Danish localisation and Danish pharmacovigilance

Broad clinical-operations lanes remain archived.

### Browser-local acquisition path

`public site / research / free tool / specimen → browser-local scope brief → user's email client → controlled private scope/intake`

No first-party analytics or tracking runtime is introduced by default. Browser-local tools remain local unless a page explicitly states otherwise.

## Search / indexing

Canonical sitemap:

`https://clinicops.dk/sitemap.xml`

This release intentionally reduces the sitemap from 38 discoverable URLs to **22 canonical index targets**. Support utilities, privacy/intake pages, specimens and legacy URLs remain accessible but carry `noindex,follow` and are excluded from the generated sitemap.

The canonical index set concentrates search authority on:

- company / solution / use-case pages;
- the flagship review;
- the main Scanner;
- high-value MedTech use cases;
- primary-source and research pages.

Legacy `evidence-change-control-pack.html` and `what-a-pilot-looks-like.html` are retained only as `noindex` move notices pointing to `regulatory-change-integrity-review.html`.

External search can still surface the obsolete 2025 Danish clinic-compliance homepage and duplicate LinkedIn company identities even though the live origin is current. Treat that as an external indexing/entity-resolution defect, not a DNS/origin defect.

Authoritative Google indexing state must be read from Search Console when an authenticated route is available. Do not reuse historical indexed-page counts as current evidence. Sitemap acceptance, crawling, indexing, impressions and qualified commercial discovery are separate facts.

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

