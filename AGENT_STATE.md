# ClinicOps shared agent state

Last reconciled: 2026-09-14 after PR #53, exact-main CI / Integrity Gate / Pages verification, live 19-URL sitemap fetch, and Integrity Gate indexing registration.

## Canonical truth

GitHub `main` is the shared source of truth. Fetch current `main`, open PRs/branches and current Actions before substantive work. Preserve concurrent Claude/ChatGPT work and never force-overwrite a newer change. Chat transcripts, local copies and project-side control files are secondary until their changes land here.

Do **not** hard-code a self-referential “current main SHA” as permanent truth because this file's own merge changes `main`. The verified PR #53 merge SHA was `3a082987d1388c597fdf89b6c8e54fc7fe87c27a`; exact-main standard CI #565, Integrity Gate workflow #18 and Pages deployment #23 all passed on that SHA. Always fetch live state again before acting.

## Current business thesis

ClinicOps is an evidence-controlled, human-reviewed operating layer for high-value expert work. The current commercial beachhead remains medical-device regulatory operations, especially MDR / EUDAMED transition, regulatory information integrity, document control and lifecycle change propagation.

The **Class III Transition Map Pilot remains the default currently sellable `DO NOW` offer**. **ClinicOps Integrity Gate is `TEST`: software-validated and deployed, but commercially unvalidated.** Do not silently call Integrity Gate a validated market offer merely because its software, CI or public page is live.

Commercial validation outranks speculative product development.

### EXP-001 validation threshold

Do not call the core offer or a new gateway commercially validated until evidence supports it. For the current core validation contract, require:

1. three qualified portfolio conversations;
2. at least two independent confirmations of repeated reconciliation / evidence-control pain addressed by the offer; and
3. at least one concrete commercial commitment such as a priced-scope request, proposed/paid pilot, procurement step or identifiable budget/approval owner.

Compliments, clicks, drafts, synthetic runs, CI and software deployment do not count as demand.

If ten qualified target-buyer conversations produce no concrete willingness to sponsor a pilot, no priced-scope request and no repeated evidence of budgeted urgency, pause product expansion and change at least one of buyer, problem, offer, packaging or distribution before building more functionality.

## ClinicOps Integrity Gate — PR #53

Status: **TEST / software-validated / deployed / commercially unvalidated**.

Purpose: before a client treats a regulatory submission, controlled-document release or approved lifecycle change as operationally complete, reconcile the client-declared controlled sources and downstream surfaces, preserve provenance, detect declared change-propagation gaps, and route ambiguity to qualified human review.

It is **not** a legal, regulatory or compliance determination. A machine `PASS` does not establish device compliance or completeness. Client RA/QA retains regulatory decisions.

### Executable path

```bash
clinicops-integrity-gate /private/case.json /private/output
clinicops-integrity-review-prepare /private/output > /private/review.json
# qualified human completes the review record
clinicops-integrity-review-gate /private/review.json /private/output
clinicops-integrity-verify /private/output /private/case.json --require-review
```

Automated evidence states:

- `PASS`
- `REVIEW_REQUIRED`
- `UNRESOLVED_AUTHORITY`
- `HOLD_FOR_HUMAN_DECISION`

Core invariants:

- client declares the bounded controlled-source population, downstream surfaces, fields and any approved changes;
- if supplied controlled sources disagree, return `UNRESOLVED_AUTHORITY`; never silently choose an authority;
- change-propagation checks compare declared old/new values against declared affected surfaces;
- every finding preserves evidence references;
- bundles are SHA-256 manifest-bound and tamper-checked;
- every automated state, including `PASS`, remains human-review gated before **delivery of the ClinicOps output bundle**;
- `release_ready=true` applies only to delivery of the reviewed ClinicOps work product. It never authorizes release of a device, controlled document or regulatory submission.

Canonical implementation/docs:

