DRAFT — requires user confirmation before publishing.
<!-- claim-use: linkedin -->
<!-- claim-ids: CO-CLM-0016, CO-CLM-0012 -->

The public EUDAMED record of an SS(C)P is four fields. Reconcile those, and say which you compared.

In the September 2026 public-source scan, the public record exposed a reference number, a revision, an issue date and a validated flag. The document itself is never retrievable publicly.

When a tracker says "SS(C)P in EUDAMED: current", ask which field was compared, against what.

The structure that holds:
- reference and revision: compare with the published file's own;
- issue date: compare with the date printed in the document;
- validated flag: record it, do not interpret it;
- Basic UDI-DI: Article 32(2)(a) requires the SS(C)P to identify the device, including the Basic UDI-DI, so page one is comparable with the registration.

The failure mode: "match" asserted on text nobody could read. In 22 consecutive rows of that scan, no published SS(C)P and EUDAMED record carried the same reference and revision. Lag, or a different document? Only the manufacturer's document control knows.

Manufacturers, authorised representatives, importers and notified bodies can share those columns.

Convenience sample; aggregates only; identifiers, not text.

#EUDAMED #SSCP #MDR

---
Footnotes (source verification)

[1] CO-CLM-0016 (qualified, observation). Registry limitation carried verbatim into the post: "Content is never retrievable through the public API; 'match' means matching identifiers, never matching text." The four exposed fields are stated in the source record read on `main` (6edb5b2) this run, `website/research-sscp-public-record-scan.md` l.60: "The public record exposes only a reference number, revision, issue date and validated flag." The 22-row figure is the registry text ("in 22 consecutive rows of the second sample no published SS(C)P and EUDAMED record carried the same reference number and revision") and l.36 of the same page. Limitations carried: convenience samples, not population rates; frames lean toward smaller firms that publish openly; extraction by language-model agents, residual extraction error cannot be excluded; aggregates only, no manufacturer or device named, not a compliance statement about any company (CLAIM_RULES rule 8).
[2] CO-CLM-0012 (verified, primary): "Article 32(2)(a) MDR requires the summary of safety and clinical performance to include the identification of the device, including the Basic UDI-DI." Sources: https://www.legislation.gov.uk/eur/2017/745/article/32 · https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32017R0745. Limitation carried: the requirement describes document content, not EUDAMED linkage mechanics, so the post says "comparable with the registration", not "the link key". Not re-fetched this run (unattended WebFetch of pages not first surfaced by a same-run search is refused); the quotation is the registry claim text, last verified at source by the verification job. Re-read Article 32(2)(a) at source before posting.

Not asserted: what the validated flag means procedurally (no registry claim covers it; the post says "record it, do not interpret it"), and who sets each field in the revised operating model (the registry claim on the MDCG 2026-4 role allocation is deliberately not cited; its review_after is 2026-10-31).

Date guard: no claim in this post expires before 2026-12-31.
