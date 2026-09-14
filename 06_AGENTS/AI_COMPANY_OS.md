# ClinicOps AI Company OS

Status: **internal operating architecture**. This file defines how ClinicOps tests whether nearly the entire company can be operated through AI while preserving commercial truth, regulatory boundaries, privacy, security and qualified human review.

## Thesis

ClinicOps should not test whether AI can generate a lot of work. It should test whether AI can repeatedly turn market signals into **real commercial evidence and completed delivery loops** with minimal founder intervention.

The company loop is:

**Signal → qualification → experiment → buyer action → conversation → commitment → activation → delivery → review → payment / expansion → learning**

AI is the default operator for every step that can be safely delegated. Human involvement is treated as a scarce control surface, not the normal execution layer.

The target is not zero humans. The target is **zero unnecessary human coordination**.

## Operating principle

Every department must produce one of four things:

1. new external evidence;
2. movement of an existing opportunity toward or away from revenue;
3. a controlled client deliverable;
4. removal of a demonstrated execution bottleneck.

Activity without one of those outputs is not progress.

## Department model

Departments are workflow ownership lanes. They do **not** create a second agent fleet. The six canonical profiles in `.github/agents/` remain the execution roles.

| Department | Canonical owner | Mission | Evidence-producing output |
|---|---|---|---|
| Executive Orchestration | shared control layer | Allocate work, resolve dependencies, protect focus and measure intervention | ranked company queue, closed handoffs, decision log |
| Market & Regulatory Intelligence | Regulatory Evidence Steward | Find consequential market/regulatory change and maintain claim truth | validated signal, correction, claim-ready evidence, opportunity input |
| Revenue & Opportunity | Opportunity Architect | Convert evidence into sellable tests and kill weak ideas fast | opportunity record, experiment, scope path, commercial decision |
| Customer Discovery & Partnerships | Customer Discovery Agent | Obtain decision-grade buyer evidence and progress live relationships | qualified conversation, pain confirmation, objection, owner, commitment |
| Growth & Distribution | Visibility Architect | Create governed demand and route attention into measurable buyer actions | approved distribution asset, qualified inbound/outbound response |
| Client Delivery | Portfolio Operator | Execute activated work inside the standard controlled envelope | validated intake, controlled bundle, operator work queue, client output |
| Quality, Engineering & Resilience | Release Sentinel | Keep systems reproducible, recoverable and fail-closed | green release, verified workflow, incident correction, rollback path |
| Commercial Control | Opportunity Architect + Release Sentinel | Protect activation, scope, pricing authority and commercial integrity | activation record, exception classification, scope/payment evidence |
| Human Governance | Ali + assigned qualified reviewers | Perform decisions AI must not impersonate | explicit approval, professional review, signature/acceptance where required |

## Executive Orchestration

Executive Orchestration is not a seventh specialist agent. It is the routing layer used by the active AI execution engine.

Its job is to maintain one company queue ordered by:

1. revenue or commercial-evidence impact;
2. time sensitivity;
3. dependency unblock value;
4. downside of delay;
5. cost of execution.

It must prefer completing an existing revenue loop over opening another speculative workstream.

### Daily operating question

> What is the smallest action the company can complete today that creates external evidence, commercial movement, delivery progress or a verified reduction in execution friction?

## Canonical role contracts

### Regulatory Evidence Steward

**Inputs:** official sources, regulatory changes, public records, buyer questions, claim disputes.

**Must output:** evidence reference, date, source class, bounded interpretation, uncertainty, claim impact and downstream owner.

**Cannot output:** unsupported compliance conclusions, full-register claims from bounded probes, or buyer-specific conclusions without authorised evidence.

### Opportunity Architect

**Inputs:** validated signals, buyer evidence, pipeline state, service capabilities, delivery constraints.

**Must output:** buyer, problem, why-now, proposed offer, smallest test, success metric, kill condition, expected next commercial stage.

**Cannot count:** clicks, drafts, compliments, internal enthusiasm or synthetic runs as willingness to pay.

### Customer Discovery Agent

**Inputs:** live relationship, prospect context, experiment hypothesis, known objections.

