# ClinicOps Revenue OS

Revenue OS turns evidence-backed commercial signals into a ranked learning and pilot queue.

It is intentionally **not** a CRM, compliance-risk model, lead scraper, or autonomous outreach system.

## Core loop

`signal → account evidence → coverage-aware priority → smallest commercial experiment → result → learning → next action`

## Account contract

The canonical machine object is `clinicops_os.revenue.AccountIntelligence`.

Required fields:
- `company`
- `segment`: `manufacturer`, `authorised_representative`, `consultancy`, `distributor`, or `other`

Optional context:
- `geography`
- `trigger`
- `source_url`
- `evidence_note`
- `experiment_id`

Commercial operating signals are scored from 0 to 5 **only when evidence exists**:
- `urgency`
- `offer_fit`
- `evidence_strength`
- `partner_leverage`
- `access_strength`
- `budget_signal`
- `reuse_potential`

Blank values remain unknown. They are not silently converted to zero.

## Outputs

Each account receives:
- `priority_score` — weighted commercial operating score among known dimensions;
- `score_coverage` — percentage of score weight supported by known dimensions;
- `priority_band` — `HOT`, `WARM`, `LEARN`, or `PARK`;
- `next_experiment` — one of `RESEARCH`, `DISCOVERY`, `WARM INTRO / DISCOVERY`, `PARTNER CONVERSATION`, or `PILOT`.

A sparse account cannot become `HOT` merely because one known dimension is high. If score coverage is below 40%, the account remains `LEARN`.

## Regulatory boundary

Revenue OS scores **commercial learning and offer-fit priority only**.

It must never be described as:
- regulatory risk;
- compliance risk;
- legal risk;
- enforcement risk;
- a finding that a manufacturer or other actor is non-compliant.

Missing public EUDAMED or SS(C)P metadata is not a compliance allegation. Regulatory claims and external copy remain subject to `CLAIM_RULES.md` and the claim registry.

## Public-repository data rule

The public repository may contain only sanitized or fictional account fixtures.

Do not commit:
- real prospect lists;
- client names tied to private findings;
- mailbox-derived private information;
- personal contact details;
- credentials;
- non-public named-device research.

Real commercial data should remain in an approved private system and be exported only in sanitized form when needed for testing.

## Example

`examples/revenue_accounts.csv` is fictional and safe for tests/demos.

Once the CLI is installed:

```bash
clinicops-revenue-rank examples/revenue_accounts.csv
```

The JSON output is designed for handoff between ChatGPT, Claude, Copilot, and future internal tooling without reparsing prose.

## Decision discipline

- `RESEARCH`: evidence is too weak for outreach assumptions.
- `DISCOVERY`: test the problem and current workaround before building.
- `WARM INTRO / DISCOVERY`: offer fit exists but access is weak or unknown.
- `PARTNER CONVERSATION`: a high-leverage AR/consultancy account has enough evidence to test integration/white-label demand.
- `PILOT`: urgency, offer fit, access, and budget signals justify testing a paid or tightly scoped pilot.

Every material commercial test should reference an experiment in `experiments/EXPERIMENT_LEDGER.md`.
