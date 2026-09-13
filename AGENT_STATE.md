# ClinicOps shared agent state

Last reconciled: 2026-09-13 after PR #46 and fresh GitHub / Search Console verification.

## Canonical truth

GitHub `main` is the shared source of truth. Fetch current `main` before work, inspect open PRs/branches, preserve concurrent Claude/ChatGPT work, and never force-overwrite a newer change. Chat transcripts, local copies and project-side control files are secondary until their changes land here.

Do **not** hard-code a self-referential “current main SHA” in this file: its own merge changes `main`. The verified baseline immediately before this refresh was `089ccb13105ed557b2a0828bc8cc277c9e4b13d6`; the content tree at that point was identical to PR #46’s merged tree after an accidental placeholder file was created and immediately removed. PR #46 merge SHA `3dd9516538ebfc4e814eadc5d0fb4c2b43d07de2` passed exact-main CI. Always fetch the live SHA again before acting.

## Current business thesis

ClinicOps is an evidence-controlled, human-reviewed operating layer for high-value expert work. The current commercial beachhead is MDR / EUDAMED transition operations, especially Class III / implantable portfolios.

The **Class III Transition Map Pilot remains the only default `DO NOW` offer**. Adjacent opportunities may be researched and tested, but must not silently replace the core offer or trigger speculative platform build-out.

Commercial validation outranks speculative product development.

### EXP-001 validation threshold

Do not call the core offer validated until all of the following occur:
1. three qualified portfolio conversations;
2. at least two independent confirmations of repeated reconciliation / evidence-control pain addressed by the offer; and
3. at least one concrete commercial commitment such as a priced-scope request, proposed/paid pilot, procurement step or identifiable budget/approval owner.

Compliments, clicks, dry runs and CI do not count.

If ten qualified target-buyer conversations produce no concrete willingness to sponsor a pilot, no priced-scope request and no repeated evidence of budgeted urgency, pause product expansion and change at least one of buyer, problem, offer, packaging or distribution before building more functionality.

## Growth / AI-gateway doctrine

The operating safeguards below are not a mandate for excessive conservatism.

Use this sequence for new opportunities:

`DISCOVER → TEST → SELL MANUALLY → PROVE REPEATABILITY → AUTOMATE`

Explore broadly across regulatory and other expert-service markets where the same primitives apply: messy evidence, expensive expert review, repeated reconciliation, version/change control, auditability, human approval and measurable business outcomes.

Target reusable AI primitives rather than one-off features:
- evidence ingestion and provenance;
- entity resolution;
- claim/evidence graphs;
- contradiction and change detection;
- temporal / role-aware reasoning;
- explicit uncertainty;
- deterministic reconciliation;
- controlled generation;
- fail-closed human escalation and review;
- reproducible audit trails.

Prefer service gateways before software gateways. Investigate adjacent revenue aggressively, but do not publish, send, price, create third-party accounts, add tracking, or make buyer commitments across existing approval boundaries.

The long-term strategic direction is an **evidence-controlled AI operating layer for valuable expert work**, proven first in medical-device regulatory operations and expanded only where real market evidence earns the right to expand.

## Standard paid-pilot operating path

The controlled path remains:

`qualified buyer / written scope → commercial activation → private intake → validation → bundle generation → qualified human review → final integrity verification → delivery / closeout → private learning`

For a standard paid pilot:

```bash
clinicops-pilot-preflight /private/path/activation-record.json
clinicops-portfolio-validate /private/path/portfolio.csv
clinicops-pilot-bundle /private/path/portfolio.csv /private/path/output YYYY-MM-DD
clinicops-pilot-review-prepare /private/path/activation-record.json /private/path/output > /private/path/review-record.json
# qualified assigned reviewer actually performs review and explicit attestations
clinicops-pilot-review-gate /private/path/activation-record.json /private/path/review-record.json /private/path/output
clinicops-pilot-verify /private/path/output /private/path/portfolio.csv
```

External release requires:
- preflight `ACTIVATED`;
- human review `REVIEW APPROVED`; and
- final bundle integrity `VERIFIED`.

A source, manifest or controlled-output change after recorded review makes that review stale. Correct/regenerate, repeat human review as applicable, create a new manifest-bound review record and rerun release gates. Never edit hashes or attestations merely to force a pass.

### Commercial activation

Material client work starts only after written scope/acceptance plus one approved activation condition:
- upfront payment;
- agreed deposit / first milestone; or
- accepted PO / signed procurement commitment with defined invoice path.

