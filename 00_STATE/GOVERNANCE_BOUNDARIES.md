# Governance Boundaries

> Migrated verbatim from the pre-2026-09-23 `AGENT_STATE.md` monolith as part of the connectome-lens shard proposal (draft, not yet reconciled against live `main`). Content below this line is unedited from the original section.

## CI / resilience gates

Current CI covers pytest, Ruff, revenue/agent/readiness contracts, the AI-company operating contract, public sample drift, site metadata, sitemap/internal links, paid-pilot gates, bundle/review/integrity checks, delegation negative control, claim registry/reference/content gates, sanitized fixtures and the public-copy claim gate.

PR #48 exact-main CI run #512 passed. The AI-company synthetic example is a contract/smoke only and explicitly cannot count as commercial evidence, revenue, founder-independence proof or qualified human review.

Never weaken a gate merely to make CI green.

Ops Watch remains bounded/read-only and covers evidence freshness, claim/reference checks, EUDAMED reachability and live HTTPS/content checks. Public research pages are under the live-check contract.

## Private commercial / CRM state

Private buyer/prospect/outreach records stay private and must not be copied into this public repository.

Claude project-side work reports the fragmented outreach master/addenda have been reconciled privately into a 448-row master. Continue send dedupe against the authoritative private master plus live Sent history.

A confirmed delivery failure was identified on 2026-09-13 for one 12 September outreach address. Treat delivery failures as send-quality evidence rather than “no reply” in the private master. Do not put the prospect identity/address here.

Google Calendar access is working. A missing confirmed-partner meeting was repaired as a local calendar hold without inviting external attendees or inventing conferencing details.

HubSpot contact/company/deal/task/call/meeting/note and one-to-one email read/write capability is available; the portal is essentially unused/sample-only and site-page write still requires reauthorization. Do not manufacture CRM pipeline records from memory.

Commercial/pipeline names, direct emails, private notes, pricing negotiations, client files and proof records never belong in public GitHub.

## External-action boundaries

Require Ali's case-by-case approval before:

- LinkedIn publishing;
- Gumroad/pricing changes;
- creating third-party accounts or live form endpoints;
- analytics/tracking deployment;
- credential revocation/rotation;
- branch-protection/ruleset changes;
- git-history rewrite.

Permanent `DO_NOT_CONTACT`:

- Ergomed Group
- PrimeVigilance

Danish-domiciled organisations are never cold-emailed; public posting only.

## Tier-0 autonomy layer — 2026-09-25

`autonomy/` holds the control plane for the unattended Tier-0 jobs (`autonomy/README.md`, `autonomy/rules.json`, `autonomy/jobs/`). The jobs run as claude.ai scheduled tasks, not as GitHub Actions; the only workflow added, `.github/workflows/autonomy-gate.yml`, is compute-only with `permissions: contents: read`, a timeout and no schedule.

Standing boundaries, encoded in `rules.json` and asserted by `clinicops-autonomy-policy selftest` in CI:

- Tier 0 (research, monitoring, drafts, verification, data building, hygiene reports, invoice preparation, backups) is autonomous; Tier 1 (standing orders) is not enabled; Tier 2 (sends, publishing, site changes, PR merges) is prepared and parked for Ali; Tier 3 (money, contracts, accounts, credentials, CAPTCHAs, compliance-status statements, Danish e-marketing, pushes to `main`, deletions) is never automated and no approval flag releases it.
- Jobs read `main` and open pull requests; they never push to `main`, never force-push, never rewrite history, never change repository settings.
- Kill switch, any one of three: `autonomy/HALT.md` on `main` (create to stop, delete to resume; it must not exist on the committed tree otherwise — `tests/test_autonomy_contract.py`), a Drive file named `CLINICOPS_HALT`, a project doc `00_CONTROL/HALT.md` or `20_AUTONOMY/HALT.md`.
- Private outputs (named EUDAMED research, pipeline, finance, mailbox-derived items) stay in Drive `ClinicOps-Autonomy` and the private project; the `DO_NOT_CONTACT` list stays private (the two permanent exclusions above are the only public entries).
- `.github/CODEOWNERS` names Ali for `autonomy/rules.json`, `autonomy/jobs/` and `.github/workflows/`; it is advisory until branch protection exists (issue #36).

## Repository governance / security

`main` remains unprotected. Green CI is an operating convention rather than an enforced merge rule.

Issue #36 tracks branch protection and least-privilege credential hardening. Broad classic PAT scope remains security debt. Do not revoke/rotate credentials or change repository governance without explicit Ali approval because it can break authorized Claude/ChatGPT workflows.

A large stale-branch set remains. D-24 identified merged/abandoned branches safe to delete, but current connector support has not established a safe branch-delete path. Do not claim cleanup occurred unless refs are actually removed.

### Write-discipline incidents — 2026-09-13

Two connector mistakes wrote harmless placeholder files directly to unprotected `main`; both were detected immediately and removed before further work. No intended repository content changed, but the extra commits remain in history. Treat this as evidence for issue #36: material writes must use a fresh branch/PR, and target branch must be verified before every connector write.

Do not rewrite history merely to hide these incidents.

### D-23 history scrub

Pre-anonymisation commit `cb01b34` remains reachable and contains named watcher outputs. Default recommendation remains **do not rewrite history** because filter-repo/force-push breaks clones/commit bases and may not immediately remove GitHub-held objects. If Ali explicitly chooses a scrub, prepare exact commands and warn before execution.

