# ClinicOps expansion architecture — 2026-09-14

## Thesis

ClinicOps is not a generic compliance consultancy. The brand should mean **evidence-controlled operations for clinical work**.

EU MDR / EUDAMED remains the current commercial beachhead. Expansion is allowed only where the work still plausibly belongs to clinic, clinical-research, medical-product, diagnostic/laboratory, or care-delivery operations and where ClinicOps' existing primitives transfer cleanly:

- evidence provenance;
- controlled-source comparison;
- change propagation;
- role-aware reconciliation;
- explicit uncertainty;
- owner routing;
- human review and decision boundaries;
- reproducible review packets and audit trails.

The operating sequence remains:

`DISCOVER → TEST → SELL MANUALLY → PROVE REPEATABILITY → AUTOMATE`

No adjacent lane earns product investment merely because the regulation is large, the market is fashionable, or a tool can be built quickly.

## Name-fit gate

A proposed ClinicOps lane must answer **yes** to at least one of these questions and **yes** to the evidence-workflow question:

1. Does the workflow happen inside or directly around a clinic, diagnostic/laboratory service, clinical trial, or care-delivery organization?
2. Does it support a medical product's clinical, quality, post-market, study, or provider-facing operations?
3. Does it govern technology or vendors used in a clinical/care workflow?
4. Does the workflow depend on reconciling changing evidence, records, systems, documents, vendors, or accountable human decisions?

If the answer is no, the opportunity should not be built under ClinicOps even if it is commercially attractive.

## Revenue architecture

ClinicOps should deliberately maintain three economic layers.

### 1. Active cashflow

High-touch work that produces buyer evidence and funds learning:

- fixed-scope evidence-integrity reviews;
- change-propagation sprints;
- study/site readiness reviews;
- QMS / quality-record reconciliation;
- AI-system governance inventory and evidence-pack creation;
- vendor evidence remediation;
- white-label delivery for CROs, ARs, quality/regulatory consultancies and clinical-technology partners;
- recurring managed evidence operations where the buyer retains final expert authority.

Active work is the discovery engine. It should expose repeated tasks that can later become controlled low-touch products.

### 2. Recurring / semi-passive income

Lower-touch services that reuse the same control layer:

- monthly or quarterly evidence monitoring;
- change-diff subscriptions;
- controlled register maintenance;
- recurring vendor-document expiry / change review;
- recurring trial/site document completeness checks;
- periodic AI-governance register review;
- partner licenses for ClinicOps packet formats, deterministic checks or branded review workflows;
- maintenance retainers after an initial remediation sprint.

These are preferable to one-off projects because the underlying problem is temporal: sources, versions, systems, vendors and responsible owners change.

### 3. Low-touch / passive acquisition and income

Self-serve assets should be narrow, evidence-first and useful without a sales call:

- browser-local integrity checks;
- paid templates / evidence-pack kits;
- controlled checklists and implementation workbooks;
- small operator courses built around a concrete workflow;
- benchmark / research briefs with transparent methods;
- lightweight subscription tools for change detection or register maintenance;
- partner-ready white-label packs;
- paid downloadable examples only after the free version proves demand.

Avoid generic ebooks, SEO page factories or broad "compliance dashboards". Low-touch assets should either generate a high-quality buyer signal or replace a repeated manual step already proven in delivery.

## Expansion lanes

### Lane A — Clinical trial and site operations

**Name fit:** very high.

Core problem: a protocol amendment, safety update, consent revision, vendor change or site decision propagates across many controlled records and owners. The operational failure mode is not merely a missing document; it is uncertainty about what changed, what is authoritative, what is affected, who reviewed it and what is still unresolved.

Candidate active offers:

- Trial Change Integrity Review;
- protocol-amendment propagation review;
- site activation / essential-document reconciliation;
- sponsor/CRO/site handoff evidence review;
- CTIS-to-operational-record reconciliation;
- trial-data transfer / reconciliation readiness support where qualified domain review is available.

Candidate recurring / low-touch products:

- amendment impact mapper;
- trial/site evidence register;
- essential-document completeness packet;
- training / acknowledgement propagation tracker;
- periodic site or study evidence-health review.

Why now: the EU Clinical Trials Regulation uses CTIS as the single entry point for EU trial submissions, and all EU/EEA trials have been under the CTR/CTIS regime since 31 January 2025. ICH E6(R3) Principles and Annex 1 have been effective in the EU since 23 July 2025 and emphasize fit-for-purpose, risk-proportionate trial conduct and reliable records/data. These changes increase the value of disciplined operational evidence without making ClinicOps the clinical or regulatory decision-maker.

