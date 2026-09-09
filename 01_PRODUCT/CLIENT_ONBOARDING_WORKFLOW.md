# ClinicOps Client Onboarding Workflow

## Objective

Convert a qualified buyer into a controlled, reproducible ClinicOps engagement without exposing private material in the public repository or presenting automated screening as a compliance determination.

The onboarding model is service-first. A client should receive useful intelligence before ClinicOps asks them to adopt a new software platform.

## 1. Qualification

Confirm five things before requesting portfolio data:

- the buyer owns or influences a real regulatory-operations workflow;
- the portfolio or document-reconciliation problem is material enough to justify review;
- ClinicOps can define a bounded deliverable;
- required evidence can be supplied or lawfully screened;
- the engagement has a named human review owner on both sides.

If these are not true, keep the interaction in discovery rather than creating a pseudo-project.

## 2. Scope the pilot

Record:

- organisation and buyer role;
- portfolio scope;
- target markets in scope;
- supplied evidence types;
- excluded questions;
- expected deliverables;
- target review date;
- acceptance criteria;
- commercial experiment / opportunity ID where applicable.

The scope must say explicitly that public-register screening and operator priority are evidence inputs, not legal or compliance determinations.

## 3. Establish a controlled client workspace

Do not ask clients to place confidential portfolios or documents in the public GitHub repository.

Use an approved access-controlled workspace for:

- source portfolio exports;
- manufacturer-controlled documents;
- correspondence supplied for the engagement;
- interim review files;
- final deliverables.

The public repository contains code, schemas, sanitized fixtures and methodology only.

## 4. Intake

Minimum portable portfolio shape is `examples/portfolio_intake_template.csv`.

Run structural validation before analysis:

```bash
clinicops-portfolio-validate <client-portfolio.csv>
```

Resolve blocking structural errors before creating deliverables. Warnings and information gaps remain visible and are not silently filled with guesses.

## 5. Analysis

Generate the deterministic operator layer:

```bash
clinicops-pilot-bundle <client-portfolio.csv> <engagement-output> YYYY-MM-DD
```

Bundle `1.1` includes:

- `client_report.html` — portable client-readable view;
- `portfolio_report.md` — analyst/handoff view;
- `portfolio_report.json` — machine-readable contract;
- `intake_diagnostics.md` — evidence and structural gaps;
- `manifest.json` — source hash, output hashes, version and interpretation boundary.

Do not run private client data through public GitHub Actions. Actions validate code and sanitized fixtures, not live engagements.

## 6. Human regulatory review

Before client delivery, a ClinicOps reviewer should check at minimum:

- actor-role interpretation;
- registration-path classification;
- certificate timing evidence;
- target-market evidence;
- SS(C)P interpretation boundaries;
- source provenance;
- unsupported inference risk;
- whether any row requires manufacturer, authorised representative or notified-body evidence.

Automated priority is operator triage only.

## 7. Deliver

Primary client-facing artifact: `client_report.html` inside the controlled workspace.

Supporting deliverables:

- Markdown for review/change tracking;
- JSON when the client or partner wants a machine-readable handoff;
- manifest for integrity/reproducibility;
- agreed action register when human review creates client-specific next steps.

Do not host confidential client bundles on public GitHub Pages.

## 8. Review meeting

Use the report to answer:

1. What evidence is strong enough to act on now?
2. What needs verification?
3. Which workstreams are time-sensitive?
4. Who owns each evidence request or action?
5. What should be explicitly excluded from the current conclusion?

Capture client corrections as new evidence rather than overwriting the original source silently.

## 9. Close the learning loop

After delivery, update the appropriate private commercial record and sanitized institutional learning:

- buyer pain confirmed / rejected;
- objections;
- willingness and pricing signal;
- data-shape friction;
- repeated manual work;
- requested portal features;
- reusable product improvement;
- experiment result and decision.

Use `clinicops-experiments` for sanitized experiment state and the Revenue OS for commercial prioritisation.

## 10. Expansion decision

Only propose recurring monitoring, partner integration or a portal feature when the engagement demonstrates a repeated need.

Preferred evolution:

small pilot
-> repeatable portfolio engagement
-> recurring intelligence service
-> partner workflow integration
-> authenticated portal for proven workflows

Do not reverse this order merely to make ClinicOps look more like a software company.

## Acceptance checklist

An engagement is ready for delivery only when:

- structural intake errors are zero;
- human review is complete for client-specific interpretation;
- material evidence gaps are visible;
- source input hash is recorded;
- generated-output hashes are recorded;
- no unsupported compliance allegation is present;
- confidential source material remains in controlled storage;
- the client can distinguish observed evidence, derived screening logic and human judgement.
