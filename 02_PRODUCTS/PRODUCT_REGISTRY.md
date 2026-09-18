# ClinicOps Product Registry

This file is the source of truth for what ClinicOps actually sells. Positioning source of truth: `01_STRATEGY/POSITIONING_2026-09-18_REGULATORY_DATA_INTEGRITY.md`.

ClinicOps separates **availability**, **technical verification**, **real-world validation**, **repeatable delivery**, **scalability** and **core-product candidacy**.

- Product-state language follows `VALIDATION_AND_SCALABILITY_GATES.md`.
- Whether repeated work deserves to become a core product follows `04_GROWTH/PRODUCT_EXTRACTION_DOCTRINE_2026-09-16.md`.

A product can be technically sound and commercially useful without being a core-product candidate. Core-product promotion requires repeated paid evidence, independent buyers/workflows, a stable input/output contract, repeat demand, measurable value and a documented competitor gap.

## Core commercial architecture

**One flagship MVP, two satellites. Every public journey routes here.**

### 1. Regulatory Change Integrity Review — FLAGSHIP MVP
Status: AVAILABLE FOR FOCUSED SCOPING (formerly presented as the "Evidence Change Control Pack"; specification in `01_PRODUCT/EVIDENCE_CHANGE_CONTROL_PACK.md`).

Input: one declared approved/authoritative regulatory or product change, a bounded downstream evidence population, available evidence and an accountable owner.

Workflow: establish authoritative source → identify declared downstream surfaces → normalize identifiers/versions → collect evidence → compare deterministically → identify mismatches, missing evidence and ownership ambiguity → route unresolved interpretation to qualified humans → produce closure queue → capture closure evidence.

Output: reviewer-ready regulatory change closure packet (source register, change-surface matrix, exception queue, owner routing, closure evidence, portable handoff). Core schema: Source · Expected · Observed · Status · Evidence · Owner · Next Action · Closure.

Target customer: EU-market medical-device RA/QA teams (primary); ARs and specialist regulatory consultancies managing manufacturer portfolios (secondary/partner channel).

Evidence required before stronger claims: independent completed external cases under the gates file.

### 2. Portfolio Integrity Scan — ENTRY PRODUCT
Status: AVAILABLE FOR BOUNDED SCOPING (pilot format; machinery exists in `src/clinicops_os` portfolio/transition/intake tooling and the client bundle generator).

Input: a defined device portfolio or regulatory export (CSV/XLSX/JSON, RIM/UDI/product-master exports, declared document registers, public EUDAMED evidence where available).

Output: portfolio evidence map, missing fields, conflicting values, missing evidence, certificate/device and AR/manufacturer relationships, SS(C)P relationships where relevant, source provenance, unresolved queue, owner/action queue, human-readable report and machine-readable export. No automated regulatory conclusions.

### 3. Continuous Portfolio Integrity Monitoring — RECURRING LAYER
Status: PILOT-STAGE / BUILD-ON-DEMAND. Scheduled evidence checks, public-record change detection, record-drift comparison, exception queues, closure history, recurring reporting. Built only as far as repeated real use proves valuable.

## Public acquisition utilities

### Regulatory Integrity Scanner (`docs/integrity-scanner.html`)
Status: PUBLIC — TECHNICALLY VERIFIED FOR DEFINED CASES. Browser-local. Two modes: **Single Change** (approved source → downstream observations → deterministic comparison → owner/queue export) and **Portfolio Scan** (CSV/XLSX/JSON import with saveable mapping profiles, normalization, missing/duplicate/conflict detection, and a filterable exception workbench with bulk owner assignment, review states and exports). The free on-ramp to the flagship.

Component/supporting pages kept for URL continuity and focused jobs: Regulatory Change Integrity Check (`integrity-check.html`), Change Surface Mapper (`change-surface-mapper.html`), Regulatory Change Impact Mapper (`regulatory-change-impact.html`), Technical File Consistency Check (`technical-file-consistency.html`).

### EUDAMED Identifier Check (`identifier-check.html`)
Status: PUBLIC utility. Structural screening only.

### Sanitized examples
Interactive Integrity Specimen, Transition Map sample. Purpose: make the method inspectable before an engagement.

### Demoted utilities
Transition Readiness Score and Regulatory Change Review Cost calculator remain reachable as sales support but are out of primary navigation prominence. No black-box score becomes a core product.

## Domain packs (one shared integrity kernel, attachable packs — never separate software products)

- **MedTech Pack — ACTIVE.** MDR / IVDR / EUDAMED / UDI / certificates / SS(C)P / SSP / labeling / IFU / MDSW-SaMD (incl. AI-enabled MDSW, connected devices, implantables, combination-product device components).
- **Pharma Information Pack — RESEARCH.** SmPC / package leaflet / labeling / ePI / IDMP / SPOR / Art. 57 where relevant / variations and post-authorisation change propagation. Built as a domain pack only; no public Pharma consultancy positioning until the reassessment evidence in the positioning file §Appendix A exists.
- **PV Pack — ACTIVE (secondary lane).** Danish literature monitoring support, medically informed Danish/English translation, DHPC language workflows, terminology/version control, reviewer evidence. Deterministic software never performs causality/medical assessment or QPPV decisions.
- **Combination Product Pack — RESEARCH ONLY.** Prefilled syringes, pens, inhalers, drug-device combinations, companion diagnostics. Strategic Pharma↔MedTech bridge; research before any public product.

Kernel entities: Source · Object · Observation · Relationship · Change · Evidence · Exception · Owner · Decision · Closure.

## Specialized use cases (landing routes, not identities)

Class III / implantable MDR transition · EUDAMED transition · SS(C)P operations · AR portfolio intelligence · medical-device document control · MDSW/SaMD version-and-verification records · language-version integrity / Danish linguistic validation · Denmark market access incl. Danish pharmacovigilance support (retained on real buyer evidence; see positioning §5). Each routes to the three products above.

## Archived / experimental (no public product status)

TrialOps, broad QualityOps, Clinical AI Ops, LabOps, Clinic Operations and generic controlled-content operations as *service categories*: archived from public architecture 2026-09-18. Internal methods and intake-form granularity remain. Regulatory Operations Training: experimental, unbuilt. The QA/RA Operations Engineering capability ladder (CAPA/NC evidence, QA data dashboards, SaMD verification) is INTERNAL-ONLY under the progression rule — specs live in the business project, not here.

## Product extraction rule

**Sell the pain. Standardize the repeated work. Automate only what survives reality.**

Do not create a core MVP merely because a problem appears horizontal or large. A concept may enter `CORE_MVP_CANDIDATE` only when the hard gate in `04_GROWTH/PRODUCT_EXTRACTION_DOCTRINE_2026-09-16.md` is fully evidenced (fixture: `examples/product_opportunity_gate.example.json`; validator: `scripts/validate_product_opportunity_gate.py`).

New-product rule: any new concept must state target user, exact job, pain, current workaround, input, output, buyer, economic signal, validation evidence, smallest test and kill condition — and the default answer is "extend the core product", not "create another product".

## Product rule

Each product must define: target customer; problem/task; evidence required; minimum input contract; delivery method; decision boundary / unsupported uses; accountable human owner; technical test contract; real-world validation state; repeatability/scalability state; extraction/core-candidacy state; success metric; kill condition; next improvement loop.

Do not promote a product state because a page exists, CI is green, traffic exists, or an internal agent judges it useful. Unknown evidence remains unknown.