Anything outside the standard envelope is **NON-STANDARD — NOT ACTIVATED**. No open-ended unpaid work.

## Founder-independence proof — PRs #33, #35, #45, #46

Do **not** claim founder-independent execution because tooling or CI is green.

Founder-independent execution is proven only by private operational evidence showing either:
- one qualifying real eligible paid pilot; or
- two qualifying complete controlled dry runs.

### Primary controlled dry-run path

PR #45 added the executable dry-run harness. PR #46 makes it the primary operator entry point for controlled proof runs:

```bash
clinicops-pilot-dry-run ...
```

Use `sales/pilot-dry-run-harness.md` and `sales/delegation-proof-protocol.md` together. The harness executes the real preflight → bundle → human-review → verify path against a bounded synthetic scenario. It stops fail-closed on a failed gate.

A canned/synthetic review record is only a mechanical smoke test. A dry run intended to count toward proof requires a genuine qualified human reviewer and private operational records. CI, automated smokes, public examples and auto-attestation are ineligible.

### Final evaluator

`clinicops-delegation-proof` remains the final evaluator:

```bash
clinicops-delegation-proof /private/path/delegation-proof-runs.json
```

Only `FOUNDER-INDEPENDENT EXECUTION PROVEN` permits the internal claim.

Proof schema 1.1 requires SHA-256 bindings to the exact activation record, saved preflight result, completed review record, review-gate result, final manifest, final bundle-verification result and source input. Two dry runs cannot qualify if they reuse the same full artifact fingerprint. Hashes prove binding, not truthfulness.

No qualifying founder-independence proof has yet been recorded merely by merging #45/#46.

## Public production surface

`clinicops.dk` is served from `docs/**` via GitHub Pages. GoDaddy is DNS only. HTTPS is enforced.

The deterministic production sitemap contains **16 canonical URLs**:
- `/`
- `/about.html`
- `/assessment-intake.html`
- `/authorised-representative-portfolio-intelligence.html`
- `/class-iii-transition.html`
- `/contact.html`
- `/eudamed-transition.html`
- `/identifier-check.html`
- `/privacy-notice/`
- `/readiness-score.html`
- `/research.html`
- `/research/eudamed-watch/`
- `/research/sscp-public-record-scan/`
- `/sscp-operations.html`
- `/tools.html`
- `/transition-map-sample/`

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

Fresh GSC verification on 2026-09-13 confirms the Search Console property `https://clinicops.dk/` **exists and is connected**. The only submitted sitemap remains the retired `https://clinicops.dk/sitemap.website.xml`, currently reporting:
- 7 submitted URLs;
- 0 indexed URLs;
- 1 warning;
- 1 error.

Issue #28 tracks the real action: submit the current 16-URL `sitemap.xml`, confirm acceptance/fetch, diagnose warning/error state on the canonical sitemap, and remove the obsolete entry only if appropriate afterward. Sitemap acceptance and indexing are separate facts.

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

Current public-API use remains bounded GET-only, identifying User-Agent, one-second spacing, finite page cap, no credentials. Re-review on material endpoint/term changes, repeated 403/429, materially increased request volume or publication of raw named records. Never evade restrictions with proxies/identity rotation.

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
- nothing external introduces ungoverned factual claims outside the verified claim/profile controls.

Corrected thesis: sampled MF-role MDR Class III registrations had linked validated SS(C)P metadata; the opportunity is transition/document-operations workload, evidence control and reconciliation—not a generic manufacturer diligence-failure allegation.

## CI / resilience gates

Current CI covers pytest, Ruff, revenue/agent/readiness contracts, public sample drift, site metadata, sitemap/internal links, paid-pilot gates, bundle/review/integrity checks, delegation negative control, claim registry/reference/content gates, sanitized fixtures, public-copy claim gate, privacy contract, EUDAMED leak/shape tests and Ops Watch contract.

PR #45 exact-main CI run #486 passed. PR #46 exact-main CI run #490 passed, including the synthetic human-review packaging smoke explicitly labelled “not delegation proof”.

Never weaken a gate merely to make CI green.

Ops Watch remains bounded/read-only and covers evidence freshness, claim/reference checks, EUDAMED reachability and live HTTPS/content checks. Public research pages are under the live-check contract.

## Private commercial / CRM state

Private buyer/prospect/outreach records stay private and must not be copied into this public repository.

Claude project-side work reports the fragmented outreach master/addenda have now been reconciled privately into a 448-row master. Treat the prior public-repo note that this merge was still outstanding as superseded. Continue send dedupe against the authoritative private master plus live Sent history.

