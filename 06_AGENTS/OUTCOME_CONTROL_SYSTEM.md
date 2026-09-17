# ClinicOps Outcome Control System

Status: canonical internal operating system

Purpose: make AI-operated work accountable to measurable business outcomes instead of activity volume.

## Operating model

Every material piece of work is a **mission** owned by one canonical agent. A mission may recruit temporary specialist workers under `06_AGENTS/WORKER_RECRUITMENT_PROTOCOL.md`, but accountability never leaves the owner.

Mission loop:

`define outcome → establish baseline → choose smallest high-information action → recruit bounded workers if useful → execute → verify evidence → update metric → close handoff → continue / modify / kill`

Do not start with a task list. Start with the outcome that must change.

## Canonical outcome classes

Use one primary class per mission:

- `commercial-evidence` — move an opportunity honestly through E0–E9;
- `revenue` — activate, deliver, collect or expand paid work;
- `buyer-learning` — resolve a high-value unknown about buyer/workflow/pain/commitment;
- `visibility-discovery` — increase qualified discovery/indexing/approved distribution reach;
- `delivery-quality` — reduce defects, review burden or reconciliation time on activated work;
- `resilience` — remove a repeat failure mode or capability dependency;
- `evidence-quality` — improve provenance, claim accuracy or ambiguity handling;
- `cycle-time` — reduce elapsed time to a controlled outcome without weakening review/approval gates.

## Outcome contract

A material mission record must include:

- mission ID and owner agent;
- primary outcome class;
- objective written as an observable change;
- baseline, target and current metric;
- metric direction (`increase` or `decrease`);
- unit;
- current E0–E9 stage where commercially relevant;
- evidence/artifact refs supporting the current state;
- deadline or review point;
- stop/kill condition;
- temporary workers, if any;
- open handoffs/blockers;
- reserved-human actions, if any.

A mission marked `completed` must have reached its target. Work completion without target achievement is not mission completion; use `active`, `waiting`, `blocked`, `failed` or `killed` honestly.

## Priority rule

Rank active missions by:

1. direct path to E6/E7/E8/E9 or qualified buyer evidence;
2. irreversible deadline / external dependency timing;
3. blocker removal for another high-value mission;
4. expected information gain per unit effort;
5. reusable delivery/distribution asset creation;
6. maintenance/resilience risk;
7. everything else.

Do not allow low-stakes internal polish to outrank a real buyer conversation, activation, delivery, payment or high-information market test.

## WIP limits

- maximum **3 top-level active missions** across the company unless an external deadline requires otherwise;
- maximum **5 active temporary workers per mission**;
- default **1–3 workers**;
- one accountable parent per worker;
- one primary metric per mission.

A blocked mission does not justify opening unlimited replacement work. First attempt to remove the blocker or kill/defer the mission.

## Evidence rules

- E0–E3 can be supported by public/internal artifacts as applicable.
- E4+ requires private external evidence.
- a completed worker requires evidence or artifact refs;
- a completed mission requires evidence/artifacts supporting the target state;
- a control violation prevents a clean control pass until resolved;
- corrected incidents remain recorded as learning but do not remain permanent failures after the resolution is evidenced;
- synthetic examples prove mechanics only.

## Outcome review

At each review point ask:

1. What metric changed since the prior review?
2. What new external evidence arrived?
3. Which assumption was strengthened or weakened?
4. What work created no decision value?
5. Which worker should be terminated?
6. Which handoff remains open and why?
7. What is the smallest next action that can materially change the mission state?
8. Should the mission continue, modify, wait or die?

## Integrity Gate commercial mission

The deployed Integrity Gate is currently a **software-validated / commercially-unvalidated** product primitive. The default outcome is not “build more features.” The default commercial mission is:

> Move Integrity Gate from internal/public technical proof toward real buyer evidence by testing one bounded change-propagation / evidence-reconciliation workflow with qualified manufacturers, ARs or regulatory operators, while keeping the existing Class III Transition Map Pilot as the only default DO NOW offer until commercial evidence earns a change.

Engineering backlog items should therefore be pulled primarily from real discovery, real delivery friction, adversarial test failures or repeated operational needs.

## Machine evaluator

Run:

```bash
clinicops-outcome-control /private/path/mission.json
```

The evaluator reports:

- outcome progress ratio;
- whether the target is achieved;
- control pass/fail;
- active worker count and cap compliance;
- completed-worker evidence integrity;
- handoff closure rate;
- unresolved control violations;
- highest commercial stage claimed;
- whether E4+ evidence requirements are satisfied.

A clean control pass means the mission record obeys the operating contract. It does **not** prove demand, revenue, PMF, founder independence or professional review.