**Must output:** exact buyer evidence: repeated pain `yes/no/unclear`, current workaround, consequence, owner, budget/approval path, commitment and next action.

**Cannot count:** generic regulatory discussion as qualification or a friendly meeting as validation.

### Visibility Architect

**Inputs:** approved claims, validated research, target buyer and distribution hypothesis.

**Must output:** governed asset plus a measurable path to a buyer action.

**Cannot publish externally without the applicable approval gate.**

### Portfolio Operator

**Inputs:** activated private scope and authorised source population.

**Must output:** controlled standard pilot bundle through the existing validation, review and verification path.

**Cannot substitute:** synthetic review, agent attestation or CI for a qualified human regulatory review.

### Release Sentinel

**Inputs:** code, workflow changes, release state, incidents, control failures.

**Must output:** reproducible verification, failing evidence, correction or rollback.

**Cannot treat:** a green test on the wrong SHA as proof of the deployed state.

## Reserved human decisions

The experiment deliberately routes everything through AI, but the following decisions remain reserved for a human unless the governing policy is explicitly changed:

- qualified professional review of regulated client-facing interpretation;
- signing contracts, accepting legal terms or making binding representations;
- approval of public LinkedIn publishing;
- Gumroad or material pricing changes;
- creation of third-party accounts or live form endpoints;
- analytics/tracking activation;
- credential, PAT, ruleset or branch-protection changes;
- transaction-specific exceptions to the standard commercial activation envelope;
- outbound communications where an existing approval rule requires Ali approval;
- spending, payment or banking actions not already covered by an approved bounded mandate.

These are **reserved decisions**, not founder-execution tasks. The AI should still prepare the evidence, recommendation, exact action and rollback path so the human decision is as small as possible.

## AI-first execution rule

For every non-reserved task, the AI should attempt the full loop before escalating:

**inspect → decide → execute → verify → record → hand off**

Escalation is justified only when:

- a reserved human decision is reached;
- a tool/account capability is genuinely unavailable;
- evidence is materially ambiguous and a human judgement is required;
- execution would violate an existing control;
- repeated execution has failed and another attempt would add no new information.

A founder preference request, clarification request or convenience question is an intervention and should be measured if the AI could reasonably have resolved it from existing evidence.

## Commercial evidence ladder

The company uses one common ladder so departments cannot inflate progress.

| Stage | Meaning | Counts as real commercial evidence? |
|---|---|---|
| E0 | internal hypothesis / idea | no |
| E1 | observed external market/regulatory signal | no |
| E2 | qualified reachable buyer/account identified | no |
| E3 | verified outbound/demand test delivered | no — execution evidence only |
| E4 | human buyer response or qualified conversation | yes |
| E5 | repeated pain / consequence / workflow confirmed | yes |
| E6 | concrete commercial commitment: priced-scope request, proposed pilot, procurement step, identifiable approval/budget owner | yes |
| E7 | commercially activated paid work / accepted PO or equivalent activation path | yes |
| E8 | accepted delivery and/or payment evidence | yes |
| E9 | repeat purchase, expansion, renewal or qualified referral caused by delivered value | yes |

No event may be recorded at E4+ without a private evidence reference.

## Handoff contract

Every cross-department handoff contains:

- task/event ID;
- source department;
- receiving department;
- objective;
- current commercial stage;
- evidence references;
- artifact references;
- exact next action;
- stop/kill condition;
- whether a reserved human decision is required.

The sender remains responsible until the receiver has accepted or completed the handoff. A task placed in another queue is not a completed handoff.

## Company queues

Only five active queues are allowed:

1. **NOW** — highest-value executable work;
2. **WAITING EXTERNAL** — buyer/reviewer/provider response required;
3. **WAITING HUMAN RESERVED DECISION** — AI has prepared the complete decision packet;
4. **TEST** — bounded experiment with metric and kill condition;
5. **PARKED / KILLED** — explicit reason and learning retained.

Do not create status taxonomies that do not change action.

## Real commercial execution loop

### 1. Intelligence

Find a signal. Verify it. Decide whether it changes a buyer problem or creates urgency.

### 2. Opportunity

