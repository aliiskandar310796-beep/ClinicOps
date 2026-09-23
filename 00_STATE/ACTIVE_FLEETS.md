# Active Fleets

> Migrated verbatim from the pre-2026-09-23 `AGENT_STATE.md` monolith as part of the connectome-lens shard proposal (draft, not yet reconciled against live `main`). Content below this line is unedited from the original section.

## Active outcome fleets — 2026-09-19

Two temporary mission fleets are active under the canonical-agent / worker-recruitment model:

1. **DISCOVERY-8** — accountable owner: Visibility Architect. Objective: raise search/discoverability to an evidence-backed 8/10 under `04_GROWTH/DISCOVERABILITY_COMMERCIAL_EVIDENCE_FLEETS_2026-09-19.md`. An 8/10 state requires current entity consistency, priority indexing, non-branded discovery and a qualified discovery action; impressions/page count cannot award the score.
2. **COMMERCIAL-8** — accountable owner: Customer Discovery Agent, with Opportunity Architect / Visibility Architect / Release Sentinel handoffs. Objective: raise flagship commercial evidence to an evidence-backed 8/10. The score is capped below 8 until a real **E7 activated paid engagement** exists.

These are two of the maximum three top-level active missions. Preserve the third slot for live delivery, urgent resilience or a time-sensitive external event.

Public-safe machine-contract examples:
- `examples/discoverability_fleet_mission.example.json`
- `examples/commercial_evidence_fleet_mission.example.json`

Real account, search-console, buyer-response, commercial-stage and activation evidence stays private.

Initial P0 discoverability defect: externally visible ClinicOps company/profile surfaces are not fully reconciled and stale/duplicate identity signals can appear in search. Treat canonical entity reconciliation and current indexing baseline as acquisition work, not cosmetic brand cleanup.

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

