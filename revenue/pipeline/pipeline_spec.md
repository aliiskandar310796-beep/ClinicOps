# ClinicOps commercial pipeline spec

Status: DRAFT operating design. Files first; HubSpot mirror later.
Source of truth for ladder definitions: `00_STATE/ACTIVE_FLEETS.md` / `06_AGENTS/AI_COMPANY_OS.md`.

## Rules

1. **Currency is EUR.** `amount_eur` only; no USD fields. Blank = unknown, never 0.
2. **Ladder before stage.** A deal's stage is derived from the highest *evidenced* E-level. Never promote on hope.
3. **E4+ requires genuine human buyer interaction.** A real person at the buyer/partner replied, spoke, or acted. Auto-replies, bounces, opens, clicks, page views, form-bot submissions, internal tests and simulated/fictional rows never count. E4+ needs a private `evidence_ref` (a pointer, e.g. private CRM note id or mailbox thread reference, not contents).
4. **Public repo hygiene.** `pipeline.csv` in the public repo holds only sanitized or fictional-labelled rows (`company_ref`/`contact_ref` are pseudonymous IDs like `ACC-014`, `CON-031`). Real names, emails and findings live in the private system (HubSpot). See `revenue/README.md`.
5. **Simulated rows** must set `simulated=true` and are refused by reporting (`scripts/pipeline_report.py`).
6. **Cold email:** ceiling 15/day company-wide; Denmark-domiciled organisations excluded from cold email (`cold_email_eligible=false`); fail closed if capacity is unknown.
7. E3 is execution evidence only; do not report it as buyer evidence.

## Stages

| Stage | Ladder | Entry criteria | Exit criteria (to next) |
|---|---|---|---|
| S0 Hypothesis | E0 | Written hypothesis + `hypothesis_id`; no external fact | Observed external signal with source URL |
| S1 Signal | E1 | Public regulatory/market signal cited | Named reachable account and segment |
| S2 Qualified account | E2 | Account fits segment + offer; reachable channel identified; `cold_email_eligible` set | Outreach or demand test actually delivered (logged) |
| S3 Test delivered | E3 | Outreach/demand test sent or offered; logged, counted against ceiling | A human replies or a call occurs |
| S4 Conversation | E4 | Human buyer response or qualified conversation; `human_interaction=true`; private `evidence_ref` | Same pain/workflow/consequence confirmed in more than one instance or by a second stakeholder |
| S5 Pain confirmed | E5 | Repeated pain/consequence/workflow confirmed; evidence_ref updated | Priced-scope request, proposed pilot, procurement step or named budget/approval owner |
| S6 Commitment | E6 | Concrete commitment signal; `amount_eur` (with `amount_basis`) if a price exists | Accepted PO or equivalent activation path |
| S7 Activated | E7 | Paid work activated (PO/signed order or equivalent) | Delivery accepted and/or payment received |
| S8 Delivered/Paid | E8 | Accepted delivery and/or payment evidence | Repeat, expansion, renewal or qualified referral caused by delivered value |
| S9 Expansion | E9 | Repeat/expansion/renewal/referral evidenced | Terminal (or new deal) |
| CLOSED-LOST | keep last E-level | Explicit no, or 60 days no response after last human contact; `closed_reason` set | Reopen creates a new deal or reverts stage with evidence |

Stage moves down only via CLOSED-LOST or a documented evidence correction (note it in `notes`). Level counts reflect the highest evidenced level, so a lost E5 deal still counts as E5 learning.

## pipeline.csv columns

`deal_id` (DEAL-nnn), `company_ref`, `contact_ref` (pseudonymous), `segment` (manufacturer / authorised_representative / consultancy / distributor / other), `geography`, `offer`, `stage` (S0..S9, CLOSED-LOST), `evidence_level` (E0..E9), `evidence_ref` (private pointer; mandatory E4+), `human_interaction` (true/false; must be true for E4+), `simulated` (true/false), `amount_eur` (number, blank if unknown), `amount_basis` (quoted / estimated / PO), `expected_close_date`, `next_action`, `next_action_date`, `owner`, `hypothesis_id`, `experiment_id` (see `experiments/EXPERIMENT_LEDGER.md`), `source_channel`, `cold_email_eligible`, `created_date`, `last_updated`, `closed_reason`, `notes`.

Amounts: only count `amount_eur` in pipeline value at E6+; below that report as "unpriced". No probability-weighted forecasting until at least three E6+ deals exist.

## Discovery ledger relation

`sales/discovery/discovery_ledger.csv` (one row per outreach touch / conversation; not yet created) is the activity log; `pipeline.csv` is the per-deal state. Expected ledger columns read by the report: `evidence_level` (or `level`), `simulated`, optional `human_interaction`. A ledger row supports pipeline evidence but does not replace it.

## HubSpot mapping (mirror later; HubSpot currently read-only, write needs founder reauthorization)

| File concept | HubSpot object | Notes |
|---|---|---|
| Deal row | Deal | Pipeline "ClinicOps Evidence Ladder"; stages S0-S9 + Closed lost. `dealname`=deal_id; `amount` in deal currency EUR (set company currency = EUR); `closedate`=expected_close_date; `dealstage`=stage |
| Account | Company | `name`, `country`, `industry`; custom `segment` |
| Person | Contact | Associated to company and deal; keep personal data only here, never in the repo |
| Touch/call | Engagement (email/call/note/meeting) | Replaces ledger rows; log human replies as engagements |

Custom properties to create (deal unless noted):

| Property (internal name) | Type | Object |
|---|---|---|
| `evidence_level` | Dropdown E0..E9 | Deal |
| `evidence_ref` | Single-line text (private pointer) | Deal |
| `human_interaction_confirmed` | Checkbox | Deal |
| `simulated` | Checkbox (default false; excluded from all reports) | Deal, Company, Contact |
| `amount_basis` | Dropdown quoted/estimated/PO | Deal |
| `hypothesis_id` | Single-line text | Deal |
| `experiment_id` | Single-line text | Deal |
| `source_channel` | Dropdown | Deal |
| `cold_email_eligible` | Checkbox | Company |
| `clinicops_segment` | Dropdown | Company |
| `next_action`, `next_action_date` | Text, Date | Deal |
| `closed_reason` | Dropdown/text | Deal |
| `pseudonymous_ref` | Text (ACC-/CON- id used in files) | Company, Contact |

Mirror procedure: (1) founder reauthorizes write; (2) create properties and pipeline; (3) import pipeline.csv rows by `deal_id`; (4) HubSpot becomes system of record for private fields, file keeps the sanitized row; (5) validate counts by level match `pipeline_report.py` output. Until then: read-only queries may be used to check for existing records to avoid duplicates; do not write.

## Reporting honesty

`python scripts/pipeline_report.py` prints counts by level; prints `NO EVIDENCE YET` when there are no valid rows; refuses simulated rows and rows claiming E4+ without `human_interaction=true` or an `evidence_ref`.
