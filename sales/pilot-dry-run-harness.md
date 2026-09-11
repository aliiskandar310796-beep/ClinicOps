# Pilot dry-run harness

Status: **internal execution control**. This is a deterministic test harness for the standard paid-pilot execution path. It does not create a new offer, define pricing, or replace human regulatory review.

## What it proves, and what it does not

`clinicops-pilot-dry-run` runs the real standard-pilot code path end to end — preflight, bundle generation, the mandatory human-review checklist, and bundle-integrity verification — against a synthetic, non-confidential fixture. Every step calls the same functions a real pilot uses (`pilot_gate`, `bundle`, `human_review_gate`, `bundle_verify`); nothing is stubbed.

This proves the *tooling* can run the operator workflow without ad hoc intervention. It does **not** by itself prove **founder-independent execution**. Per the delegation proof test in `sales/commercial-activation-gate.md`, that standard is met only by one eligible real paid pilot, or **two** complete controlled dry runs, each with zero Ali transaction-level decisions and no unplanned exception — and each dry run is far more meaningful when the human-review checkpoint is completed by a genuine qualified reviewer reading real (even if synthetic) output, not a pre-filled attestation file. Running this harness with a canned review record is a mechanical smoke test, not a dry run for proof purposes; use it that way for CI, and run it with a real reviewer at the keyboard for an actual proof attempt.

## Usage

```bash
clinicops-pilot-dry-run <preflight.json> <review.json> <portfolio.csv> <output-dir> [YYYY-MM-DD]
```

- `preflight.json` — a standard pilot activation record; see `examples/standard_pilot_preflight.example.json` and `sales/standard-pilot-preflight.md`.
- `review.json` — a human-review confirmation; see `examples/human_review_confirmation.example.json`. Every field is a fail-closed attestation, same pattern as the preflight record — an omitted field is never treated as `true`.
- `portfolio.csv` — the bounded evidence population; see `examples/portfolio.csv` for the synthetic fixture shape.
- `output-dir` — where the schema-1.1 bundle is generated.

The command prints a dry-run completion record and exits non-zero if any step failed or the run halted before completion (`"escalated": true`). Sequence:

1. **Preflight** — `pilot_gate.evaluate_standard_pilot`. A non-standard record halts here; no bundle is generated.
2. **Bundle** — `bundle.build_pilot_bundle`. Produces the controlled schema-1.1 outputs and manifest.
3. **Human review** — `human_review_gate.evaluate_human_review`. A missing or incomplete review record halts here; verification never runs without it. This mirrors the real rule that a bundle must never leave ClinicOps without completed human review, regardless of what preflight and bundle generation already confirmed.
4. **Verify** — `bundle_verify.verify_pilot_bundle`. Recomputes and checks every source/output hash against the manifest.

## Recording a real proof run

A dry run intended to count toward the delegation proof test is not complete when the command exits zero. Record, privately (never in this public repository):

- who acted as the reviewer, and that they genuinely read the generated bundle rather than pre-approving it;
- the date and which of the two required runs this was;
- whether any step required a decision not already covered by the standard envelope — if so, this is exactly the "undocumented decision" the founder-independence proof test exists to surface; capture and resolve it in `sales/commercial-activation-gate.md` or `sales/standard-pilot-preflight.md` rather than treating the run as clean.

Two such runs (or one eligible real paid pilot), each with zero escalations, are what allow founder-independent execution to be described as proven — not the existence of this harness on its own.
