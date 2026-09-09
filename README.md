# ClinicOps EUDAMED OS

A reproducible research and screening toolkit for ClinicOps' public-source EUDAMED work.

## Design principles
- Public/read-only data only.
- Separate machine comparison from regulatory judgement.
- Preserve corrections as code-level guardrails.
- Never imply full-register coverage when API reachability is partial.
- Prefer issue-date comparisons unless revision-number equivalence is established.
- Treat legacy/B-prefix SS(C)P-link behavior as a derived screening rule, not a quoted Commission rule.

## Capabilities
- Identifier classification and GS1 Mod-10 check digit validation.
- EUDAMED trade-name search and UDI-DI detail retrieval.
- Basic UDI-DI linked SS(C)P metadata extraction.
- Currency comparison helper using issue dates.
- Claim guard that flags known high-risk/incorrect formulations.
- CSV/JSON result normalization for longitudinal snapshots.
- GitHub Actions for tests and monthly scheduled research runs.

## Important limitations
The public EUDAMED interface does not expose an SS(C)P document body through the endpoints used here. A metadata 'match' is not a textual-content match. Deep offset pagination may become unreachable; page size may be capped; counts can be unstable. Any published result must state the sampling method and access limitations.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
clinicops-id-check B-123456789
```

## Suggested repository visibility
Keep raw device-level research private by default. Publish only sanitized tooling, methodology, aggregate outputs, and anonymised examples unless a deliberate disclosure decision is made.

## Opportunity ranking
ClinicOps uses a small scoring model to keep the idea backlog lean. It rewards evidence, leverage, defensibility, reuse and urgency, while penalising regulatory/reputation risk and ongoing maintenance burden.

```bash
clinicops-rank-opportunities examples/opportunities.json
```

Treat the output as a portfolio triage aid, not an automatic business decision. High-risk, low-reversibility ideas are explicitly escalated rather than merely given a lower numerical score.
