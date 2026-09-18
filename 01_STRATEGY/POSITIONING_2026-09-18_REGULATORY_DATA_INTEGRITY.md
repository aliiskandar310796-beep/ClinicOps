# ClinicOps positioning — source of truth (2026-09-18)

Status: ACTIVE. This document supersedes all earlier broad positioning ("clinical operations", multi-lane Ops portfolio) for every public surface. Older strategy files remain as history; where they conflict with this file, this file wins.

## 1. The company

**ClinicOps — EU MedTech Regulatory Data Integrity.**

> Keep EUDAMED, UDI, certificates, SS(C)P and controlled regulatory records aligned when products change.

Operational expression: an approved regulatory or product fact changes in one place. ClinicOps helps determine which downstream regulated records should reflect that change, compares the available evidence deterministically, identifies mismatches or missing evidence, and produces a reviewer-ready closure queue. Machines compare; qualified humans interpret and decide.

The fundamental primitive:

`authoritative source → expected downstream surfaces → observed evidence → deterministic comparison → status (aligned / mismatch signal / missing evidence / conflicting evidence / unresolved / not applicable / requires qualified review) → accountable owner → next action → closure evidence`

## 2. Boundary

ClinicOps IS: a regulatory-data integrity layer between systems; an evidence-reconciliation workflow; a cross-system consistency checker; a structured regulatory-change review; an exception-management and reviewer-support capability; human-reviewed regulatory operations.

ClinicOps IS NOT: an autonomous regulatory decision maker; a notified body or competent authority; a replacement for qualified RA/QA staff, RIM, QMS, PLM or ERP; a technical-documentation system; a broad clinical-operations, AI or laboratory consultancy.

Status vocabulary is bounded: aligned · mismatch signal · missing evidence · conflicting evidence · unresolved · not applicable · requires qualified review. Never: compliant / non-compliant / safe / approved / rejected (unless a qualified human records that determination). No black-box scores.

## 3. Commercial architecture (one flagship MVP, two satellites)

**The main MVP is Product 2, the Regulatory Change Integrity Review.** It is the offer every journey lands on: the Scanner's Single Change mode is its free on-ramp, the Portfolio Integrity Scan is its low-friction entry engagement, and Continuous Monitoring is its recurring extension. Sales, tooling and delivery effort concentrate there.

1. **Portfolio Integrity Scan** — a defined device portfolio / regulatory export in; a bounded evidence-reconciliation view out (evidence map, missing fields, conflicting values, missing evidence, relationships, unresolved queue, owner/action queue, human- and machine-readable report).
2. **Regulatory Change Integrity Review** (flagship; the engagement formerly presented as the Evidence Change Control Pack) — one approved change + a bounded downstream evidence population in; a reviewer-ready closure packet out (source register, change-surface matrix, deterministic comparison, exception queue, owner routing, closure evidence).
3. **Continuous Portfolio Integrity Monitoring** — recurring integrity checks, drift detection, exception queues and closure history. Pilot-stage; built only as far as repeated real use proves valuable.

Public acquisition utility: **Regulatory Integrity Scanner** (browser-local; Single Change mode + Portfolio Scan mode) plus the EUDAMED Identifier Check.

## 4. Use cases, not identities

EUDAMED, UDI, SS(C)P, certificates, Class III/implantable MDR transition, AR portfolios, controlled regulatory documents, and **language-version integrity** are data surfaces and use cases of the one discipline — never separate company identities.

## 5. Deliberate deviations from the 2026-09-18 repositioning directive (evidence-based)

The directive's own validation rule — investment follows real buyer evidence — requires keeping visible the only two lanes with actual revenue or warm-call evidence:

- **Danish pharmacovigilance support** stays a named offer under Denmark Market Access (secondary entry page, not homepage identity). Evidence: an active PV/RA vendor-onboarding conversation (see CRM), Danish-language PV capability is verified and differentiated.
- **Language-version integrity / Danish linguistic validation** stays a public use case. Evidence: the only paid delivery history in the book is medical linguistic work. Reframed truthfully as data integrity across language surfaces (the same approved fact held consistent across IFU/label/SSCP language versions), which is what it operationally is.

Broad clinical-operations lanes (TrialOps, LabOps, Clinic Operations, Clinical AI Ops, broad QualityOps, generic controlled-content operations) are ARCHIVED from public architecture: no homepage or navigation presence, no equal-service framing. Internal methods and intake-form granularity remain.

The **expert network** is an internal delivery mechanism. The customer buys a regulatory-data-integrity outcome, not network access. The page survives for transparency but leaves all primary journeys.

The internal capability frontier (QA/RA Operations Engineering ladder: change control → CAPA/NC → regulatory change impact → technical-file integrity → QA data integrity → PMS → SaMD verification; see 01_STRATEGY/QARA_OPS_ENGINEERING_EXPANSION and the internal schemas) is unchanged and stays internal under the progression rule.

## 6. ICP

Primary: EU-market device manufacturers with tens to low-thousands of device records, MDR transition workload, EUDAMED/UDI obligations, SS(C)P where applicable, small-to-medium RA/QA teams living in spreadsheets/exports/RIM/QMS + manual reconciliation.

Secondary: EU Authorised Representatives and specialist regulatory consultancies managing multiple manufacturer portfolios — ClinicOps as reconciliation infrastructure under their judgement, never replacing the AR.

Large manufacturers are evidence of the problem, not the first ICP.

## 7. Ecosystem position

Consultants sell judgement and execution. RIM/QMS/PLM/ERP store and manage records. Submission providers move data into registries. **ClinicOps reconciles whether regulated facts remain consistent across all of them and turns exceptions into an evidence-backed reviewer queue.** That is the wedge; it does not broaden without real-world evidence.