Primary public references:

- European Commission clinical trials overview: https://health.ec.europa.eu/medicinal-products/clinical-trials_en
- EMA ICH E6(R3) overview: https://www.ema.europa.eu/en/ich-e6-good-clinical-practice-scientific-guideline

### Lane B — Medical-device quality and QMS operations

**Name fit:** high and closest to the current beachhead.

Core problem: quality-system changes have to propagate across procedures, records, supplier controls, training, CAPA, design/manufacturing interfaces and inspection evidence.

Candidate active offers:

- QMS Change Integrity Review;
- QMSR transition evidence reconciliation;
- CAPA / procedure / training propagation review;
- supplier-quality evidence pack cleanup;
- inspection-readiness evidence packet preparation, without representing the result as a compliance determination.

Candidate recurring / low-touch products:

- QMS change propagation checker;
- controlled-record evidence packet template;
- recurring SOP/training/version drift review;
- supplier evidence register maintenance;
- partner white-label review packets.

Why now: FDA's Quality Management System Regulation became effective on 2 February 2026 and incorporates ISO 13485:2016 by reference; FDA also changed its medical-device inspection process at that time. This is a direct extension of ClinicOps' change-integrity and evidence-control capabilities.

Primary public reference:

- FDA QMSR: https://www.fda.gov/medical-devices/postmarket-requirements-devices/quality-management-system-regulation-qmsr

### Lane C — Clinical AI governance operations

**Name fit:** high when scoped to AI used in clinical, diagnostic, medical-product or care-delivery workflows.

Core problem: organizations need a durable record of what AI systems are used, intended purpose, owners, vendors, evidence, human-oversight boundaries, changes, incidents and decisions. The operational weakness is often fragmented ownership and undocumented change rather than lack of policy text.

Candidate active offers:

- Clinical AI System Inventory Sprint;
- AI Governance Evidence Pack;
- AI vendor evidence review;
- model / workflow change-control setup;
- human-oversight and decision-boundary mapping.

Candidate recurring / low-touch products:

- AI system register;
- model/vendor change packet;
- periodic governance evidence review;
- decision-log template;
- partner license for a clinical AI evidence-control workflow.

Guardrail: ClinicOps should not market generic AI-law advice. It should manage the evidence and operating controls around AI used in clinical environments, with legal, safety, medical and regulatory interpretations reserved to qualified owners.

Primary public references:

- ISO/IEC 42001:2023 overview: https://www.iso.org/standard/42001
- European Commission high-risk AI guidance / timeline: https://digital-strategy.ec.europa.eu/en/policies/guidelines-ai-high-risk-systems

### Lane D — Diagnostic laboratory and point-of-care quality operations

**Name fit:** very high.

Core problem: laboratories and POCT environments depend on controlled methods, equipment, competencies, reagents, external providers, records and change histories. The same ClinicOps primitives apply to evidence freshness, owner routing and change propagation.

Candidate active offers:

- Lab Change Integrity Review;
- document / method / competency propagation review;
- equipment / service / evidence register cleanup;
- accreditation-readiness evidence structuring with qualified laboratory review retained by the client.

Candidate recurring / low-touch products:

- equipment / certificate evidence register;
- competency and document-change tracker;
- periodic evidence completeness review;
- browser-local lab change packet builder.

Primary public reference:

- ISO 15189:2022 overview: https://www.iso.org/standard/76677.html

### Lane E — Clinic vendor, SOP and operational evidence

**Name fit:** highest in literal brand terms.

Core problem: clinics rely on software, devices, laboratories, service providers, policies, staff training and local procedures. Evidence often becomes fragmented across inboxes, shared drives and vendor portals. ClinicOps can structure the evidence and flag unresolved operational gaps without making clinical decisions.

Candidate active offers:

- Clinic Operations Evidence Review;
- vendor onboarding / renewal evidence cleanup;
- SOP-change propagation review;
- staff acknowledgement / training evidence reconciliation;
- incident-to-action evidence structuring.

Candidate recurring / low-touch products:

- vendor evidence register with expiry/change review;
- SOP propagation checker;
- monthly evidence-health packet;
- clinic audit-pack builder;
- partner delivery through clinic-management or quality consultancies.

