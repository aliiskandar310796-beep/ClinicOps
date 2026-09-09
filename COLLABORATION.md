# ClinicOps multi-agent collaboration contract

GitHub and Notion are the shared state between assistants working on ClinicOps. Do not assume another assistant has seen chat history.

## Read first
1. `CLAIM_RULES.md`
2. `research/corrections/2026-09-08-headline-reversal.md`
3. `PRIMARY_SOURCES.md`
4. `README.md`
5. Current Notion `ClinicOps OS — Command Center` and execution backlog

## Handoff protocol
Every material change should leave enough state for the next agent to continue without reconstructing context:
- what changed;
- why it changed;
- evidence/source;
- confidence and unresolved uncertainty;
- next executable action;
- whether an external action has already occurred.

Prefer commits and structured files over prose-only chat handoffs.

## Conflict resolution
When agents disagree, prefer in order:
1. current primary source;
2. reproducible public data;
3. explicit dated correction record;
4. tested code;
5. working hypothesis.

A newer assertion does not override an older correction unless the new evidence is recorded.

## High-agency rule
Do reversible research, analysis, code, tests, internal documentation and prioritisation without ceremony. Keep regulatory publication/outbound claims behind the claim gate and preserve source/limitation context.

## Lean rule
Do not create an agent, automation, dashboard or dependency merely because it is possible. Create it only when it removes repeated work, increases evidence quality, reduces operational risk, or produces a reusable asset.

## Current strategic thesis
The highest-value ClinicOps opportunity is the legacy-to-MDR transition work plan for class III/implantable portfolios, not an allegation that MDR manufacturer registrations generally lack linked SS(C)Ps. The free/public scan is the front door; accountable regulatory judgement is the paid layer.
