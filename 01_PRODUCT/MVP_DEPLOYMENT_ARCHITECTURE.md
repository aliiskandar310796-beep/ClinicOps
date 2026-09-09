# ClinicOps MVP Deployment Architecture

## Goal

Give paying clients secure access to useful ClinicOps intelligence now, without forcing a premature SaaS build or moving confidential client data into the public repository.

This architecture deliberately separates public authority, private engagement data and reusable analysis code.

## Recommended deployment model

### Layer 1 — Public acquisition

Primary domain: `clinicops.dk`.

Role:
- explain the offer;
- establish EU-wide regulatory-operations positioning;
- expose approved research and the free Identifier Check;
- convert qualified visitors into assessment requests.

Keep the existing GoDaddy site as the marketing surface until evidence justifies a migration. Do not introduce a second public hosting stack solely because another tool is technically convenient.

### Layer 2 — Controlled intake

The public website should collect only low-sensitivity qualification metadata.

For portfolio exports or confidential documents, send the client to an access-controlled workspace approved for the engagement.

Do not accept sensitive client evidence into:
- public GitHub issues;
- public pull requests;
- public GitHub Pages;
- public website forms without an approved secure-storage path.

### Layer 3 — ClinicOps analysis engine

Canonical reusable code remains in GitHub.

For a live engagement:

1. copy the client export into an analyst-controlled environment;
2. run `clinicops-portfolio-validate`;
3. correct structural intake problems with the client where needed;
4. run `clinicops-pilot-bundle`;
5. perform human regulatory review;
6. move the reviewed deliverables into the controlled client workspace.

Public GitHub Actions may test code and sanitized examples. They should not process private client portfolios by default.

### Layer 4 — Client delivery

Bundle schema `1.1` is the immediate client-access layer.

Primary artifact:
- `client_report.html` — self-contained, print-friendly, client-readable report.

Supporting artifacts:
- `portfolio_report.md` — review/handoff format;
- `portfolio_report.json` — stable machine-readable projection;
- `intake_diagnostics.md` — evidence gaps;
- `manifest.json` — source and generated-output SHA-256 hashes plus contract version.

Delivery should occur through an authenticated client workspace or equivalent controlled share, not through a public URL.

This means ClinicOps can sell and deliver today without waiting for a portal application.

## Why this is the most feasible strategy

It optimizes for the real bottlenecks:

- buyer trust;
- evidence quality;
- repeatable delivery;
- data security;
- learning from actual client workflows.

A custom portal before those workflows repeat would add authentication, hosting, database, security and maintenance burden without proving that clients need them.

## Portal trigger criteria

Build an authenticated portal only when at least one of these patterns repeats across engagements:

- clients repeatedly upload updated versions of the same portfolio;
- multiple users at one client need separate access;
- clients repeatedly need action-status tracking;
- machine-to-machine JSON handoff becomes common;
- recurring monitoring becomes paid and operationally material;
- secure document exchange is becoming the dominant manual cost.

A portal should remove observed friction, not invent workflow.

## Phase 2 portal architecture

When triggered, build the thinnest possible authenticated layer around existing contracts.

### Frontend

Responsibilities:
- authentication;
- organisation-scoped portfolio list;
- report view;
- evidence-gap view;
- action queue;
- secure upload/download links.

### Application API

Responsibilities:
- map authenticated organisations to engagement records;
- invoke or consume the existing ClinicOps analysis contracts;
- expose versioned JSON payloads;
- enforce human-review status before a client sees interpreted findings.

### Database

Use a relational store only when persistent multi-client workflow requires it.

Minimum entities should follow `01_PRODUCT/KNOWLEDGE_GRAPH_SPEC.md` rather than inventing an unrelated application schema.

### Object/document storage

Store client documents separately from the public repository with:
- organisation isolation;
- access control;
- auditability;
- retention/deletion policy;
- encryption provided by the selected platform.

### Authentication

Choose managed authentication rather than building credentials in-house.

Requirements before vendor selection:
- EU/EEA data-residency needs assessed;
- role-based access requirements known;
- client SSO demand known;
- contractual/security expectations known.

Do not lock the product to a vendor before those requirements are observed.

## Deployment boundaries

### Public GitHub

Use for:
- source code;
- claim registry;
- regulatory methods;
- sanitized fixtures;
- agent instructions;
- CI/CD;
- issue templates;
- public research suitable for disclosure.

### GitHub Actions

Use for:
- tests;
- Ruff;
- claim and content gates;
- sanitized client-bundle smoke tests;
- experiment-contract validation;
- bounded public-source canaries;
- deployment of public tools.

Do not use public-repo Actions as a default processor for confidential client exports.

### GitHub Issues

Use selectively for:
- validated commercial experiments;
- reproducible software defects;
- true deployment blockers.

Do not turn every conversation or prospect into an issue.

### Controlled client workspace

Use for:
- client data;
- reviewed client deliverables;
- confidential evidence;
- private engagement notes where appropriate.

## Release discipline

For client-facing bundle contracts:

1. version schema changes explicitly;
2. preserve backwards clarity;
3. add tests before changing semantics;
4. run full CI;
5. use deterministic sanitized fixtures;
6. record source/output hashes;
7. keep rollback to the previous contract straightforward.

## Near-term client experience

A client should experience ClinicOps as:

Request assessment
-> receive secure intake instructions
-> provide portfolio/evidence
-> receive evidence-gap feedback if intake is incomplete
-> receive reviewed `client_report.html`
-> review priority workstreams with ClinicOps
-> receive machine-readable JSON when useful
-> agree next actions or recurring service

The internal complexity stays invisible. Clients buy a defensible work plan, not access to an agent swarm.

## Evolution path

### Now

Marketing site + controlled workspace + bundle `1.1` + human review.

### After repeated paid usage

Authenticated read-only portal around the same bundle/JSON contract.

### After recurring operational demand

Collaborative action tracking, portfolio refreshes, partner integrations and recurring intelligence.

### Only after strong demand

Broader platform capabilities.

This preserves speed, security, reversibility and capital efficiency while keeping a clean path to a scalable product.
