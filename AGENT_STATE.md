# ClinicOps shared agent state

Last updated: 2026-09-09 by ChatGPT after PR #2 merge and post-merge validation.

## Canonical truth
This GitHub repository is the shared source of truth. Local terminal state, ZIPs and chat transcripts are secondary until their changes land here.

## Latest verified deployment baseline
- `main` code baseline: `d16672161ff6bf4aa84cfafd8adadb4e6be85a67` — **Build Transition Readiness Score and executable agent gates**.
- PR: `#2` — merged by squash after green PR CI.
- PR CI: run `34388234445` completed successfully after a narrow Ruff timezone fix; **67 pytest tests** passed plus every configured repository gate.
- Post-merge CI: run `34388328839` completed successfully on `main`.
- Pages deployment: run `34388328683` completed successfully on the same `main` commit.
- Pages artifact: `github-pages`, artifact `10118588012`, SHA-256 digest `00e4b35676ac2d3da8f54214b468e132c690db6d50dd7c8b9a203ace53f53bc8`.
- The downloaded Pages artifact was inspected and contains both `index.html` and `readiness-score.html`; the readiness artifact contains the browser-local privacy statement and the Regulatory Intelligence Assessment CTA.

## Public tools
### EUDAMED Identifier Check
- `docs/index.html`
- Client-side only.
- GS1 Mod-10 validation, SRN role decoding and B-prefix structural screening.
- Existing public Pages root remains the free identifier front door.

### Transition Readiness Score
- `docs/readiness-score.html`
- New browser-only lead-magnet tool.
- Five self-reported operational work-plan questions.
- Deterministic 0–100 readiness signal with explicit gap explanations.
- The number is an **operational evidence/work-plan readiness signal**, not a regulatory risk, compliance, legal or enforcement score.
- No live EUDAMED lookup and no browser network calls.
- Result CTA: **Request a Regulatory Intelligence Assessment** via `info@clinicops.dk`.
- The Identifier Check cross-links to the readiness tool; the readiness tool links back.
- Contract validator: `scripts/validate_readiness_page.py` enforces 5–8 questions, 100 total weight, complete 0–100 band coverage, gap messages, privacy copy, CTA copy and local-only behavior.

## Executable agent layer
The repo already had six canonical `.github/agents/` profiles. The new runtime does **not** add a second fleet.

Canonical execution profiles:
1. Regulatory Evidence Steward
2. Portfolio Operator
3. Release Sentinel
4. Opportunity Architect
5. Customer Discovery Agent
6. Visibility Architect

`06_AGENTS/AGENT_OPERATING_MODEL.md` now reconciles older conceptual names into those profiles:
- Evidence Guardian / Intelligence Scout / Research Scout → Regulatory Evidence Steward
- Growth Agent / Content Engine → Visibility Architect
- Opportunity Agent / Revenue Agent → Opportunity Architect
- Resilience Agent → Release Sentinel

Executable runtime:
- `src/clinicops_os/agents.py`
- `scripts/agent_gate.py`
- sanitized fixture `examples/agent_tasks.json`
- tests `tests/test_agents.py`

Five mandatory gates are enforced in code:
1. Evidence check
2. Claim safety check
3. Business value check
4. Reproducibility check
5. Human review for external publication

The runtime reuses `clinicops_eudamed.claim_guard.check_claim()` and the existing claim registry. It does not create a parallel regulatory-claim checker.

## Claim governance
- `research/claims.jsonl` remains the versioned claim registry.
- `src/clinicops_eudamed/claim_guard.py` remains the known-bad-phrasing guard.
- `src/clinicops_os/claim_registry.py` remains the claim-status/use/review gate.
- Public factual/regulatory copy must remain traceable to `CO-CLM-####` claims and their allowed-use boundaries.
- PR #2 removed a blocked-phrase example from `sales/obelis-transition-conversation.md` without weakening the underlying safety instruction.
- CI public-copy claim-gate coverage now includes `offers`, `sales`, `research`, and `content` in addition to the prior public surfaces.

## Corrected regulatory thesis
- Do not revive the rejected manufacturer-diligence-failure headline from the class III census.
- In the corrected 8 Sep 2026 sample, all sampled MF-role MDR class III registrations had linked validated SS(C)P metadata; the commercial opportunity is the **legacy-to-MDR transition/document-operations workload**, not a generic allegation about manufacturer diligence.
- B-prefix handling is a ClinicOps screening/derivation layer unless the exact proposition is directly supported by the registered primary source.
- Do not imply an end-to-end public-register audit when API reachability is bounded.
- Preserve MF/AR/IM/PR role distinctions.
- Commercial priority scores are not regulatory/compliance/legal risk scores.

