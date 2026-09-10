# ClinicOps EUDAMED OS

A reproducible research, screening, commercial-learning and regulatory-operations toolkit for ClinicOps' public-source EUDAMED work.

## Operating thesis

Use machines for repeatable public-data screening, evidence capture, portfolio triage and commercial learning. Sell the accountable human judgement required to turn those signals into a regulatory work plan.

The current commercial focus is the **legacy-to-MDR transition and SS(C)P/document-operations workload**, not a manufacturer-diligence allegation.

## Design principles

- Public/read-only source data by default.
- Separate machine comparison from regulatory judgement.
- Preserve corrections as code-level and data-level guardrails.
- Never imply full-register coverage when API reachability is partial.
- Prefer issue-date comparisons unless revision-number equivalence is established.
- Treat legacy/B-prefix downstream SS(C)P consequences as derived screening logic, not quoted Commission law.
- Keep actor roles explicit: MF, AR, IM and PR are not interchangeable analysis buckets.
- Keep commercial priority scores separate from regulatory/compliance risk.
- Add automation only where repeated work or external change justifies its maintenance cost.
- Keep private client/prospect data out of the public repository.

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
- Revenue OS account prioritisation with unknown-signal coverage and explicit commercial-only interpretation.
- Executable experiment registry with required hypothesis, metric, success threshold, kill condition, result, learning and decision state.
- AR/manufacturer portfolio transition report generation with operator-priority triage.
- Machine-readable portfolio JSON for downstream tools and agent handoffs.
- Portfolio intake diagnostics for missing evidence and structural conflicts.
- One-command pilot bundle generation with source/output hashes, diagnostics, Markdown, JSON and a self-contained client HTML report.
- Read-only EUDAMED API reachability canary with reviewed drift semantics.
- CI gates for tests, Ruff, Revenue OS contracts, client-bundle smoke delivery, custom-agent profiles, claim-registry integrity, governed website copy, generated fixtures and public-facing copy.
- Live client-side Identifier Check deployed from `docs/`.

## Important limitations

The public EUDAMED interface does not expose an SS(C)P document body through the endpoints used here. A metadata `MATCH` is not a textual-content match. Deep-offset pagination may become unreachable; page size may be capped; counts and API behavior can change. Published results must state the sampling method, evidence date and access limitations.

Commercial scores and experiments are learning tools. They are not regulatory, compliance, legal or enforcement-risk determinations.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
clinicops-id-check B-123456789
clinicops-claims research/claims.jsonl 2026-09-09
clinicops-rank-opportunities examples/opportunities.json
clinicops-revenue-rank examples/revenue_accounts.csv
clinicops-experiments examples/experiments.json
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
- **Opportunity Architect** — evidence-backed business experiments and prioritisation.
- **Customer Discovery Agent** — structured buyer learning and product decisions.
- **Visibility Architect** — claim-governed research, SEO and distribution assets.

Use the narrowest agent that matches the work. The custom-agent files are execution profiles, not background daemons.

Unattended recurring work lives in `.github/workflows/ops-watch.yml`. `Ops Watch` runs weekly and on relevant automation/canary changes. It checks evidence freshness and records a bounded EUDAMED reachability snapshot as a workflow artifact. It does not publish content, send communications or make compliance findings.

GitHub Issue Forms include a commercial-experiment template for real Revenue OS tests. Use issues selectively for validated experiments, reproducible defects and genuine deployment blockers rather than turning GitHub into a noisy CRM.

## Revenue OS and experiments

`03_OPERATIONS/REVENUE_OS.md` defines the commercial loop. `src/clinicops_os/revenue.py` provides the executable account-priority model and `clinicops-revenue-rank` renders its versioned JSON output.

`03_OPERATIONS/EXPERIMENT_ENGINE.md` defines the experiment lifecycle. `src/clinicops_os/experiments.py` enforces the machine-readable contract: planned/running/completed/cancelled state, explicit success and kill thresholds, and mandatory result/learning/decision fields for completed experiments. `examples/experiments.json` is the sanitized CI fixture.

Commercial results feed product decisions; they do not become regulatory claims merely because a buyer responded positively.

## Class III Transition Map

`offers/class-iii-transition-map.md` is the canonical product specification: portfolio segmentation, certificate/transition timing, evidence gaps, SS(C)P operations and market-language work planning. The deterministic scan is the low-cost front door; the paid layer is human-reviewed regulatory judgement.

