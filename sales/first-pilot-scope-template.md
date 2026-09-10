# ClinicOps first-pilot scope template

Status: **internal reusable commercial template**. Never commit buyer names, emails, portfolio files, pricing negotiations, confidential evidence, or client-specific details to this public repository. Copy this template into an approved private workspace before filling it in for a real prospect.

## Purpose

Convert a qualified buyer conversation into the smallest commercially useful Class III Transition Map engagement without ambiguity about inputs, outputs, evidence boundaries, human review, or acceptance criteria.

This template supports `EXP-001`. It is not a proposal generator, legal contract, regulatory opinion, or public marketing claim.

---

# 1. Pilot summary

**Buyer type:** [AR / regulatory consultancy / Class III or implantable manufacturer / other qualified portfolio owner]

**Portfolio scope:** [one manufacturer portfolio / one device family / another deliberately limited record set]

**Buyer problem in their own words:** [private copy only]

**Repeated workflow being tested:** [portfolio reconciliation / evidence control / identifier joins / certificate timing / SS(C)P operations / market-language handoff / other]

**Decision owner:** [private]

**Operational owner:** [private]

**Commercial form:** [paid pilot / design-partner pilot / priced scope requested]

**Commercial terms:** [fill only in private approved copy]

**Target delivery date:** [agreed date; do not promise a turnaround before confirming scope and input quality]

---

# 2. Scope boundary

The pilot covers only the supplied and/or explicitly reachable evidence agreed for this engagement.

The pilot does **not** constitute:

- a complete EUDAMED audit;
- a legal opinion;
- an autonomous compliance determination;
- a notified-body assessment;
- a substitute for the manufacturer's, authorised representative's, or responsible RA/QA team's judgement;
- evidence that a missing public field or link is itself non-compliance.

Unknown or unsupported facts remain explicit evidence gaps rather than being inferred.

---

# 3. Buyer inputs

Request only what is necessary for the agreed pilot. Where available:

- portfolio/device list;
- manufacturer/legal-entity identifier;
- actor role where relevant (MF / AR / PR / other supported role);
- Basic UDI-DI, UDI-DI, EUDAMED DI or other agreed join keys;
- certificate identifier, regime and timing already known to the buyer;
- SS(C)P metadata or controlled document references already available;
- target-market / language context where relevant;
- source documents or URLs the buyer is authorised to share;
- `as_of` date for the evidence population.

Do not block the pilot merely because optional fields are missing. Missing join keys may be valuable findings when recorded explicitly.

## Data handling before work starts

- Keep real portfolio files out of the public ClinicOps repository.
- Use an approved private storage location.
- Do not request patient-identifiable data.
- Confirm the buyer is authorised to share the material.
- Keep the evidence population and `as_of` date explicit.

---

# 4. ClinicOps work performed

For the agreed evidence population, ClinicOps will:

1. validate the supplied portfolio structure and surface input-quality issues;
2. normalize evidence-supported records and identifiers;
3. separate supported registration/portfolio categories without turning structural signals into compliance conclusions;
4. identify unresolved joins, missing evidence and conflicting fields that require review;
5. generate the deterministic operator-priority work queue;
6. perform human regulatory review of material next-step recommendations before delivery;
7. package the outputs in the current controlled client-bundle format.

Where a regulatory statement is needed, use only current claim-registry entries whose status and allowed use permit that statement.

---

# 5. Deliverables

Expected bundle schema `1.1`:

- `client_report.html` — human-readable portfolio work plan;
- `portfolio_report.md` — reviewable narrative report;
- `portfolio_report.json` — machine-readable representation of the same structured work queue;
- `intake_diagnostics.md` — input-quality and evidence-gap diagnostics;
- `manifest.json` — source/output hashes and bundle metadata.

Material findings should distinguish:

- supplied fact;
- public/reachable evidence;
- deterministic structural derivation;
- unresolved evidence gap;
- human-reviewed recommendation.

The priority score is an operator-triage aid only. It is not a regulatory-risk, compliance, legal, enforcement, or safety score.

---

# 6. Acceptance criteria

The pilot is complete when all of the following are true:

