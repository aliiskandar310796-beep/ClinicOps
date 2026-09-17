# ClinicOps shared agent state

Last reconciled: 2026-09-17 after the expanded-portfolio stabilisation pass (fixture/deploy-gating/routing fixes on top of 554463c). The public site now presents 29 canonical URLs and multiple service lanes; this file's thesis section reflects that deliberately.

## Canonical truth

GitHub `main` is the shared source of truth. Fetch current `main`, open PRs/branches and current Actions before substantive work. Preserve concurrent Claude/ChatGPT work and never force-overwrite a newer change. Chat transcripts, local copies and project-side control files are secondary until their changes land here.

Do **not** hard-code a self-referential “current main SHA” as permanent truth in this file because its own merge changes `main`. Historical anchor only: PR #48 merged as `eeee68d8…` with exact-main CI run #512 green (2026-09-13); many merges have landed since — always fetch live state again before acting. PR #54 was closed 2026-09-17 as superseded: its outcome/risk/economic controls were selectively ported onto current main (with a fail-closed fix to the economic evaluator) and its stale shared-state changes dropped.

## Current business thesis

ClinicOps is an evidence-controlled, human-reviewed operating layer for high-value expert work: it controls how regulated evidence moves across documents, systems, markets and accountable human owners.

**Long-term category (2026-09-17): QA/RA Operations Engineering for regulated healthcare/MedTech**, with Regulatory Information Integrity as the proven first wedge. Quality Operations (change control → CAPA/NC evidence integrity → regulatory change impact → technical-file integrity → QA data integrity → PMS/complaints → SaMD verification operations) is the internal capability frontier — developed in that adjacency order, internal-only until each capability earns a public offer via the progression rule: learn → primary-source model → internal schema → sanitized prototype → design partner → controlled delivery → delivery evidence → repeat demand → public offer.

**Current portfolio (deliberate, 2026-09-17): multiple live service lanes.** Do not "correct" the site back to a single-offer state — the breadth is intentional. The lanes are:

- **Default cross-domain commercial entry:** Regulatory Integrity Review / Evidence Change Control Pack around one bounded real workflow. Every lane funnels into this one paid entry.
- **Strongest existing wedges (most buyer evidence so far):** MedTech / EUDAMED / Class III transition; Denmark market access / Danish PV / localisation.
- **Adjacent service lanes (live, less validated):** TrialOps, QualityOps, Clinical AI evidence review, LabOps, Clinic Operations, controlled medical content.

**Validation rule: availability ≠ proven demand.** Each lane earns stronger investment only through real buyer evidence (the EXP-001 ladder below applies per lane). Do not claim all lanes are equally validated, and do not let breadth become confusion: one umbrella operating model, one obvious default paid entry.

Commercial validation outranks speculative product development.

### EXP-001 validation threshold

Do not call the core offer validated until all of the following occur:

1. three qualified portfolio conversations;
2. at least two independent confirmations of repeated reconciliation / evidence-control pain addressed by the offer; and
3. at least one concrete commercial commitment such as a priced-scope request, proposed/paid pilot, procurement step or identifiable budget/approval owner.

Compliments, clicks, drafts, synthetic runs and CI do not count.

If ten qualified target-buyer conversations produce no concrete willingness to sponsor a pilot, no priced-scope request and no repeated evidence of budgeted urgency, pause product expansion and change at least one of buyer, problem, offer, packaging or distribution before building more functionality.

## AI Company OS — PR #48

ClinicOps is now explicitly testing whether nearly the entire company can run AI-first while preserving commercial truth and human/regulatory controls.

Canonical architecture:

- `06_AGENTS/AI_COMPANY_OS.md`
- `03_OPERATIONS/AI_COMPANY_EXPERIMENT.md`
- `src/clinicops_os/company_run.py`
- `examples/ai_company_run.example.json` — synthetic only

The six existing custom agents remain canonical. Departments are workflow lanes, **not a second agent fleet**:

- Executive Orchestration — shared AI control layer;
- Market & Regulatory Intelligence — Regulatory Evidence Steward;
- Revenue & Opportunity — Opportunity Architect;
- Customer Discovery & Partnerships — Customer Discovery Agent;
- Growth & Distribution — Visibility Architect;
- Client Delivery — Portfolio Operator;
- Quality, Engineering & Resilience — Release Sentinel;
- Commercial Control — Opportunity Architect + Release Sentinel;
- Human Governance — Ali + assigned qualified reviewers for reserved decisions.

