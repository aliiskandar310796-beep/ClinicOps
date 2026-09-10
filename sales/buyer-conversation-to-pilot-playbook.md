# ClinicOps buyer conversation → first-pilot playbook

Status: **internal operator playbook**. Keep buyer-specific notes, names, emails, portfolio files and commercial details out of the public repository.

## Purpose

Use a real conversation to learn whether ClinicOps solves a repeated, budget-relevant portfolio problem and, only when the signal is present, move to the smallest useful Class III Transition Map pilot.

This playbook is deliberately narrower than a general sales script. The objective is not to win agreement in the room; it is to obtain decision-grade evidence for `EXP-001` and reduce friction between a qualified conversation and a controlled pilot.

## One-sentence positioning

ClinicOps provides a human-reviewed portfolio evidence and work-planning layer: it reconciles supplied/reachable regulatory evidence, makes gaps and unresolved joins explicit, prioritises what needs review, and leaves final regulatory judgement with the responsible team.

Do not position the service as an autonomous compliance audit, legal conclusion, or replacement for an authorised representative / RA-QA owner.

## Before the conversation

Open only the proof needed for the discussion:

- Public Transition Map sample: `https://clinicops.dk/transition-map-sample/`
- Browser-local assessment brief: `https://clinicops.dk/assessment-intake.html`
- Free readiness signal: `https://clinicops.dk/readiness-score.html`
- Class III transition page: `https://clinicops.dk/class-iii-transition.html`

Know the current commercial validation rule from `experiments/EXPERIMENT_LEDGER.md`. A positive conversation is not validation by itself.

If the relationship began around referrals, language services, AR support, or another adjacent service, preserve that original reason for the conversation. Introduce the Transition Map only if the buyer describes a portfolio reconciliation / evidence-control problem that it actually addresses.

## 25-minute conversation structure

### 0–5 min — relationship and workflow context

Understand the buyer's existing role before discussing ClinicOps tooling.

Questions:

1. What portfolio or client workflow consumes the most repeated reconciliation effort today?
2. Where does responsibility sit when device, certificate, identifier, SS(C)P or market-document evidence does not line up cleanly?
3. Is that work centralised, handled manufacturer-by-manufacturer, or split across systems / people?

Do not diagnose a defect from the answer. Capture the workflow and ownership problem.

### 5–15 min — test the repeated-pain hypothesis

Use questions that can falsify the offer:

1. Which joins or evidence checks are repeatedly reconstructed by hand?
2. What usually blocks action: missing evidence, uncertain ownership, identifier mismatch, timing, or regulatory judgement?
3. Does the same reconciliation pattern recur across more than one manufacturer / device family?
4. What is the consequence of not having a compact evidence-gap / work queue: delay, rework, duplicated review, handoff friction, or something else?
5. What would have to be true for an external evidence/work-planning layer to be worth using?

A useful signal is a concrete repeated workflow with an owner and consequence. Generic interest in EUDAMED or regulatory education is not enough.

### 15–20 min — show proof only if the problem is real

Use the sanitized Transition Map sample to demonstrate **structure**, not allegations about the buyer's portfolio.

Show four things only:

1. evidence-quality diagnostics;
2. explicit unresolved / missing evidence;
3. prioritised operator work queue;
4. human-reviewed next-step layer.

Explain that the public sample is generated from the same report path used by the pilot bundle. Do not claim that the sample proves a compliance outcome.

### 20–25 min — test the smallest commercial commitment

If the workflow pain is confirmed, ask for the smallest next step that creates buying evidence:

- permission to scope a deliberately small portfolio / record set;
- identification of the person who owns the portfolio evidence / budget decision;
- a request for a priced scope;
- a proposed design-partner or paid pilot;
- agreement to review the sample against one real workflow.

Do not force a pilot if the buyer has not described a relevant problem.

## Qualification decision

Mark the conversation **qualified for EXP-001** only when all of the following are true:

- target buyer is an AR, regulatory consultancy, Class III / implantable manufacturer, or equivalent portfolio owner;
- the discussion reaches a real portfolio / workflow rather than generic education;
- the buyer can describe repeated reconciliation / evidence-control work or explicitly says the problem is absent;
- next-step ownership is identifiable.

The current offer is not considered validated until the ledger threshold is met: three qualified conversations, two independent repeated-pain confirmations, and one concrete commercial commitment.

## Conversation branching

### Branch A — referral / partnership is the primary need

Preserve the partner relationship. Do not manufacture urgency for the Transition Map.

Useful next step: agree how referrals are routed, what ClinicOps can support, and whether there is a later operational workflow worth testing.

### Branch B — repeated portfolio reconciliation pain is present

Show the sample, confirm the exact repeated step, then propose a deliberately narrow pilot.

### Branch C — the buyer wants generic regulatory advice only

Answer within evidence boundaries, but do not count the conversation as commercial validation. Record that the current offer did not surface a budget-relevant workflow.

### Branch D — the buyer already has a system/process that solves the problem well

Treat this as negative evidence. Ask what makes their current process sufficient and which ClinicOps assumption is wrong. Do not pitch around the objection.

## Small pilot definition

The first pilot should be one manufacturer portfolio or another deliberately limited record set — not a platform rollout.

### Buyer supplies privately, where available

- portfolio/device list;
- actor role where known;
- identifiers already available;
- certificate / transition timing already available;
- target markets / language context where relevant;
- source files / URLs they are authorised to share.

Missing fields may remain explicit evidence gaps. Do not guess them.

### ClinicOps produces

- intake / evidence-quality diagnostics;
- normalized portfolio map;
- deterministic operator-priority work queue;
- unresolved evidence / join-key list;
- human-reviewed next-step plan;
- machine-readable output where useful;
- bundle manifest with source/output hashes.

The priority score is operator triage only. It is not a compliance, legal, enforcement or regulatory-risk score.

## Pilot execution path

Never place a real buyer portfolio or activation record in this public repository. The standard founder-independent path applies only to an eligible **paid pilot**. Design-partner work or any non-standard condition remains `NON-STANDARD — NOT ACTIVATED` unless the governing policy is changed at policy level.

With the authorised materials stored in an approved private location, start from the sanitized activation-record example and run the fail-closed commercial/operational preflight before material work:

```bash
clinicops-pilot-preflight /private/path/activation-record.json
```

Proceed only when it returns `"status": "ACTIVATED"`. Missing or ambiguous negative attestations do not default to safe; they block activation.

Then validate and generate the controlled bundle:

```bash
clinicops-portfolio-validate /private/path/portfolio.csv
clinicops-pilot-bundle /private/path/portfolio.csv /private/path/output YYYY-MM-DD
```

The bundle generator must block on intake errors. Review warnings / information gaps before interpreting outputs.

Expected bundle schema `1.1`:

- `client_report.html`
- `portfolio_report.md`
- `portfolio_report.json`
- `intake_diagnostics.md`
- `manifest.json`

After the qualified human-review gate and any required regeneration, verify the final private source and every schema-1.1 controlled output immediately before external release:

```bash
clinicops-pilot-verify /private/path/output /private/path/portfolio.csv
```

External release requires `"status": "VERIFIED"`. A mismatch means the controlled source/output set changed: correct or regenerate the bundle, repeat human review as applicable, and verify again. Do not edit hashes or the manifest to make changed files appear verified.

A successful synthetic example, CI preflight or CI bundle verification does **not** prove founder-independent execution. The delegation proof condition remains the one defined in `sales/commercial-activation-gate.md`.

## Human-review gate before client delivery

Before anything leaves ClinicOps:

1. verify the supplied evidence population and `as_of` date;
2. review every material derived statement against the evidence actually supplied/reached;
3. separate machine-detected structure from human regulatory judgement;
4. confirm MF / AR / PR distinctions where relevant;
5. leave unresolved facts unresolved rather than inferring them;
6. remove any internal-only notes not intended for the buyer;
7. approve the final client-facing interpretation as the responsible qualified human reviewer;
8. after any required regeneration, run `clinicops-pilot-verify` on the exact final private source/bundle and require `VERIFIED` immediately before release.

Integrity verification proves file correspondence, not regulatory correctness, and never replaces the responsible human review.

## Evidence boundaries for discussion

Use only claim-registry entries whose status and allowed use permit the discussion. Existing offer-spec references include `CO-CLM-0001`, `CO-CLM-0004`, `CO-CLM-0005`, `CO-CLM-0009` and `CO-CLM-0010` with their existing limitations.

Do not:

- allege non-compliance from public metadata;
- turn a B-prefix into proof of a specific compliance outcome;
- imply complete EUDAMED public-register coverage;
- present a non-binding recommendation as a statutory deadline;
- make claims about a buyer's portfolio without actual authorised evidence.

## Private post-call capture

Keep the actual notes in an approved private system, not this repository. Record only enough to make `EXP-001` decision-grade:

- buyer type;
- repeated pain present? `yes / no / unclear`;
- exact repeated step in the buyer's own words;
- operational consequence;
- current workaround;
- owner of the workflow;
- budget / approval owner if known;
- sample shown? `yes / no`;
- concrete commitment: `none / follow-up owner / portfolio review / priced scope / proposed pilot / paid pilot`;
- objection or reason not to proceed;
- next action and date;
- what ClinicOps assumption was strengthened or weakened.

Do not count compliments, clicks, or a friendly meeting as willingness to pay.

## Decision after each conversation

- **Strong signal:** repeated pain + owner + concrete next step → scope the smallest pilot.
- **Learning signal:** real pain but no budget / ownership → refine buyer, packaging or buying path, not the software.
- **Negative signal:** problem absent or already solved well → update the hypothesis and do not argue with the evidence.
- **No signal:** generic education only → do not treat as validation.

If ten qualified target-buyer conversations produce no concrete willingness to sponsor a pilot, no priced-scope request and no repeated evidence of budgeted urgency, pause product expansion and change at least one of buyer, problem, offer, packaging or distribution before building more functionality.
