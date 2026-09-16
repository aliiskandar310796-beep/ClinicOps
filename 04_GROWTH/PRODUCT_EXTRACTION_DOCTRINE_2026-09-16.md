# ClinicOps Product Extraction Doctrine — 2026-09-16

Status: ACTIVE INTERNAL OPERATING RULE.

## Core principle

**Sell the pain. Standardize the repeated work. Automate only what survives reality.**

ClinicOps does not promote an attractive software idea into a core product because it sounds horizontal, innovative or technically feasible. Revenue work is the discovery engine. Every engagement should help answer:

> What part of this work could become infrastructure that the next 1,000 companies would pay for?

The route is deliberately asymmetric:

**painful niche → repeated paid work → stable primitive → standardized delivery → product candidate → expansion**

The product may become horizontal later. It does not need to begin horizontal.

## Exploit loop

For each real engagement, capture privately and in structured form:

1. trigger / event that created the work;
2. buyer and accountable owner;
3. current workaround;
4. inputs required to start;
5. systems / documents / people touched;
6. manual steps and review steps;
7. recurring failure modes;
8. outputs the buyer actually uses;
9. turnaround, rework and reviewer effort where measurable;
10. acceptance / rejection / return state;
11. willingness to pay and actual commercial movement;
12. whether the same job repeats;
13. what can be standardized without removing required human authority.

Named client, prospect and mailbox evidence stays outside the public repository. Public GitHub may contain only sanitized fixtures and aggregated learnings.

## Promotion states

### REJECTED
A plausible idea that fails a material market, competition, feasibility, authority, privacy or willingness-to-pay test. Keep the rejection reason so the idea is not repeatedly rediscovered without new evidence.

### OBSERVED PAIN
A recurring problem is visible in real workflows, but there is not yet enough paid and independent evidence to define a product.

### PAID PATTERN
Independent paid work shows a recurring job with materially similar inputs, outputs and failure modes. Product extraction can begin as internal tooling or a standardized service, but the company does not yet treat it as the core MVP.

### CORE MVP CANDIDATE
A product hypothesis may enter this state only when every hard gate below is evidenced.

## Hard gate for a core MVP candidate

All conditions are required:

- at least **10 completed real cases** of substantially the same underlying job;
- at least **3 independent organizations or genuinely independent buying workflows**;
- at least **5 buyers with evidenced willingness to pay** for the standardized version;
- at least **2 repeat purchases, reorders or recurring commercial commitments**;
- the same minimum input/output contract holds in at least **80% of cases**;
- buyers describe the problem or current workaround without being taught the proposed product category first;
- a documented competitor review shows the complete job is not already solved adequately by an incumbent for the target segment;
- at least one measurable value dimension is evidenced: rework avoided, reviewer effort reduced, turnaround improved, missed work detected, revenue unlocked, delay reduced, or another buyer-valued outcome;
- the standardized version requires materially less marginal effort than bespoke reconstruction;
- required human authority, expert judgment, privacy and escalation boundaries remain explicit;
- there is a credible path to repeated use rather than a one-off novelty purchase.

Unknown is not zero and is not pass. A missing gate blocks promotion.

## Evidence hierarchy

Strongest to weakest for product promotion:

1. repeat purchase / renewal / recurring paid use;
2. paid completed work accepted by an independent buyer;
3. signed scope / procurement / paid pilot;
4. explicit buyer willingness to pay tied to a real workflow;
5. unsolicited description of the pain / workaround by a target buyer;
6. repeated operational evidence from delivery;
7. job postings, RFPs, budget lines and consultancy spend showing active workaround economics;
8. competitor gaps and public reviews;
9. market reports / trend signals;
10. internal opinion, traffic, opens, CI, demos and agent enthusiasm.

Only the upper part of this hierarchy can close the core-product gate.

## Kill discipline

ClinicOps should kill ideas quickly when:

- a mature incumbent already solves the complete job adequately;
- the buyer cannot be identified clearly;
- the pain is interesting but not budgeted;
- the workflow is too rare to support repeat use;
- the product would require replacing a deeply embedded system before delivering value;
- delivery depends on unbounded expert judgment that cannot be standardized responsibly;
- privacy, authorization or liability makes the MVP disproportionate to the value;
- the standardized artifact does not reduce marginal effort;
- buyer conversations contradict the thesis.

Killed concepts stay killed until materially new evidence appears.

## Competitive doctrine

ClinicOps competes against consultancies by converting repeated work into reusable operating infrastructure instead of maximizing bespoke hours. It competes against software vendors by entering through a narrow painful job, working with the buyer's existing stack, and earning product scope through observed reality rather than platform ambition.

Do not build a generic horizontal platform merely because the addressable market sounds larger. Prefer a narrow problem with clear budget, ugly manual work, repeated failure and measurable buyer value.

## Build order

1. Sell and deliver the painful job manually or semi-manually.
2. Instrument the work privately.
3. Identify the invariant primitive across independent cases.
4. Standardize the service before building software.
5. Automate deterministic, reusable steps first.
6. Keep judgment, authority and exceptions visible.
7. Test whether customers buy the standardized result repeatedly.
8. Only then promote the primitive into a core MVP candidate.
9. Expand horizontally only after the primitive survives multiple real contexts.

## Relationship to existing ClinicOps governance

This doctrine governs **whether something deserves to become a product**. `VALIDATION_AND_SCALABILITY_GATES.md` governs **what may be claimed about a product once it exists**. Both apply. Technical success, public deployment, traffic or internal confidence cannot substitute for buyer evidence.
