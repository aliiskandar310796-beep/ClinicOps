# ClinicOps agent fleet — human in the loop

Status: **OPERATING DESIGN, not proof that unattended agents are live** · 2026-10-27

## Operating objective

ClinicOps is operated by a Spanish-registered individual AR and provides an adjacent, distinct regulatory data-integrity service. Build reliable evidence-handling capacity, not fake agent headcount or unsupervised regulatory delegation. Existing Tier-0 jobs and GitHub Copilot agent profiles are the starting point; see `autonomy/README.md`. Their existence in GitHub **does not confirm a scheduler is active**.

## Seven accountable cells (multiple bounded subagents per cell, as needed)

| Cell | Work permitted without case approval | Human gate |
| --- | --- | --- |
| 1. Regulatory evidence | MDR/IVDR, EUDAMED, MDCG and national primary-source monitoring; source+date+limitation registry | Ali/qualified RA signs off interpretations and published claims |
| 2. AR mandate operations | Prepare manufacturer intake checklist, document index, review queues, EUDAMED public-data comparisons | Ali accepts/rejects mandate; approves EUDAMED actor/mandate actions, incident reports and authority interactions |
| 3. Product and engineering | Test scanner, open branches and PRs, bounded CI, accessibility/security checks | Ali reviews/merges/deploys; no secrets or production credentials |
| 4. QA/clinical and language | Controlled EN↔DA terminology checking, SS(C)P/IFU version comparisons, review-ready evidence | Qualified reviewer approves conclusions and regulated documents |
| 5. Intelligence and 33-cell sales | Research high-signal prospects, classify buyer role, verify public event, maintain suppression-required state | Private outreach master + Gmail & Outlook Sent checks, legal/jurisdiction review and Ali approval before any contact |
| 6. Partnerships / growth | Build non-spam, source-backed landing-page drafts, SEO and content/test proposals | Ali approves claims, campaigns and publication |
| 7. Finance / executive control | Prepare pipeline summaries, anonymised KPI evidence, invoices as drafts, capacity alerts and costs | Ali authorises spending, invoices, contracts and pricing |

## Scheduler and status contract

Every actual job must have:
`job_id, owner_cell, schedule_source, last_started_utc, last_completed_utc, output_uri, execution_status, validation_status, next_action, requires_ali, halt_state`.

Unknown scheduler/last run = `NOT_VERIFIED`, never `ACTIVE`. Only count agents with real scheduler evidence and completed run logs. Reuse the eleven existing Tier-0 jobs, but treat **scheduled-on-Claude claims as unverified until their trigger state and latest dated logs are inspected**.

No autonomous direct messages, cold email, calendar invites to others, contract signature, external publication, money movement, regulatory filing or compliance conclusion. Write proposed drafts and PRs, and park them for Ali. New work is read-only/draft-only by default.

## AR-specific handoff

`prospect_signal → company/domain suppression → manufacturer intake (private) → authorised business/legal screen → document sufficiency queue → qualified reviewer → Ali's mandate decision → contract execution → controlled ongoing records`.

The SRN is an actor identity, not a permit to promise device-specific representation. Treat every document review as a signal requiring an accountable human decision.

## Security and suppression

- **Public GitHub:** public code, non-client fixtures, bounded operating rules only. No client document exports, watchlists, personal ID, residence, personal email/phone, mandates or credentials.
- **Private vault/CRM:** manufacturer and client records, sensitive correspondence, account-level restrictions, evidence access and billing.
- Cold outreach suppression must fail closed when the private master is unavailable or mailbox history cannot be checked. Always exclude Ergomed Group, PrimeVigilance and cold messaging to Danish-domiciled organisations.
- Allow no more than **15 proposed cold outbound contacts/day company-wide** even if a legacy policy ceiling is higher; no autonomous sending; legal channel review still required.
- Existing kill switches remain authoritative (repo, private Drive, private project). No job may bypass them.
- Use least-privilege credentials, protected main branch, peer-reviewed PRs; see issue #36.
- Do not feed confidential docs to third-party agents/tools without documented authorisation and suitable data-processing agreements.

## Daily human dashboard (proposed)

Show a short status snapshot: AR mandate readiness; open regulatory escalations; live-site/CI; source freshness; critical scanner defects; E4–E6 opportunities; **suppression-blocked** leads; costs; upcoming deadlines; and only the top five actionable `NEEDS_ALI` decisions.

## Done when, not just designed

1. Independent evidence exists for the registered operator and published positioning.
2. At least one actual scheduled Tier-0 run has verifiable output and logs for each active job.
3. Every live workflow has a halt check and a manual fallback.
4. PR CI has passed and a person has reviewed/approved each material release.
5. The private suppression master is restored before outbound starts.
6. No client or personal data has entered the public repo.
