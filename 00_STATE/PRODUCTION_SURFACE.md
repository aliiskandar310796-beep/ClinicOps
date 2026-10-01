# Production Surface

Reconciled against live `main` on 2026-09-29 (supersedes the pre-2026-09-23 monolith copy, which described an obsolete three-lane site, a 16/29-URL sitemap and a `sitemap.website.xml` submission). Sections from *EUDAMED Watch* onward are unchanged.

## Public production surface

`clinicops.dk` is served from `docs/**` via GitHub Pages. GoDaddy is DNS only. HTTPS is enforced. Deploys run from `.github/workflows/pages.yml` for the exact SHA after workflow "CI" succeeds on `main`, followed by `scripts/check_live_site.py`. CDN and browser caching can show stale content for a short time after a deploy.

### Architecture (current)

The site tells one story: **EU MedTech regulatory data integrity** — keep EUDAMED, UDI, certificates, SS(C)P and controlled records aligned when products change, with source-linked exception queues for qualified human review. Positioning source of truth: `01_STRATEGY/POSITIONING_2026-09-18_REGULATORY_DATA_INTEGRITY.md`. Denmark market access, Danish localisation and pharmacovigilance are secondary specialist capabilities, not separate lanes. The old clinical-operations lane is retired; `docs/clinical-operations.html` is a `noindex` move notice pointing at `/services`.

Page families (see the sitemap for the authoritative list): home; Solution (`/services`, flagship `/evidence-change-control-pack`, `/what-a-pilot-looks-like`, `/integrity-gate`); Use cases (EUDAMED, Class III transition, SS(C)P operations, AR portfolio intelligence, Denmark, document control, regulatory intelligence); Research and primary sources; Tools hub and the Integrity Scanner; About, Contact, Expert network, Privacy.

The expert network (PR #90, `src/clinicops_os/expert_network.py`) is part of the public surface only as `/expert-network` (governed description) and the noindex interest form. The real expert roster is private and never committed here.

### Sitemap and index policy

The sitemap is the canonical list of primary, indexable URLs — **derive it, do not hard-code counts here**. Source of truth: `docs/sitemap.xml`, generated and checked by `scripts/render_sitemap.py --check`, which already skips any page marked `noindex`. As of 2026-09-29 it holds 24 URLs.

Support utilities are served and linked but are `noindex,follow` and out of the sitemap: assessment intake, the calculators and checkers, the specimen register, the sanitized Transition Map sample, and the expert-interest form. The exact set is pinned in `tests/test_strategic_invariants.py` (`NOINDEX_SUPPORT_SET`), and `validate_noindex_pages` in `src/clinicops_os/site_quality.py` fails the build for any page that is neither in the sitemap nor `noindex` (redirect stubs and `404.html` exempt). `SITEMAP_URL_CEILING` in the same test file is the growth guard; raising it is a deliberate decision, not a side effect.

Do not mass-produce thin SEO pages while current production pages are still being discovered.

### Browser-local acquisition path

Current low-infrastructure path:

`public site / free tool / sanitized sample → browser-local assessment brief → user's email client → controlled private scope/intake`

`docs/assessment-intake.html` has no backend form action, analytics, tracking, `fetch`, XHR, `sendBeacon` or WebSocket submission. User input stays local until the user explicitly creates an email draft to `info@clinicops.dk`. The page warns against patient-identifiable data.

The Readiness Score → assessment handoff uses one-shot tab-scoped `sessionStorage` containing score/band/gaps/timestamp only; no company/customer data.

Keep the EUDAMED Identifier Check and Transition Readiness Score free.

## Search / indexing

Production canonical sitemap: `https://clinicops.dk/sitemap.xml` (advertised in `docs/robots.txt`).

Google Search Console (read via the Windsor.ai `searchconsole` connector, which exposes analytics and sitemap status only): property `https://clinicops.dk/` is connected. Observation on 2026-09-20: `sitemap.xml` last submitted 2026-09-17, last downloaded 2026-09-20 with 33 submitted URLs (the pre-cut count); only the homepage had impressions. The submitted count will fall to the current sitemap on the next fetch. Sitemap acceptance and indexing are separate facts; do not read either as a ranking claim.

The obsolete `sitemap.website.xml` submission and Issue #28 are historical. No connector can submit a sitemap, inspect URLs or request indexing in the GSC UI — those stay manual account-admin actions for Ali, and recrawl requests should follow only after live correctness is verified. Do not modify healthy XML merely because a GSC report is red.

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

## Autonomy Gate — 2026-09-25

Workflow: `.github/workflows/autonomy-gate.yml` (name `Autonomy Gate`). Triggers: `push` and `pull_request` limited by `paths` to `autonomy/**`, `src/clinicops_os/autonomy/**`, the autonomy/termbase/backup-manifest tests, `data/termbase/**`, `pyproject.toml` and the workflow itself, plus `workflow_dispatch`. **No schedule.** `permissions: contents: read`, `concurrency: clinicops-autonomy-gate`, `timeout-minutes: 8`, Python 3.11. Steps: focused pytest, Ruff, `clinicops-termbase validate` and `qa` on `data/termbase/termbase_public.csv`, `clinicops-autonomy-jobs list`, `clinicops-autonomy-policy selftest`.

The Tier-0 jobs themselves are claude.ai scheduled tasks (see `autonomy/README.md`); they are not part of the GitHub Actions surface. Their public-safe outputs reach the repository only as pull requests (`autonomy/<topic>-<date>` branches) and pass the existing CI gates like any other change. `data/termbase/termbase_public.csv` is the only new committed data surface; it holds public-source rows only.

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