- `src/clinicops_os/integrity_gate.py`
- `src/clinicops_os/integrity_review.py`
- `src/clinicops_os/integrity_cli.py`
- `tests/test_integrity_gate.py`
- `examples/integrity_gate_case.example.json` — synthetic only
- `.github/workflows/integrity-gate.yml`
- `sales/integrity-gate-pilot.md`
- `website/integrity-gate.md`
- `docs/integrity-gate.html`

Technical validation proves deterministic input handling, reconciliation/change checks, unresolved-authority behavior, bundle generation, hash binding, tamper rejection and fail-closed human-review mechanics. It does **not** prove buyer demand, product-market fit, revenue, professional judgement quality or real-world field coverage.

Do not expand Integrity Gate into a broad platform before discovery. The next product work should be driven by repeated buyer workflow evidence, false-positive/false-negative learning from controlled pilots, and actual operator friction.

## AI Company OS — PRs #48–#50

ClinicOps is explicitly testing whether nearly the entire company can run AI-first while preserving commercial truth and human/regulatory controls.

Canonical architecture:

- `06_AGENTS/AI_COMPANY_OS.md`
- `03_OPERATIONS/AI_COMPANY_EXPERIMENT.md`
- `src/clinicops_os/company_run.py`
- `examples/ai_company_run.example.json` — synthetic only
- six canonical custom-agent profiles under `.github/agents/**`

Departments are workflow lanes, **not a second agent fleet**:

- Executive Orchestration — shared AI control layer;
- Market & Regulatory Intelligence — Regulatory Evidence Steward;
- Revenue & Opportunity — Opportunity Architect;
- Customer Discovery & Partnerships — Customer Discovery Agent;
- Growth & Distribution — Visibility Architect;
- Client Delivery — Portfolio Operator;
- Quality, Engineering & Resilience — Release Sentinel;
- Commercial Control — Opportunity Architect + Release Sentinel;
- Human Governance — Ali + assigned qualified reviewers for reserved decisions.

Company loop:

`signal → qualification → experiment → buyer action → conversation → commitment → activation → delivery → review → payment/expansion → learning`

### Commercial evidence ladder

- `E0` internal hypothesis/build — not commercial evidence;
- `E1` external market/regulatory signal — not buyer evidence;
- `E2` qualified reachable buyer/account — not buyer evidence;
- `E3` verified demand test delivered — execution evidence only;
- `E4` human buyer response / qualified conversation — real commercial evidence;
- `E5` repeated pain/workflow/consequence confirmed — real commercial evidence;
- `E6` priced-scope request, proposed pilot, procurement step or identifiable budget/approval owner — concrete commercial signal;
- `E7` commercially activated paid work / accepted PO or equivalent activation path;
- `E8` accepted delivery and/or payment evidence;
- `E9` repeat purchase, expansion, renewal or qualified referral caused by delivered value.

No event may be recorded at `E4+` without a private evidence reference. The Integrity Gate build/deploy is `E0/E1` execution evidence only unless a real buyer creates stronger evidence.

### AI-COMPANY-001

Run real company events privately and evaluate with:

```bash
clinicops-company-run /private/path/company-run.json
```

An **AI OPERATING PASS** requires at least 90% AI-first completion of eligible completed tasks, at least 95% handoff closure and no unresolved integrity/control error. Operational autonomy and product-market fit are separate questions.

Default AI execution loop:

`inspect → decide → execute → verify → record → hand off`

Escalate only for a reserved human decision, genuine tool/account limitation, material ambiguity requiring human judgement, a control boundary, or repeated failure where another attempt adds no information.

## Growth / AI-gateway doctrine

Use:

`DISCOVER → TEST → SELL MANUALLY → PROVE REPEATABILITY → AUTOMATE`

Explore regulatory and adjacent expert-service markets where the same primitives apply: messy evidence, expensive expert review, repeated reconciliation, version/change control, auditability, human approval and measurable business outcomes.

Reusable primitives include evidence ingestion/provenance, entity resolution, claim/evidence graphs, contradiction/change detection, temporal/role-aware reasoning, explicit uncertainty, deterministic reconciliation, controlled generation, fail-closed review and reproducible audit trails.

