# ClinicOps Expert Network Operating System

Status: ACTIVE INTERNAL OPERATING MODEL

## Purpose

The ClinicOps expert network is a **project-specific delivery capability**, not vanity headcount and not a public marketplace.

Its purpose is to let ClinicOps add verified competence exactly where a client workflow requires it while preserving one accountable engagement owner, explicit professional boundaries and a reproducible evidence trail.

The network supports the core ClinicOps model:

```text
buyer problem
→ bounded scope
→ required competence
→ verified specialist
→ assignment gate
→ minimum necessary evidence
→ specialist observation/review
→ ClinicOps integration
→ accountable client decision
→ closure evidence
```

## Network architecture

Use three layers.

### Layer A — core regulatory/data-integrity specialists

Examples:

- MDR / IVDR regulatory affairs;
- EUDAMED / UDI / master-data operations;
- SS(C)P lifecycle and technical documentation;
- PMS / PMCF / clinical-evidence operations;
- IVD;
- SaMD / software regulatory work;
- human factors / usability;
- medical-device cybersecurity where specifically qualified;
- quality/document-control specialists.

### Layer B — local-market and language nodes

Start with Denmark, then add country nodes only when real demand and verified capability exist.

Potential future nodes:

- Sweden;
- Norway;
- Finland;
- Iceland;
- other EU/EEA markets where client demand justifies sourcing.

A language speaker is not automatically a market-regulatory specialist. Track language, professional scope, jurisdiction and permitted work separately.

### Layer C — clinical / PV / specialist reviewers

Examples:

- physicians;
- nurses;
- pharmacists;
- pharmacovigilance / medical-information specialists;
- clinical researchers;
- biostatistics / methodology specialists;
- therapeutic-area SMEs.

Use this layer when a bounded evidence question actually requires that expertise.

## Private status model

- `SOURCED` — potentially relevant; no qualification implied.
- `SCREENING` — qualification in progress.
- `VERIFIED` — credentials/fit checked, but not currently ready for assignment.
- `AVAILABLE` — assignment-ready subject to project-specific checks.
- `LIMITED` — assignable only within stated constraints.
- `PAUSED` — temporarily unavailable.
- `DO_NOT_ASSIGN` — do not use; retain only the minimum private reason necessary to prevent reassignment.

Only `AVAILABLE` and `LIMITED` are assignable.

## Competence model

Do not ask “is this person an expert?” in the abstract.

Ask:

- For which work type?
- For which market/jurisdiction?
- In which language?
- At which evidence/decision role?
- Under which professional/legal scope?
- With what current verification?
- With what conflicts or exclusions?

The same person may be assignable for one task and unsuitable for another.

## Assignment gate

Before activation, the engagement must have:

1. a written scope;
2. a named ClinicOps engagement owner;
3. a named client/accountable owner;
4. a scoped question/work product;
5. expert competence matched to the work type and market;
6. current credential verification;
7. assignment-specific conflict check;
8. confidentiality terms;
9. contract/compensation terms;
10. insurance/not-required determination where relevant;
11. minimum necessary data access;
12. explicit role type: advisory, reviewer or a separately governed reserved decision role.

Use `clinicops-expert-network-validate` as a deterministic preflight. It is a gate, not a substitute for professional judgement.

## Delivery model

The specialist does not receive an unbounded client workspace.

Default packet:

- scoped question;
- relevant evidence only;
- known uncertainty;
- required output format;
- due date;
- prohibited conclusions if applicable;
- disclosure of role boundary.

Default output:

- observation/review;
- rationale;
- evidence relied upon;
- uncertainty;
- additional evidence needed;
- reviewer identity;
- date/version.

ClinicOps then integrates that evidence into the engagement deliverable.

## Public representation

Never imply that every specialist is:

- an employee;
- a standing officer;
- permanently retained;
- available on demand;
- a regulatory authority;
- responsible for client release decisions.

Permitted wording must be verified and consented.

Do not publish a public roster by default.

## System of record

The real roster is private. Do **not** commit names, personal contact details, rates, conflicts, credential documents or contracts to the public repository.

Public GitHub may contain:

- schemas;
- validators;
- synthetic examples;
- governance;
- sanitized aggregate coverage.

The private system of record should hold actual expert/contact data. Prefer HubSpot or another access-controlled business system already in use rather than creating a second CRM.

## Commercial use

The network should increase revenue resilience by enabling:

- country-specific release integrity;
- Nordic/multilingual work without pretending ClinicOps itself employs every language;
- specialist regulatory/clinical review;
- partner/co-delivery;
- overflow capacity;
- continuity when one person is unavailable.

It must not become an excuse to broaden ClinicOps into every life-science service.

## Capacity rule

Do not advertise a market or specialty as covered merely because one candidate exists.

A capability becomes externally marketable only when:

- at least one verified specialist is actually assignable;
- scope is defined;
- commercials/contracting are workable;
- delivery/QA path is documented;
- the claim is approved for public use.

For strategically important recurring markets, target at least two independent qualified options to reduce single-person dependency.

## Review cadence

- assignment-specific conflict check: within 30 days of activation;
- network record review: at least every 180 days for assignable experts;
- credential verification: at least annually unless the credential has a shorter expiry or the task requires fresher verification;
- public-profile wording: re-confirm when role/credentials materially change.

These are ClinicOps operating controls, not representations of statutory validity periods.

## Metrics

Track privately:

- coverage by market;
- coverage by competency;
- number of assignment-ready experts;
- single-point-of-failure markets;
- time to source a specialist;
- assignment acceptance rate;
- delivery timeliness;
- client correction/rework;
- expert-caused quality issues;
- repeat assignments;
- contribution margin;
- network-sourced referrals;
- conflicts/declines.

Do not publish vanity network size.
