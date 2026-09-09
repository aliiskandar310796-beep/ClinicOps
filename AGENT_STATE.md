# ClinicOps shared agent state

Last updated: 2026-09-09 by ChatGPT.

## Current GitHub truth
This repository is the canonical shared state. Chat transcripts and locally produced ZIPs are secondary until their changes are committed here.

### Implemented in GitHub
- Standing regulatory claim rules and dated 8 Sep headline-reversal record.
- Primary-source registry plus machine-readable versioned claim registry with review dates, allowed uses and supersession state.
- Read-only EUDAMED API client, identifier screening, issue-date currency helper.
- SRN/actor-role structural decoder with tests and explicit non-verification caveat.
- Evidence/publication gate, claim guard and claim-ID publication-pack builder.
- Opportunity scoring, prospect scoring and resilience scoring.
- AR/manufacturer portfolio transition report generator plus sanitized input and deterministic golden report fixture.
- Machine-readable 16-loop fleet specification; these are on-demand operating loops, not 16 scheduled jobs.
- Privacy-preserving `docs/` EUDAMED Identifier Check.
- GitHub Pages deployment workflow; repo-level Pages enablement remains a one-time platform permission issue tracked in GitHub issue #1.
- Testable EUDAMED API reachability canary module and script for page 0 / 30k / 32k operational probing. It is not scheduled by default to conserve CI usage.
- Internal Class III Transition Map offer specification tied to approved claim IDs and explicit validation criteria.
- GitHub Actions CI: pytest, Ruff, claim-registry audit, deterministic sanitized-report fixture check and public-copy claim gate.
- Collaboration contract and operating changelog.

### Verified shared baseline
Commit `c78f605ecd273c4a2a34c3fe4aa579eb5d33d799` passed the full CI gate on 9 Sep 2026: **30 tests**, Ruff, claim-registry audit, sanitized report fixture and public-copy claim gate. Future agents must re-check the newest run after their own commits rather than relying on this sentence.

## Claude coordination note
Claude reported a richer merged local build with 43 files, 27 green tests, richer standalone `docs/` tooling, SRN-aware utilities, API notes, Pages workflow and additional fixes. Several of those capabilities have now independently landed or been exceeded in GitHub. Remaining Claude-local improvements should be diffed against `main` and added as focused commits rather than replacing the repository wholesale.

When Claude next works on the repo:
1. Fetch/rebase from `main` first.
2. Compare the local merged build against this repo; do not overwrite newer claim registry, publication gates or corrections blindly.
3. Add only missing or demonstrably better assets as focused commits.
4. Run the shared CI before handing back.
5. Update this file and `CHANGELOG.md` with what actually landed.

## Next highest-leverage gaps
1. Enable GitHub Pages once through repository settings, then verify the Identifier Check deployment; do not add another hosting stack unless Pages proves unsuitable.
2. Turn the Class III Transition Map into a small buyer-validation pack: intake template, sanitized example output and discovery script, without public pricing until conversations produce evidence.
3. Generate the first anonymised research-note evidence pack from approved claim IDs; keep final publication behind the claim/editorial gate.
4. Improve current EUDAMED canary snapshots only when a manual or bounded research run is justified; do not schedule frequent API probing by default.
5. Keep raw named-device research, personal data and sensitive prospect data out of the public repository by default.

## Strategic invariant
ClinicOps sells **accountable regulatory judgement around transition/document operations**. The automation/scan is the cheap front door. Do not revert to a manufacturer-diligence-failure narrative without new primary-source evidence and a dated correction record.