This lane should be tested carefully by clinic type and jurisdiction. Do not generalize healthcare-provider legal obligations across countries.

### Lane F — Medical content, localization and controlled-market materials

**Name fit:** medium-high when tied to clinical/medical-product operations.

Core problem: approved medical or regulatory content changes while language versions, patient-facing materials, IFUs, labels, training materials or partner-held copies lag behind.

Candidate active offers:

- controlled-language propagation review;
- source-to-market-language evidence reconciliation;
- partner / distributor change packet;
- white-label evidence layer for specialist language, AR or regulatory firms.

Candidate recurring / low-touch products:

- terminology/version register;
- source-to-language change diff;
- controlled handoff packet;
- periodic multilingual evidence review.

This is commercially adjacent to current ClinicOps relationships and can be partnership-led rather than built as a standalone translation business.

## Priority stack

### Tier 1 — test now with humans, no heavy product build

1. **Clinical trial / site change integrity** — strongest new-market name fit and clear reuse of current evidence primitives.
2. **QMSR / medical-device quality change integrity** — closest adjacency to current credibility and immediately current in 2026.
3. **Clinical AI governance evidence operations** — broad growth lane with strong recurring potential, but must remain evidence/operations rather than legal or clinical judgement.

### Tier 2 — research and partner discovery

4. **Diagnostic laboratory / POCT quality operations**.
5. **Clinic vendor + SOP evidence operations**.
6. **Medical content / localization change operations** through partners.

### Partnership-first / do not internalize yet

- pharmacovigilance case processing or safety judgement;
- clinical coding / billing;
- healthcare cybersecurity operations;
- legal/privacy interpretation;
- clinical decision support;
- statistical trial analysis;
- full quality-system certification consulting.

These can contain attractive revenue, but they introduce specialist delivery obligations beyond ClinicOps' current controlled-evidence role. Enter only with qualified partners and a sharply bounded evidence-operations layer.

## Validation gates for every adjacent lane

Do not call a lane validated until it independently produces:

1. three qualified conversations with people who own or operate the workflow;
2. at least two independent confirmations of repeated reconciliation / evidence-control pain;
3. one E6 commercial signal: priced-scope request, proposed pilot, procurement step or identifiable budget/approval owner.

Do not automate the lane until at least one manual delivery demonstrates repeatable inputs, outputs, review boundaries and measurable buyer value.

A lane should be paused or reframed if ten qualified buyer conversations produce no concrete willingness to sponsor a pilot, no priced-scope request and no repeated evidence of budgeted urgency.

## Fleet execution topology

The temporary fleet that carries each lane through discovery and scoring (defined in `04_GROWTH/EXPANSION_FLEET_EXECUTION_2026-09-14.md`) does not run as one fixed serial queue. Regulatory Evidence Steward's bounded-claims output is a genuine upstream prerequisite for every other function, so it still runs first. Visibility Architect, Customer Discovery Agent and Portfolio Operator do not depend on one another's output and now run as a parallel discovery/scoring group once Evidence Steward's output exists. Opportunity Architect converges that group's outputs into one sellable entry offer, and Release Sentinel remains the final serial release gate over the converged result. See that file's "Execution topology" section and `opportunity_pipeline` in `04_GROWTH/expansion_lanes.json` for the full rationale and the machine-readable form.

## Reusable product spine

Every successful lane should reuse one common ClinicOps product spine rather than spawn a separate platform:

`approved reference → observations → deterministic signals → unresolved questions → accountable owner → human decision → evidence packet → change history`

The nouns differ by lane; the control architecture should not.

A future ClinicOps workspace can therefore support multiple packs:

- Device Change Pack;
- Trial Change Pack;
- QMS Change Pack;
- Clinical AI Governance Pack;
- Lab Change Pack;
- Clinic Vendor / SOP Pack.

This creates resilience: revenue can move between adjacent clinical-operation markets while the underlying software, evidence model and brand remain coherent.

## Commercial portfolio target

The intended long-run mix is deliberately diversified:

- **active**: bounded reviews, remediation and implementation sprints;
- **recurring**: monitoring, maintenance and managed evidence operations;
- **low-touch**: browser tools, controlled templates, operator kits and narrow subscriptions;
- **channel**: white-label / partner delivery where ClinicOps supplies the evidence-control layer and a qualified partner supplies specialist judgement.

The goal is not to maximize the number of offers. It is to create multiple ways to monetize the same evidence-control engine while keeping ClinicOps recognizably about clinical operations.
