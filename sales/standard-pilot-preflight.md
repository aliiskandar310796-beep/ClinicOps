# Standard paid-pilot preflight

Status: **internal execution control**. This is the executable projection of the standard paid-pilot delegation envelope in `sales/commercial-activation-gate.md`; it does not create a new offer, relax human review, or prove commercial validation.

## When to use it

For a real Class III Transition Map paid pilot, create the activation record only in approved private storage after the buyer has accepted the written scope and the commercial activation condition is satisfied. Then run:

```bash
clinicops-pilot-preflight /private/path/activation-record.json
```

A standard delegated pilot proceeds only when the command returns `"status": "ACTIVATED"` and exits successfully. Any missing, ambiguous, false, or non-standard envelope condition returns `NON-STANDARD — NOT ACTIVATED` with reasons and a non-zero exit status.

Do not override a failed preflight by editing the result, guessing an omitted field, or routing the transaction to Ali for an ad-hoc exception. Park or decline the non-standard work unless a later policy-level decision changes the approved envelope.

## Private activation record

Start from `examples/standard_pilot_preflight.example.json`, copy it into the approved private workspace, and replace only the private operating facts. Never commit a real buyer's record to this public repository.

The record deliberately requires explicit attestations for:

- `EXP-001` buyer eligibility and paid-pilot commercial form;
- written scope acceptance and identified commercial/procurement ownership;
- a bounded evidence population and standard deliverables;
- approved standard commercial terms and a satisfied activation condition;
- approved private storage, buyer authority to share, and explicit exclusion of patient-identifiable data;
- bundle schema `1.1`;
- a named, qualified human reviewer assigned before kickoff; and
- explicit absence of novel public claims, custom regulatory conclusions, non-standard liability, and unsupported interpretation.

Negative conditions are fail-closed. Omitting `patient_identifiable_data`, `unsupported_interpretation`, or another required negative attestation does not mean “no”; it blocks activation until the private record states the condition explicitly.

## What this control does not prove

A passing synthetic example or CI run is **not** a delegation proof run. Founder-independent execution remains unproven until the proof test in `sales/commercial-activation-gate.md` is satisfied by an eligible paid pilot or two complete controlled dry runs with the required human-review and closeout gates.

The preflight also does not replace intake validation, evidence review, claim governance, human regulatory review, bundle integrity checks, or commercial closeout. It only answers whether the transaction is inside the already-approved standard operating envelope before material work begins.
