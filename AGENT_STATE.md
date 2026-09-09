# ClinicOps shared agent state

Last updated: 2026-09-09 by ChatGPT.

## Canonical truth
This GitHub repository is the shared source of truth. Local ZIPs and chat transcripts are secondary until their changes land here.

## What is live in the repo
- Corrected 8 Sep 2026 class III headline reversal and primary-source registry.
- Versioned claim registry with evidence class, allowed uses, limitations, review dates and supersession.
- Claim guard, publication gate and claim-ID publication-pack builder.
- Governed website copy whose declared claim IDs are checked against allowed website use and review dates.
- Identifier screening, GS1 structural checks and SRN actor-role decoder.
- Read-only EUDAMED API client, bounded reachability canary, reviewed canary baseline and drift evaluator.
- Opportunity, prospect and resilience scoring.
- Portfolio transition report with MF/PR-aware segmentation, certificate-timing triage, Danish-market relevance and evidence cautions.
- Portfolio intake validator for missing/contradictory evidence before human review.
- Machine-readable portfolio JSON contract (`schema_version` 1.0) using the same ordered analysis as the Markdown report.
- Pilot bundle contract `1.1` with `client_report.html`, Markdown, JSON, intake diagnostics, source SHA-256 and generated-output SHA-256 values.
- Sanitized portfolio CSV, Markdown and JSON fixtures with deterministic drift checks.
- Canonical Class III Transition Map offer specification.
- Canonical transition-focused homepage deployment pack under `website/homepage-v2.md`.
- ClinicOps.dk visibility plan plus focused landing-page deployment packs under `website/`.
- Internal anonymised class III transition research-note draft.
- Internal Obelis transition-work-plan conversation brief.
- Internal source-locked C-10/24 LinkedIn correction pack.
- 16-loop on-demand fleet specification; not 16 scheduled jobs.
- Client-side Identifier Check under `docs/`, deployed through GitHub Pages.
- Experiment ledger under `experiments/EXPERIMENT_LEDGER.md`.
- Revenue OS account prioritisation in `src/clinicops_os/revenue.py`, sanitized fixture `examples/revenue_accounts.csv`, tests and `clinicops-revenue-rank` JSON CLI.
- Executable commercial experiment registry in `src/clinicops_os/experiments.py`, sanitized fixture `examples/experiments.json`, tests and `clinicops-experiments` JSON CLI.
- Revenue/experiment operating contracts under `03_OPERATIONS/`, including explicit success thresholds, kill conditions and learning capture.
- Client onboarding workflow under `01_PRODUCT/CLIENT_ONBOARDING_WORKFLOW.md`.
- Service-first deployment architecture under `01_PRODUCT/MVP_DEPLOYMENT_ARCHITECTURE.md`.
- Lean cross-system data model under `01_PRODUCT/KNOWLEDGE_GRAPH_SPEC.md`.
- GitHub Issue Form under `.github/ISSUE_TEMPLATE/experiment.yml` for real, bounded commercial experiments without private prospect/client data.
- CI gates: pytest, Ruff, Revenue OS experiment-contract smoke, client-bundle smoke, custom-agent profile audit, claim-registry audit, claim-reference integrity, governed-content claim validation, sanitized report fixtures and public-copy claim guard.
- Repository-wide agent doctrine under `.github/copilot-instructions.md` and `AGENTS.md`.

## GitHub custom agents
Six repository-scoped Copilot agent profiles live under `.github/agents/`:

1. **Regulatory Evidence Steward** — primary-source verification, claim lifecycle, corrections and publication evidence gates.
2. **Portfolio Operator** — intake validation, transition analysis, deterministic reports, JSON handoffs and pilot bundles.
3. **Release Sentinel** — CI/deployment health, generated artifacts, rollback discipline and scheduled operational checks.
4. **Opportunity Architect** — evidence-backed opportunities, experiments, kill criteria and Revenue OS prioritisation.
5. **Customer Discovery Agent** — structured buyer learning, objections, willingness signals and evidence-backed Revenue OS updates.
6. **Visibility Architect** — claim-approved research-to-SEO, website, partner and content assets.

These profiles are specialization/instruction layers. Their existence does **not** mean they are continuously running. Unattended recurring work is implemented separately through GitHub Actions.