Integrity Gate is the first substantial reusable product primitive built under this doctrine. Its strongest hypothesis is **change propagation**: when an approved fact changes, identify which declared downstream surfaces should change and detect where propagation is incomplete. That hypothesis remains commercially unproven until buyer evidence says otherwise.

Prefer service gateways before software gateways. Do not publish on LinkedIn, change pricing/Gumroad, create external accounts/forms, add tracking or make buyer commitments across existing approval boundaries without Ali's explicit approval.

## Standard paid-pilot operating path

Controlled path:

`qualified buyer / written scope → commercial activation → private intake → validation → bundle generation → qualified human review → final integrity verification → delivery / closeout → private learning`

```bash
clinicops-pilot-preflight /private/path/activation-record.json
clinicops-portfolio-validate /private/path/portfolio.csv
clinicops-pilot-bundle /private/path/portfolio.csv /private/path/output YYYY-MM-DD
clinicops-pilot-review-prepare /private/path/activation-record.json /private/path/output > /private/path/review-record.json
# qualified assigned reviewer actually performs review
clinicops-pilot-review-gate /private/path/activation-record.json /private/path/review-record.json /private/path/output
clinicops-pilot-verify /private/path/output /private/path/portfolio.csv
```

External client delivery requires `ACTIVATED`, `REVIEW APPROVED` and `VERIFIED`. A source, manifest or controlled-output change after review makes that review stale; regenerate/re-review rather than editing hashes or attestations.

Material client work starts only after written scope/acceptance plus upfront payment, agreed deposit/first milestone, or accepted PO/signed procurement path. Anything else is `NON-STANDARD — NOT ACTIVATED`. No open-ended unpaid work.

## Founder-independence proof — PRs #33, #35, #45, #46

Do **not** claim founder-independent execution because tooling or CI is green.

Proof requires private operational evidence showing either one qualifying real eligible paid pilot or two qualifying complete controlled dry runs with genuine qualified human review.

Primary controlled dry-run entry point:

```bash
clinicops-pilot-dry-run ...
```

Final evaluator:

```bash
clinicops-delegation-proof /private/path/delegation-proof-runs.json
```

Synthetic/canned review is smoke testing only. CI, public examples and automated attestations are ineligible. Artifact hashes prove binding, not truthfulness.

## Public production surface

`clinicops.dk` is served from `docs/**` via GitHub Pages. GoDaddy is DNS only. HTTPS is enforced.

Production canonical sitemap now contains **19 URLs**:

- `/`
- `/about.html`
- `/assessment-intake.html`
- `/authorised-representative-portfolio-intelligence.html`
- `/class-iii-transition.html`
- `/contact.html`
- `/eudamed-transition.html`
- `/identifier-check.html`
- `/integrity-gate.html`
- `/medical-device-document-control.html`
- `/privacy-notice/`
- `/readiness-score.html`
- `/regulatory-intelligence.html`
- `/research.html`
- `/research/eudamed-watch/`
- `/research/sscp-public-record-scan/`
- `/sscp-operations.html`
- `/tools.html`
- `/transition-map-sample/`

The browser-local acquisition path remains:

`public site / free tool / sanitized sample → browser-local assessment brief → user's email client → controlled private scope/intake`

`docs/assessment-intake.html` has no backend form action, analytics or tracking. User input stays local until the user explicitly creates an email draft. Keep the EUDAMED Identifier Check and Transition Readiness Score free.

Do not mass-produce thin SEO pages while current pages are still being discovered.

## Search / indexing

Canonical sitemap: `https://clinicops.dk/sitemap.xml`.

Fresh 2026-09-14 verification after PR #53:

- live sitemap fetch returns all **19** canonical production URLs, including `/integrity-gate.html`;
- homepage is the only URL currently showing settled GSC impressions (19 impressions, 2 clicks in the latest settled window used for the verification);
- the other pre-existing production URLs were inspected as `URL is unknown to Google`;
- `/integrity-gate.html` was added to the GSC Wizard indexing tracker and immediately inspected as `NEUTRAL / URL is unknown to Google`, with no crawl time yet;
- current sitemap performance is 1/19 URLs with settled GSC impressions.

