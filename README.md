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
- AR/manufacturer portfolio transition report generation.
- Read-only EUDAMED API reachability canary.
- CI gates for tests, Ruff, claim-registry integrity and public-facing copy.
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
clinicops-portfolio-report examples/portfolio.csv 2026-09-09
clinicops-publication-pack "Transition gap note" CO-CLM-0001,CO-CLM-0002,CO-CLM-0004 research-note 2026-09-09
```

## Claim lifecycle

Every material external claim should move through:

`signal → source/evidence → claim registry → use gate → draft → claim guard → adversarial read → publish/deliver → correction/supersession`

A rejected claim stays in the registry as institutional memory rather than disappearing. That makes later assistants and scripts less likely to rediscover the same attractive mistake.

## Class III Transition Map

`offers/class-iii-transition-map.md` defines the first productised service layer around the toolkit: portfolio segmentation, certificate/transition timing, evidence gaps, SS(C)P operations and market-language work planning. The deterministic scan is the low-cost front door; the paid layer is human-reviewed regulatory judgement.

## Identifier Check deployment

`docs/index.html` is prepared for GitHub Pages. Pages enablement is the only remaining manual hosting dependency and is tracked in repository issue #1. Do not introduce a second hosting stack unless Pages proves unsuitable.

## Repository visibility

Keep raw named-device research, private prospect information and client data out of this public repository by default. Publish sanitized tooling, methodology, aggregate outputs and anonymised examples unless a deliberate disclosure decision is made.
