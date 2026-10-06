DRAFT — requires user confirmation before publishing.
<!-- claim-use: linkedin -->
<!-- claim-ids: CO-CLM-0016, CO-CLM-0015 -->

"Rev. 4" on a published SS(C)P and "Rev. 4" on a EUDAMED record are not necessarily the same document.

In a September 2026 public-source convenience sample, no published SS(C)P and EUDAMED record in 22 consecutive rows carried the same reference number and revision. In the three of those rows where EUDAMED held an SS(C)P, it carried a different reference from the published file.

That is not, by itself, a defect. MDCG 2019-9 rev.1 describes a document-control model in which an updated revision can exist while notified-body validation is in process, so a published revision may legitimately sit between validation cycles.

The failure mode is comparing counters that were never on the same scale. Three habits help:
- compare issue dates where revision schemes are not proven equivalent;
- say "match" only when identifiers and dates align, never about document text;
- route every difference to a qualified reviewer as "unresolved", not "wrong".

Sample: three convenience samples, 69 device rows, ~42 manufacturers; aggregates only, no manufacturer named; the public record exposes metadata, not document bodies.

#MDR #EUDAMED #SSCP #DocumentControl

---
Footnotes (source verification)

[1] CO-CLM-0016 (qualified, observation): "…in 22 consecutive rows of the second sample no published SS(C)P and EUDAMED record carried the same reference number and revision, the three EUDAMED-held SS(C)Ps in those rows carried a different reference from the published file…" Sources: website/research-sscp-public-record-scan.md; research/corrections/2026-09-08-headline-reversal.md. Limitations carried into the post (CLAIM_RULES rule 8): convenience samples, not population rates; aggregates only; content never retrievable through the public API, so "match" means identifiers. Unresolved cases: the 19 rows without a EUDAMED-held SS(C)P are not characterised in the post and must not be read as missing registrations (rule 5). Residual language-model extraction error cannot be excluded (claim limitation).
[2] CO-CLM-0015 (qualified, secondary/primary guidance): "…MDCG 2019-9 rev.1 describes an SS(C)P document-control model in which an updated revision can exist while notified-body validation timing is in process, so a published revision may legitimately be published between validation cycles." Sources: https://health.ec.europa.eu/document/download/5f082b2f-8d51-495c-9ab9-985a9f39ece4_en?filename=md_mdcg_2019_9_sscp_en.pdf · EUDAMED Information Centre system/procedure-pack Basic UDI-DI page. Limitation carried: a document-vs-record difference is not converted into an irregularity.
[3] CLAIM_RULES.md rule 6 (issue dates when revision semantics are not proven equivalent) and rule 7 ("MATCH" = metadata) are the basis of the three habits; they are editorial rules, not regulatory claims.

Verification note (2026-10-06 run): WebFetch of the MDCG 2019-9 rev.1 PDF was refused (PROVENANCE_REQUIRED). Footnote [2] quotes the registry claim text; re-read the MDCG 2019-9 rev.1 passage at source before publishing.
