# ClinicOps Integrity Gate — experimental pilot

## Positioning

ClinicOps Integrity Gate is an experimental pre-release evidence-reconciliation and change-propagation workflow for medical-device regulatory information.

It is designed to answer a bounded operational question:

> Does the supplied regulatory information still agree across the declared controlled sources and downstream surfaces, and did an approved change propagate everywhere the client says it should?

It does **not** determine legal or regulatory compliance.

## Core workflow

1. ingest client-approved controlled sources and declared downstream surfaces;
2. compare declared fields against the supplied authoritative value where one unambiguous value exists;
3. refuse to infer authority when supplied controlled sources disagree;
4. test declared approved changes against the downstream surfaces the client identifies as affected;
5. classify discrepancies as review-required, unresolved authority, or hold-for-human-decision;
6. package every finding with evidence references;
7. require a named human reviewer before external delivery of the ClinicOps output.

## Automated gate states

- `PASS` — no discrepancy found by the declared automated checks;
- `REVIEW_REQUIRED` — a supplied field is missing or does not match the single supplied controlled value;
- `UNRESOLVED_AUTHORITY` — supplied controlled evidence does not establish one authoritative value;
- `HOLD_FOR_HUMAN_DECISION` — an approved change has not propagated, a declared change source does not match the new value, or a downstream surface contains a conflicting value.

All four states remain human-review gated before the ClinicOps output can be delivered externally. Human approval of that output does not authorize release of a device, controlled document or regulatory submission.

## Synthetic example

Controlled source:

- IFU revision: `IFU-12`

Declared downstream surfaces:

- IFU: `IFU-12`
- EUDAMED export: `IFU-11`

Declared approved change:

- old value: `IFU-11`
- new value: `IFU-12`
- expected surfaces: IFU + EUDAMED

Automated result:

- `HOLD_FOR_HUMAN_DECISION`
- finding code: `CHANGE_NOT_PROPAGATED`
- evidence references: controlled source + EUDAMED export
- ClinicOps output delivery: human review required

The example is synthetic and demonstrates mechanics only. It is not buyer validation or a compliance finding.

## Current validation status

The MVP is validated for deterministic software behaviour through automated tests, synthetic fixtures, bundle hashing, tamper detection, and a fail-closed human-review gate.

Commercial validation remains separate. ClinicOps should only call the offer commercially validated after real buyer conversations and commitments meet the existing EXP-001 thresholds.

## Initial pilot boundary

A pilot should stay small:

- one device family or Basic UDI-DI group;
- a bounded set of client-approved controlled sources;
- a bounded set of downstream surfaces;
- explicit fields and change-propagation expectations;
- one human reviewer;
- no automatic regulatory judgement.

Pricing is intentionally not set in this deployment pack.