Issue #28 now tracks submission of the **19-URL** canonical sitemap. The old submitted `sitemap.website.xml` remains stale at 7 submitted / 0 indexed / 1 warning / 1 error.

This is a discovery/submission bottleneck, not evidence of malformed canonical sitemap XML. Do not create thin filler pages or modify healthy XML merely because the obsolete submission is red.

The connected tools can fetch the live sitemap, inspect URLs and track indexing, but still cannot submit the sitemap in the Google Search Console UI. That remains a browser/manual action.

## EUDAMED Watch / regulatory evidence

Workflow: `.github/workflows/eudamed-watch.yml`.

Triggers remain only manual `workflow_dispatch` and monthly `17 6 1 * *`; no push trigger.

Hard public anonymisation invariant: nothing committed or printed to public CI may identify manufacturer, device, trade name, Basic UDI-DI or SS(C)P reference. Named output is local/private only. Leak tests are governance controls: fix code, never weaken the test.

Zero rows means “not findable under the tested string at that time”, never “not registered”. Missing public SS(C)P link is not evidence of non-compliance.

Public API use remains bounded GET-only with identifying User-Agent, one-second spacing and finite page cap. Re-review on endpoint/term changes, repeated 403/429, material request-volume increase or publication of raw named records. Never evade restrictions.

Commission Playground/help v3.31.2 documents manufacturer-side SS(C)P workflow concepts. Treat this as Playground/help evidence, **not proof Production rollout has occurred**.

## Privacy / claim governance

Production privacy notice is an invariant. Current posture: static GitHub Pages, no ClinicOps cookies, no analytics/tracking runtime, browser-local tools and sitemap-wide privacy links.

Do not add analytics/tracking or materially change privacy posture without Ali's explicit approval plus corresponding notice/contract updates.

Canonical claim controls include `research/claims.jsonl`, `src/clinicops_eudamed/claim_guard.py`, `src/clinicops_os/claim_registry.py` and governed claim/profile records.

Preserve:

- missing/null public SS(C)P link ≠ non-compliance;
- do not imply complete EUDAMED public-register/API coverage;
- B-prefix is structural screening only;
- preserve MF / AR / IM / PR roles;
- do not present non-binding recommendations as statutory deadlines;
- deterministic scores/gate states are operational triage/evidence states, not legal/compliance/safety conclusions;
- nothing external introduces ungoverned factual claims.

Corrected thesis: sampled MF-role MDR Class III registrations had linked validated SS(C)P metadata; opportunity is transition/document-operations workload, evidence control and reconciliation—not a generic manufacturer diligence-failure allegation.

## CI / resilience gates

Standard CI covers pytest, Ruff, revenue/agent/readiness contracts, AI-company operating contract, sample drift, site metadata, sitemap/internal links, paid-pilot gates, bundle/review/integrity checks, delegation negative control, claim registry/reference/content gates, sanitized fixtures and public-copy gate.

PR #53 additionally introduced `.github/workflows/integrity-gate.yml`, which independently exercises synthetic bundle generation, expected change hold, fail-closed human review, hash-bound synthetic review, final verification and focused Integrity Gate tests.

Exact PR #53 merge SHA `3a082987...` passed standard main CI #565, Integrity Gate #18 and Pages #23. Never weaken a gate merely to make CI green.

## Private commercial / CRM state

Buyer/prospect/outreach/client/proof records stay private and must not be copied into public GitHub.

Private outreach master was previously reported reconciled to 448 rows. Continue dedupe against the authoritative private master plus live Sent history. Treat delivery failures as send-quality evidence, not “no reply”.

Google Calendar access is working; a missing confirmed partner meeting was repaired as a local hold without inventing conferencing details.

HubSpot core CRM read/write capability is available, but the portal was sample-only/essentially unused when last checked. Do not manufacture CRM records from memory.

## External-action boundaries

