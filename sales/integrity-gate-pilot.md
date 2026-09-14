# Integrity Gate pilot — internal operating scope

Status: **EXPERIMENTAL / TEST**
Public name: **ClinicOps Integrity Gate**
Default commercial status: **not yet commercially validated**

## Job to be done

Before a regulatory submission, document release or approved lifecycle change is treated as operationally complete, reconcile the client-declared controlled sources and downstream surfaces, identify discrepancies, preserve provenance, and route ambiguity to a qualified human reviewer.

The pilot is not a compliance audit and does not determine what the law requires for an unspecified device. The client defines the bounded source population, affected surfaces and fields to reconcile. RA/QA retains regulatory decisions.

## Recommended first pilot

Keep the first live pilot deliberately narrow:

- one device family or one Basic UDI-DI group;
- 1–3 client-approved controlled sources;
- 2–6 downstream surfaces;
- 3–10 declared fields;
- optional approved change set with explicit old/new values and affected surfaces;
- one named qualified human reviewer.

## Required inputs

1. client-approved controlled source(s) with evidence references;
2. downstream surfaces to inspect (for example supplied EUDAMED export, IFU, SS(C)P, label record, RIM/master-data extract);
3. declared reconciliation rules;
4. for change-propagation work: approved source, old value, new value and expected downstream surfaces;
5. named human reviewer for any external deliverable.

If supplied controlled sources disagree, record `UNRESOLVED_AUTHORITY`. Never silently choose a source.

## Outputs

The engine creates:

- `integrity_report.json`
- `integrity_report.md`
- `integrity_report.html`
- `manifest.json`

Every bundle is draft-only until human review is completed against the exact manifest/report hashes.

Review flow:

```bash
clinicops-integrity-gate /private/case.json /private/output
clinicops-integrity-review-prepare /private/output > /private/review.json
# qualified human completes the review record
clinicops-integrity-review-gate /private/review.json /private/output
clinicops-integrity-verify /private/output /private/case.json --require-review
```

External delivery of the **ClinicOps output bundle** requires `VERIFIED`, `REVIEW APPROVED`, and `release_ready=true`. The `release_ready` field applies only to delivery of that ClinicOps output. It is not authorization to release a device, controlled document or regulatory submission.

## Automated states

- `PASS`
- `REVIEW_REQUIRED`
- `UNRESOLVED_AUTHORITY`
- `HOLD_FOR_HUMAN_DECISION`

These are operational evidence states, not legal/compliance conclusions.

## Validation and kill criteria

Software validation can prove deterministic mechanics, hash binding, tamper detection and fail-closed review. It cannot prove demand.

Run discovery before product expansion. The Integrity Gate earns promotion from TEST only when buyer evidence reaches the existing EXP-001 threshold or an equivalent stronger commitment.

If qualified conversations do not show repeated pain, willingness to scope, or budget/procurement movement, keep the engine as an internal delivery primitive and do not expand it into a platform.

## Pricing

No public or standard price is set here. Pricing remains approval-gated and should follow buyer discovery plus delivery-time evidence.
