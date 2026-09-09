# ClinicOps shared agent state

Last updated: 2026-09-09 by ChatGPT.

## Current GitHub truth
This repository is the canonical shared state. Chat transcripts and locally produced ZIPs are secondary until their changes are committed here.

### Implemented in GitHub
- Standing regulatory claim rules and dated 8 Sep headline-reversal record.
- Primary-source registry.
- Read-only EUDAMED API client, identifier screening, issue-date currency helper.
- Evidence/publication gate and claim guard.
- Opportunity scoring, prospect scoring, resilience scoring.
- AR/manufacturer portfolio transition report generator.
- Machine-readable 16-loop fleet specification; these are on-demand operating loops, not 16 scheduled jobs.
- GitHub Actions CI: pytest, Ruff, and public-copy claim-gate smoke test.
- Collaboration contract and operating changelog.

## Claude coordination note
Claude reported a richer merged local build with 43 files, 27 green tests, a standalone `docs/` EUDAMED Identifier Check, SRN-aware tooling, API notes, Pages workflow, and additional fixes. Those assets should be considered **proposed/locally verified** until their actual files or commits appear in this repository.

When Claude next works on the repo:
1. Fetch/rebase from `main` first.
2. Compare the local merged build against this repo; do not overwrite newer claim rules or corrections blindly.
3. Prefer adding the missing richer assets (`docs/`, SRN-aware utilities, extra tests, Pages deployment) as focused commits.
4. Run the shared CI before handing back.
5. Update this file and `CHANGELOG.md` with what actually landed.

## Next highest-leverage gaps
1. Land/verify the standalone EUDAMED Identifier Check under `docs/` and enable Pages deployment.
2. Add SRN/actor-role decoder and its tests if not already present.
3. Add API canary/reachability recorder without pretending to audit the whole register.
4. Add sanitized example portfolio data + generated report fixture.
5. Keep raw named-device research and sensitive prospect data out of the public repository by default.

## Strategic invariant
ClinicOps sells **accountable regulatory judgement around transition/document operations**. The automation/scan is the cheap front door. Do not revert to a manufacturer-diligence-failure narrative without new primary-source evidence and a dated correction record.
