# ClinicOps Regulatory Integrity Review

Internal engine name: **Integrity Gate**. Public service name: **Regulatory Integrity Review**.

Status: software-validated; commercially available as a bounded review; commercial validation continues through real buyer workflows and activation evidence.

## Operational problem

One regulated fact changes. The practical question is whether every client-declared surface that should carry that fact still agrees: EUDAMED data, RIM/master data, IFU, SS(C)P, labels, artwork or other controlled records.

ClinicOps performs evidence reconciliation and change-propagation review. It does **not** determine legal or regulatory compliance.

## Review flow

1. client defines the evidence population and fields in scope;
2. ClinicOps loads client-approved controlled sources and declared downstream surfaces;
3. deterministic comparisons run where the evidence permits them;
4. conflicting controlled sources become **AUTHORITATIVE SOURCE UNRESOLVED** rather than a guessed value;
5. approved changes are checked against the downstream surfaces the client identifies as affected;
6. findings are packaged with source references and action ownership;
7. a named qualified human reviews the exact output before external delivery.

## Machine states

- `PASS`
- `REVIEW_REQUIRED`
- `UNRESOLVED_AUTHORITY`
- `HOLD_FOR_HUMAN_DECISION`

These are operational evidence states, never automated compliance conclusions.

## Typical first review

- one device family / Basic UDI-DI group;
- 1–3 client-approved controlled sources;
- 2–6 downstream surfaces;
- 3–10 declared fields;
- optional approved change event;
- one qualified human reviewer.

## Deliverable proof

Stable public specimen permalink:

`https://clinicops.dk/specimen-register/`

The current specimen is synthetic and demonstrates the discrepancy-register structure: findings, evidence excerpts, action routing, unresolved-authority handling and RA/QA decision ownership.

## Commercial continuation

The review is the entry point, not the whole business:

**Review → Remediate → Maintain**

### Regulatory Information Remediation

After client RA/QA approves authoritative values, ClinicOps can coordinate agreed corrections across records and documents placed in scope.

### Regulatory Change Operations

For recurring change, ClinicOps can identify impacted records, map affected surfaces, coordinate implementation, verify propagation and document closure.

## Evidence boundary

The review gate applies only to external delivery of the exact ClinicOps work product. It never authorises release of a device, controlled document or regulatory submission. Client RA/QA retains authoritative-source and release decisions.

## Economic validation

For live work, measure reviewer minutes, finding dispositions, false positives, current-state manual review burden, confirmed operational value and buyer repeat/expand decisions. Do not manufacture a savings percentage or call the market commercially validated without buyer evidence.
