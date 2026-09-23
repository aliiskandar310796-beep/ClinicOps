# Production Surface

> Migrated verbatim from the pre-2026-09-23 `AGENT_STATE.md` monolith as part of the connectome-lens shard proposal (draft, not yet reconciled against live `main`). Content below this line is unedited from the original section.

## Public production surface

`clinicops.dk` is served from `docs/**` via GitHub Pages. GoDaddy is DNS only. HTTPS is enforced.

The deterministic sitemap is the canonical list of production URLs — **derive it, do not hard-code it here** (this file previously said 16 while production had 29; transient counts belong in generated artifacts, not shared state). Source of truth: `docs/sitemap.xml`, generated and checked by `scripts/render_sitemap.py --check` (29 URLs as of 2026-09-17). The public surface spans the umbrella home, the three lanes (Denmark market access, MedTech/regulatory, clinical operations), the specialist service pages, tools, research, specimens, expert network, about/contact and privacy.

Do not mass-produce thin SEO pages while current production pages are still being discovered.

### Browser-local acquisition path

Current low-infrastructure path:

`public site / free tool / sanitized sample → browser-local assessment brief → user's email client → controlled private scope/intake`

`docs/assessment-intake.html` has no backend form action, analytics, tracking, `fetch`, XHR, `sendBeacon` or WebSocket submission. User input stays local until the user explicitly creates an email draft to `info@clinicops.dk`. The page warns against patient-identifiable data.

The Readiness Score → assessment handoff uses one-shot tab-scoped `sessionStorage` containing score/band/gaps/timestamp only; no company/customer data.

Keep the EUDAMED Identifier Check and Transition Readiness Score free.

## Search / indexing

Production canonical sitemap:

`https://clinicops.dk/sitemap.xml`

Fresh GSC verification on 2026-09-13 confirms the Search Console property `https://clinicops.dk/` exists and is connected. The obsolete submitted sitemap `https://clinicops.dk/sitemap.website.xml` reports 7 submitted URLs, 0 indexed URLs, 1 warning and 1 error.

Issue #28 tracks the actual action: submit the current 16-URL `sitemap.xml`, confirm acceptance/fetch, diagnose warning/error state and remove the obsolete entry only if appropriate afterward. Sitemap acceptance and indexing are separate facts.

The canonical sitemap itself is fetchable and contains the expected 16 URLs. Do not modify healthy XML merely because the obsolete GSC submission is red.

No current connector can submit the sitemap into the GSC UI; this remains a manual browser action.

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

