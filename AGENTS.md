# ClinicOps agent instructions

This repository is a regulated-domain operating system. Accuracy, evidence provenance and reversible execution outrank speed.

Read these files before substantive work:
- `AGENT_STATE.md`
- `CLAIM_RULES.md`
- `research/claims.jsonl` when regulatory claims are involved

Use the repository custom agents under `.github/agents/` when their scope matches the task.

Specialization gate (2026-09-18): before creating any new product, tool, service, page, workflow, agent, report or research program, ask **"does this strengthen EU MedTech Regulatory Data Integrity?"** If no — do not build it by default. If adjacent — record as backlog. If yes — it must serve a validated user problem, a core workflow, evidence, sales, delivery or reliability. Positioning source of truth: `01_STRATEGY/POSITIONING_2026-09-18_REGULATORY_DATA_INTEGRITY.md`. Customer-facing language uses the integrity/evidence/reconciliation taxonomy; OS/engine/fleet/swarm terms stay internal.

Non-negotiables:
- preserve dated corrections and rejected hypotheses as institutional memory;
- distinguish primary rule, observation, derivation and hypothesis;
- never infer full-register EUDAMED coverage from bounded probes;
- never treat missing public metadata as a compliance finding;
- keep MF, AR, IM and PR roles explicit;
- keep client/prospect/private mailbox/credential data out of the public repo;
- fetch latest `main` before writing and merge concurrent changes instead of overwriting them;
- run the relevant tests and GitHub Actions gates before declaring work complete;
- do not autonomously publish external regulatory content or send outbound communications.

Optimize for durable, composable assets that reduce repeated human reconciliation. Avoid agent sprawl, dashboard sprawl and recurring jobs without a demonstrated operational need.

## YAGNI / build-less rule (Ponytail-lite)
Before writing new code, check in this order: (1) is this feature actually needed now? (2) does the standard library or the platform already do it? (3) can an existing dependency do it? Only build if all three are no. Prefer deleting code over adding it; the smallest correct change wins. This rule applies to every subagent too.
