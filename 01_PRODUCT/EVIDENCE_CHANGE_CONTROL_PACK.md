# Regulatory Change Integrity Review (Evidence Change Control Pack)

Status: AVAILABLE FOR BOUNDED SCOPING — not yet described as real-world validated or scalable.

This specification underlies the flagship commercial offer **Regulatory Change Integrity Review** (see `02_PRODUCTS/PRODUCT_REGISTRY.md` and `01_STRATEGY/POSITIONING_2026-09-18_REGULATORY_DATA_INTEGRITY.md`). "Evidence Change Control Pack" remains the internal name of the delivery format.

## Purpose

Turn one declared approved/authoritative change and a bounded evidence population into a reviewer-ready reconciliation and closure packet.

This is a paid ClinicOps delivery format, not an automated compliance verdict.

## Intended buyers / users

- medical-device regulatory / quality (RA/QA) teams — the primary market;
- EU authorised representatives and specialist regulatory consultancies managing manufacturer portfolios — the partner channel.

Narrowed 2026-09-18: earlier horizontal buyer lists (trials, labs, clinics, clinical AI, generic controlled content) are removed from the target market until real delivery evidence proves an expansion; the method remains domain-portable internally.

## Minimum input contract

A scoped engagement must declare:

1. one change event or tightly related change set;
2. authoritative / approved source reference;
3. version / approval / effective-date evidence where available;
4. declared population of affected or potentially affected records, systems, documents, vendors, sites or people;
5. available evidence exports / links / controlled copies;
6. accountable client/project owner;
7. known decision boundaries and domain-specific reviewer needs.

If the evidence population cannot be bounded, the engagement remains discovery/scoping until a defensible population is established.

## Deliverables

### 1. Source register
- approved/authoritative source reference;
- source version / date;
- provenance/evidence pointer;
- scope assumptions and exclusions.

### 2. Change-surface matrix
For each declared operational surface:
- surface / record / system / document;
- expected relationship to the change;
- evidence observed;
- deterministic comparison where appropriate;
- status: aligned / mismatch signal / missing evidence / not applicable / unresolved;
- accountable owner;
- required closure evidence.

A deterministic mismatch is a review signal, not a regulatory, clinical, safety or compliance conclusion.

### 3. Unresolved queue
- missing evidence;
- ownership ambiguity;
- conflicting versions;
- unverified assumptions;
- questions requiring qualified interpretation;
- explicit next owner/action.

### 4. Reviewer-ready closure packet
- evidence population summary;
- findings/signals separated from judgments;
- qualified-owner decisions or unresolved routing;
- closure evidence references;
- versioned packet manifest.

### 5. Portable handoff
Default delivery should remain portable where feasible:
- HTML for human review;
- JSON for machine-readable handoff;
- CSV for tabular evidence queues;
- Markdown/PDF only when the engagement requires them.

No public GitHub delivery of confidential client evidence.

## Decision boundary

ClinicOps may structure evidence, reconcile declared sources, flag gaps and prepare reviewer-ready work queues. Reserved clinical, regulatory, legal, safety, quality and release decisions remain with the appropriately qualified person or organisation.

## Commercial activation

A paid Change Control Pack starts only after:
- written scope;
- evidence/data handling route agreed;
- accountable owner named;
- standard commercial activation completed;
- non-standard terms escalated under the existing activation gate.

Do not commit pricing, delivery dates or outcome guarantees from this specification alone.

## Validation plan

Current lifecycle target: **PUBLIC / AVAILABLE FOR BOUNDED PILOT**, not "validated" or "scalable".

Promote only through `VALIDATION_AND_SCALABILITY_GATES.md`.

Minimum evidence before real-world validated language:
- at least two independent representative cases complete the intended packet workflow without developer rescue;
- accountable workflow owners judge the packet useful for a real operational step;
- observed failure modes are recorded and addressed;
- exact validated domain/use case is stated.

Minimum evidence before scalable language:
- at least three independent completed cases across at least two organisations or genuinely independent workflows;
- common input/output schema holds;
- marginal delivery effort and review capacity are measured;
- portable fallback and privacy boundaries remain workable;
- economics are observed rather than assumed.

## Productization rule

Do not add infrastructure because the concept is attractive. Automate only the repeated stable portions observed in actual delivery. Preserve human judgment and domain-specific authority as explicit review steps.
