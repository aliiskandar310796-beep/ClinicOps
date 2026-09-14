# ClinicOps Economic Validation Protocol

Status: canonical commercial truth contract

Purpose: distinguish **market plausibility**, **buyer evidence**, **commercial commitment**, **paid transaction proof** and **repeatability** so software progress or attention cannot masquerade as economic validation.

## Core principle

Economic validation means somebody outside ClinicOps allocates scarce resources because the problem matters: time, internal ownership, procurement effort, budget, money, renewal or referral.

The evidence hierarchy is:

`category budget signal → buyer response → repeated pain → concrete commitment → activation → accepted delivery/payment → repeat/expansion`

Category spend is useful but not sufficient. A competitor charging money or a manufacturer hiring a dedicated role proves budget exists around the workflow; it does not prove the buyer will purchase ClinicOps.

## Evidence classes

### Supporting market evidence — not buyer validation

`market-budget-signal` examples:

- a medical-device manufacturer hires dedicated EUDAMED/UDI/regulatory-data staff;
- a current job description explicitly owns regulatory data quality, change impact or lifecycle maintenance;
- a comparable vendor charges subscription/professional-service fees for traceability/change control;
- a mandatory regulatory deadline creates observable workload.

These normally remain E1/E2.

### Direct buyer evidence

- `buyer-response` — E4;
- `pain-confirmation` — E5;
- `commercial-commitment` — E6;
- `activation` — E7;
- `accepted-delivery` — E8;
- `payment` — E8;
- `expansion` — E9.

Every E4+ record requires a private evidence reference and a stable private buyer key so independent buyers can be counted without putting identities in public GitHub.

## EXP-001 market threshold

The current default threshold remains:

1. at least 3 qualified buyer conversations;
2. at least 2 independent confirmed repeated pain/workflow/consequence signals;
3. at least 1 concrete commercial commitment.

This is a **market evidence threshold**, not yet transaction proof.

## Initial economic proof

Do not call an offer economically validated merely because EXP-001 passes.

Initial economic proof additionally requires:

- at least the configured minimum number of paid buyers (default real private threshold should be >=1);
- actual payment evidence;
- direct cash cost captured for paid work;
- actual delivery/review hours captured where the service consumed material expert time;
- contribution before labor is not negative;
- configured revenue-per-delivery-hour target is met when such a target is supplied;
- no unresolved critical risk in the linked risk register.

If accepted delivery exists but payment is pending, record E8 truthfully but do not count a paid buyer yet.

## Repeatability proof

One payment can prove that the transaction is possible. It does not prove a business.

Repeatability is stronger when either:

- at least 3 independent buyers pay for substantially the same bounded offer; or
- at least 1 buyer reaches E9 through repeat purchase, expansion, renewal or a qualified referral caused by delivered value;
- delivery economics remain within the configured thresholds rather than deteriorating with each case.

## Pricing experiments

Test willingness to pay without corrupting trust:

- prefer a bounded fixed-price pilot or paid diagnostic;
- define scope, review boundary and delivery conditions before quoting;
- avoid open-ended discounting;
- when testing price, change one material pricing variable at a time;
- record explicit buyer objections, not inferred price sensitivity;
- distinguish `too expensive`, `no budget owner`, `no urgency`, `procurement friction`, and `problem not important`;
- never count an unaccepted quote as revenue.

Public/Gumroad pricing changes remain subject to existing approval controls. Private scope/quote preparation may proceed inside approved commercial authority, but binding commitments and exceptions remain governed.

## Unit-economics fields

For paid delivery capture privately:

- actual payment amount;
- direct cash cost;
- actual AI/operator preparation time where measurable;
- qualified human review time;
- total delivery hours;
- rework/iteration count;
- payment timing;
- accepted-delivery status;
- expansion/referral outcome.

The machine evaluator currently uses total delivery hours and direct cash cost. Keep more granular timing privately for future learning.

## Market evidence already supporting the Integrity Gate hypothesis

As of 2026-09-14, current public evidence supports **budgeted category spend** around the problem:

- the European Commission states the EUDAMED UDI/Device module became mandatory to use from 28 May 2026;
- current medical-device hiring includes dedicated EUDAMED/UDI leadership, regulatory data governance and RIM/data-quality responsibilities;
- current regulatory roles explicitly own change-impact assessment and downstream labeling/document accuracy;
- adjacent medical-device workflow vendors monetize traceability/change-control/QMS automation through subscription and enterprise sales models.

This evidence raises plausibility but remains E1/E2. It does not advance Integrity Gate to E4.

## Economic validation mission for Integrity Gate

Primary question:

> Will a qualified manufacturer, AR or regulatory operator allocate budget to detect and resolve cross-system regulatory-information/change-propagation gaps before release or submission?

Secondary questions:

- Which narrow workflow owns the budget: UDI/EUDAMED data, document control, labeling, lifecycle change, AR portfolio oversight, or another adjacent process?
- Is the buyer paying to reduce expert hours, prevent rework, accelerate release/submission, improve evidence quality, or reduce audit/remediation risk?
- What source population is realistic to ingest without expensive preprocessing?
- What false-positive rate/reviewer burden is acceptable?
- Does the buyer prefer a service, recurring managed control, or software integration?

Do not build the answers. Obtain them from buyer behavior.

## Machine evaluator

Use a private ledger:

```bash
clinicops-economic-validation /private/path/economic-validation.json
```

The evaluator separates:

- category budget signals;
- unique qualified buyers;
- pain confirmations;
- concrete commitments;
- activations;
- paid buyers and revenue;
- contribution before labor;
- observed revenue per delivery hour;
- expansion/repeatability evidence;
- EXP-001 pass;
- initial economic proof;
- repeatability proof.

Synthetic examples are mechanics only. Real buyer keys, quotes, payment records and private evidence stay outside public GitHub.
