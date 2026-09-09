# ClinicOps repository instructions for GitHub Copilot

Before substantive work, read `AGENT_STATE.md` and `CLAIM_RULES.md`.

Use the narrowest relevant custom agent under `.github/agents/` when the task matches its scope:
- `regulatory-evidence-steward.agent.md` for regulatory claims, evidence, source verification and corrections;
- `portfolio-operator.agent.md` for intake validation, transition analysis, reports, JSON handoffs and pilot bundles;
- `release-sentinel.agent.md` for CI, workflows, deployment health, reproducibility and rollback.

Repository rules:
1. Treat `main` as canonical. Fetch the latest file before editing and merge concurrent changes rather than force-overwriting them.
2. Regulatory statements must preserve evidence class, limitations and allowed-use context from `research/claims.jsonl`.
3. Never revive the rejected narrative that MDR class III manufacturer registrations generally lack linked SS(C)P metadata without new evidence and a dated correction.
4. Never imply full-register EUDAMED coverage from bounded public API routes.
5. Keep MF, AR, IM and PR actor roles explicit and do not interpret PR/system-procedure-pack rows as ordinary MF registrations.
6. Treat B-prefix consequences as ClinicOps screening logic unless an official source explicitly states the exact consequence.
7. Never convert missing public metadata into a client-specific non-compliance allegation.
8. Keep client data, prospects, mailbox content, credentials and private named-device research out of this public repository.
9. Add tests before changing scoring, schema, validation or claim-gating semantics.
10. Do not weaken CI, Ruff, claim gates, registry audits, content-use validation or generated-fixture checks to make a build pass.
11. Do not autonomously publish external content, send email, modify LinkedIn or make client-facing compliance conclusions.
12. Prefer small reversible changes and portable Markdown/JSON/CSV over new platform dependencies.

When an observation changes, preserve the old dated observation, add the new evidence, and update the interpretation instead of deleting institutional memory.