- the agreed evidence population is documented;
- input validation has completed and material warnings are reviewed;
- unresolved facts are explicitly marked rather than guessed;
- every material client-facing conclusion is traceable to the evidence actually supplied/reached;
- MF / AR / PR or other relevant role distinctions are preserved;
- the work queue is understandable to the buyer's operating owner;
- the human-review gate is completed before external delivery;
- the final bundle manifest and hashes correspond to the final source/output set;
- internal-only notes are excluded from the client-facing bundle.

A buyer disagreeing with a regulatory interpretation is not automatically a delivery defect; record the disagreement and re-check the evidence and governing claim before changing the output.

---

# 7. Execution commands

For a standard paid pilot, first copy `examples/standard_pilot_preflight.example.json` into the approved private workspace, replace the synthetic values with the private operating facts, and run the fail-closed activation check:

```bash
clinicops-pilot-preflight /private/path/activation-record.json
```

Do not begin material delivery unless the preflight returns `"status": "ACTIVATED"`. A failing result is **NON-STANDARD — NOT ACTIVATED** and must be parked or declined under `sales/commercial-activation-gate.md`, not bypassed with an ad-hoc transaction exception.

Then use an approved private path for real buyer data:

```bash
clinicops-portfolio-validate /private/path/portfolio.csv
clinicops-pilot-bundle /private/path/portfolio.csv /private/path/output YYYY-MM-DD
```

The bundle process must block on intake errors. Warnings and information gaps must be reviewed before interpretation or delivery. The preflight does not replace the final human-review gate.

---

# 8. Human-review gate

Before release to the buyer:

1. confirm the agreed population and evidence date;
2. review every material derived statement against the actual evidence set;
3. confirm structural signals are not presented as compliance findings;
4. verify role distinctions and responsibility context;
5. keep unsupported facts unresolved;
6. verify source/output hashes and bundle version;
7. remove internal comments and prospect-sensitive notes not intended for the buyer;
8. approve the final client-facing interpretation as the responsible human reviewer.

---

# 9. Pilot success test

The pilot is commercially informative when at least one of the following happens after delivery:

- buyer requests expansion to another device family or portfolio;
- buyer asks for recurring/repeat review;
- buyer asks for a priced next phase;
- buyer refers another relevant portfolio/team;
- buyer identifies the output as useful enough to replace or materially reduce a repeated manual reconciliation step.

Do not count politeness, compliments, opens, clicks, or a completed meeting as commercial validation.

Capture the actual result privately against `EXP-001`.

---

# 10. Follow-up decision

After the pilot, classify the result:

**Expand** — repeated pain confirmed and buyer wants another scope, repeat use or related work.

**Refine** — buyer values the problem but the scope, packaging, evidence request or handoff creates friction. Fix the smallest proven friction before adding features.

**Reposition** — useful work exists, but another buyer/problem/packaging path is clearly stronger.

**Stop / change hypothesis** — no meaningful value, urgency, budget path or repeated workflow is demonstrated.

If ten qualified target-buyer conversations still produce no concrete willingness to sponsor a pilot, no priced-scope request and no repeated evidence of budgeted urgency, pause product expansion and change at least one of buyer, problem, offer, packaging or distribution before building more functionality.

---

# 11. Short scope-email skeleton

Use only after a qualified conversation and customize privately:

**Subject:** ClinicOps — proposed narrow Transition Map pilot

Thank you for the discussion. Based on the workflow we discussed, the smallest useful test is a deliberately limited portfolio/record set rather than a platform rollout.

For that agreed set, ClinicOps would validate the supplied structure, reconcile evidence-supported identifiers and portfolio signals, surface unresolved evidence gaps, generate a prioritised work queue, and apply human review before delivery. Unsupported facts remain explicit rather than being guessed, and the responsible regulatory team retains final judgement.

To scope it accurately, the minimum useful starting material is the portfolio/device list plus the identifiers, certificate timing, source references and target-market context already available. Missing fields can remain visible evidence gaps.

**Proposed scope:** [private]

**Commercial terms:** [private]

**Target timing:** [private, only after input quality/scope confirmation]

If that scope matches the need, the next step is to agree the private input set and evidence date.

Do not send this skeleton unchanged. Tailor it to the buyer's actual workflow and remove sections that are not relevant.
