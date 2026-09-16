# ClinicOps Product Registry

ClinicOps separates **availability**, **technical verification**, **real-world validation**, **repeatable delivery**, **scalability** and **core-product candidacy**.

- Product-state language follows `VALIDATION_AND_SCALABILITY_GATES.md`.
- Whether repeated work deserves to become a core product follows `04_GROWTH/PRODUCT_EXTRACTION_DOCTRINE_2026-09-16.md`.

A product can be technically sound and commercially useful without being a core-product candidate. Core-product promotion requires repeated paid evidence, independent buyers/workflows, a stable input/output contract, repeat demand, measurable value and a documented competitor gap.

## Free entry products

### Change Surface Mapper
Status: PUBLIC CANDIDATE — TECHNICAL VERIFICATION REQUIRED BEFORE MERGE/DEPLOY.

Purpose: help a user structure one approved/authoritative change across potentially affected systems, records, documents and owners without uploading inputs to ClinicOps.

Target users: regulatory, quality, trial, AI, laboratory, clinic and controlled-content operations owners.

Primary output: browser-local change-surface brief + JSON handoff.

Validation requirement: independent representative external workflow evidence is required before any real-world validated or scalable claim.

Core-product state: not promoted. Treat it as an acquisition/delivery asset unless repeated paid work independently satisfies the product-extraction gate.

### Regulatory Change Integrity Check
Status: PUBLIC.

Purpose: structure one regulatory change event into a portable evidence packet and reviewer queue.

### EUDAMED Identifier Check
Status: PUBLIC.

Purpose: create trust and demonstrate bounded structural regulatory intelligence.

### Transition Readiness Score
Status: PUBLIC.

Purpose: help users identify self-reported transition work-plan gaps and potential customer needs.

### Regulatory Change Review Cost
Status: PUBLIC.

Purpose: let users estimate their own manual workload/economics assumptions without claiming ClinicOps savings.

### Interactive Integrity Specimen / Transition Map sample
Status: PUBLIC SANITIZED EXAMPLES.

Purpose: make the ClinicOps evidence-control method inspectable before a paid engagement.

## Paid products / delivery formats

### Evidence Change Control Pack
Status: AVAILABLE FOR FOCUSED SCOPING.

Input: one declared approved/authoritative change, defined evidence population, available evidence and accountable owner.

Output: source register, change-surface matrix, unresolved queue, reviewer-ready closure packet and portable handoff.

Target customer: medical-device regulatory/quality teams, ARs/consultancies, sponsors/CROs/sites, quality owners, clinical-AI operations, laboratory/clinic operations and controlled medical-content teams.

Evidence required before stronger product claims: independent completed external cases under `VALIDATION_AND_SCALABILITY_GATES.md`.

Core-product state: not promoted. Use real paid delivery to test whether a stable primitive survives across independent cases.

### Transition Intelligence Scan
Input: device portfolio and evidence.
Output: bounded portfolio evidence map, priorities and reviewer questions. Any risk terminology must remain governed and must not imply an automated compliance or enforcement determination.

### Portfolio Intelligence Monitoring
Recurring service for repeated regulatory/evidence signals and controlled change where cadence is demonstrated.

### Regulatory Operations Training
Structured learning products where source validity and learning scope are explicit.

## Product extraction rule

ClinicOps follows:

**Sell the pain. Standardize the repeated work. Automate only what survives reality.**

Do not create a core MVP merely because a problem appears horizontal or large. Prefer a painful niche with clear budget, repeated manual work, observable failure and measurable value. The product may become horizontal after the invariant primitive survives multiple independent real contexts.

A concept may enter `CORE_MVP_CANDIDATE` only when the hard gate in `04_GROWTH/PRODUCT_EXTRACTION_DOCTRINE_2026-09-16.md` is fully evidenced. The machine-readable fixture and CI validator are `examples/product_opportunity_gate.example.json` and `scripts/validate_product_opportunity_gate.py`.

## Product rule

Each product must define:

- target customer / intended user;
- problem solved / intended task;
- evidence required;
- minimum input contract;
- delivery method;
- decision boundary / unsupported uses;
- accountable human owner;
- technical test contract;
- real-world validation state;
- repeatability/scalability state;
- product-extraction / core-candidacy state;
- success metric;
- kill condition;
- next improvement loop.

Do not promote a product state because a page exists, CI is green, traffic exists, or an internal agent judges it useful. Unknown evidence remains unknown.
