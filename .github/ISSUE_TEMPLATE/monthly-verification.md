---
name: Monthly verification
about: First-Monday regulatory verification routine (about 105 minutes, hard cap 2 hours). The Regulatory Watch workflow opens this automatically; use the template only to open it by hand.
title: "Monthly verification YYYY-MM"
labels: monthly-verification
---

Fixed slot: first Monday of the month, 09:00. Budget 105 minutes, hard cap 2 hours. Anything not done is carried forward in writing below, not dropped.

Source of this routine: lens 29 (accuracy governance), section 9. Rule for every step: update a claim, date or stamp only after reading the primary source yourself. A feed item, a hash change or a law-firm blog post is a prompt to read, never evidence.

- [ ] 1. (10 min) Read the open Issues labelled `regulatory-watch`: Commission EUDAMED RSS, EMA What's new, Danish Medicines Agency news. Also check whether any feed shows a "not readable" Issue; if so, read that source by hand this month.
- [ ] 2. (20 min) Class A claims (dated duties and planning dates): re-read the primary source for every claim with a `review_after` or a dated duty inside the next 60 days. Update `last_verified` only after reading.
- [ ] 3. (20 min) Class B (guidance and operating model): open the MDCG documents page and the Commission EUDAMED page. Look for any new or revised MDCG number touching UDI, EUDAMED, SS(C)P, legacy devices, classification or clinical evidence. Open the document; change claims only on a read.
- [ ] 4. (15 min) EUR-Lex: look for amendments or corrigenda to Regulation (EU) 2017/745, 2017/746, 2024/1860, 2014/536 and Decision (EU) 2025/2371. Cite the Official Journal, not a consolidated copy, for dates.
- [ ] 5. (15 min) Run the claim audits (`python scripts/audit_claim_registry.py`, `python scripts/validate_content_claims.py`) and the tool-constant tests; fix any warning that names a public page.
- [ ] 6. (10 min) Danish layer: Danish Medicines Agency news for device or clinical-trial items; CTIS newsflash by hand (no feed is verified).
- [ ] 7. (10 min) Corrections inbox and public log: reader reports received, material corrections to publish (date, number, citation, scope or conclusion that a reader could act on). A rule that changed after we wrote it is an update, not a correction.
- [ ] 8. (5 min) Move "Rules as of" only on pages actually re-read. Check Actions: Ops Watch and Regulatory Watch both enabled and last run under 35 days ago, and the Ops Watch heartbeat issue has a comment from the last 35 days. Close this Issue with a one-line outcome.

Quarterly (months 3, 6, 9, 12), extra 60 minutes:

- [ ] Re-run or retire class D observations (ClinicOps samples and probes).
- [ ] Class E stable-text check: consolidated-version changes to the articles we cite.
- [ ] Shrink the ungoverned-page allow-list, if one exists.
- [ ] FDA and ICH: manual look only (no verified feed).

Escalate out of the routine, same day: two live claims giving different values for the same fact; a date on the site inside 7 days or already past; a 403 or 429 from any watched source (stop polling that source, note it in the reuse review).

Carried forward / outcome:

