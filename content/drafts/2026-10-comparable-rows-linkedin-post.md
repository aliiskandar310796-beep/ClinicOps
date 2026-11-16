DRAFT — requires user confirmation before publishing.
<!-- claim-use: linkedin -->
<!-- claim-ids: CO-CLM-0016 -->

Before you report a mismatch rate, count how many rows could have matched.

In a September 2026 public-source convenience sample of 22 consecutive device rows, a published SS(C)P could be set next to an SS(C)P held in EUDAMED in only three. In all three, the references differed. In the other rows the public data held no SS(C)P to compare against.

Pool all 22 into one "mismatch" figure and a reader sees a register failure that the data does not show. Missing public metadata is not a finding.

A reconciliation table needs at least four outcome states, each with its own count:
- match: identifiers and dates align (metadata, never document text);
- difference: both sides present, values differ, routed to a qualified reviewer;
- not comparable: one side absent from the data you can see;
- unresolved: the evidence cannot decide.

Then state the denominator. Manufacturers, authorised representatives, importers and notified bodies reading the same portfolio should all be able to see it.

Sample: convenience sample, aggregates only, no manufacturer named; identifiers compared, not document bodies.

#EUDAMED #MDR #SSCP #DataIntegrity

---
Footnotes (source verification)

[1] CO-CLM-0016 (qualified, observation), registry text: "…in 22 consecutive rows of the second sample no published SS(C)P and EUDAMED record carried the same reference number and revision, the three EUDAMED-held SS(C)Ps in those rows carried a different reference from the published file…" Source record read at source on `main` (6edb5b2) this run, `website/research-sscp-public-record-scan.md` l.36: "In the three of those rows where EUDAMED held an SS(C)P at all, it held a d[ifferent reference]…". Also `research/corrections/2026-09-08-headline-reversal.md`.
Limitations carried (CLAIM_RULES rule 8): convenience samples, not population rates, and the frames lean toward smaller firms that publish openly; content is never retrievable through the public API, so "match" means identifiers (rule 7); extraction by language-model agents reading JSON, residual extraction error cannot be excluded; aggregates only, no manufacturer or device named, not a compliance statement about any company. Unresolved cases: the 19 rows without a EUDAMED-held SS(C)P in the public data are reported as "not comparable", never as missing registrations (rule 5).
[2] The four outcome states restate CLAIM_RULES rules 5 and 7 and the repository non-negotiable "never treat missing public metadata as a compliance finding". They are an editorial method, not a regulatory claim.

Why this post exists: the 8 Oct 2026 verification of the 6 Oct batch (PR #96, post 1) failed that post because it pooled the 22 rows. This post turns the correction into the lesson.
