# ClinicOps shared agent state

Last updated: 2026-09-09 by ChatGPT.

## Canonical truth
This GitHub repository is the shared source of truth. Local ZIPs and chat transcripts are secondary until their changes land here.

## What is live in the repo
- Corrected 8 Sep 2026 class III headline reversal and primary-source registry.
- Versioned claim registry with evidence class, allowed uses, limitations, review dates and supersession.
- Claim guard, publication gate and claim-ID publication-pack builder.
- Identifier screening, GS1 structural checks and SRN actor-role decoder.
- Read-only EUDAMED API client and bounded reachability canary.
- Opportunity, prospect and resilience scoring.
- Portfolio transition report with MF/PR-aware segmentation, certificate-timing triage, Danish-market relevance and evidence cautions.
- Portfolio intake validator for missing/contradictory evidence before human review.
- Sanitized portfolio input/output fixtures and deterministic fixture drift check.
- Canonical Class III Transition Map offer specification.
- Internal anonymised class III transition research-note draft.
- Internal Obelis transition-work-plan conversation brief.
- 16-loop on-demand fleet specification; not 16 scheduled jobs.
- Client-side Identifier Check under `docs/`.
- CI gates: pytest, Ruff, claim-registry audit, claim-reference integrity, sanitized report fixture and public-copy claim guard.

## Last fully verified baseline
Commit `e6ef28046bc2c93a2d83e9e2089334ea37ac9faf` passed CI on 9 Sep 2026 with **34 tests**, Ruff, claim-registry audit, sanitized fixture and public-copy claim gate. Newer commits extend documentation/research/sales and claim-reference integrity; always verify the newest CI run before calling the latest head green.

## Known manual dependency
GitHub Pages repository enablement is still required once. It is tracked in issue #1. Do not introduce a second hosting stack merely to bypass this one-time setting.

## Claude / ChatGPT coordination
Before changing shared files:
1. Fetch `main` first.
2. Treat this repo as canonical over local merged ZIPs.
3. Prefer focused commits over wholesale replacement.
4. Preserve corrections, claim IDs and evidence limitations.
5. Run CI after code or generated-output changes.
6. Update this file only when the operational truth materially changes.

## Current commercial thesis
ClinicOps sells **accountable regulatory judgement around legacy-to-MDR transition, SS(C)P/document operations and portfolio work planning**. Automation is the inexpensive screening/front-door layer.

The default buyer-validation sequence is:
`portfolio export → evidence validation → role-aware segmentation → priority queue → evidence ledger → human-reviewed action plan`

Do not revert to a manufacturer-diligence-failure narrative without new evidence and a dated correction.

## Next high-leverage work
1. Validate the Class III Transition Map in real portfolio conversations before building a larger dashboard.
2. Keep improving intake/report reliability around actual buyer data shapes.
3. Convert only claim-registry-approved research into external content.
4. Re-test time-sensitive EUDAMED/API observations before publication rather than scheduling high-frequency probes.
5. Keep raw named-device, prospect and client data out of the public repo by default.
