# ClinicOps Risk Control System

Status: canonical internal operating control

Purpose: make material risks explicit, owned, triggerable and evidence-bound across AI-operated missions.

## Principle

A green metric does not cancel an unresolved material risk.

Every material mission should identify the small number of risks that could make the apparent outcome misleading, unsafe, uneconomic or unrecoverable. Risks are decision inputs, not boilerplate.

## Risk categories

Use one of:

- `commercial` — false demand, weak willingness to pay, channel failure, buyer concentration;
- `financial` — negative contribution, cash-flow exposure, uncontrolled scope, collection risk;
- `regulatory` — unsupported interpretation, source ambiguity, role confusion, stale rules;
- `legal` — contracts, representations, terms, liability or authority;
- `privacy` — private/client/prospect data exposure or improper processing;
- `security` — credentials, repository/admin controls, external-system compromise;
- `delivery` — quality, timeliness, review burden, input insufficiency, acceptance failure;
- `reputation` — unsupported claims, intrusive outreach, misleading positioning;
- `dependency` — browser/account/provider/reviewer/crawler or single-person dependency;
- `model` — hallucination, overconfident inference, silent authority selection, unstable reasoning;
- `operational` — handoff failure, duplicate work, queue overload, stale state.

## Scoring

Use integer likelihood and impact from 1–5.

`risk_score = likelihood × impact`

Interpretation:

- `1–5`: low;
- `6–9`: moderate;
- `10–15`: high;
- `16–25`: critical.

Scores are operational prioritisation only. They are not legal/regulatory/compliance/safety ratings.

## Required risk contract

Each risk includes:

- `risk_id`;
- category;
- description;
- likelihood 1–5;
- impact 1–5;
- accountable canonical agent;
- status: `open`, `mitigated`, `accepted`, `closed`;
- mitigation;
- trigger/early-warning condition;
- evidence refs;
- next review point;
- reserved-human-decision flag.

## Fail-closed rules

- every open risk requires a mitigation and trigger;
- an `open` critical risk (`score >= 16`) fails the risk-control pass;
- an `accepted` high/critical risk (`score >= 10`) requires an evidence/decision reference;
- `closed` or `mitigated` risks require evidence of the changed state;
- risk ownership must resolve to a canonical agent;
- a reserved-human risk may be prepared by AI but cannot be self-accepted on behalf of the human authority;
- no risk may be deleted merely because it is inconvenient to a green metric. Close it with evidence or retain it as institutional memory.

## Mission-level economic risks

Economic-validation missions should always consider at least:

1. false-positive demand from friendly conversations;
2. price sensitivity / willingness-to-pay mismatch;
3. delivery-hours expansion destroying contribution;
4. reviewer burden making the service unscalable;
5. buyer concentration / single-partner dependency;
6. procurement/security requirements lengthening the cycle;
7. product build outrunning commercial proof;
8. outreach fatigue or reputation damage;
9. hidden data-quality/input-preparation costs;
10. existing systems or consultants solving the workflow adequately.

Do not force all ten into every mission. Select the material ones and make them testable.

## Integrity Gate risk posture

Integrity Gate remains `TEST`. Important risks include:

- buyers may agree the workflow is painful but not pay for a separate tool/service;
- the strongest value may sit in a narrower UDI/EUDAMED or document-change workflow than the current generic gate;
- client source populations may be too inconsistent to automate cheaply;
- false positives may consume more expert time than they save;
- a buyer may interpret `PASS` as regulatory approval unless the boundary remains explicit;
- enterprise procurement/security expectations may exceed a bootstrapped service stack;
- incumbent RIM/eQMS/consulting providers may already own the budget and integration surface.

These are validation questions, not reasons to stop. Economic experiments should deliberately reduce the highest uncertainties first.

## Machine control

Run:

```bash
clinicops-risk-control /private/path/risks.json
```

A clean pass proves only that the risk register obeys the control contract. It does not prove the risks are gone or the business is viable.