The company loop is:

`signal → qualification → experiment → buyer action → conversation → commitment → activation → delivery → review → payment/expansion → learning`

### Commercial evidence ladder

- `E0` internal hypothesis — not commercial evidence;
- `E1` external market/regulatory signal — not buyer evidence;
- `E2` qualified reachable buyer/account — not buyer evidence;
- `E3` verified demand test delivered — execution evidence only;
- `E4` human buyer response / qualified conversation — real commercial evidence;
- `E5` repeated pain/workflow/consequence confirmed — real commercial evidence;
- `E6` priced-scope request, proposed pilot, procurement step or identifiable budget/approval owner — concrete commercial signal;
- `E7` commercially activated paid work / accepted PO or equivalent activation path;
- `E8` accepted delivery and/or payment evidence;
- `E9` repeat purchase, expansion, renewal or qualified referral caused by delivered value.

No event may be recorded at `E4+` without a private evidence reference.

### AI-COMPANY-001

Run real company events privately and evaluate with:

```bash
clinicops-company-run /private/path/company-run.json
```

Operational autonomy and product-market fit are separate questions.

An **AI OPERATING PASS** requires:

- at least 90% of completed non-reserved tasks completed AI-first without founder transaction-level intervention;
- at least 95% handoff closure;
- no unresolved integrity/control error.

Strong commercial proof still requires external evidence. A synthetic example, green CI or an AI-generated score cannot prove revenue, product-market fit, founder independence or qualified human review.

The default AI execution loop for non-reserved tasks is:

`inspect → decide → execute → verify → record → hand off`

Escalate only for a policy-reserved human decision, genuine tool/account limitation, material ambiguity requiring human judgement, a control boundary, or repeated failure where another attempt adds no information.

## Growth / AI-gateway doctrine

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

The long-term direction is an **evidence-controlled AI operating layer for valuable expert work**, proven first where ClinicOps has credibility and expanded only where market evidence earns the right to expand.

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

PR #45 added the executable dry-run harness. PR #46 made it the primary operator entry point:

```bash
clinicops-pilot-dry-run ...
```

Use `sales/pilot-dry-run-harness.md` and `sales/delegation-proof-protocol.md` together. A canned/synthetic review record is only a mechanical smoke test. A proof-eligible run requires a genuine qualified human reviewer and private operational records. CI, automated smokes, public examples and auto-attestation are ineligible.

### Final evaluator

`clinicops-delegation-proof` remains the final evaluator:

```bash
clinicops-delegation-proof /private/path/delegation-proof-runs.json
```

Only `FOUNDER-INDEPENDENT EXECUTION PROVEN` permits the internal claim.

Proof schema 1.1 requires SHA-256 bindings to the exact activation record, saved preflight result, completed review record, review-gate result, final manifest, final bundle-verification result and source input. Two dry runs cannot qualify if they reuse the same full artifact fingerprint. Hashes prove binding, not truthfulness.

No qualifying founder-independence proof has yet been recorded merely by merging tooling.

## Agent taxonomy (canonical, 2026-09-17)

Three layers, not three competing fleets:

1. **Core accountable business agents (6, canonical)** — the named agents in `06_AGENTS`/department mapping (Regulatory Evidence Steward, Opportunity Architect, Customer Discovery Agent, Visibility Architect, Portfolio Operator, Release Sentinel). Accountability and department ownership live here.
2. **Specialist profiles (`.github/agents/*.agent.md`, currently 8)** — sentinels/builders operating *under* the core agents (the 6 above plus specialist additions such as validation-scalability-sentinel and asset-fleet-builder). They add capability, not accountability.
3. **Operational loops (`agents/fleet.json`, currently 16)** — bounded recurring tasks/automation roles (radars, canaries, miners, triage). These are legacy-named automation loops, **not** accountable agents; they run under a core agent's remit and their sends/posts always route through the top-level session per E-007.

