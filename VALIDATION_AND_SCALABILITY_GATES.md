# ClinicOps validation and scalability gates

Status: ACTIVE CONTROL

ClinicOps does not call an asset **validated**, **proven** or **scalable** merely because it exists, deploys successfully, passes CI, receives traffic or looks plausible internally.

## Validation dimensions

Every material asset is assessed separately across seven dimensions:

1. **Source validity** — factual/regulatory claims are tied to current authoritative evidence and stated limitations.
2. **Technical correctness** — deterministic logic, export/import behavior, edge cases, local-storage/session behavior and failure states work as specified.
3. **Usability** — representative intended users can understand the task, complete it and interpret the output without developer rescue.
4. **Workflow fit** — the output maps to a real operational decision, handoff, evidence queue or closure step owned by an accountable person.
5. **Buyer/user value** — an external intended user or buyer judges the result useful enough to save work, reduce ambiguity, improve control or support a real paid scope.
6. **Delivery repeatability** — the same bounded method works on independent cases without rebuilding the process from scratch.
7. **Scalability** — common inputs/outputs, bounded review work, measured marginal effort, resilient delivery and economics support expansion without proportional bespoke effort.

A pass in one dimension does not imply a pass in another.

## Lifecycle states

### PROTOTYPE
Internal build. No external-value claim.

Required:
- purpose and intended user defined;
- inputs/outputs and decision boundary documented;
- no unsupported public claims.

### PUBLIC — TECHNICALLY VERIFIED
May be deployed as a free/public asset.

Required:
- source claims checked where applicable;
- defined deterministic cases and material edge cases tested;
- no silent transmission or undeclared tracking;
- basic mobile and keyboard use checked;
- explicit unsupported-use boundary;
- clear next human owner / escalation path;
- no broken internal links or dead conversion path;
- repository integrity checks pass.

This state does **not** mean real-world validated.

### PILOT — EXTERNALLY TESTED
Representative intended users/cases have used the asset, but evidence is still limited.

Required:
- PUBLIC — TECHNICALLY VERIFIED gate passed;
- at least one independent external representative user/case completes the intended task;
- observed failure modes and confusion are captured;
- external usefulness feedback is recorded privately or in a sanitized evidence note.

### REAL-WORLD VALIDATED
The asset may be described internally as validated for the exact tested use case.

Required:
- PILOT gate passed;
- at least two independent representative users/cases complete the intended task without developer rescue;
- the accountable workflow owner judges the output useful for a real operational step;
- material failure modes found in pilot testing are addressed or explicitly bounded;
- no unsupported claim is needed to explain value;
- the exact validated use case/population is stated. Validation does not automatically transfer to another segment, jurisdiction or workflow.

For commercial validation, genuine E4+ buyer evidence is additionally required. Availability, traffic and internal testing are insufficient.

### REPEATABLE DELIVERY
Required before calling a paid method repeatable.

- at least three independent completed cases;
- common input/output schema holds;
- reviewer role and escalation rules remain stable;
- exceptions are measurable rather than ad hoc;
- turnaround and rework are measured;
- client-specific evidence remains private.

### SCALABLE
The word scalable may be used internally only after all of the following are evidenced:

- REAL-WORLD VALIDATED and REPEATABLE DELIVERY gates pass;
- at least three independent cases across at least two organisations or genuinely independent workflows, unless a stricter product-specific threshold exists;
- common input/output contract holds across cases;
- marginal delivery effort is measured and materially lower than bespoke reconstruction;
- human-review capacity is explicit and bounded;
- privacy/security responsibilities remain workable at greater volume;
- dependency failure has a portable fallback;
- delivery economics or operational capacity are measured, not assumed;
- no domain-specific authority is silently automated.

## Scale test

Before investing in infrastructure, answer with evidence:

- What work repeats exactly?
- What work remains expert judgment?
- What is the minimum complete input contract?
- Which exceptions consume most review time?
- What is marginal effort per additional case?
- Which dependency would stop delivery if it failed?
- Can a portable HTML/CSV/JSON/Markdown fallback keep the work moving?
- Does the next unit improve contribution margin, capacity or turnaround without degrading review quality?

If these are unknown, the asset is not yet scalable.

## Validation ledger contract

For every candidate product or major public tool, record:

| Field | Required |
| --- | --- |
| Asset / version | yes |
| Intended user | yes |
| Intended task | yes |
| Explicit non-use / boundary | yes |
| Source-validity status + refs | yes when claims are material |
| Technical test status + cases | yes |
| Usability evidence | yes before real-world validation |
| Workflow-fit evidence | yes before real-world validation |
| External-value evidence | yes before real-world validation |
| Independent completed cases | yes |
| Organisations / independent workflows represented | yes before scalable |
| Measured delivery effort | yes before repeatable/scalable |
| Failure modes / exceptions | yes |
| Current lifecycle state | yes |
| Smallest next validation test | yes |

Unknown stays **UNKNOWN**. Never promote an unknown field to pass because another field is strong.

## Public wording discipline

Allowed before external validation:
- "browser-local tool"
- "pilot-stage"
- "available for bounded review"
- "designed to help structure…"
- "technically verified for the defined test cases"

Not allowed without evidence:
- "validated"
- "proven"
- "guaranteed"
- "production-proven"
- "market-tested"
- "scalable"
- "reduces X%" or "saves Y hours" without measured evidence for the stated population

## Governance

The Validation & Scalability Sentinel owns gate interpretation. Release Sentinel owns technical release evidence. Opportunity Architect / Demand Signal Steward own demand-test design. Asset Fleet Builder owns implementation. Portfolio Operator owns activated delivery. Commercial evidence remains private unless deliberately sanitized.
