# ClinicOps founder-independence proof protocol

Status: **internal operating control**. This protocol evaluates whether the existing standard paid-pilot envelope has actually been executed without founder transaction-level decisions. It does not validate the commercial offer and does not replace qualified human regulatory review.

## Proof threshold

Founder-independent execution is proven only when `clinicops-delegation-proof` evaluates private operational records and finds either:

- at least **one qualifying real eligible paid pilot**; or
- at least **two qualifying complete controlled dry runs** with unique run IDs and distinct controlled-artifact bindings.

Anything else remains **FOUNDER-INDEPENDENT EXECUTION NOT PROVEN**.

The threshold comes from `sales/commercial-activation-gate.md`. Do not lower it transaction by transaction.

## What can never count

The following are categorically ineligible:

- CI runs;
- automated smoke tests;
- unit/integration tests;
- the public sanitized example under `examples/`;
- incomplete operator rehearsals;
- runs needing an Ali transaction-level decision;
- runs containing an unplanned or non-standard scope, claim or commercial exception;
- runs without a qualified named human reviewer and `REVIEW APPROVED` result;
- runs without final bundle integrity status `VERIFIED`;
- records not explicitly approved for proof use and retained in a private operational location;
- a copied execution relabelled with a different `run_id`.

Software can test the proof evaluator. Software tests are not proof of the organization operating independently.

## Private proof record

Keep real proof records and all referenced run artifacts out of this public repository. Store them together in the corresponding private scope/run evidence location.

A qualifying record must explicitly capture:

- unique `run_id`;
- `run_kind`: `paid_pilot` or `controlled_dry_run`;
- completion date;
- trained operator identity;
- qualified reviewer identity;
- private-record and proof-use authorization;
- confirmation that the run was not CI/automation;
- qualification stage completed;
- written scope stage completed;
- preflight status `ACTIVATED`;
- intake validation completed;
- schema-1.1 bundle generated;
- human review status `REVIEW APPROVED`;
- final bundle integrity status `VERIFIED`;
- controlled delivery/release stage completed;
- evidence, claim-safety, commercial and data-handling gates satisfied;
- zero founder transaction-level decisions;
- no unplanned exception;
- no non-standard scope, claim or commercial exception;
- controlled closeout completed;
- operational/commercial learning recorded privately against `EXP-001`;
- immutable SHA-256 bindings to the actual controlled artifacts listed below.

### Required artifact bindings

Proof schema `1.1` requires lowercase 64-character SHA-256 values for:

- `activation_record_sha256` — exact activation record used for the run;
- `preflight_result_sha256` — exact saved output from `clinicops-pilot-preflight` showing the evaluated result;
- `review_record_sha256` — exact completed private human-review record;
- `review_gate_result_sha256` — exact saved output from `clinicops-pilot-review-gate`;
- `bundle_manifest_sha256` — exact final `manifest.json` reviewed and released;
- `bundle_verification_record_sha256` — exact saved output from `clinicops-pilot-verify`;
- `source_sha256` — exact source portfolio/input population bound to the final bundle.

These hashes do not make a false attestation truthful. They prevent a proof record from floating free of the actual controlled files and make later substitution or accidental reuse detectable.

For the two-dry-run proof route, the evaluator also rejects two otherwise qualifying records that carry the same full artifact-binding fingerprint. Renaming one execution is not a second independent run.

For a real paid-pilot proof, the record must additionally confirm that it was a real eligible paid pilot and that the agreed payment/procurement path was followed through closeout.

For a controlled dry run, the record must explicitly state that it was **not** a real paid pilot and that it was a full operator dry run rather than a software smoke.

## Controlled dry-run procedure

A dry run exists to discover hidden founder decisions before a real client depends on the workflow. It is not a shortcut to commercial validation.

1. Use a fresh bounded synthetic scenario that exercises the standard paid-pilot envelope without real buyer data.
2. Have a trained operator execute the workflow as if it were a standard eligible paid pilot, beginning with qualification/scope simulation rather than jumping directly to bundle generation.
3. Use an approved private working location for the run record, activation record, saved gate results, review record and generated bundle. The public repository may contain sanitized templates only.
4. Save the actual preflight output rather than relying only on memory or a copied status, for example: `clinicops-pilot-preflight /private/path/activation-record.json > /private/path/preflight-result.json`.
5. Run intake validation and bundle generation under the normal controlled path.
6. Have the assigned qualified human reviewer actually perform the review, complete the private review record, and save the actual review-gate result: `clinicops-pilot-review-gate /private/path/activation-record.json /private/path/review-record.json /private/path/output > /private/path/review-gate-result.json`.
7. Immediately run final integrity verification and save the exact result: `clinicops-pilot-verify /private/path/output /private/path/portfolio.csv > /private/path/bundle-verification.json`.
8. Compute SHA-256 values from the exact final activation record, preflight result, completed review record, review-gate result, final manifest, final bundle-verification result and source portfolio. Record those values in the private proof record. Do not type substitute values from memory.
9. Simulate the delivery/release and closeout steps under the documented standard policy. Do not create a real invoice, PO, buyer claim or external communication for a dry run.
10. If the operator needs Ali to decide what the transaction should do, set `founder_transaction_decision_required` to `true`. The run fails proof. Do not ask Ali to make the run pass.
11. If an undocumented exception or decision class appears, set the corresponding exception field, stop treating that run as proof, document the decision class privately, and narrow or clarify the standard envelope before trying again.
12. Record dry-run learning privately against `EXP-001` as **operational/process learning only**. It does not count as a qualified buyer conversation, repeated-pain confirmation, willingness to pay or commercial commitment.
13. Complete a second independently executed dry run with a unique run ID and distinct controlled artifacts before claiming founder independence through the dry-run route.

A qualified human reviewer must actually perform the human-review steps. Auto-flipping review attestations, as CI does for packaging smoke coverage, invalidates a real proof run.

## Evaluation command

Collect only the private proof records intended for evaluation into a private JSON file containing a `runs` list, then run:

```bash
clinicops-delegation-proof /private/path/delegation-proof-runs.json
```

Only the exact status below permits the internal founder-independence claim:

```text
FOUNDER-INDEPENDENT EXECUTION PROVEN
```

A non-zero exit and `FOUNDER-INDEPENDENT EXECUTION NOT PROVEN` means the threshold is not met. Do not edit fields or hashes merely to force a passing result; correct the operating gap and execute a new qualifying run.

## Relationship to EXP-001 validation

Delegation proof and offer validation are separate questions:

- **Delegation proof:** can the documented standard pilot be executed safely without Ali making transaction-level decisions?
- **EXP-001 validation:** have real qualified buyers demonstrated repeated pain and concrete commercial commitment?

Two perfect dry runs can prove the first and prove nothing about the second.

## Public example

`examples/delegation_proof.example.json` exists only to document the record shape and exercise fail-closed tooling. It is intentionally marked:

- `private_operational_record: false`;
- `proof_use_allowed: false`;
- `ci_or_automated_smoke: true`.

Its SHA-256 strings are illustrative placeholders, not evidence. It must therefore remain ineligible by construction.
