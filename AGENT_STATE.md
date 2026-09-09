# ClinicOps shared agent state

Last updated: 2026-09-09 by ChatGPT.

## Current GitHub truth
This repository is the canonical shared state. Chat transcripts and locally produced ZIPs are secondary until their changes are committed here.

### Implemented in GitHub
- Standing regulatory claim rules and dated 8 Sep headline-reversal record.
- Primary-source registry.
- Read-only EUDAMED API client, identifier screening, issue-date currency helper.
- SRN/actor-role structural decoder with tests and explicit non-verification caveat.
- Evidence/publication gate and claim guard.
- Opportunity scoring, prospect scoring, resilience scoring.
- AR/manufacturer portfolio transition report generator plus sanitized example input.
- Machine-readable 16-loop fleet specification; these are on-demand operating loops, not 16 scheduled jobs.
- Privacy-preserving `docs/` EUDAMED Identifier Check.
- GitHub Pages deployment workflow; repo-level Pages enablement was added after the first configuration-only failure.
- EUDAMED API reachability canary script for page 0 / 30k / 32k operational probing. It is not scheduled by default to conserve CI usage.
- GitHub Actions CI: pytest, Ruff, and public-copy claim-gate smoke test.
- Collaboration contract and operating changelog.

### Verified shared baseline
Latest verified CI baseline after the Ruff cleanup: tests, Ruff, and the public-copy claim gate all passed. Future agents should re-check the newest run after their own commits rather than relying on this sentence.

## Claude coordination note
Claude reported a richer merged local build with 43 files, 27 green tests, richer standalone `docs/` tooling, SRN-aware utilities, API notes, Pages workflow, and additional fixes. Several of those capabilities have now independently landed in GitHub. Remaining Claude-local improvements should be diffed against `main` and added as focused commits rather than replacing the repository wholesale.

When Claude next works on the repo:
1. Fetch/rebase from `main` first.
2. Compare the local merged build against this repo; do not overwrite newer claim rules or corrections blindly.
3. Add only missing or demonstrably better assets as focused commits.
4. Run the shared CI before handing back.
5. Update this file and `CHANGELOG.md` with what actually landed.

## Next highest-leverage gaps
1. Verify the current GitHub Pages deployment and only troubleshoot further if the latest run still fails.
2. Add tests for the EUDAMED canary's output contract without making live network calls in ordinary CI.
3. Add a generated sanitized portfolio-report fixture to make report changes reviewable.
4. Add richer identifier/SRN tool behavior only where it survives the claim gate and improves user value.
5. Keep raw named-device research and sensitive prospect data out of the public repository by default.

## Strategic invariant
ClinicOps sells **accountable regulatory judgement around transition/document operations**. The automation/scan is the cheap front door. Do not revert to a manufacturer-diligence-failure narrative without new primary-source evidence and a dated correction record.