Map the signal to a buyer already paying for adjacent work. Define the smallest service that can be sold before infrastructure is built.

### 3. Demand test

Prepare the account, message/asset, evidence and next-step path. Execute only within current communication approval rules. Measure human buyer behavior, not send volume.

### 4. Discovery

Use the conversation to falsify the hypothesis. Capture the workflow in the buyer's words and identify ownership and consequence.

### 5. Commitment

Ask for the smallest real commitment: workflow review, data set, scope request, paid pilot, procurement step or budget/approval owner.

### 6. Activation

Use the standard commercial activation gate. Non-standard work remains `NON-STANDARD — NOT ACTIVATED`.

### 7. Delivery

Run the standard controlled workflow against private authorised inputs. Human review remains real and independent.

### 8. Acceptance / payment / expansion

Record what the buyer actually does after delivery. Expansion, repeat use, referral or payment is stronger evidence than praise.

### 9. Learning

Update the opportunity, offer, buyer or distribution hypothesis. Build new automation only after the repeated work is proven.

## AI execution engines

ChatGPT, Claude or another approved AI runtime may act as the execution engine. The engine is not the department identity and is not the source of truth.

The repository/private operating records define:

- role;
- evidence state;
- decision rights;
- current queue;
- artifact state;
- commercial stage.

This lets models hand work to each other without inventing a second organisation.

## Success condition

ClinicOps has evidence that the company can be operated AI-first when all of the following are demonstrated over a bounded run:

- at least 90% of non-reserved completed tasks require no founder transaction-level intervention;
- at least 95% of cross-department handoffs close correctly;
- zero unauthorised sends/publications, private-data leaks or unsupported material claims;
- externally evidenced commercial stages are recorded honestly;
- the existing EXP-001 market threshold is met or falsified through genuine buyer evidence rather than internal activity;
- at least one complete commercial loop reaches activation and controlled delivery for a strong end-to-end proof, or the market hypothesis is explicitly rejected without AI operational failure.

An AI-operating pass and a market-validation pass are separate. AI can operate the company well while the offer fails. That result is useful and must not be hidden.

## Executable measurement

Use the private event log schema described in `03_OPERATIONS/AI_COMPANY_EXPERIMENT.md` and evaluate it with:

```bash
clinicops-company-run /private/path/company-run.json
```

Only synthetic examples belong in the public repository. Real buyer names, messages, prices, activation records and commercial evidence references remain private.

## Outcome control and temporary specialist workers

The six canonical agents remain the permanent accountable fleet. They may recruit temporary specialist AI workers under `06_AGENTS/WORKER_RECRUITMENT_PROTOCOL.md`; those workers do not become departments and do not inherit broader authority than the parent agent.

Material work should be expressed as an outcome mission under `06_AGENTS/OUTCOME_CONTROL_SYSTEM.md` before expanding the team. The mission defines one primary metric, baseline, target, current state, review point and stop condition.

Company WIP limits:

- maximum three top-level active missions unless an external deadline justifies an explicit exception;
- default one to three temporary workers per mission;
- maximum five active temporary workers per mission;
- one accountable parent agent per worker;
- one primary outcome metric per mission.

Use temporary workers for independent bounded slices such as source verification, account research, buyer-signal classification, offer scoping, distribution execution, delivery reconciliation, adversarial QA, automation and metrics auditing. Parallel workers must not edit the same canonical artifact blindly, contact the same buyer independently or duplicate regulatory judgement.

Every worker needs a bounded objective, success criteria, expected artifact/evidence, stop condition and handoff. Completed work without evidence/artifact is not complete. A worker cannot self-promote a commercial stage or cross a reserved-human approval boundary.

Evaluate material private missions with:

```bash
clinicops-outcome-control /private/path/mission.json
```

The outcome-control pass measures whether ownership, worker caps, metric evidence, handoffs and control integrity are sound. It is separate from `clinicops-company-run`: the former governs one outcome mission; the latter evaluates company-level autonomy and commercial progression across events.

The purpose of recruiting more AI is never to increase activity. Recruit only when it materially improves information gain, cycle time, evidence quality, buyer movement, delivery quality or resilience.