Commercial/pipeline names, direct emails, private notes, pricing negotiations, client files and proof records never belong in public GitHub.

## External-action boundaries

Require Ali's case-by-case approval before:
- LinkedIn publishing;
- Gumroad/pricing changes;
- creating third-party accounts or live form endpoints;
- analytics/tracking deployment;
- credential revocation/rotation;
- branch-protection/ruleset changes;
- git-history rewrite.

Permanent `DO_NOT_CONTACT`:
- Ergomed Group
- PrimeVigilance

Danish-domiciled organisations are never cold-emailed; public posting only.

## Repository governance / security

`main` remains unprotected. Green CI is an operating convention rather than an enforced merge rule.

Issue #36 tracks branch protection and least-privilege credential hardening. Broad classic PAT scope remains security debt. Do not revoke/rotate credentials or change repository governance without explicit Ali approval because it can break authorized Claude/ChatGPT workflows.

A large stale-branch set remains. D-24 identified about 28 merged/abandoned branches safe to delete, including `noop-test`; `pilot-dry-run-harness-20260911` can join the cleanup list now that PR #45 is merged. The current connector does not expose delete-ref, so do not claim cleanup occurred unless refs are actually removed.

### Write-discipline incident — 2026-09-13

A ChatGPT connector call accidentally created `AGENT_STATE_NEW.md` directly on `main`; it was detected immediately and deleted in the next commit before any further work. Net content returned to the PR #46 tree. Lesson: every material file write must use a fresh branch, and connector calls must be checked for target branch before execution.

### D-23 history scrub

Pre-anonymisation commit `cb01b34` remains reachable and contains named watcher outputs. Default recommendation remains **do not rewrite history** because filter-repo/force-push breaks clones/commit bases and may not immediately remove GitHub-held objects. If Ali explicitly chooses a scrub, prepare exact commands and warn before execution.

## Budget / resilience doctrine

ClinicOps is bootstrapped. Default to:
- low fixed cost;
- GitHub + Pages + existing domain/mail + AI leverage;
- service revenue before expensive SaaS infrastructure;
- automate repeated paid-work friction only;
- reinvest validated revenue into infrastructure.

## Recent merged operating changes

- #29 — fail-closed paid-pilot preflight.
- #30 — final bundle integrity verification.
- #31 — canonical controlled execution order.
- #32 — manifest-bound human-review release gate.
- #33 — founder-independence evaluator/protocol.
- #35 — schema 1.1 artifact bindings / independent-run fingerprints.
- #38 — public SS(C)P scan research page.
- #39 — EUDAMED Watch anonymisation / private watchlist / page-cap fix.
- #40 — public EUDAMED Watch method page.
- #41 — official-source Public API reuse review / raw secret-copy rule.
- #42 — public research pages under scheduled live Ops Watch.
- #43 — prior shared-state reconciliation.
- #44 — SS(C)P Playground workflow evidence recorded with Production boundary.
- #45 — executable controlled dry-run harness + fail-closed human-review checklist gate.
- #46 — dry-run harness made primary proof-run execution path while preserving final evaluator.

## Coordination protocol

1. Fetch `main`, open PRs, branches and current Actions before work.
2. Treat `main` as canonical over chat/local state.
3. Preserve claim IDs, anonymisation, privacy and commercial boundaries.
4. Reuse existing modules before parallel logic.
5. Preserve concurrent Claude/ChatGPT work; never force-overwrite.
6. Fresh branch/PR for material changes.
7. Fix root causes, not gates.
8. Verify exact merged-SHA CI before declaring green; verify live Pages/Ops Watch after public changes.
9. Keep buyer/client/proof/outreach records private.
10. Discover broadly, validate cheaply, sell manually, build narrowly.

## Highest-leverage next work

1. **Real commercial evidence remains the primary bottleneck.** Use qualified conversations and concrete commitments to test EXP-001.
2. **Run genuine founder-independence work only with a real qualified human reviewer.** The harness is ready; software alone cannot supply proof.
3. **Submit the canonical 16-URL sitemap in GSC** and diagnose the old sitemap warning/error under issue #28.
4. **Use the AI-gateway mandate to discover new revenue paths** across regulatory and adjacent expert-service markets, but keep them in DISCOVER/TEST until buyer evidence justifies manual selling/building.
5. **Prepare security/branch cleanup, but execute governance/credential changes only with explicit approval and actual tool capability.**
6. **Address private-side decision blockers in the Claude control tree** rather than copying private CRM/prospect state into GitHub.
7. After real delivery/buyer objections, automate only repeated evidenced friction.
