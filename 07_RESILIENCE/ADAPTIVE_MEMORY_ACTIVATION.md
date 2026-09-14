# ClinicOps Adaptive Memory Activation

Status: internal operating architecture.

## Purpose

ClinicOps should remember enough to compound learning without dragging every old transcript, hypothesis and operational detail into every decision.

The operating rule is:

`retain evidence -> lower stale memory accessibility -> reactivate on relevance/uncertainty -> reinforce only when useful`

This is an original ClinicOps implementation of the general hierarchical / decay-driven memory-control idea. It does **not** import, vendor or copy NEC Research's Oblivion implementation. The public Oblivion repository currently describes its code as proprietary, so ClinicOps treats the research as architectural inspiration only unless a separate licence is obtained.

## Three layers

### L1 — durable control memory

Examples:

- `AGENT_STATE.md`;
- `CLAIM_RULES.md`;
- approval boundaries;
- commercial evidence ladder;
- permanent suppression / do-not-contact rules;
- active offer and kill criteria.

L1 is loaded first and decays slowly. A newer correction overrides an older hypothesis, but the correction history is preserved.

### L2 — semantic operating memory

Examples:

- validated regulatory claims and source metadata;
- current search/indexing state;
- market observations;
- known account facts;
- reusable buyer objections and workflow patterns;
- channel performance summaries.

L2 is activated by task-topic relevance and time sensitivity. Facts that can change must carry an observation date or source freshness signal.

### L3 — episodic evidence

Examples:

- specific buyer conversations;
- outreach delivery / bounce events;
- private pilot records;
- failed experiments;
- exact run artefacts;
- human-review evidence.

L3 is not retrieved merely because it exists. It is activated when a task requires operational history, proof, contradiction resolution, or the model is uncertain enough that deeper evidence could change the decision.

Private L3 evidence remains fail-closed unless the task explicitly permits private scope.

## Retrieval policy

The deterministic helper in `src/clinicops_os/adaptive_memory.py` scores memories from:

- task-topic overlap;
- current utility;
- confidence;
- interaction-based decay;
- layer retention;
- uncertainty-driven depth boost.

Decay changes retrieval priority, not retention. Evidence is never deleted merely because its accessibility score falls.

## Reinforcement policy

Increase utility only when a memory materially helps a verified outcome, such as:

- prevents a duplicate or prohibited outreach;
- catches an unsupported public claim;
- identifies an authoritative source conflict;
- changes account prioritisation correctly;
- shortens a controlled delivery step;
- helps convert E3 execution into E4/E5/E6 buyer evidence;
- prevents repetition of a documented failure.

Do not reinforce a memory because an agent repeated it, generated it confidently or found it convenient.

## Decay policy

Decay faster when:

- the fact is market- or account-specific;
- it is a one-off interaction detail;
- a newer observation exists;
- the information was low confidence;
- the memory has repeatedly entered context without affecting decisions.

Decay slowly when:

- it is a control or safety boundary;
- it is a dated correction to a previously wrong hypothesis;
- it defines a commercial truth test;
- it has repeatedly prevented errors.

## Promotion and demotion

A repeated L3 pattern may be promoted into L2 only after the underlying evidence supports a reusable statement.

A repeated L2 principle may be promoted into L1 only when it becomes an explicit company control, durable strategy or approval boundary.

L1 controls can be revised, but revisions must be explicit and preserve dated history rather than silently overwriting inconvenient evidence.

## Company use

Every agent run should conceptually follow:

`L1 controls -> relevant L2 facts -> L3 only when required -> action -> verified outcome -> memory reinforcement/decay`

This keeps ClinicOps high-agency without becoming high-interference: the company can explore broadly, while old context must earn its way back into working memory.
