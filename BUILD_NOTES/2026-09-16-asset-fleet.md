# ClinicOps asset fleet build — 2026-09-16

Status: branch implementation prepared for PR/CI. Public deployment is not claimed until merged and Pages deployment is verified. Real-world validation/scalability are explicitly not claimed.

## Why this build exists

The active ClinicOps portfolio has a reusable operational primitive across multiple segments:

`approved / authoritative change -> affected surfaces -> observed evidence -> accountable owner -> unresolved queue -> closure evidence`

Current official external context continues to make change propagation operationally relevant:

- European Commission EUDAMED overview / UDI pages state that the first four EUDAMED modules, including UDI/Devices, became mandatory from 28 May 2026.
- EMA's CTIS sponsor training/support page lists the sponsor handbook as the reference document for CTIS sponsor use and shows a 17 July 2026 update.

These are market/context signals only. They do not prove ClinicOps demand or validate the assets.

## Built

### Free asset
`docs/change-surface-mapper.html`

Browser-local Change Surface Mapper with seven workstream presets:
- medical-device regulatory integrity;
- TrialOps;
- QualityOps;
- Clinical AI Ops;
- LabOps;
- Clinic Operations;
- Controlled Medical Content.

It captures one change, source reference, surface status, owner and expected closure evidence, then produces a local summary and JSON export. It has no form action, analytics or network API call by design.

### Paid delivery asset
`01_PRODUCT/EVIDENCE_CHANGE_CONTROL_PACK.md`
`docs/evidence-change-control-pack.html`

Defines a bounded paid delivery format:
- source register;
- change-surface matrix;
- unresolved queue;
- reviewer-ready closure packet;
- portable handoff.

The paid pack is available for bounded scoping but is not described as real-world validated or scalable.

### Machine-readable contract
`examples/change_control_packet.example.json`
`scripts/validate_change_control_packet.py`

Sanitized fixture and validator enforce a common packet shape and require unresolved/mismatch/missing-evidence rows to appear in the unresolved queue. Synthetic fixtures are forbidden from claiming real-world validation or scalability.

### Technical public-tool contract
`scripts/validate_change_surface_mapper.py`

Checks required tool fields/workstreams, decision-boundary language, conversion links, no form action, and rejects common network/telemetry markers.

### Validation/scalability governance
`VALIDATION_AND_SCALABILITY_GATES.md`
`04_GROWTH/ASSET_VALIDATION_LEDGER_2026-09-16.md`

Separates:
- source validity;
- technical correctness;
- usability;
- workflow fit;
- external user/buyer value;
- repeatability;
- scalability.

CI green or public launch cannot promote an asset to real-world validated/scalable.

### Agent fleet
Added two non-overlapping specialist agents:
- Asset Fleet Builder;
- Validation & Scalability Sentinel.

Two initially drafted overlapping roles were deliberately removed before PR because existing Opportunity Architect / Customer Discovery / Visibility agents already own those loops. This keeps coordination cost bounded.

## Site integration

Updated:
- Tools page;
- Services page;
- scope-intake local handoff;
- sitemap;
- product registry;
- Copilot routing instructions;
- CI workflow.

The Change Surface Mapper can place a bounded summary into `sessionStorage` and pass it to the existing browser-local scope brief. Nothing is transmitted until the user explicitly opens/sends an email draft.

## Validation state at branch completion

Technical validation: pending PR CI plus manual post-deploy browser checks.

Real-world workflow validation: not established.

Commercial validation: not established.

Scalability: not established.

The validation ledger defines the exact evidence needed to promote each state. Unknown remains unknown.

## Next external validation test

For the free mapper:
1. representative intended user maps one real non-sensitive change;
2. complete without developer rescue;
3. capture friction/missing fields;
4. confirm whether output supports the next real operational handoff.

For the paid pack:
1. activate one bounded real case under normal commercial/data controls;
2. measure preparation, reconciliation, reviewer and rework minutes;
3. capture exception types and whether the common packet shape holds;
4. obtain accountable-owner usefulness evidence;
5. repeat independently before any validated/scalable claim.

## Merge rule

Do not weaken CI to land this branch. Re-fetch `main` before merge because concurrent agents may move the production baseline.
