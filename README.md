# ClinicOps EUDAMED OS

A reproducible research, screening and regulatory-operations toolkit for ClinicOps' public-source EUDAMED work.

## Operating thesis

Use machines for repeatable public-data screening, evidence capture and portfolio triage. Sell the accountable human judgement required to turn those signals into a regulatory work plan.

The current commercial focus is the **legacy-to-MDR transition and SS(C)P/document-operations workload**, not a manufacturer-diligence allegation.

## Design principles

- Public/read-only source data by default.
- Separate machine comparison from regulatory judgement.
- Preserve corrections as code-level and data-level guardrails.
- Never imply full-register coverage when API reachability is partial.
- Prefer issue-date comparisons unless revision-number equivalence is established.
- Treat legacy/B-prefix downstream SS(C)P consequences as derived screening logic, not quoted Commission law.
- Keep actor roles explicit: MF, AR, IM and PR are not interchangeable analysis buckets.
- Add automation only where repeated work or external change justifies its maintenance cost.

## Capabilities

- Identifier classification and GS1 Mod-10 check-digit validation.
- Structural SRN role decoding with explicit non-verification caveat.
- EUDAMED trade-name search and UDI-DI detail retrieval.
- Basic UDI-DI linked SS(C)P metadata extraction.
- Currency comparison helper using issue dates.
- Claim guard for known high-risk/incorrect formulations.
- Versioned claim registry with evidence class, limitations, allowed uses, review dates and supersession.
- Evidence-gated publication-pack generation.
- Opportunity scoring that penalises regulatory/reputation risk and ongoing maintenance burden.
- AR/manufacturer portfolio transition report generation with operator-priority triage.
- Machine-readable portfolio JSON for downstream tools and agent handoffs.
- Portfolio intake diagnostics for missing evidence and structural conflicts.
- One-command pilot bundle generation with input hash, diagnostics, Markdown and JSON outputs.
- Read-only EUDAMED API reachability canary.
- CI gates for tests, Ruff, claim-registry integrity, governed website copy, generated fixtures and public-facing copy.
- Client-side Identifier Check under `docs/`.

## Important limitations

The public EUDAMED interface does not expose an SS(C)P document body through the endpoints used here. A metadata `MATCH` is not a textual-content match. Deep-offset pagination may become unreachable; page size may be capped; counts and API behavior can change. Published results must state the sampling method, evidence date and access limitations.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
clinicops-id-check B-123456789
clinicops-claims research/claims.jsonl 2026-09-09
clinicops-rank-opportunities examples/opportunities.json
clinicops-portfolio-validate examples/portfolio_intake_template.csv
clinicops-portfolio-report examples/portfolio.csv 2026-09-09
clinicops-portfolio-json examples/portfolio.csv 2026-09-09
clinicops-pilot-bundle examples/portfolio.csv /tmp/clinicops-pilot 2026-09-09
clinicops-publication-pack "Transition gap note" CO-CLM-0001,CO-CLM-0002,CO-CLM-0004 research-note 2026-09-09
```

## Claim lifecycle

Every material external claim should move through:

`signal → source/evidence → claim registry → use gate → draft → claim guard → adversarial read → publish/deliver → correction/supersession`

A rejected claim stays in the registry as institutional memory rather than disappearing. That makes later assistants and scripts less likely to rediscover the same attractive mistake.

## GitHub agents and unattended automation

Repository-scoped Copilot profiles under `.github/agents/` divide high-agency work without creating a permanently running agent swarm:

- **Regulatory Evidence Steward** — primary-source verification, claim lifecycle and corrections.
- **Portfolio Operator** — intake validation, portfolio analysis, reports, JSON handoffs and pilot bundles.
- **Release Sentinel** — CI/deployment health, reproducibility and rollback discipline.

Use the narrowest agent that matches the work. The custom-agent files are execution profiles, not background daemons.

Unattended recurring work lives in `.github/workflows/ops-watch.yml`. `Ops Watch` runs weekly and on relevant automation/canary changes. It checks evidence freshness and records a bounded EUDAMED reachability snapshot as a workflow artifact. It does not publish content, send communications or make compliance findings.

## Class III Transition Map

`offers/class-iii-transition-map.md` is the canonical product specification: portfolio segmentation, certificate/transition timing, evidence gaps, SS(C)P operations and market-language work planning. The deterministic scan is the low-cost front door; the paid layer is human-reviewed regulatory judgement.

The AR/regulatory-firm posture is partner-first where useful: established firms already sell EUDAMED registration and representation, so ClinicOps differentiates on portfolio evidence reconciliation, prioritisation, machine-readable handoff and a human-reviewed work queue. The dated positioning scan is in `research/market/2026-09-09-ar-eudamed-positioning.md`.

Use `examples/portfolio_intake_template.csv` as the minimum portable intake shape. Extra client-export columns are tolerated by the report loader, while `clinicops-portfolio-validate` surfaces missing dates, evidence links, actor-role uncertainty and conflicting registration signals before review begins.

`clinicops-portfolio-report` renders the human-facing work plan. `clinicops-portfolio-json` emits the same ordered analysis as a versioned JSON contract for Notion, client portals, future web forms or other agents. `examples/portfolio_report.md` and `examples/portfolio_report.json` are reproducible sanitized fixtures checked by CI.

`clinicops-pilot-bundle` packages a validated portfolio into `portfolio_report.md`, `portfolio_report.json`, `intake_diagnostics.md` and `manifest.json`. The manifest includes the input SHA-256 so a delivered bundle can be tied back to the exact source export used for that analysis.

## Research-note pipeline

`research/drafts/2026-09-classIII-transition-gap.md` is the internal first-draft research note built from the corrected 8 September census. It is deliberately not published. Its pre-publication gate requires current API canary evidence, claim-registry approval, publication-pack generation and an adversarial final read.

## Website deployment pack

`website/homepage-v2.md` is the canonical transition-focused homepage copy prepared for clinicops.dk. Its material regulatory statements are linked to claim IDs and CI checks that those claims remain valid for website use. Browser-assisted implementation can therefore be fast without bypassing evidence governance.

## Identifier Check deployment

`docs/index.html` is prepared for GitHub Pages. Pages enablement is the only remaining manual hosting dependency and is tracked in repository issue #1. Do not introduce a second hosting stack unless Pages proves unsuitable.

## Repository visibility

Keep raw named-device research, private prospect information and client data out of this public repository by default. Publish sanitized tooling, methodology, aggregate outputs and anonymised examples unless a deliberate disclosure decision is made.
