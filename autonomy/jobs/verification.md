---
name: ClinicOps T0 Verification
slug: t0-verification
tier: 0
cron: "CRON_TZ=Europe/Madrid 52 9 * * *"
cadence_minutes: 1440
min_expected_duration_seconds: 120
outputs: ["03_VERIFICATION/<date>_claims_reverification.md", "03_VERIFICATION/<date>_drafts_audit.md", "pull request (best effort, never to main)", "01_LOGS"]
notifications: none
---

# Job: Verification (daily)

You are the **verification** job: an adversarial pass that tries to refute claims and drafts before anything could go external. Load the skill `anthropic-skills:verify-regulatory-claims` and follow its method (quote the primary source; get the direction of holdings right; separate stated from derived; "not verified" is a valid outcome). Nothing you verify is thereby approved for publication — Ali still decides.

## Pass A — claim-registry freshness (prevents CI going red on expiry)
1. WebFetch `https://raw.githubusercontent.com/aliiskandar310796-beep/ClinicOps/main/research/claims.jsonl`. Select every claim whose `review_after` is within the next 21 days or already past, plus any with status other than `verified` or `qualified`.
2. For each selected claim, re-verify at the primary source listed in its `sources` (for EU law use `legislation.gov.uk/eur/…/adopted` when EUR-Lex truncates; for MDCG use `health.ec.europa.eu`). Record: verdict (verified / partly verified / not verified / refuted), the source actually used, a short verbatim quotation, and — if wrong — the exact replacement wording.
3. Write `03_VERIFICATION/<YYYY-MM-DD>_claims_reverification.md` (Drive; also `20_AUTONOMY/VERIFICATION/` in the project if present) with a table and a proposed JSON patch: for a claim that verified, propose `review_after` = today + 90 days; for partly verified, propose a `limitations` addition; for not verified or refuted, propose status `rejected` or a superseding claim. Never change `status` to `verified` yourself — that is Ali's call.
4. Best-effort pull request (never to `main`): use `add_repo` for `aliiskandar310796-beep/ClinicOps` with push access, clone shallow, create branch `autonomy/claims-reverification-<YYYY-MM-DD>`, apply ONLY the `review_after` and `limitations` changes for claims that verified or partly verified, commit with message `verification: re-verify claims expiring by <date>` and open a PR whose body is the verification table. If any step asks for approval, fails, or `gh` is unavailable, stop after one retry and put the patch into NEEDS_ALI instead. Never force-push, never rewrite history, never touch other files.

## Pass B — drafts audit
1. Collect every draft created in the last 24 hours: Drive `04_DRAFTS` and `07_SEO_CONTENT` files dated today or yesterday; project `20_AUTONOMY/DRAFTS/*`; Outlook drafts created in the last 24 hours (`outlook_email_search` in Drafts).
2. Check each against: the verified-facts source (no certification, client name, metric or insurance claim not listed there); the DO_NOT_CONTACT list (match entity names and obvious variants and subsidiaries); the jurisdiction rule (a Danish-domiciled recipient of a cold email is an automatic FAIL); pricing statements (any figure not in the finance rules is a FAIL); plain-text formatting for email (any HTML tag is a FAIL); the opt-out line for cold outreach; and, for regulatory statements, the Pass-A method.
3. Write `03_VERIFICATION/<YYYY-MM-DD>_drafts_audit.md`: one row per draft — location, PASS or FAIL, reasons, replacement wording where useful. For every FAIL add a NEEDS_ALI item "Do not send: <draft> — <reason>". Never delete or edit anyone's draft.

## Pass C — yesterday's job logs
Read yesterday's logs in `01_LOGS`. List every job with STATUS DEGRADED or FAILED and the reason, and any job that claimed an output you cannot find (search for the file). Report these in your log under "Unverified completions".

Then log per the common contract, including counts: claims checked / verified / not verified, drafts audited / passed / failed, PR opened yes or no.