## 8. Operating rules carried forward

- Lean/DMAIC measures replace asset counts: real external users, paid scopes, completed cases, mismatches found, missing-evidence rate, review effort, closure cycle time, repeat intent, marginal delivery effort.
- Specialization gate for all autonomous work: **does this strengthen EU MedTech Regulatory Data Integrity?** No → don't build by default. Adjacent → backlog. Yes → must serve a validated problem, a core workflow, evidence, sales, delivery or reliability.
- New products require: target user, exact job, pain, current workaround, input, output, buyer, economic signal, validation evidence, smallest test, kill condition. Default answer: extend the core product.
- Validation language per `VALIDATION_AND_SCALABILITY_GATES.md`; browser-local privacy stance; no telemetry; client exports never in the public repo or public CI.
- Customer-facing naming taxonomy: integrity, evidence, reconciliation, portfolio, regulatory, device, change, closure, review, source, record. Internal-only: OS, engine, fleet, swarm, control tower.

## 9. Page disposition (2026-09-18)

| Page | Disposition |
|---|---|
| index.html | REWRITTEN — EU MedTech Regulatory Data Integrity |
| services.html | REWRITTEN — Product page: 3 offers + secondary Denmark/PV + use-case links |
| use-cases.html | NEW — use-case hub (EUDAMED, SSCP, Class III, AR, document control, language versions, Denmark) |
| integrity-scanner.html | NEW — consolidated public tool (Single Change + Portfolio Scan) |
| evidence-change-control-pack.html | REFRAMED as Regulatory Change Integrity Review (URL kept) |
| integrity-check.html, change-surface-mapper.html | KEEP + banner: components of the Scanner |
| regulatory-change-impact.html, technical-file-consistency.html | KEEP — supporting utilities under the same discipline |
| identifier-check.html | KEEP — utility |
| readiness-score.html, integrity-economics.html | DEMOTED — reachable, out of primary navigation/tools grid prominence |
| eu-mdr-regulatory-integrity.html, eudamed-transition.html, sscp-operations.html, class-iii-transition.html, authorised-representative-portfolio-intelligence.html, medical-device-document-control.html, regulatory-intelligence.html | KEEP — use-case landing pages routed to the 3 products |
| denmark-market-access.html | KEEP — secondary entry incl. Danish PV |
| expert-network.html | DEMOTED — internal delivery mechanism; off primary journeys |
| about.html, contact.html, research pages, specimens, privacy | KEEP (nav updated) |
| clinical-operations.html | Legacy stub, out of sitemap (unchanged) |

---

## Appendix A — Master Execution Directive adoption (2026-09-18, second cycle)

The CLINICOPS MASTER EXECUTION DIRECTIVE (2026-09-18) is adopted and supersedes earlier directives where they conflict. Deltas it adds to this file:

**North star restated:** regulated product information, change and evidence integrity. The longer-term internal category is *Regulated Product Information Integrity for Life Sciences* — NOT public until Pharma independently demonstrates repeatable use (≥3 representative Pharma workflows, ≥2 independent organisations, repeated pain, common I/O structure, ≥1 real commercial activation, no rebuild required).

**Domain-pack architecture:** one shared integrity kernel (Source · Object · Observation · Relationship · Change · Evidence · Exception · Owner · Decision · Closure) with attachable domain packs — MedTech Pack (ACTIVE: MDR/IVDR/EUDAMED/UDI/certificates/SS(C)P/labeling/IFU/MDSW), Pharma Information Pack (RESEARCH: SmPC/leaflet/labeling/ePI/IDMP/SPOR/variations), PV Pack (ACTIVE-SECONDARY: literature/language/translation/reviewer routing), Combination Product Pack (RESEARCH ONLY — prefilled syringes, pens, inhalers, drug-device combinations, companion diagnostics; strategic Pharma↔MedTech bridge; no public product before buyer evidence). No separate software product per domain.

**MedTech wedge explicitly includes:** MDSW/SaMD, AI-enabled MDSW, connected devices, implantables/Class III, diagnostics, combination-product device components.

**Segmentation model:** client role × company size × product modality × workflow × therapeutic/medical area × regulatory geography. Mid-market EU manufacturers = strongest initial ICP (RIM/QMS exist but disconnected; portfolios big enough to hurt; no appetite for another enterprise implementation). Enterprise = workflow evidence/partnerships only. Therapeutic area = research/targeting metadata, never a product family and never a claimed specialist expertise. Priority research intersections: oncology/CDx, diabetes (pens/pumps/CGM/apps), cardiology (Class III/implantables), imaging/radiology (SaMD), lab diagnostics/IVD, respiratory (inhalers), rare disease/ATMP, neurology, ophthalmology.

**WIP guardrail (directional):** ~40% product/delivery · 25% demand/buyer evidence · 15% trust/quality · 10% visual/UX · 10% resilience/capability. Live-customer value outranks the ratio.

**Visual communication is a core capability:** design tokens (see `design/DESIGN_TOKENS.md`), diagram-as-code preferred, real product screenshots only (Playwright, sanitized fixtures), evidence figures only from real data with figure governance. No fake dashboards, no generated imagery presented as evidence.

**Capability registry:** `03_OPERATIONS/CAPABILITY_REGISTRY.md` tracks major capabilities (PROPOSED/PILOT/ACTIVE/DEGRADED/DISABLED/RETIRED). Experimental infrastructure (semantic memory, Headroom, OmniRoute, deck.gl, Storybook, backend) stays PROPOSED until evidence.

**Final rule (verbatim):** flagship workflow over another idea; test the primitive over a new market; less user friction over more technology; external evidence over internal confidence.
