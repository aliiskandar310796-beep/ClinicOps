# Business Thesis

> Migrated verbatim from the pre-2026-09-23 `AGENT_STATE.md` monolith as part of the connectome-lens shard proposal (draft, not yet reconciled against live `main`). Content below this line is unedited from the original section.

## Canonical truth

GitHub `main` is the shared source of truth. Fetch current `main`, open PRs/branches and current Actions before substantive work. Preserve concurrent Claude/ChatGPT work and never force-overwrite a newer change. Chat transcripts, local copies and project-side control files are secondary until their changes land here.

Do **not** hard-code a self-referential “current main SHA” as permanent truth in this file because its own merge changes `main`. Historical anchor only: PR #48 merged as `eeee68d8…` with exact-main CI run #512 green (2026-09-13); many merges have landed since — always fetch live state again before acting. PR #54 was closed 2026-09-17 as superseded: its outcome/risk/economic controls were selectively ported onto current main (with a fail-closed fix to the economic evaluator) and its stale shared-state changes dropped.

## Current business thesis

**Public identity (2026-09-18, supersedes the multi-lane portfolio): ClinicOps — EU MedTech Regulatory Data Integrity.** One flagship MVP — the **Regulatory Change Integrity Review** — entered via the free Regulatory Integrity Scanner and the Portfolio Integrity Scan, extended by Continuous Portfolio Integrity Monitoring. EUDAMED, UDI, SS(C)P, certificates, Class III transition, AR portfolios, document control and language-version integrity are use cases/surfaces, not identities. Danish PV and Danish linguistic validation stay visible as secondary demand-evidenced entries (positioning §5). Broad Ops lanes (TrialOps, LabOps, Clinic Ops, Clinical AI, broad QualityOps, generic controlled content) are archived from public architecture; internal methods remain. Source of truth: `01_STRATEGY/POSITIONING_2026-09-18_REGULATORY_DATA_INTEGRITY.md` — where the lane text below conflicts with it, the positioning file wins. The MASTER EXECUTION DIRECTIVE (2026-09-18) is adopted — see the positioning file's Appendix A for the domain-pack architecture (MedTech ACTIVE, Pharma Information RESEARCH, PV secondary, Combination RESEARCH), segmentation model, WIP guardrails, visual-communication mandate and `03_OPERATIONS/CAPABILITY_REGISTRY.md`.

ClinicOps is an evidence-controlled, human-reviewed operating layer for high-value expert work: it controls how regulated evidence moves across documents, systems, markets and accountable human owners.

**Long-term category (2026-09-17): QA/RA Operations Engineering for regulated healthcare/MedTech**, with Regulatory Information Integrity as the proven first wedge. Quality Operations (change control → CAPA/NC evidence integrity → regulatory change impact → technical-file integrity → QA data integrity → PMS/complaints → SaMD verification operations) is the internal capability frontier — developed in that adjacency order, internal-only until each capability earns a public offer via the progression rule: learn → primary-source model → internal schema → sanitized prototype → design partner → controlled delivery → delivery evidence → repeat demand → public offer.

**Portfolio history (2026-09-17, SUPERSEDED 2026-09-18 by the deliberate narrowing above):** the site briefly presented multiple equal service lanes. That breadth was reversed by the repositioning directive; do not restore it. The lane list below is kept as history and as the internal capability map:

- **Default cross-domain commercial entry:** Regulatory Integrity Review / Evidence Change Control Pack around one bounded real workflow. Every lane funnels into this one paid entry.
- **Strongest existing wedges (most buyer evidence so far):** MedTech / EUDAMED / Class III transition; Denmark market access / Danish PV / localisation.
- **Adjacent service lanes (live, less validated):** TrialOps, QualityOps, Clinical AI evidence review, LabOps, Clinic Operations, controlled medical content.
- **QA/RA capability-ladder prototypes (2026-09-17, sanitized-prototype stage):** Regulatory Change Impact Mapper (`regulatory-change-impact.html`) and Technical File Consistency Check (`technical-file-consistency.html`), with intake presets `regulatory-change-impact` and `technical-file-consistency`. These are public *method demonstrations* under the progression rule — never present them as delivered services or claim CAPA/audit/62304 breadth from them. CAPA/NC evidence integrity, QA data dashboards and SaMD verification automation remain LEARNING-STAGE and internal-only (specs live in the business project, not this repo).

**Validation rule: availability ≠ proven demand.** Each lane earns stronger investment only through real buyer evidence (the EXP-001 ladder below applies per lane). Do not claim all lanes are equally validated, and do not let breadth become confusion: one umbrella operating model, one obvious default paid entry.

Commercial validation outranks speculative product development.


## Growth / AI-gateway doctrine

Use this sequence for new opportunities:

`DISCOVER → TEST → SELL MANUALLY → PROVE REPEATABILITY → AUTOMATE`

Explore broadly across regulatory and other expert-service markets where the same primitives apply: messy evidence, expensive expert review, repeated reconciliation, version/change control, auditability, human approval and measurable business outcomes.

Target reusable AI primitives rather than one-off features:

- evidence ingestion and provenance;
- entity resolution;
- claim/evidence graphs;
- contradiction and change detection;
- temporal / role-aware reasoning;
- explicit uncertainty;
- deterministic reconciliation;
- controlled generation;
- fail-closed human escalation and review;
- reproducible audit trails.

Prefer service gateways before software gateways. Investigate adjacent revenue aggressively, but do not publish, send, price, create third-party accounts, add tracking, or make buyer commitments across existing approval boundaries.

The long-term direction is an **evidence-controlled AI operating layer for valuable expert work**, proven first where ClinicOps has credibility and expanded only where market evidence earns the right to expand.

## Budget / resilience doctrine

ClinicOps is bootstrapped. Default to:

- low fixed cost;
- GitHub + Pages + existing domain/mail + AI leverage;
- service revenue before expensive SaaS infrastructure;
- automate repeated paid-work friction only;
- reinvest validated revenue into infrastructure.

