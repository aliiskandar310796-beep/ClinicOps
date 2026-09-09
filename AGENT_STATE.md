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
- Sanitized portfolio CSV, Markdown and JSON fixtures with deterministic drift checks.
- Canonical Class III Transition Map offer specification.
- Canonical transition-focused homepage deployment pack under `website/homepage-v2.md`.
- ClinicOps.dk visibility plan plus focused landing-page deployment packs under `website/`.
- Internal anonymised class III transition research-note draft.
- Internal Obelis transition-work-plan conversation brief.
- Internal source-locked C-10/24 LinkedIn correction pack.
- 16-loop on-demand fleet specification; not 16 scheduled jobs.
- Client-side Identifier Check under `docs/`.
- Experiment ledger under `experiments/EXPERIMENT_LEDGER.md`.
- Revenue OS: coverage-aware commercial account prioritisation in `src/clinicops_os/revenue.py`, sanitized fixture `examples/revenue_accounts.csv`, tests, `clinicops-revenue-rank` JSON CLI, operating contract in `revenue/README.md`, and Claude continuation handoff in `revenue/CLAUDE_HANDOFF.md`.
- CI gates: pytest, Ruff, custom-agent profile audit, claim-registry audit, claim-reference integrity, governed-content claim validation, sanitized report fixtures and public-copy claim guard.
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

The CLI handoff is:

```bash
clinicops-revenue-rank <accounts.csv>
```

It emits a versioned JSON object with score coverage, priority band and next experiment so ChatGPT, Claude, Copilot and future tooling can share the same commercial semantics without reparsing prose.

## GitHub automation
`.github/workflows/ops-watch.yml` runs weekly on Monday at 06:13 UTC, can be dispatched manually, and self-tests when the canary/evidence automation files change.

It performs only two bounded unattended jobs:

- **Evidence freshness** — claim-registry review dates, claim-reference integrity and governed-content claim validation. Expired/error-level evidence gates fail the workflow rather than silently allowing stale claims.
- **EUDAMED reachability canary** — probes pages 0, 30,000 and 32,000 of the bounded public route, writes a timestamped JSON contract, compares the result with the reviewed baseline, and uploads the snapshot as a 90-day workflow artifact. Page-0 loss is treated as an error; deep-offset behavior changes are review warnings rather than compliance signals.

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

## Last verified baselines
- Commit `16efcc15f60bf45bb9775802de1afc715ee7d4fc` passed the full CI job on 9 Sep 2026 after Revenue OS implementation and the Claude handoff were added. The chain included 54 pytest tests, Ruff, custom-agent audit, claim registry/reference checks, governed content, sanitized fixtures and the public-copy gate.
- Commit `de1dc92a93bc57e4535d5811d338e1f13c769d87` passed both the full CI chain and drift-aware `Ops Watch` on 9 Sep 2026.
- Commit `611833caaad884a9720c892ad80a88821693b09e` passed CI after repository-wide Copilot/agent instructions were added.

## Known manual dependencies
1. GitHub Pages repository enablement is still required once. It is tracked in issue #1. Do not introduce a second hosting stack merely to bypass this one-time setting.
2. Browser/account execution for GoDaddy, clinicops.dk, LinkedIn and Gumroad can be delegated to Claude when it has working account access. These surfaces are not a blocker for GitHub-native Revenue OS, portfolio, evidence, research or visibility development.

## Claude / ChatGPT / Copilot coordination
Before changing shared files:
1. Fetch `main` first.
2. Treat this repo as canonical over local merged ZIPs.
3. Prefer focused commits over wholesale replacement.
4. Preserve corrections, claim IDs and evidence limitations.
5. If a write receives HTTP 409, fetch the newest file and merge rather than force-overwriting concurrent work.
6. Run CI after code or generated-output changes.
7. Use `clinicops-portfolio-json` / `examples/portfolio_report.json` for portfolio machine handoffs instead of reparsing Markdown where practical.
8. Use `clinicops-revenue-rank` and `revenue/README.md` for commercial prioritisation semantics; keep real prospect data private.
9. Use the narrowest relevant custom agent rather than a general-purpose agent when delegating GitHub work.
10. Treat `.github/copilot-instructions.md`, `AGENTS.md`, `AGENT_STATE.md` and `CLAIM_RULES.md` as the shared doctrine floor.
11. Update this file only when the operational truth materially changes.

## Current commercial thesis
ClinicOps sells **accountable regulatory judgement around legacy-to-MDR transition, SS(C)P/document operations and portfolio work planning**. Automation is the inexpensive screening/front-door layer.

The buyer-validation loop is now:
`signal → commercial evidence → Revenue OS ranking → smallest buyer experiment → portfolio export → evidence validation → role-aware segmentation → priority queue → evidence ledger → human-reviewed action plan → measured learning`

Do not revert to a manufacturer-diligence-failure narrative without new evidence and a dated correction.

## Next high-leverage work
1. Operationalise Revenue OS against a small private set of real AR/consultancy/manufacturer accounts and run 3–5 high-information experiments rather than mass outreach.
2. Validate the Class III Transition Map in real portfolio conversations before building a larger dashboard.
3. Keep improving intake/report reliability around actual buyer data shapes while preserving stable JSON handoff contracts.
4. Convert only claim-registry-approved research into external content and feed results into EXP-002.
5. Use the weekly Ops Watch for evidence aging/API reachability; do not add higher-frequency probes without a demonstrated operational need.
6. Keep raw named-device, prospect and client data out of the public repo by default.
7. When external browser/account execution is available, verify live clinicops.dk indexing/SEO changes and LinkedIn/Gumroad updates; record only verified changes.
