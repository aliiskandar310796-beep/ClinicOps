# ClinicOps temporary worker recruitment protocol

Status: canonical internal operating control

Purpose: let the six accountable ClinicOps agents recruit temporary specialist AI workers without creating agent sprawl, diluted ownership or activity theatre.

## Core rule

Temporary workers are **execution capacity, not accountable departments**. One of the six canonical agents must own every mission from start to verified handoff. The parent agent remains responsible for scope, evidence, control boundaries, outcome quality and termination of the worker.

Do not create a new durable agent merely because a task exists.

Recruit only when all of the following are true:

1. the mission has a named accountable parent agent;
2. the mission has a measurable outcome or decision target;
3. the worker has one bounded specialty and one bounded deliverable;
4. success/failure can be verified with evidence or an artifact;
5. the worker does not need authority beyond the parent agent's authority;
6. using a worker is cheaper/faster/safer than serial execution by the parent agent;
7. a stop condition is known before the worker starts.

Default team size is **1–3 temporary workers**. Hard concurrent cap is **5 active workers per mission**. If a mission appears to need more, reduce scope, sequence the work, or split it into separate accountable missions.

## Recruitable specialties

Use the smallest suitable role. These are temporary worker archetypes, not permanent departments.

| Specialty | Job | Typical parent |
| --- | --- | --- |
| `market-scout` | find current market/company/workflow signals and preserve source refs | Regulatory Evidence Steward / Opportunity Architect |
| `regulatory-source-analyst` | verify one bounded regulatory fact against primary sources | Regulatory Evidence Steward |
| `account-researcher` | prepare one bounded account/buyer brief from public/private approved evidence | Customer Discovery / Visibility Architect |
| `buyer-signal-analyst` | classify explicit buyer statements, objections and commitment signals | Customer Discovery / Opportunity Architect |
| `offer-scope-designer` | turn confirmed workflow pain into a small scope/test with metric and kill condition | Opportunity Architect |
| `distribution-operator` | execute one approved distribution/discovery task and measure the external result | Visibility Architect |
| `integrity-case-builder` | normalize declared controlled sources/surfaces into an Integrity Gate case | Portfolio Operator |
| `delivery-reconciler` | reconcile bounded client/sanitized evidence and surface contradictions | Portfolio Operator |
| `adversarial-qa` | challenge assumptions, output integrity, claims and failure modes | Release Sentinel / Regulatory Evidence Steward / Portfolio Operator |
| `automation-engineer` | automate repeated evidenced friction with tests and rollback | Release Sentinel / Portfolio Operator |
| `metrics-auditor` | verify outcome metrics, evidence refs, stage claims and denominator integrity | Release Sentinel / Opportunity Architect |
| `coordination-runner` | close deterministic handoffs and capability dependencies without inventing completion | Release Sentinel |

A parent agent may use a different temporary specialty only when the role is explicitly bounded in the mission record. Repeated creation of ad-hoc worker types is a signal to simplify the workflow.

## Worker outcome contract

Before recruitment, record:

- `worker_id`;
- `specialty`;
- `parent_agent`;
- exact objective;
- 1–5 success criteria;
- expected artifact/evidence;
- current commercial stage where relevant;
- allowed tools/data boundary;
- explicit stop/kill condition;
- receiving agent or department for the handoff;
- whether any next action is reserved for a human.

A completed worker without an artifact or evidence reference is not complete.

A worker may never self-promote an opportunity to `E4+`. `E4+` requires the same private external evidence as the company operating system.

## Authority boundaries

Temporary workers inherit the **narrower** of:

- the parent agent's authority;
- the mission's declared authority;
- ClinicOps global policy/approval boundaries.

Workers may not independently:

- publish LinkedIn or other public social posts across the existing approval gate;
- change pricing/Gumroad configuration;
- create third-party accounts/live form endpoints where approval is reserved;
- deploy analytics/tracking;
- rotate/revoke credentials or change branch protection/rulesets;
- sign scopes, approve purchases, move money or make binding buyer commitments;
- impersonate a qualified human reviewer;
- convert an automated screen into a legal/regulatory/compliance determination;
- place private buyer/client/device/proof data into public GitHub.

A worker encountering a reserved action returns a decision packet to the parent agent; it does not broaden its own authority.

## Parallelism rules

Parallelize only work that is genuinely independent.

Good parallelism:

- source verification + buyer/account research;
- one account brief per worker;
- code implementation + adversarial QA after interfaces are fixed;
- independent evidence extraction from non-overlapping sources.

Bad parallelism:

- multiple workers editing the same canonical file without coordination;
- multiple agents contacting the same buyer;
- duplicate market research with no distinct hypothesis;
- multiple workers trying to decide the same regulatory judgement;
- spawning workers to make an uncertain plan look busy.

One parent agent owns merge/reconciliation of parallel outputs.

## Termination and promotion

Terminate a worker when:

- its deliverable is verified and handed off;
- its stop/kill condition is met;
- the evidence shows the task is no longer useful;
- another worker already produced the needed result;
- progress is blocked by a true reserved-human or external capability dependency;
- two retries add no new information.

Do not promote a temporary specialty into a durable agent until **at least three independent missions** show the same recurring responsibility, inputs, outputs, authority boundary and measurable value. Even then, prefer improving the parent agent's playbook or automation before increasing the permanent fleet.

## Outcome rule

The question is never "how many agents worked?"

The questions are:

1. Did the mission metric move?
2. Did new external/commercial evidence appear?
3. Did a blocker disappear?
4. Did cycle time or expert effort fall without weakening controls?
5. Did the system create a reusable asset or learning?
6. Did the next accountable handoff close?

Worker count, token volume, drafts, code volume and meeting preparation are activity metrics unless they move one of those outcomes.

## Machine control

Use the outcome-control contract for material multi-agent missions:

```bash
clinicops-outcome-control /private/path/mission.json
```

The evaluator enforces parent ownership, the active-worker cap, evidence-bearing completion, E4+ evidence requirements, handoff integrity, outcome math and unresolved control violations.

Public/synthetic examples are contract tests only. Real buyer/client mission records stay private.