`competitor-radar` is renamed **`peer-market-radar`** (2026-09-17): ClinicOps treats Visiana/BoneXpert, consultancies, CROs and QA/RA teams as peers, benchmarks, partners and possible buyers — never adversaries. It observes public hiring, buying patterns, operational pain and tooling adoption to find white space; it never uses non-public information, and hiring demand counts as E1 market evidence only, never buyer validation.

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

## CI / resilience gates

Current CI covers pytest, Ruff, revenue/agent/readiness contracts, the AI-company operating contract, public sample drift, site metadata, sitemap/internal links, paid-pilot gates, bundle/review/integrity checks, delegation negative control, claim registry/reference/content gates, sanitized fixtures and the public-copy claim gate.

PR #48 exact-main CI run #512 passed. The AI-company synthetic example is a contract/smoke only and explicitly cannot count as commercial evidence, revenue, founder-independence proof or qualified human review.

Never weaken a gate merely to make CI green.

Ops Watch remains bounded/read-only and covers evidence freshness, claim/reference checks, EUDAMED reachability and live HTTPS/content checks. Public research pages are under the live-check contract.

## Private commercial / CRM state

Private buyer/prospect/outreach records stay private and must not be copied into this public repository.

Claude project-side work reports the fragmented outreach master/addenda have been reconciled privately into a 448-row master. Continue send dedupe against the authoritative private master plus live Sent history.

A confirmed delivery failure was identified on 2026-09-13 for one 12 September outreach address. Treat delivery failures as send-quality evidence rather than “no reply” in the private master. Do not put the prospect identity/address here.

Google Calendar access is working. A missing confirmed-partner meeting was repaired as a local calendar hold without inviting external attendees or inventing conferencing details.

HubSpot contact/company/deal/task/call/meeting/note and one-to-one email read/write capability is available; the portal is essentially unused/sample-only and site-page write still requires reauthorization. Do not manufacture CRM pipeline records from memory.

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

A large stale-branch set remains. D-24 identified merged/abandoned branches safe to delete, but current connector support has not established a safe branch-delete path. Do not claim cleanup occurred unless refs are actually removed.

### Write-discipline incidents — 2026-09-13

Two connector mistakes wrote harmless placeholder files directly to unprotected `main`; both were detected immediately and removed before further work. No intended repository content changed, but the extra commits remain in history. Treat this as evidence for issue #36: material writes must use a fresh branch/PR, and target branch must be verified before every connector write.

Do not rewrite history merely to hide these incidents.

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
- #46 — dry-run harness made primary proof-run path while preserving final evaluator.
- #47 — shared state and growth doctrine reconciled.
- #48 — AI Company OS, 30-day operating experiment and executable commercial-evidence/autonomy evaluator.

## Coordination protocol

1. Fetch `main`, open PRs, branches and current Actions before work.
2. Treat `main` as canonical over chat/local state.
3. Preserve claim IDs, anonymisation, privacy and commercial boundaries.
4. Reuse existing modules before parallel logic.
5. Preserve concurrent Claude/ChatGPT work; never force-overwrite.
6. Fresh branch/PR for every material change.
7. Fix root causes, not gates.
8. Verify exact merged-SHA CI before declaring green; verify live Pages/Ops Watch after public changes.
9. Keep buyer/client/proof/outreach/company-run evidence private.
10. Log real AI-COMPANY-001 events honestly, including founder interventions and negative market evidence.
11. Discover broadly, validate cheaply, sell manually, build narrowly.

## Highest-leverage next work

1. **Run AI-COMPANY-001 on real private work.** Route live commercial, research, delivery and coordination events through the department model and record founder interventions instead of hiding them.
2. **Real commercial evidence remains the primary bottleneck.** Use qualified conversations, partnership mechanics and concrete commitments to move `E4 → E6+`; do not optimize send volume.
3. **Run genuine founder-independence work only with a real qualified human reviewer.** The harness is ready; software alone cannot supply proof.
4. **Submit the canonical 16-URL sitemap in GSC** and diagnose the obsolete sitemap warning/error under issue #28.
5. **Use the AI-gateway mandate to discover new revenue paths** across regulatory and adjacent expert-service markets, but keep them in DISCOVER/TEST until buyer evidence justifies manual selling/building.
6. **Prepare security/branch cleanup, but execute governance/credential changes only with explicit approval and actual tool capability.**
7. After real delivery/buyer objections, automate only repeated evidenced friction.
