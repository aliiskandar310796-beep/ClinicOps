# ClinicOps Outcome Control Tower

Status: canonical operating runbook

Use this runbook to operate the AI-first company through a small set of measurable missions. Private mission records may contain buyer/client evidence; public repository content must stay sanitized.

## Company WIP

At any moment maintain no more than **three top-level active missions** unless a real external deadline makes a temporary exception necessary.

Recommended slots:

1. **COMMERCIAL** — closest path to E6/E7/E8/E9 or strongest buyer-learning test;
2. **VISIBILITY / DISTRIBUTION** — strongest measurable route to qualified discovery or buyer action;
3. **DELIVERY / RESILIENCE** — activated delivery, critical capability unblock or demonstrated repeat failure removal.

If there is no activated delivery or material resilience issue, slot 3 should support the commercial mission rather than create unrelated build work.

## Daily control loop

For each active mission:

1. fetch current evidence/state;
2. run `clinicops-outcome-control` on the private mission record;
3. run `clinicops-risk-control` on the linked private risk register;
4. for commercial missions, run `clinicops-economic-validation` on the relevant private offer ledger;
5. identify the single metric that matters;
6. inspect open handoffs, blockers and critical risks;
7. recruit/terminate temporary workers as needed;
8. execute the smallest action capable of materially changing the metric or reducing the highest decision-relevant uncertainty;
9. verify the external/artifact result;
10. update the mission, risk and economic records as applicable;
11. choose `continue`, `modify`, `wait`, `kill`, or `complete`;
12. record the related company event in AI-COMPANY-001 when material.

Do not create a new mission because the current mission is waiting externally. Waiting is a valid state. Open another mission only when it is already one of the three highest-value company outcomes.

## Queue semantics

### NOW

Executable without a missing external dependency or reserved human decision. Work it before opening new internal tasks.

### WAITING EXTERNAL

A buyer, reviewer, provider, crawler or third party must act. Preserve the next check date/condition and stop generating premature follow-up activity.

### WAITING HUMAN RESERVED DECISION

AI has completed the evidence/recommendation/action/rollback packet. Human involvement should be a small decision, not delegated research.

### BLOCKED CAPABILITY

A required tool/account capability is unavailable. Attempt the available safe routes first, then record the exact missing capability and impact.

### TEST

Bounded experiment with metric, review point and kill condition. If the test cannot change a decision, do not run it.

### KILLED / PARKED

Retain the evidence and reason. Do not silently revive a killed idea without new evidence.

## Priority formula

Use judgement, but the order is fixed:

1. activated delivery / payment / acceptance risk;
2. E6 commitment or E4–E5 buyer-evidence opportunity;
3. external deadline / confirmed relationship event;
4. blocker or critical-risk removal for items 1–3;
5. qualified discovery/distribution experiment;
6. repeated delivery-efficiency improvement;
7. preventive resilience with demonstrated risk;
8. internal polish.

A speculative feature cannot outrank an available qualified conversation merely because the feature is easier for AI to execute.

## Risk rule

Follow `06_AGENTS/RISK_CONTROL_SYSTEM.md`.

A mission cannot hide behind progress while a material risk is unowned. Every material risk needs an accountable canonical agent, mitigation, trigger and review point. Open critical risks fail the risk-control contract. Accepted high/critical risks require a decision/evidence reference.

Risk scores are operational prioritisation only and never regulatory/legal/compliance/safety conclusions.

## Economic rule

Follow `03_OPERATIONS/ECONOMIC_VALIDATION_PROTOCOL.md`.

Category spend, hiring, competitor pricing, traffic, sends, demos and software deployment can establish plausibility or execution evidence, but cannot establish economic validation. The economic ladder must climb through real buyer behavior: response → pain → commitment → activation → payment/accepted delivery → repeat/expansion.

For every paid case, capture actual payment, direct cash cost and actual delivery/review hours. One paid buyer proves transaction possibility; repeatability requires multiple independent paid buyers or E9 expansion/repeat evidence.

## Temporary worker staffing

Follow `06_AGENTS/WORKER_RECRUITMENT_PROTOCOL.md`.

- parent agent owns the mission;
- default 1–3 workers;
- hard cap 5 active workers;
- parallelize only independent slices;
- worker output requires evidence/artifact;
- worker handoff must close;
- terminate workers when the bounded objective is done or killed.

A worker is not a new queue and not a new department.

## Integrity Gate current operating posture

Integrity Gate is deployed and software-validated but commercially and economically unvalidated. Its commercial mission should be staffed around discovery, willingness-to-pay and bounded pilot learning, not speculative feature expansion.

Preferred worker pattern for a qualified workflow test:

- Opportunity Architect owns the mission;
- `account-researcher` prepares bounded account/workflow context;
- Customer Discovery owns any actual buyer learning;
- `buyer-signal-analyst` classifies explicit response evidence;
- `offer-scope-designer` prepares the smallest scope only after pain/workflow evidence exists;
- Portfolio Operator enters only for authorized/sanitized case preparation or after activation for real delivery;
- `adversarial-qa` challenges the case/output and false-positive/false-negative risk;
- Release Sentinel verifies reproducibility and controls;
- `metrics-auditor` checks that economic stage, unit-economics denominators and evidence refs are honest.

No worker is allowed to manufacture E4–E6 evidence from public research or software deployment.

## Review cadence

### Per material event

Update the private mission, risk/economic records as applicable, and AI-COMPANY-001 immediately after:

- human buyer response;
- E-stage change;
- scope/procurement/budget signal;
- activation;
- delivery/review/acceptance/payment;
- repeat/expansion/referral caused by delivered value;
- important negative evidence;
- material risk opening/mitigation/acceptance/closure;
- material control incident;
- capability blocker opened/closed.

### Weekly

Review:

- mission progress ratios;
- highest real commercial stage;
- EXP-001 state;
- paid buyers/revenue/contribution before labor;
- observed revenue per delivery hour where available;
- repeatability state;
- highest open risk and critical-risk count;
- open handoffs;
- temporary worker count/termination;
- non-reserved founder interventions;
- channel/discovery movement;
- repeated delivery friction;
- kill criteria reached.

Do not report code, content, outreach or research volume as company success by itself.

## Commands

Mission control:

```bash
clinicops-outcome-control /private/path/mission.json
```

Risk control:

```bash
clinicops-risk-control /private/path/risks.json
```

Economic validation:

```bash
clinicops-economic-validation /private/path/economic-validation.json
```

Company-level autonomy/commercial truth:

```bash
clinicops-company-run /private/path/company-run.json
```

Integrity Gate controlled workflow:

```bash
clinicops-integrity-gate /private/case.json /private/output
clinicops-integrity-review-prepare /private/output > /private/review.json
# qualified human review
clinicops-integrity-review-gate /private/review.json /private/output
clinicops-integrity-verify /private/output /private/case.json --require-review
```

The commands measure different things. Never substitute one for another.
