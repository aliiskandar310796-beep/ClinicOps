# ClinicOps Integrity Gate — regulatory integrity review

Status: **SOFTWARE-VALIDATED / COMMERCIAL VALIDATION IN PROGRESS**

## The operational problem

One regulated fact changes. The practical question is whether every client-declared surface that should carry that fact still agrees: EUDAMED data, RIM/master data, IFU, SS(C)P, labels, artwork or other controlled records.

ClinicOps Integrity Gate is a bounded evidence-reconciliation and change-propagation workflow. It does **not** determine legal or regulatory compliance.

## What it does

1. loads client-approved controlled sources and declared downstream surfaces;
2. compares only the declared fields;
3. refuses to infer authority when supplied controlled sources disagree;
4. tests declared approved changes against the surfaces the client identifies as affected;
5. packages findings with evidence references;
6. requires a named human reviewer before the ClinicOps output can be delivered externally;
7. records review minutes and a reviewer disposition for every finding so usefulness and false positives can be measured.

## Machine states

- `PASS`
- `REVIEW_REQUIRED`
- `UNRESOLVED_AUTHORITY`
- `HOLD_FOR_HUMAN_DECISION`

All are operational evidence states, never automated compliance conclusions.

## Typical first review

- one device family / Basic UDI-DI group;
- 1–3 client-approved controlled sources;
- 2–6 downstream surfaces;
- 3–10 declared fields;
- optional approved change event;
- one qualified human reviewer.

The output is a human-reviewed evidence/discrepancy pack. The review gate applies only to external delivery of the exact ClinicOps work product. It never authorises release of a device, controlled document or regulatory submission.

## Economic validation

Before claiming value, measure it. Every live review should capture reviewer minutes, finding dispositions, false-positive rate, current-state manual review burden and the buyer's repeat/expand decision.

Public browser-local tools:

- `https://clinicops.dk/integrity-check.html`
- `https://clinicops.dk/integrity-economics.html`

Do not call Integrity Gate commercially validated until buyer and activation evidence reaches the ClinicOps commercial-validation threshold.
