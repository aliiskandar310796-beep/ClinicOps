# ClinicOps agent instructions

This repository is a regulated-domain operating system. Accuracy, evidence provenance and reversible execution outrank speed.

Read these files before substantive work:
- `AGENT_STATE.md`
- `CLAIM_RULES.md`
- `research/claims.jsonl` when regulatory claims are involved

Use the repository custom agents under `.github/agents/` when their scope matches the task.

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