Do not add another agent when one of these six can absorb the capability. Expand capability before fleet size.

`Release Sentinel` also protects `research/canary/baseline.json` from silent drift: a baseline change must be reviewed and, when material, accompanied by a dated correction/method note and claim-registry update rather than merely following the latest observed behavior.

## Revenue OS operating boundary
Revenue OS implements:

`commercial signal → evidence coverage → ranked account → smallest commercial experiment → result → learning`

The score is for commercial learning and pilot selection only. It is **not** regulatory, compliance, legal, enforcement, or manufacturer risk.

Unknown commercial values stay unknown. Budget, access, urgency and offer-fit fields must not be guessed to improve a ranking.

Real account/prospect working sets remain private. Public GitHub may contain sanitized fixtures and aggregated learnings only.

Machine handoffs:

```bash
clinicops-revenue-rank <accounts.csv>
clinicops-experiments <experiments.json>
```

The account CLI emits versioned JSON with score coverage, priority band and next experiment. The experiment CLI enforces planned/running/completed/cancelled state plus predeclared success and kill thresholds; completed experiments must record result, learning and a decision.

## Client-delivery operating boundary
The current deployment strategy is service-first rather than SaaS-first:

`clinicops.dk acquisition → controlled private intake → ClinicOps validation/analysis → human regulatory review → secure client bundle → feedback → Revenue OS learning`

The immediate client access layer is pilot bundle schema `1.1`:

- `client_report.html` — self-contained, print-friendly client view;
- `portfolio_report.md` — review/handoff view;
- `portfolio_report.json` — stable machine-readable projection;
- `intake_diagnostics.md` — structural and evidence gaps;
- `manifest.json` — source hash, output hashes, schema version and interpretation boundary.

Confidential client bundles do not belong on public GitHub Pages or in public GitHub Actions. Public Actions test code and sanitized fixtures only.

Build an authenticated portal only when repeated paid engagements prove recurring upload, multi-user access, action tracking, machine integration or secure document-exchange demand. The future portal should wrap the existing JSON/bundle contracts rather than replacing them.

## GitHub automation
`.github/workflows/ops-watch.yml` runs weekly on Monday at 06:13 UTC, can be dispatched manually, and self-tests when the canary/evidence automation files change.

It performs only two bounded unattended jobs:

- **Evidence freshness** — claim-registry review dates, claim-reference integrity and governed-content claim validation. Expired/error-level evidence gates fail the workflow rather than silently allowing stale claims.
- **EUDAMED reachability canary** — probes pages 0, 30,000 and 32,000 of the bounded public route, writes a timestamped JSON contract, compares the result with the reviewed baseline, and uploads the snapshot as a 90-day workflow artifact. Page-0 loss is treated as an error; deep-offset behavior changes are review warnings rather than compliance signals.

CI additionally smoke-tests the Revenue OS experiment fixture and generates a sanitized pilot bundle with a non-empty `client_report.html` and bundle schema `1.1`.

No GitHub agent/workflow is authorized to publish regulatory conclusions, send emails, modify LinkedIn, change the public website, or create client-specific compliance allegations autonomously.

## Live canary correction — 9 Sep 2026
The first live Ops Watch run (`34352492799`) did **not** reproduce the 8 Sep apparent page-32,000 reachability wall.

At `2026-09-09T12:42:04Z` the public `udiDiData` route returned HTTP 200 and 50 records at pages 0, 30,000 and 32,000. The page-32,000 request took about 13.3 seconds versus about 0.55 seconds at page 0.

Operational consequence:
- the 8 Sep failure remains a valid dated observation;
- it must not be described as a stable API boundary;
- `CO-CLM-0011` records the 9 Sep reversal;
- `research/corrections/2026-09-09-api-reachability-update.md` is the canonical correction note;
- future canaries compare reachability shape against `research/canary/baseline.json` rather than hard-coding the discarded ~32k-wall inference.

## GitHub Pages status
GitHub Pages is now enabled and the client-side Identifier Check deployed successfully.

- Successful deployment run: `34354035445` (`Deploy Identifier Check`).
- Public URL documented in `README.md`: `https://aliiskandar310796-beep.github.io/ClinicOps/`.
- The previous one-time Pages enablement blocker is resolved.