Require Ali's case-by-case approval before:

- LinkedIn publishing;
- Gumroad/pricing changes;
- creating third-party accounts or live form endpoints;
- analytics/tracking deployment;
- credential revocation/rotation;
- branch-protection/ruleset changes;
- git-history rewrite.

Permanent `DO_NOT_CONTACT`: Ergomed Group and PrimeVigilance. Danish-domiciled organisations are never cold-emailed; public posting only.

## Repository governance / security

`main` remains unprotected. Green CI is an operating convention rather than an enforced merge rule.

Issue #36 tracks branch protection and least-privilege credentials. Do not change repository governance or credentials without explicit approval.

A large stale-branch set remains. D-24 has Ali's `go`, but current connector support has not established a safe delete-ref action. Do not claim cleanup occurred unless refs are actually removed.

Two harmless connector placeholder writes hit unprotected `main` on 2026-09-13 and were immediately reversed. Do not rewrite history to hide them; treat them as evidence for issue #36.

Pre-anonymisation commit `cb01b34` remains reachable and contains named watcher outputs. Default remains **do not rewrite history** unless Ali explicitly chooses a scrub after receiving exact commands and warnings.

## Budget / resilience doctrine

ClinicOps is bootstrapped. Default to low fixed cost, GitHub/Pages/current domain-mail/AI leverage, service revenue before expensive SaaS infrastructure, automation only for repeated paid-work friction, and reinvestment of validated revenue.

## Recent merged operating changes

- #45 — executable controlled dry-run harness + fail-closed human-review checklist gate.
- #46 — dry-run harness made primary proof-run path while preserving final evaluator.
- #47 — shared state and growth doctrine reconciled.
- #48 — AI Company OS, 30-day experiment and executable evidence/autonomy evaluator.
- #49 — AI Company shared-state / CI contract hardening.
- #50 — department/evidence/handoff rules embedded in all six canonical agents.
- #51 — regulatory-intelligence and medical-device-document-control production pages; sitemap 16→18.
- #52 — both new commercial pages surfaced directly from homepage.
- #53 — Integrity Gate MVP: deterministic reconciliation/change propagation, fail-closed hash-bound human review, dedicated CI and experimental production page; sitemap 18→19.

## Coordination protocol

1. Fetch `main`, open PRs/branches and Actions before work.
2. Treat `main` as canonical over chat/local state.
3. Preserve claim IDs, anonymisation, privacy and commercial boundaries.
4. Reuse existing modules before parallel logic.
5. Preserve concurrent Claude/ChatGPT work; never force-overwrite.
6. Use a fresh branch/PR for every material change.
7. Fix root causes, not gates.
8. Verify exact merged-SHA CI and Pages after public changes.
9. Keep buyer/client/proof/outreach/company-run evidence private.
10. Log AI-COMPANY-001 events honestly, including founder intervention and negative evidence.
11. Discover broadly, validate cheaply, sell manually, build narrowly.

## Highest-leverage next work

1. **Commercially validate or kill Integrity Gate.** Use the deployed synthetic demo and exact workflow in qualified discovery; look for repeated reconciliation/change-propagation pain, unprompted product pull and E6 commitment. Do not add broad features until those conversations produce evidence.
2. **Move real commercial evidence from E4 → E6+.** The system is no longer the primary bottleneck; buyer conversations, scoped commitments and activation are.
3. **Use Integrity Gate first as a manually sold, bounded service primitive.** Learn field mappings, source-authority ambiguity, reviewer effort, false positives/negatives and delivery time before platformization.
4. **Run AI-COMPANY-001 on real work** and record this build as internal execution evidence only, not demand.
5. **Submit the canonical 19-URL sitemap in the GSC UI** and monitor the indexing tracker under issue #28.
6. **Run genuine founder-independence work only with a real qualified reviewer.** Software cannot substitute for proof.
7. **Prepare security/branch cleanup**, but execute governance/credential changes only with explicit approval and actual tool capability.
8. After real buyer/delivery objections, automate only repeated evidenced friction.
