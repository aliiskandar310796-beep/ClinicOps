# ClinicOps Agent Operating Model

Agents are capabilities, not replacements for accountability. The repository already has six canonical GitHub custom-agent profiles under `.github/agents/`; those profile names are the execution names. Conceptual names used in older planning/deployment notes are aliases only and must not create a second fleet.

## Canonical execution profiles

| Canonical profile | Primary job | Older aliases that resolve here |
|---|---|---|
| Regulatory Evidence Steward | Primary-source verification, claim lifecycle, corrections, claim-adjacent signal intake | Evidence Guardian, Intelligence Scout, Research Scout |
| Portfolio Operator | Intake validation, portfolio analysis, reports, JSON and pilot bundles | — |
| Release Sentinel | CI/deployment integrity, reproducibility, rollback and technical resilience | Resilience Agent |
| Opportunity Architect | Evidence-backed commercial experiments and prioritisation | Opportunity Agent, Revenue Agent |
| Customer Discovery Agent | Structured buyer learning and product decisions | — |
| Visibility Architect | Claim-governed SEO, research distribution and public-content drafting | Growth Agent, Content Engine |

Do not create an additional profile when one of these six can absorb the capability.

## Phase 6 execution order

When a workflow crosses several roles, route it in this order:

1. **Regulatory Evidence Steward** — verify evidence and claim boundaries first.
2. **Regulatory Evidence Steward (scout mode)** — classify the regulatory/market signal without turning it into a conclusion.
3. **Visibility Architect** — turn validated intelligence into a governed draft or distribution asset.
4. **Opportunity Architect** — convert validated market response into a bounded commercial experiment.
5. **Release Sentinel** — verify reproducibility/deployment state where software or public artifacts are involved.

Portfolio Operator and Customer Discovery Agent enter whenever the task concerns a supplied portfolio or direct buyer learning.

## Five mandatory gates

Every agent output must pass the repository validation protocol:

1. Evidence check
2. Claim safety check
3. Business value check
4. Reproducibility check
5. Human review when externally published

The executable gate is implemented in `src/clinicops_os/agents.py` and exposed through:

```bash
python scripts/agent_gate.py examples/agent_tasks.json 2026-09-09
```

The gate resolves aliases to the canonical `.github/agents/*.agent.md` profile, reuses `clinicops_eudamed.claim_guard.check_claim()`, checks registered claim IDs against their allowed use, requires evidence and reproducibility metadata, and blocks external publication without recorded human review.

## Boundaries

- Agents may draft, classify, validate, prioritise and prepare artifacts.
- A passing agent gate is not a regulatory, compliance or legal conclusion.
- Public/client publication still requires the repository claim gates and the applicable human approval path.
- Private client/prospect data must not be placed in this public repository.
- More agents are not the goal. Better decisions, faster learning and safer execution are the goal.
