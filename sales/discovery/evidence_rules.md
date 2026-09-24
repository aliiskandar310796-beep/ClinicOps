# Evidence rules for the discovery ledger

Applies to `discovery_ledger.csv`. The ledger is empty until a real contact occurs.

## Non-negotiable rules
1. One row per real contact event. Never add simulated, synthetic, example or back-filled rows.
2. E4 and above require genuine human buyer interaction: a real person at a real organisation responding or speaking. Automated replies, bounces and outbound activity never qualify.
3. Rows describe what happened, not what was hoped. When unsure, choose the lower level.
4. `source_note` must point to where the evidence lives (for example a private message id or dated note). Without a source, the row is capped at E1.
5. Keep personal data minimal. `org` and `role` only; no private contact details in this repository.
6. Danish-domiciled organisations are not cold-contacted; log only warm or inbound contact.
7. Compliments, interest or "sounds interesting" are E4 at most. Scores and compliance conclusions are never recorded.

## Columns
`id` sequential (D001...); `date` ISO; `org`; `role`; `channel` (email, linkedin, call, event, referral, inbound); `contact_type` (cold, warm, inbound, partner); `outcome` (see below); `evidence_level` (E0-E9); `next_step`; `source_note`.

## Ladder (E1-E9 follow `sales/clinical-operations-offer-pack.md`; E0 added here)
- E0: no evidence, hypothesis only.
- E1: public market or workflow signal.
- E2: qualified, reachable account with a verified route.
- E3: outreach delivered to a verified route.
- E4: substantive human response or qualified conversation.
- E5: repeated pain, consequence and workflow confirmed by the person.
- E6: priced-scope request, procurement step or identifiable budget owner.
- E7: paid or activated work.
- E8: accepted delivery or payment.
- E9: repeat, renewal, expansion or referral caused by delivered value.

## Outcome to level

| outcome | level | note |
|---|---|---|
| researched_only | E0-E1 | no contact made |
| route_verified | E2 | account and route checked, no message sent |
| sent | E3 | delivered without bounce; sending alone is not a response |
| bounce / auto_reply / out_of_office | E3 at most | delivery evidence, not E4 |
| opted_out / not_relevant | E3 | log, suppress permanently; the reason may still inform hypotheses |
| polite_reply_no_substance | E4 max | only if a real person replied |
| interview_completed | E4 | conversation held, no confirmed repeated pain |
| pain_confirmed | E5 | specific past events, cost and workflow, in their words |
| scope_or_budget_signal | E6 | asked for scope/price, or named a budget owner or procurement step |
| paid_work_activated | E7 | signed order or payment path exists |
| delivered_accepted | E8 | delivery accepted or payment received |
| repeat_or_referral | E9 | caused by delivered value |

## Review
Before reporting any level above E3 outside this repository, re-check the source note. Discovery activity counts (emails drafted, rows added) are diagnostic only and are never reported as validation.
