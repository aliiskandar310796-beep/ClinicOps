# Integrity Gate pilot — internal operating scope

Status: **ACTIVE TEST / SOFTWARE-VALIDATED / ECONOMICALLY UNVALIDATED**
Public name: **ClinicOps Integrity Gate**

## Job to be done

Before a regulatory handoff, submission or controlled-document change is treated as operationally complete, reconcile the client-declared controlled sources and downstream surfaces, identify discrepancies, preserve provenance, and route ambiguity to a qualified human reviewer.

The pilot is not a compliance audit and does not determine what the law requires for an unspecified device. The client defines the bounded source population, affected surfaces and fields to reconcile. RA/QA retains regulatory decisions.

## First-pilot envelope

- one device family or one Basic UDI-DI group;
- 1–3 client-approved controlled sources;
- 2–6 downstream surfaces;
- 3–10 declared fields;
- optional approved change set with explicit old/new values and affected surfaces;
- one named qualified human reviewer;
- one review cycle.

Anything materially outside this envelope is separately scoped before activation.

## Required governance declarations

The operator CLI fails closed unless the private case explicitly records:

- `contains_patient_identifiable_data: false`;
- `processing_authorized: true`;
- `source_population_approved: true`.

Do not use Integrity Gate for patient-identifiable data. Do not place live client cases in the public repository.

## Required inputs

1. client-approved controlled source(s) with evidence references;
2. downstream surfaces to inspect (for example supplied EUDAMED export, IFU, SS(C)P, label record, RIM/master-data extract);
3. declared reconciliation rules;
4. for change-propagation work: approved source, old value, new value and expected downstream surfaces;
5. named qualified human reviewer for any external deliverable.

If supplied controlled sources disagree, record `UNRESOLVED_AUTHORITY`. Never silently choose a source.

## Outputs

- `integrity_report.json`
- `integrity_report.md`
- `integrity_report.html`
- `manifest.json`
- after genuine review: `review_gate.json`

Every bundle is draft-only until human review is completed against the exact manifest/report hashes.

```bash
clinicops-integrity-gate /private/case.json /private/output
clinicops-integrity-review-prepare /private/output > /private/review.json
# qualified human completes review_minutes, notes, all attestations and every finding disposition
clinicops-integrity-review-gate /private/review.json /private/output
clinicops-integrity-verify /private/output /private/case.json --require-review
```

Final verification may report `clinicops_output_delivery_ready=true` only for the exact ClinicOps work product. It never authorises release of a device, controlled document or regulatory submission.

## Reviewer dispositions

Every machine finding must receive exactly one human disposition:

- `CONFIRMED`
- `RESOLVED_BY_CONTEXT`
- `NOT_ACTIONABLE`
- `FALSE_POSITIVE`

The review record also requires actual reviewer minutes. Non-PASS bundles require reviewer notes. This creates measurable evidence about precision and delivery effort rather than allowing an unqualified approval click.

## Automated states

- `PASS`
- `REVIEW_REQUIRED`
- `UNRESOLVED_AUTHORITY`
- `HOLD_FOR_HUMAN_DECISION`

These are operational evidence states, not legal/compliance conclusions.

## Commercial activation

Material client work still requires written scope/acceptance plus an approved activation condition: upfront payment, agreed deposit/first milestone, or accepted PO/signed procurement path.

Internal willingness-to-pay experiments and promotion thresholds are defined in `sales/integrity-gate-commercial-validation.md`.

## What a live pilot must measure

Privately capture:

- current-state client review burden for comparable scope;
- input preparation minutes;
- automated reconciliation and change checks;
- machine findings by state;
- genuine reviewer minutes;
- human disposition for every finding;
- false-positive rate;
- total ClinicOps delivery time;
- client accept/reject/repeat/expand decision;
- invoice/payment evidence where applicable.

Do not claim labour savings until comparable before/after evidence exists.

## Kill rule

If 10 qualified target-buyer conversations produce fewer than two independent confirmations of repeated pain and no E6 commercial signal, stop expanding Integrity Gate as a standalone product. Change the buyer/problem/packaging/channel or retain the engine only as an internal delivery primitive.
