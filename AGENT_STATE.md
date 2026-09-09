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
- Read-only EUDAMED API client and bounded reachability canary.
- Opportunity, prospect and resilience scoring.
- Portfolio transition report with MF/PR-aware segmentation, certificate-timing triage, Danish-market relevance and evidence cautions.
- Portfolio intake validator for missing/contradictory evidence before human review.
- Machine-readable portfolio JSON contract (`schema_version` 1.0) using the same ordered analysis as the Markdown report.
- Sanitized portfolio CSV, Markdown and JSON fixtures with deterministic drift checks.
- Canonical Class III Transition Map offer specification.
- Canonical transition-focused homepage deployment pack under `website/homepage-v2.md`.
- Internal anonymised class III transition research-note draft.
- Internal Obelis transition-work-plan conversation brief.
- Internal source-locked C-10/24 LinkedIn correction pack.
- 16-loop on-demand fleet specification; not 16 scheduled jobs.
- Client-side Identifier Check under `docs/`.
- CI gates: pytest, Ruff, claim-registry audit, claim-reference integrity, governed-content claim validation, sanitized report fixtures and public-copy claim guard.

## GitHub custom agents
Three repository-scoped Copilot agent profiles live under `.github/agents/`:

1. **Regulatory Evidence Steward** — primary-source verification, claim lifecycle, corrections and publication evidence gates.
2. **Portfolio Operator** — intake validation, transition analysis, deterministic reports, JSON handoffs and pilot bundles.
3. **Release Sentinel** — CI/deployment health, generated artifacts, rollback discipline and scheduled operational checks.

These profiles are specialization/instruction layers. Their existence does **not** mean they are continuously running. Unattended recurring work is implemented separately through GitHub Actions.

## GitHub automation
`.github/workflows/ops-watch.yml` runs weekly on Monday at 06:13 UTC and can also be dispatched manually.

It performs only two bounded unattended jobs:

- **Evidence freshness** — claim-registry review dates, claim-reference integrity and governed-content claim validation. Expired/error-level evidence gates fail the workflow rather than silently allowing stale claims.
- **EUDAMED reachability canary** — probes pages 0, 30,000 and 32,000 of the bounded public route, writes a timestamped JSON contract to the job, and uploads the snapshot as a 90-day workflow artifact. Canary output is operational evidence only, never a compliance signal or full-register claim.

No GitHub agent/workflow is authorized to publish regulatory conclusions, send emails, modify LinkedIn, change the public website, or create client-specific compliance allegations autonomously.

## Last fully verified baseline
Commit `6158eff59e00264afe38530e75d11a6ad7e57069` passed the full CI chain on 9 Sep 2026 after the three-agent/weekly-ops-watch rollout: tests, Ruff, claim-registry audit, claim-reference integrity, governed website-copy validation, sanitized Markdown/JSON fixture validation and public-copy claim gate.

## Known manual dependencies
1. GitHub Pages repository enablement is still required once. It is tracked in issue #1. Do not introduce a second hosting stack merely to bypass this one-time setting.
2. Opera Browser Connector is not currently reachable by ChatGPT even when the user reports it connected; browser-dependent GoDaddy, clinicops.dk, LinkedIn and Gumroad changes remain deferred until the connector returns tabs successfully.

## Claude / ChatGPT / Copilot coordination
Before changing shared files:
1. Fetch `main` first.
2. Treat this repo as canonical over local merged ZIPs.
3. Prefer focused commits over wholesale replacement.
4. Preserve corrections, claim IDs and evidence limitations.
5. If a write receives HTTP 409, fetch the newest file and merge rather than force-overwriting concurrent work.
6. Run CI after code or generated-output changes.
7. Use `clinicops-portfolio-json` / `examples/portfolio_report.json` for machine handoffs instead of reparsing Markdown where practical.
8. Use the narrowest relevant custom agent rather than a general-purpose agent when delegating GitHub work.
9. Update this file only when the operational truth materially changes.

## Current commercial thesis
ClinicOps sells **accountable regulatory judgement around legacy-to-MDR transition, SS(C)P/document operations and portfolio work planning**. Automation is the inexpensive screening/front-door layer.

The default buyer-validation sequence is:
`portfolio export → evidence validation → role-aware segmentation → priority queue → evidence ledger → human-reviewed action plan`

Do not revert to a manufacturer-diligence-failure narrative without new evidence and a dated correction.

## Next high-leverage work
1. Validate the Class III Transition Map in real portfolio conversations before building a larger dashboard.
2. Keep improving intake/report reliability around actual buyer data shapes, while preserving a stable JSON handoff contract.
3. Convert only claim-registry-approved research into external content.
4. Use the weekly Ops Watch for evidence aging/API reachability; do not add higher-frequency probes without a demonstrated operational need.
5. Keep raw named-device, prospect and client data out of the public repo by default.
6. When browser access works, verify GoDaddy/email continuity first, then implement `website/homepage-v2.md`, then handle LinkedIn correction/Gumroad optimization.