Do not use Pages for confidential client bundles.

## Last verified baselines
- Commit `f80e10553f84e3175168c8a2f007d79355ad681e` passed the full CI chain on 9 Sep 2026 (run `34369294611`): **60 pytest tests**, Ruff, Revenue OS experiment-contract smoke, client-bundle smoke, custom-agent audit, claim registry/reference checks, governed content, sanitized fixtures and the public-copy gate.
- The preceding service-first client-delivery commit `11cb504fa7ac85408c76c3759fa5083f929eaef7` intentionally exposed a Ruff `TRY004` defect in the new experiment loader; the defect was fixed by using explicit `TypeError` semantics and adding regression tests. Preserve this as normal validation history rather than hiding the failed run.
- Commit `de1dc92a93bc57e4535d5811d338e1f13c769d87` passed both the full CI chain and drift-aware `Ops Watch` on 9 Sep 2026.
- Pages deployment run `34354035445` completed successfully on 9 Sep 2026.

## Known manual/external dependencies
1. Browser/account execution for GoDaddy, clinicops.dk, LinkedIn and Gumroad can be delegated to Claude when it has working account access. These surfaces are not blockers for GitHub-native Revenue OS, portfolio, evidence, research or client-delivery development.
2. Live client engagements require an approved controlled workspace for confidential source files and reviewed deliverables. Do not substitute this public repository for client document storage.

## Claude / ChatGPT / Copilot coordination
Before changing shared files:
1. Fetch `main` first.
2. Treat this repo as canonical over local merged ZIPs.
3. Prefer focused commits; use atomic multi-file Git commits when changes form one contract or deployment unit.
4. Preserve corrections, claim IDs and evidence limitations.
5. If a write receives HTTP 409, fetch the newest file and merge rather than force-overwriting concurrent work.
6. Run CI after code, workflow, contract or generated-output changes and verify the newest run before declaring green.
7. Use `clinicops-portfolio-json` / `examples/portfolio_report.json` for portfolio machine handoffs instead of reparsing Markdown where practical.
8. Use `clinicops-revenue-rank` for commercial account semantics and `clinicops-experiments` for experiment state; keep real prospect/client data private.
9. Use `clinicops-pilot-bundle` schema `1.1` for client-delivery generation and preserve manifest hashes.
10. Use GitHub Issue Forms selectively for real experiments, reproducible defects and genuine blockers; do not turn GitHub into a noisy CRM.
11. Use the narrowest relevant custom agent rather than a general-purpose agent when delegating GitHub work.
12. Treat `.github/copilot-instructions.md`, `AGENTS.md`, `AGENT_STATE.md` and `CLAIM_RULES.md` as the shared doctrine floor.
13. Update this file only when the operational truth materially changes.

## Current commercial thesis
ClinicOps sells **accountable regulatory judgement around legacy-to-MDR transition, SS(C)P/document operations and portfolio work planning**. Automation is the inexpensive screening/front-door layer.

The buyer-validation and delivery loop is now:
`signal → commercial evidence → Revenue OS ranking → smallest buyer experiment → controlled portfolio intake → evidence validation → role-aware segmentation → priority queue → human regulatory review → secure client bundle → measured client learning`

Do not revert to a manufacturer-diligence-failure narrative without new evidence and a dated correction.

## Next high-leverage work
1. Run 3–5 high-information experiments against a small private set of real AR/consultancy/manufacturer accounts; avoid mass outreach.
2. Deliver the first paid or design-partner Class III Transition Map using bundle schema `1.1` and capture every data-shape/review friction point.
3. Build portal features only from repeated client friction observed in real engagements.
4. Convert only claim-registry-approved research into external content and feed attributable outcomes into the experiment registry.
5. Keep improving intake/report reliability while preserving stable JSON and bundle contracts.
6. Use the weekly Ops Watch for evidence aging/API reachability; do not add higher-frequency probes without a demonstrated operational need.
7. Keep raw named-device, prospect and client data out of the public repo by default.
8. When external browser/account execution is available, verify live clinicops.dk indexing/SEO changes and LinkedIn/Gumroad updates; record only verified changes.