## EUDAMED API correction
The 9 Sep 2026 canary did not reproduce the prior apparent page-32,000 failure boundary. Pages 0, 30,000 and 32,000 returned HTTP 200 with 50 records in the bounded run. Treat the 8 Sep failure as a dated observation, not a stable boundary. Canonical claim: `CO-CLM-0011`.

## Revenue OS
Current commercial loop:

`signal → evidence coverage → ranked account → smallest commercial experiment → result → learning → reusable asset → revenue`

Executable components:
- `src/clinicops_os/revenue.py` + `clinicops-revenue-rank`
- `src/clinicops_os/experiments.py` + `clinicops-experiments`
- `experiments/EXPERIMENT_LEDGER.md`
- `.github/ISSUE_TEMPLATE/experiment.yml`

Real prospect/account data stays private. Public GitHub contains sanitized fixtures and reusable code only.

## Client delivery
Service-first deployment remains canonical:

`clinicops.dk acquisition → controlled private intake → ClinicOps validation/analysis → human regulatory review → secure client bundle → feedback → Revenue OS learning`

Existing bundle schema `1.1` includes:
- `client_report.html`
- `portfolio_report.md`
- `portfolio_report.json`
- `intake_diagnostics.md`
- `manifest.json` with source/output hashes

Do not place confidential client bundles or named private prospect data on public GitHub Pages/Actions.

## CI and GitHub automation
Current CI checks:
- pytest
- Ruff
- Revenue OS experiment-contract smoke
- executable agent five-gate smoke
- Transition Readiness Score contract
- client-bundle smoke
- custom-agent profile audit
- claim-registry audit
- claim-reference integrity
- governed website content validation
- sanitized report fixture check
- widened public-copy claim gate

`.github/workflows/ops-watch.yml` remains the bounded unattended regulatory-operations workflow: evidence freshness + EUDAMED reachability canary only. It does not publish, contact prospects, or make client compliance findings.

## GitHub Pages
- Pages is enabled and deployment works.
- Identifier Check and Transition Readiness Score are deployed from `docs/` through `.github/workflows/pages.yml`.
- Known Pages root: `https://aliiskandar310796-beep.github.io/ClinicOps/`.
- Readiness path: `/ClinicOps/readiness-score.html`.
- Do not use Pages for confidential client content.

## Website / external account boundary
This build did **not** publish or modify:
- clinicops.dk / GoDaddy
- LinkedIn
- Gumroad pricing/listings

Those remain separate browser/account execution surfaces. GitHub contains the governed deployment assets and public free-tool layer; external publication requires the applicable account access and human approval boundary.

## Budget/resilience doctrine
ClinicOps is currently bootstrapped. Default architecture:
- low fixed cost;
- GitHub + Pages + existing domain/mail + AI leverage;
- sell accountable intelligence before building expensive SaaS;
- convert repeated client friction into automation;
- reinvest validated revenue into infrastructure only after buyer evidence exists.

Avoid expensive CRM/cloud/portal/data purchases until real paid usage proves the need.

## Coordination protocol
Before shared-file changes:
1. Fetch `main` first.
2. Treat GitHub `main` as canonical over chat/local state.
3. Preserve corrections, claim IDs and evidence limitations.
4. Reuse existing modules before adding parallel logic.
5. If a write conflicts, fetch newest and merge; never force-overwrite concurrent work.
6. Use feature branches/PRs for material multi-file changes.
7. Verify the newest CI run before declaring code green.
8. Verify Pages deployment when `docs/**` changes.
9. Use the narrowest existing custom agent; expand capability before fleet size.
10. Keep private customer/prospect evidence out of the public repo.

## Current highest-leverage next work
1. Connect the verified public GitHub tools into the clinicops.dk acquisition funnel when browser/domain publication is approved.
2. Run a small number of high-information buyer experiments against ARs, regulatory consultancies and class III/implantable manufacturers; avoid mass outreach.
3. Deliver the first paid/design-partner Class III Transition Map using bundle schema `1.1` and capture friction as structured experiment evidence.
4. Turn only claim-approved research into distribution assets and measure qualified conversations, not vanity traffic.
5. Build portal features only when repeated paid engagements prove multi-user/upload/action-tracking needs.
6. Keep the readiness score and Identifier Check free; monetize the human-reviewed portfolio judgement and monitoring layer.
