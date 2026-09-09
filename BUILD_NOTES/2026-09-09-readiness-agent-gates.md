# Build note — Transition Readiness Score + executable agent gates

Date: 2026-09-09
Branch: `chatgpt/readiness-agent-gates-20260909`

## Scope

This build closes two gaps identified in the Claude-to-ChatGPT handoff without rebuilding existing ClinicOps capabilities.

### Transition Readiness Score

- New browser-only lead-magnet page at `docs/readiness-score.html`.
- Five self-reported operational-work-plan questions.
- Deterministic 0–100 readiness signal with explicit gap explanations.
- No live EUDAMED lookup and no browser network calls.
- Result explicitly framed as operational readiness rather than regulatory/compliance risk.
- CTA: Request a Regulatory Intelligence Assessment.
- Existing Identifier Check preserved; only a cross-link was added.
- Contract validator enforces question count, weight total, score-band coverage, gap explanations, privacy copy and local-only behavior.

### Executable agent gate

- New `src/clinicops_os/agents.py` runtime.
- Reconciles older conceptual names into the existing six `.github/agents/` profiles rather than creating a second agent fleet.
- Enforces the five-gate protocol: evidence, claim safety, business value, reproducibility, and human review for external publication.
- Reuses the existing `check_claim()` and claim registry; no parallel claim checker was added.
- New sanitized task fixture and automated tests.

### Governance repair

- Removed a blocked-phrase example from `sales/obelis-transition-conversation.md` without changing its underlying safety instruction.
- Widened CI public-copy claim-gate coverage to `offers`, `sales`, `research`, and `content`, matching the stronger intended audit scope.
- Added CI smoke gates for the executable agent runtime and readiness-page contract.

## Publication boundary

This branch does not modify clinicops.dk, LinkedIn, Gumroad pricing, or private client/prospect data. GitHub Pages deployment occurs only after merge to the configured deployment branch/workflow.

## Validation target

The PR must pass the repository CI before merge. A successful merge is not itself a regulatory approval; public/business outputs remain subject to the established human-review and claim-governance boundaries.
