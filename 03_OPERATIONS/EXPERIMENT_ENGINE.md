# ClinicOps Experiment Engine

## Purpose

Turn commercial assumptions into bounded tests and preserve the resulting learning as institutional memory.

The executable registry lives in `src/clinicops_os/experiments.py`. A sanitized example lives in `examples/experiments.json` and can be validated/rendered with:

```bash
clinicops-experiments examples/experiments.json
```

## Required experiment contract

Every experiment records:

- `experiment_id`
- `opportunity_id`
- hypothesis
- target buyer
- smallest test
- metric
- success threshold
- kill condition
- supporting evidence
- status
- result
- learning
- decision
- optional reusable asset path

## Lifecycle

`planned -> running -> completed`

An experiment can also be cancelled when continuing would waste time or create unnecessary risk.

Completed experiments must record a result, learning, and one explicit decision:

- `scale`
- `modify`
- `kill`
- `repeat`

Incomplete experiments cannot be silently labelled successful.

## Operating rules

1. The experiment must test a commercial or product hypothesis, not manufacture a regulatory conclusion.
2. Prefer the smallest test that can change a decision.
3. Define the success threshold and kill condition before running the test.
4. Preserve negative results. A killed idea is useful knowledge.
5. Do not use vanity metrics when a qualified-buyer metric is available.
6. Link experiments to the Revenue OS through `opportunity_id` and, where useful, account records through `experiment_id`.
7. Client/prospect private data stays outside the public repository.
8. A reusable asset is a bonus, not a reason to continue an invalidated experiment.

## Default loop

Signal
-> Opportunity score
-> Experiment
-> Result
-> Learning
-> Decision
-> Reusable asset
-> Revenue / archive

## Initial experiments

`EXP-001` tests whether authorised representatives value portfolio-level transition work planning.

`EXP-002` tests whether evidence-approved research produces qualified conversations more effectively than generic compliance marketing.

Both are hypotheses. Neither should be presented externally as proven demand until the experiment record is completed with evidence.