The AR/regulatory-firm posture is partner-first where useful: established firms already sell EUDAMED registration and representation, so ClinicOps differentiates on portfolio evidence reconciliation, prioritisation, machine-readable handoff and a human-reviewed work queue. The dated positioning scan is in `research/market/2026-09-09-ar-eudamed-positioning.md`.

Use `examples/portfolio_intake_template.csv` as the minimum portable intake shape. Extra client-export columns are tolerated by the report loader, while `clinicops-portfolio-validate` surfaces missing dates, evidence links, actor-role uncertainty and conflicting registration signals before review begins.

`clinicops-portfolio-report` renders the human-facing work plan. `clinicops-portfolio-json` emits the same ordered analysis as a versioned JSON contract for client portals, future web forms or other agents. `examples/portfolio_report.md` and `examples/portfolio_report.json` are reproducible sanitized fixtures checked by CI.

`clinicops-pilot-bundle` packages a validated portfolio using bundle schema `1.1` into:

- `client_report.html` — portable client-facing report;
- `portfolio_report.md` — review/handoff report;
- `portfolio_report.json` — machine-readable contract;
- `intake_diagnostics.md` — structural/evidence gaps;
- `manifest.json` — source SHA-256, generated-output SHA-256 values, bundle version and interpretation boundary.

The HTML report is deliberately dependency-free so it can be delivered through an authenticated client workspace immediately and later shown behind a portal without replacing the underlying analysis contract.

## Client delivery architecture

`01_PRODUCT/CLIENT_ONBOARDING_WORKFLOW.md` defines the service-first engagement flow. `01_PRODUCT/MVP_DEPLOYMENT_ARCHITECTURE.md` defines the recommended deployment boundary:

`clinicops.dk acquisition → controlled private intake → ClinicOps analysis engine → human review → secure bundle delivery → client feedback → Revenue OS learning`

Do not put confidential client bundles on public GitHub Pages or send private client portfolios through public GitHub Actions. The public repository contains reusable code, governance, methodology and sanitized examples; live client evidence belongs in controlled storage.

`01_PRODUCT/KNOWLEDGE_GRAPH_SPEC.md` defines the lean cross-system entity contract. It deliberately starts as a data model over existing JSON/Revenue OS/experiment projections rather than introducing graph-database infrastructure before client usage requires it.

## Research-note pipeline

`research/drafts/2026-09-classIII-transition-gap.md` is the internal first-draft research note built from the corrected 8 September census. It is deliberately not published. Its pre-publication gate requires current API canary evidence, claim-registry approval, publication-pack generation and an adversarial final read.

## Website deployment pack

`website/homepage-v2.md` is the canonical transition-focused homepage copy prepared for clinicops.dk. Its material regulatory statements are linked to claim IDs and CI checks that those claims remain valid for website use. Browser-assisted implementation can therefore be fast without bypassing evidence governance.

Focused landing-page deployment packs and `website/visibility-plan.md` separate high-intent EUDAMED, SS(C)P, authorised-representative and Denmark-market search intents rather than forcing every topic onto one homepage.

## Production site deployment

`docs/` now holds the full clinicops.dk production site (Home, About, Research,
Tools, EUDAMED Intelligence, MDR Transition, SS(C)P Operations, Authorised
Representative Intelligence, Contact), rendered from the `website/*.md`
deployment packs, plus the two free client-side tools:
`docs/identifier-check.html` (EUDAMED Identifier Check, moved off the root
path) and `docs/readiness-score.html` (Transition Readiness Score). `docs/index.html`
is now the site Home page, not the Identifier Check tool — update any bookmark
or external link accordingly.

Deployed through GitHub Pages at:

https://aliiskandar310796-beep.github.io/ClinicOps/

Deployment is controlled by `.github/workflows/pages.yml` and uses Node-24-native GitHub Actions majors. Repository issue #1 was closed after successful deployment run `34354035445`.

**DNS is intentionally not yet pointed at this deployment.** clinicops.dk still
resolves to the existing GoDaddy-hosted site. Do not cut the domain over until
the production site above has been reviewed and explicitly approved for
publication — see the deployment-plan and DNS-migration notes in
`website/CLINICOPS_DK_DEPLOYMENT_PLAN.md`.

## Repository visibility

Keep raw named-device research, private prospect information and client data out of this public repository by default. Publish sanitized tooling, methodology, aggregate outputs and anonymised examples unless a deliberate disclosure decision is made.
