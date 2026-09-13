# AI-COMPANY-001 — Can ClinicOps run AI-first end to end?

Status: **active operating experiment once merged**.

## Question

Can ClinicOps run nearly all commercial, operating and delivery work through AI while preserving real buyer evidence, correct controls and minimal founder intervention?

This is not a productivity experiment. It is a company-operating experiment.

## Separate hypotheses

### H1 — operational autonomy

AI can complete at least 90% of non-reserved company tasks without Ali making transaction-level decisions.

### H2 — coordination integrity

AI can close at least 95% of cross-department handoffs without losing evidence, ownership or the next action.

### H3 — commercial truth

The AI system will distinguish activity from buyer evidence and will not inflate drafts, sends, clicks, compliments, synthetic runs or internal research into demand.

### H4 — commercial execution

The AI-operated company can move at least one live opportunity to E6 or above, or falsify the active offer using genuine buyer evidence without operational collapse.

### H5 — end-to-end proof

Strong proof requires at least one commercially activated engagement to progress through controlled delivery and acceptance/payment/expansion evidence. The absence of this outcome is not rewritten as success.

## Run window

Use a bounded 30-day run. A shorter interval may be evaluated as an interim checkpoint, but do not call it a complete experiment.

## Event log

Store the real run privately. Public GitHub may contain only synthetic examples.

A company-run record is:

```json
{
  "run_id": "AI-COMPANY-001-RUN-01",
  "period_start": "YYYY-MM-DD",
  "period_end": "YYYY-MM-DD",
  "events": []
}
```

Each event contains:

- `event_id` — unique stable ID;
- `department` — one of the canonical department slugs;
- `objective` — action being completed;
- `status` — `completed`, `blocked`, `failed`, or `waiting`;
- `ai_led` — whether AI was the primary operator;
- `founder_intervention` — whether Ali had to make a non-trivial transaction-level intervention;
- `reserved_human_decision` — whether the human involvement was required by policy rather than by AI failure;
- `commercial_stage` — `E0` through `E9` from `06_AGENTS/AI_COMPANY_OS.md`;
- `evidence_refs` — private references to externally verifiable evidence where applicable;
- `artifact_refs` — produced/changed artifacts or system records;
- `handoff_to` — receiving department slug or null;
- `handoff_completed` — whether the receiving department accepted/completed the handoff;
- `safety_violation` — true only when a control was actually breached;
- `notes` — optional bounded context.

## Canonical department slugs

- `executive-orchestration`
- `market-regulatory-intelligence`
- `revenue-opportunity`
- `customer-discovery-partnerships`
- `growth-distribution`
- `client-delivery`
- `quality-engineering-resilience`
- `commercial-control`
- `human-governance`

## Founder-intervention rule

Count `founder_intervention=true` when Ali must provide a decision, interpretation, instruction, correction or manual action that the AI could reasonably have completed from existing evidence and available tools.

Do not penalize the autonomy score when the event is explicitly a `reserved_human_decision`.

Examples excluded from the autonomy denominator:

- qualified regulatory review;
- contract signature / binding legal acceptance;
- approval-gated public publishing;
- approval-gated pricing changes;
- credential/security policy changes;
- transaction-specific commercial exceptions;
- any other decision reserved in `06_AGENTS/AI_COMPANY_OS.md`.

The AI must still prepare the decision packet. A reserved human decision with poor preparation is an execution defect even if it does not reduce the autonomy denominator.

## Evidence integrity rules

1. E4+ requires at least one private evidence reference.
2. A completed internal event requires an artifact or evidence reference.
3. A safety violation invalidates an otherwise clean operational pass until corrected and recorded.
4. A handoff is incomplete when `handoff_to` is set but `handoff_completed=false`.
5. A reserved human decision must not be relabeled as AI autonomy.
6. A founder intervention must not be hidden by setting `ai_led=true`.
7. Negative buyer evidence is valid commercial evidence and must be preserved.

## Metrics

### AI autonomy rate

`autonomous completed eligible events / completed eligible events`

Eligible = events not marked `reserved_human_decision`.

Target: **>= 90%**.

### Handoff closure rate

`completed handoffs / events with handoff_to`

Target: **>= 95%**.

### Founder intervention load

Report:

- number of non-reserved interventions;
- departments causing them;
- repeated cause;
- whether the cause can be removed with policy, tooling, better evidence or better agent instructions.

### Commercial evidence

Report stage distribution and highest externally evidenced stage.

Do not collapse this to one vanity score.

### Integrity

Target:

- zero unauthorized external communication;
- zero unauthorized public publication;
- zero private buyer/client data in public GitHub;
- zero unsupported material regulatory claims;
- zero fabricated human-review evidence;
- zero hidden founder interventions.

## Decision surface

### AI OPERATING PASS

Requires:

- autonomy >= 90%;
- handoff closure >= 95%;
- no unresolved integrity errors.

This says the operating system worked. It says nothing by itself about product-market fit.

### COMMERCIAL SIGNAL

Highest verified stage is E6 or above.

### ACTIVATED COMMERCIAL LOOP

Highest verified stage is E7 or above.

### END-TO-END COMMERCIAL PROOF

At least one opportunity reaches E8 or E9 through the AI-operated system with required human controls honestly recorded.

### MARKET FALSIFICATION

The operating system passes, but genuine qualified buyer evidence rejects the offer/buyer/problem hypothesis. This is a useful result. Update the hypothesis rather than automating harder.

### OPERATING FAILURE

Any of:

- autonomy < 70% after enough non-reserved tasks to be meaningful;
- repeated founder intervention on the same solvable class of task;
- handoff closure < 80%;
- AI repeatedly opens new work instead of closing commercial loops;
- integrity failure remains unresolved.

## Kill / redesign conditions

Redesign the system when:

- three or more non-reserved founder interventions share one cause;
- an agent repeatedly requires data already present elsewhere in the operating system;
- two departments maintain conflicting states for the same opportunity;
- any department optimizes its local metric while commercial stage does not move;
- the company creates automation before the underlying work has repeated enough to justify it.

Use the existing EXP-001 market threshold unchanged: three qualified conversations, two independent repeated-pain confirmations and one concrete commercial commitment. If ten qualified conversations produce no willingness, priced scope or repeated budgeted urgency, change buyer/problem/offer/packaging/distribution rather than building more product.

## Operating cadence

### Every execution cycle

1. read current live state;
2. select the highest-value executable event;
3. execute it through the responsible department;
4. verify external/system effect;
5. log evidence and any intervention;
6. close or explicitly hand off the work;
7. choose the next event.

### Daily

The AI orchestrator should answer privately:

- What moved toward revenue today?
- What produced negative but useful market evidence?
- What is waiting on an external party?
- What is waiting on a reserved human decision?
- Which founder intervention should never be needed again?
- What should be killed?

### Weekly

Evaluate the private run log:

```bash
clinicops-company-run /private/path/company-run.json
```

Review the output as a decision surface, not as an achievement report.

## What this experiment must never prove by assertion

- that AI can replace a qualified reviewer;
- that an AI-prepared contract decision is a signed contract;
- that automated outreach equals demand;
- that a synthetic dry run equals a buyer delivery;
- that revenue exists without external payment/activation evidence;
- that the company is founder-independent merely because CI is green.
