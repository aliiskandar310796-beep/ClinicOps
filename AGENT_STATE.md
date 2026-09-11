# ClinicOps shared agent state

Last updated: 2026-09-11 after PR #33 founder-independence proof hardening.

## Canonical truth
GitHub `main` is the shared source of truth. Fetch current `main` before work, inspect open PRs/branches, preserve concurrent Claude/ChatGPT work, and never force-overwrite a newer change. Chat transcripts, local copies and ZIPs are secondary until their changes land here.

Current canonical main at this refresh:

`080edb3651c2c6b6c4f7f3ccdef01b50625d82f6` — **Make founder-independence proof fail closed (#33)**.

## Current business thesis
ClinicOps is a human-reviewed portfolio evidence and work-planning layer for MDR / EUDAMED transition operations, especially Class III / implantable portfolios.

The **Class III Transition Map Pilot is the only default `DO NOW` service entry**. Adjacent service ideas remain experiments/backlog until real buyer evidence activates the exact workflow. Do not build new offers, pricing surfaces, outreach, delivery infrastructure or SaaS features merely because an adjacent idea exists.

Commercial validation outranks speculative product development.

### EXP-001 validation threshold
Do not call the core offer validated until all of the following occur:
1. three qualified portfolio conversations;
2. at least two independent confirmations of repeated reconciliation / evidence-control work addressed by the offer; and
3. at least one concrete commercial commitment such as a priced-scope request, proposed/paid pilot, procurement step or identifiable budget/approval owner.

Compliments, clicks, generic interest, dry runs and CI do not count.

If ten qualified target-buyer conversations produce no concrete willingness to sponsor a pilot, no priced-scope request and no repeated evidence of budgeted urgency, pause product expansion and change at least one of buyer, problem, offer, packaging or distribution before building more functionality.

## Standard paid-pilot operating path
The controlled standard path is now executable and fail closed:

`qualified buyer / written scope → commercial activation → private intake → validation → bundle generation → qualified human review → final integrity verification → delivery / closeout → private learning`

For a standard paid pilot:

```bash
clinicops-pilot-preflight /private/path/activation-record.json
clinicops-portfolio-validate /private/path/portfolio.csv
clinicops-pilot-bundle /private/path/portfolio.csv /private/path/output YYYY-MM-DD
clinicops-pilot-review-prepare /private/path/activation-record.json /private/path/output > /private/path/review-record.json
# qualified assigned reviewer actually completes the review and explicit attestations
clinicops-pilot-review-gate /private/path/activation-record.json /private/path/review-record.json /private/path/output
clinicops-pilot-verify /private/path/output /private/path/portfolio.csv
```

External release requires:
- preflight `ACTIVATED`;
- human review `REVIEW APPROVED`; and
- final bundle integrity `VERIFIED`.

A source, manifest or controlled-output change after recorded review makes that review stale. Correct/regenerate, repeat human review as applicable, create a new manifest-bound review record and rerun both release gates. Do not edit hashes or attestations merely to force a pass.

### Commercial activation gate
Material work starts only after written scope/acceptance plus an approved activation condition:
- upfront payment;
- agreed deposit / first milestone; or
- accepted PO / signed procurement commitment with defined invoice path.

No open-ended unpaid work. A no-fee/reduced-fee design-partner pilot is outside the standard delegated workflow and requires a separately approved, time-bounded policy rather than an ad hoc transaction exception.

Anything outside the standard envelope is **NON-STANDARD — NOT ACTIVATED** and is parked or declined rather than routed to Ali for transaction-level improvisation.

### Paid-pilot preflight — PR #29
`src/clinicops_os/pilot_gate.py` + `clinicops-pilot-preflight` turn the delegation envelope into a deterministic fail-closed gate.

The standard path requires explicit evidence of buyer eligibility, bounded written scope, commercial activation, approved private-data route, controlled bundle schema, assigned qualified reviewer and absence of unsupported/non-standard work. Missing or ambiguous negative attestations block activation; omission is not equivalent to `false`.

### Client bundle schema 1.1
Controlled outputs:
- `client_report.html`
- `portfolio_report.md`
- `portfolio_report.json`
- `intake_diagnostics.md`
- `manifest.json`

`manifest.json` records source/output hashes. Real buyer inputs and client bundles stay in approved private storage, never this public repository.

### Human-review gate — PR #32
`src/clinicops_os/review_gate.py` provides:
- `clinicops-pilot-review-prepare`
- `clinicops-pilot-review-gate`

The private review record is bound to the exact final manifest SHA-256, source hash, evidence date and reviewer assigned in the activated pilot. Preparation creates all substantive review attestations as `false`; preparation is not review.

The qualified reviewer must actually confirm evidence population/date, warnings and information gaps, material derived statements, structural-vs-regulatory distinction, actor-role distinctions, unresolved facts, internal-note removal and final client-facing interpretation.

The gate also requires `founder_transaction_decision_required=false` and `unplanned_exception=false` for the standard path.

The gate validates the recorded attestation and exact-file binding. It cannot prove the reviewer performed the work truthfully and never replaces professional regulatory judgement.

### Bundle integrity gate — PR #30
`src/clinicops_os/bundle_verify.py` + `clinicops-pilot-verify` recompute source and controlled-output hashes immediately before release and require the exact schema-1.1 output population.

Missing, substituted, modified or manifest-omitted controlled files fail verification. Integrity verification proves file correspondence, not regulatory correctness.

## Founder-independence proof — PR #33
Do **not** claim founder-independent execution merely because the tooling or CI is green.

Founder-independent execution is proven only after private operational evidence shows either:
- one qualifying real eligible paid pilot; or
- two unique qualifying complete controlled dry runs.

Use:

```bash
clinicops-delegation-proof /private/path/delegation-proof-runs.json
```

Only `FOUNDER-INDEPENDENT EXECUTION PROVEN` permits the internal claim.

A qualifying run must complete the full lifecycle from qualification/written scope through activation, intake, controlled bundle, qualified human review, final integrity verification, delivery/release and closeout, with every existing evidence/claim/commercial/data gate satisfied, zero Ali transaction-level decisions, no unplanned/non-standard exception and private learning capture.

CI, unit tests, automated smokes and the public sanitized example are categorically ineligible. `examples/delegation_proof.example.json` is intentionally marked `private_operational_record=false`, `proof_use_allowed=false`, `ci_or_automated_smoke=true` and must remain non-qualifying.

Protocol: `sales/delegation-proof-protocol.md`.

Dry-run learning is operational/process learning only. It does **not** count toward EXP-001 qualified conversations, repeated-pain confirmation, willingness to pay or commercial commitment.

## Public production surface
`clinicops.dk` is served from `docs/**` through GitHub Pages. GoDaddy is DNS only. HTTPS is enforced.

Current sitemap has 14 public canonical URLs:
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
- `/sscp-operations.html`
- `/tools.html`
- `/transition-map-sample/`

Do not mass-produce thin SEO pages or duplicate the existing EUDAMED/MDR-transition pillars while current URLs are still being discovered.

### Browser-local acquisition path
The production path remains deliberately low-infrastructure:

`public site / free tool / sanitized sample → browser-local assessment brief → user's email client → controlled private scope/intake`

`docs/assessment-intake.html` has no backend form action, analytics, tracking, `fetch`, XHR, `sendBeacon` or WebSocket submission. User input remains local until the user explicitly creates an email draft to `info@clinicops.dk`. The page warns against patient-identifiable data.

The Readiness Score → assessment handoff uses one-shot tab-scoped `sessionStorage` containing score/band/gaps/timestamp only; no company/customer data. Preserve `tests/test_readiness_handoff_contract.py` and `tests/test_assessment_intake_contract.py`.

Do not create a third-party form endpoint/account without Ali's explicit approval.

### Public free tools
Keep both free:
- EUDAMED Identifier Check — browser-only structural identifier screening;
- Transition Readiness Score — browser-only operational work-plan readiness signal.

The Readiness Score is not a regulatory/compliance/legal/enforcement risk score. B-prefix output is structural screening, not a compliance conclusion.

### Sanitized Transition Map sample
`docs/transition-map-sample/index.html` is generated from the same report-rendering path used by the paid bundle through `scripts/render_public_demo.py`. Its fixture is fictional/sanitized. The sample demonstrates structure, not a compliance outcome.

Do not hand-edit generated output in a way that creates renderer drift and never put buyer/prospect data into a public Pages artifact.

## Privacy / tracking posture — PR #26
`https://clinicops.dk/privacy-notice/` is a production invariant because prior business-development communications referenced it.

Current posture:
- static GitHub Pages;
- ClinicOps sets no cookies;
- no analytics/tracking runtime;
- browser-local tools;
- sitemap-wide privacy link visibility.

`tests/test_privacy_surface_contract.py` enforces the current no-tracking/public-privacy contract, and Ops Watch checks the live privacy endpoint.

Do not add analytics/tracking or materially change privacy posture without Ali's explicit approval plus corresponding notice/contract updates.

## Claim governance and corrected regulatory thesis
Canonical controls:
- `research/claims.jsonl`
- `src/clinicops_eudamed/claim_guard.py`
- `src/clinicops_os/claim_registry.py`

Preserve these boundaries:
- do not infer non-compliance from missing/null public SS(C)P links;
- do not imply complete EUDAMED public-register/API coverage;
- B-prefix signals are structural screening only;
- preserve MF / AR / IM / PR actor-role distinctions;
- do not present non-binding recommendations as statutory deadlines;
- do not make buyer-specific regulatory claims without authorised evidence;
- deterministic priority scores are operator triage, not regulatory/compliance/legal/safety risk scores.

Corrected thesis: sampled MF-role MDR Class III registrations had linked validated SS(C)P metadata; the opportunity is legacy→MDR transition/document-operations workload, evidence control and reconciliation—not a generic allegation of manufacturer diligence failure.

Do not revive the rejected diligence-failure headline.

## CI / resilience gates
Current CI covers:
- pytest and Ruff;
- Revenue OS experiment contract;
- agent five-gate contract;
- Readiness Score and intake/handoff contracts;
- public sample renderer drift;
- site metadata, deterministic sitemap and internal links;
- fail-closed paid-pilot preflight;
- client bundle smoke;
- synthetic human-review-gate packaging smoke, explicitly **not delegation proof**;
- final client-bundle integrity verification;
- delegation-proof negative control requiring the public CI example to return **NOT PROVEN**;
- custom-agent profile audit;
- claim-registry/reference/content gates;
- sanitized report fixture;
- public-copy claim gate;
- privacy/no-tracking contract.

Ops Watch remains bounded/read-only and covers evidence freshness, claim/reference checks, the bounded EUDAMED reachability canary and live HTTPS/content checks including the privacy notice.

Do not weaken a gate merely to get CI green; fix the underlying inconsistency.

## Search / indexing
Production canonical sitemap:

`https://clinicops.dk/sitemap.xml`

Google Search Console previously showed only the older `sitemap.website.xml` submission (7 submitted / 0 indexed, no warnings/errors) while production now exposes the 14-URL canonical sitemap.

GitHub issue #28 tracks the remaining manual action: submit `sitemap.xml` in the actual Google Search Console UI, verify acceptance, and remove the older sitemap only if appropriate afterward. Connected GSC tooling can inspect but does not provide the required Google sitemap-submission action.

Do not create extra SEO pages simply to inflate URL count while current production pages are still being discovered.

## External-action boundaries
Require Ali's case-by-case approval before:
- LinkedIn publishing;
- Gumroad/pricing changes;
- creating third-party accounts or live form endpoints;
- analytics/tracking deployment.

Permanent `DO_NOT_CONTACT`:
- Ergomed Group
- PrimeVigilance

Keep prospect/customer names, emails, portfolio files, pricing negotiations, private notes and proof records out of the public repository.

## Budget / resilience doctrine
ClinicOps is bootstrapped. Default to:
- low fixed cost;
- GitHub + Pages + existing domain/mail + AI leverage;
- service revenue before expensive SaaS infrastructure;
- automation only for repeated paid-work friction;
- reinvest validated revenue into infrastructure.

Do not add paid CRM/cloud/portal/data infrastructure until real paid use proves it is needed.

## Recent merged operating changes
- #26 — hardened public privacy surface and production privacy check.
- #27 — standardized founder-independent paid-pilot delegation envelope.
- #29 — executable fail-closed paid-pilot preflight.
- #30 — final client-bundle source/output integrity verification.
- #31 — canonical operator docs locked to controlled execution order.
- #32 — manifest-bound executable human-review release gate.
- #33 — fail-closed founder-independence proof evaluator and controlled dry-run protocol.

## Coordination protocol
1. Fetch `main` and inspect open PRs before work.
2. Treat `main` as canonical over chat/local state.
3. Preserve evidence corrections, claim IDs, privacy posture and commercial boundaries.
4. Reuse existing modules before adding parallel logic.
5. Preserve concurrent Claude/ChatGPT work; never force-overwrite.
6. Use feature branches/PRs for material changes.
7. Fix root causes when CI catches a real inconsistency.
8. Verify exact merged-SHA CI before declaring code green; verify Pages/Ops Watch for public-site changes.
9. Keep all real buyer/client/proof records private.
10. Prefer the smallest durable control or commercial experiment over a larger feature.

## Highest-leverage next work
1. **Real commercial evidence remains the primary bottleneck.** Use qualified buyer conversations to test EXP-001; do not substitute dry runs or software activity for demand.
2. If a real eligible paid pilot arrives, execute the full controlled path and evaluate it as the strongest founder-independence proof candidate.
3. Otherwise, conduct two genuine controlled operator dry runs under `sales/delegation-proof-protocol.md` with actual qualified human review; use them to discover hidden founder decisions. Do not auto-attest review or count CI.
4. Submit/verify the canonical production sitemap in Google Search Console under issue #28.
5. After real delivery or buyer objections, automate only repeated friction that the evidence exposes. Do not expand the offer or platform speculatively.
