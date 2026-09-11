# ClinicOps shared agent state

Last updated: 2026-09-12 after PR #42 live research monitoring verification.

## Canonical truth

GitHub `main` is the shared source of truth. Fetch current `main` before work, inspect open PRs/branches, preserve concurrent Claude/ChatGPT work, and never force-overwrite a newer change. Chat transcripts, local copies and ZIPs are secondary until their changes land here.

Current canonical main at this refresh:

`b0a5d66328acec0cdc5d27a633721a38f60d3ebd` — **Put new research pages under live Ops Watch (#42)**.

Exact-main verification completed on 2026-09-12:
- CI run #475: `success`;
- Ops Watch run #22: `success`;
- `Live site health`: `success` against `clinicops.dk` over HTTPS;
- EUDAMED reachability canary: `success`;
- Evidence freshness: `success`.

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

The controlled standard path is executable and fail closed:

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

### Controlled paid-pilot gates

- PR #29: `clinicops-pilot-preflight` turns the delegation envelope into a deterministic fail-closed gate. Missing or ambiguous negative attestations block activation; omission is not `false`.
- PR #30: `clinicops-pilot-verify` recomputes source/output hashes and requires the exact schema-1.1 controlled output population immediately before release.
- PR #32: `clinicops-pilot-review-prepare` + `clinicops-pilot-review-gate` bind recorded human review to the exact final manifest, source, evidence date and assigned qualified reviewer. Preparation starts substantive attestations `false`; preparation is not review.

Client bundle schema 1.1 controlled outputs:
- `client_report.html`
- `portfolio_report.md`
- `portfolio_report.json`
- `intake_diagnostics.md`
- `manifest.json`

Real buyer inputs, activation records, review records, proof records and client bundles stay in approved private storage, never this public repository.

## Founder-independence proof — PRs #33 and #35

Do **not** claim founder-independent execution merely because tooling or CI is green.

Founder-independent execution is proven only after private operational evidence shows either:
- one qualifying real eligible paid pilot; or
- two qualifying complete controlled dry runs.

Use:

```bash
clinicops-delegation-proof /private/path/delegation-proof-runs.json
```

Only `FOUNDER-INDEPENDENT EXECUTION PROVEN` permits the internal claim.

PR #35 hardened delegation-proof schema **1.1**. A qualifying run must bind by SHA-256 to the exact controlled artifacts, including the activation record, saved preflight result, completed review record, saved review-gate result, final manifest, saved bundle-verification result and source input. Two supposed dry runs cannot count as independent proof when they reuse the same full artifact fingerprint.

A qualifying run must still complete the full lifecycle with every evidence/claim/commercial/data gate satisfied, zero Ali transaction-level decisions, no unplanned/non-standard exception, controlled closeout and private learning capture.

CI, unit tests, automated smokes and public sanitized examples are categorically ineligible. A qualified human reviewer must actually perform the human-review steps; automated attestation cannot make a proof run qualify.

Protocol: `sales/delegation-proof-protocol.md`.

Dry-run learning is operational/process learning only. It does **not** count toward EXP-001 qualified conversations, repeated-pain confirmation, willingness to pay or commercial commitment.

## Public production surface

`clinicops.dk` is served from `docs/**` through GitHub Pages. GoDaddy is DNS only. HTTPS is enforced.

Current deterministic sitemap has **16 public canonical URLs**:
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

Do not mass-produce thin SEO pages or duplicate the existing EUDAMED/MDR-transition pillars while current URLs are still being discovered.

### Browser-local acquisition path

The production path remains deliberately low-infrastructure:

`public site / free tool / sanitized sample → browser-local assessment brief → user's email client → controlled private scope/intake`

`docs/assessment-intake.html` has no backend form action, analytics, tracking, `fetch`, XHR, `sendBeacon` or WebSocket submission. User input remains local until the user explicitly creates an email draft to `info@clinicops.dk`. The page warns against patient-identifiable data.

The Readiness Score → assessment handoff uses one-shot tab-scoped `sessionStorage` containing score/band/gaps/timestamp only; no company/customer data.

Do not create a third-party form endpoint/account without Ali's explicit approval.

### Public free tools

Keep both free:
- EUDAMED Identifier Check — browser-only structural identifier screening;
- Transition Readiness Score — browser-only operational work-plan readiness signal.

The Readiness Score is not a regulatory/compliance/legal/enforcement risk score. B-prefix output is structural screening, not a compliance conclusion.

### Public research surfaces

- `/research/sscp-public-record-scan/` — public SS(C)P/public-record research note.
- `/research/eudamed-watch/` — public method page for the ongoing EUDAMED monitoring capability.

PR #42 adds both pages to the scheduled live HTTPS checker. `tests/test_ops_watch_contract.py` prevents the weekly Ops Watch schedule or live-check invocation from silently disappearing.

## EUDAMED Watch — PRs #39–#41

The EUDAMED Watch workflow is `.github/workflows/eudamed-watch.yml`.

Trigger surface is intentionally narrow:
- manual `workflow_dispatch`;
- monthly schedule `17 6 1 * *`;
- **no push trigger**.

### Public-repository anonymisation contract

This repository is public. Do not weaken this property:

> nothing committed under the public watcher outputs, and nothing printed to public CI logs, may identify a manufacturer, device, trade name, Basic UDI-DI or SS(C)P reference.

Current design:
- real 14-entry watchlist is private in `EUDAMED_WATCHLIST` repository secret;
- optional stable pseudonymous per-device keys use truncated HMAC-SHA256 under private `EUDAMED_HMAC_KEY`;
- committed snapshots / diffs / `LATEST.md` are aggregate-only or pseudonymous;
- fully named output exists only via local/private `--full-out DIR`;
- `--max-pages 8` avoids the previously observed silent truncation at 5 pages;
- leak-assertion tests are a governance control: fix code, never loosen the test to make a leak pass.

First verified anonymised live run on 2026-09-11 queried 14 watchlist entries, returned 147 distinct devices, had 0 truncated entries and retained 2 zero-row entries as findability canaries. Zero rows means “not findable under the tested string at that time”, never “not registered”.

### EUDAMED public-API reuse review — PR #41

`research/eudamed-public-api-reuse-review.md` closes the D-17 due-diligence gap for the current bounded monthly implementation.

Reviewed official materials state that the Commission Public API is public, usable by individuals/organisations and intended for third-party software integration. No EUDAMED-specific quota/rate rule was stated in the reviewed current guide. This is **not** a claim of unlimited service or perpetual terms.

Current operating rule remains conservative: GET-only, fixed identifying User-Agent, one-second spacing, finite page cap, no credentials. Stop and re-review on new published terms, material endpoint changes, repeated 403/429 responses, materially increased request volume or a change toward publishing raw named records. Never work around an operator restriction with proxies, identity rotation or other evasion.

### Exact-syntax secret handling — E-015

A 2026-09-11 setup attempt failed safely because macOS TextEdit smart quotes changed straight JSON quotation marks. The workflow JSON-validation guard caught this before data processing.

For JSON/code/keys or other syntax-sensitive values, validate and copy raw bytes from Terminal rather than GUI editors that may transform characters:

```bash
python -m json.tool /path/to/private-watchlist.json >/dev/null
pbcopy < /path/to/private-watchlist.json
```

Keep the workflow validation fail closed.

## Privacy / tracking posture

`https://clinicops.dk/privacy-notice/` is a production invariant because prior business-development communications referenced it.

Current posture:
- static GitHub Pages;
- ClinicOps sets no cookies;
- no analytics/tracking runtime;
- browser-local tools;
- sitemap-wide privacy link visibility.

`tests/test_privacy_surface_contract.py` enforces the current no-tracking/public-privacy contract, and Ops Watch checks the live privacy endpoint.

Do not add analytics/tracking or materially change privacy posture without Ali's explicit approval plus corresponding notice/contract updates.

## Claim governance and regulatory boundaries

Canonical controls include:
- `research/claims.jsonl`;
- `src/clinicops_eudamed/claim_guard.py`;
- `src/clinicops_os/claim_registry.py`;
- governed external-profile/claim records where present in the repository.

Preserve these boundaries:
- do not infer non-compliance from missing/null public SS(C)P links;
- do not imply complete EUDAMED public-register/API coverage;
- B-prefix signals are structural screening only;
- preserve MF / AR / IM / PR actor-role distinctions;
- do not present non-binding recommendations as statutory deadlines;
- do not make buyer-specific regulatory claims without authorised evidence;
- deterministic priority scores are operator triage, not regulatory/compliance/legal/safety risk scores;
- nothing published externally should introduce an ungoverned claim outside the repository’s verified claim/profile controls.

Corrected thesis: sampled MF-role MDR Class III registrations had linked validated SS(C)P metadata; the opportunity is legacy→MDR transition/document-operations workload, evidence control and reconciliation—not a generic allegation of manufacturer diligence failure.

Do not revive the rejected diligence-failure headline.

## CI / resilience gates

Current CI covers, among other controls:
- pytest and Ruff;
- Revenue OS / commercial-priority contracts;
- readiness/intake/handoff contracts;
- public sample renderer drift;
- site metadata, deterministic sitemap and internal links;
- paid-pilot preflight;
- bundle generation / human-review packaging / final bundle verification;
- delegation-proof negative control;
- claim registry/reference/content gates;
- sanitized report fixtures;
- public-copy claim gate;
- privacy/no-tracking contract;
- EUDAMED watch leak/shape tests;
- Ops Watch schedule/live-check contract.

Ops Watch remains bounded/read-only and covers evidence freshness, claim/reference checks, the bounded EUDAMED reachability canary and live HTTPS/content checks. Exact-main run #22 on `b0a5d663…` completed successfully after PR #42, including the two public research pages.

Do not weaken a gate merely to get CI green; fix the underlying inconsistency.

## Search / indexing

Production canonical sitemap:

`https://clinicops.dk/sitemap.xml`

It currently contains **16 URLs**. Google Search Console previously showed only the older `sitemap.website.xml` submission with 7 submitted / 0 indexed in that sitemap record.

GitHub issue #28 now tracks the accurate action: submit the current **16-URL** `sitemap.xml` in the actual Google Search Console UI, verify acceptance, and remove the older sitemap only if appropriate afterward.

Do not create extra SEO pages merely to inflate URL count while current production pages are still being discovered.

## External-action boundaries

Require Ali's case-by-case approval before:
- LinkedIn publishing;
- Gumroad/pricing changes;
- creating third-party accounts or live form endpoints;
- analytics/tracking deployment.

Permanent `DO_NOT_CONTACT`:
- Ergomed Group
- PrimeVigilance

The do-not-contact rule applies to every code/tool path that could send outreach, not only one script.

Keep prospect/customer names, emails, portfolio files, pricing negotiations, private notes, outreach master/addenda and proof records out of the public repository.

## Repository governance / security

`main` is currently unprotected; green CI is an operating convention rather than an enforced merge rule.

Issue #36 tracks repository-access hardening and least-privilege credential cleanup. Do not change branch/ruleset policy or revoke/rotate credentials without Ali's explicit approval because it can disrupt Claude/ChatGPT/connector workflows.

A large set of stale merged/abandoned one-off branches remains on origin. Cleanup is worthwhile, but the current ChatGPT GitHub connector exposes branch creation/update rather than branch deletion. Do not claim branch cleanup has occurred unless branches are actually removed.

An accidental stale branch named `noop-test` was created during the 2026-09-12 work and should be included in the eventual cleanup.

### D-23 history-scrub decision

Pre-anonymisation commit `cb01b34` remains reachable in git history and contains named watcher outputs. Default recommendation remains **do not rewrite history**: `git filter-repo` + force-push breaks existing clones/commit bases and GitHub may retain hash-reachable objects until garbage collection/support action. If Ali explicitly chooses a scrub anyway, prepare exact commands for review and warn about clone/history disruption before execution.

## Private outreach-log debt

The project-side outreach master has dated addenda across incompatible CSV schemas. This is operational debt, not currently a send-safety gap because the outreach workflow deduplicates against master + addenda + live Sent history.

Do not reconstruct the master from chat memory and do not put private prospect data in public GitHub. As of this refresh, the named master/addenda were not available on the current Project/Library file surface, so no merge was attempted. Reconcile them only when the exact private files or a verified Drive identity are available.

## Budget / resilience doctrine

ClinicOps is bootstrapped. Default to:
- low fixed cost;
- GitHub + Pages + existing domain/mail + AI leverage;
- service revenue before expensive SaaS infrastructure;
- automation only for repeated paid-work friction;
- reinvest validated revenue into infrastructure.

Do not add paid CRM/cloud/portal/data infrastructure until real paid use proves it is needed.

## Recent merged operating changes

- #29 — executable fail-closed paid-pilot preflight.
- #30 — final client-bundle source/output integrity verification.
- #31 — canonical operator docs locked to controlled execution order.
- #32 — manifest-bound executable human-review release gate.
- #33 — fail-closed founder-independence proof evaluator and controlled dry-run protocol.
- #35 — delegation-proof schema 1.1 bound to exact controlled artifacts and independent-run fingerprints.
- #38 — public SS(C)P public-record scan research page.
- #39 — EUDAMED Watch public-output anonymisation / private watchlist / page-cap fix.
- #40 — public EUDAMED Watch method page.
- #41 — official-source EUDAMED public-API reuse review + exact-syntax secret-copy rule.
- #42 — both new research pages placed under scheduled live Ops Watch, with contract coverage.

## Coordination protocol

1. Fetch `main` and inspect open PRs/branches before work.
2. Treat `main` as canonical over chat/local state.
3. Preserve evidence corrections, claim IDs, anonymisation, privacy posture and commercial boundaries.
4. Reuse existing modules before adding parallel logic.
5. Preserve concurrent Claude/ChatGPT work; never force-overwrite.
6. Use feature branches/PRs for material changes.
7. Fix root causes when CI catches a real inconsistency.
8. Verify exact merged-SHA CI before declaring code green; verify Pages/Ops Watch for public-site changes.
9. Keep all real buyer/client/proof/outreach records private.
10. Prefer the smallest durable control or commercial experiment over a larger feature.

## Highest-leverage next work

1. **Real commercial evidence remains the primary bottleneck.** Use qualified buyer conversations to test EXP-001; do not substitute dry runs or software activity for demand.
2. If a real eligible paid pilot arrives, execute the full controlled path and evaluate it as the strongest founder-independence proof candidate.
3. Otherwise, conduct genuine controlled operator dry runs under `sales/delegation-proof-protocol.md` only with actual qualified human review; do not auto-attest review or count CI.
4. Submit/verify the current 16-URL canonical production sitemap in Google Search Console under issue #28.
5. With explicit Ali approval, address issue #36 (branch protection / least-privilege credentials) without breaking authorized agent workflows.
6. When exact private outreach files are available, reconcile the outreach-log addenda deterministically without exposing prospect data.
7. After real delivery or buyer objections, automate only repeated friction that the evidence exposes. Do not expand the offer or platform speculatively.
