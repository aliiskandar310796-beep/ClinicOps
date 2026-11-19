DRAFT — requires user confirmation before publishing.
<!-- claim-use: linkedin -->
<!-- claim-ids: CO-CLM-0017 -->

"We searched EUDAMED and found nothing" is a sentence about the search, not about the register.

On the public EUDAMED device API in September 2026, trade-name search behaved as an unanchored substring match; there was no Basic UDI-DI lookup and no "has an SS(C)P" filter; and the riskClass and legislation parameters were ignored, totals unchanged. Point-in-time observations, not a service description; re-test before reliance.

In a portfolio check:
- a device is "not found" because the trade name was typed as labelled, not as registered;
- a "class III only" extract is in fact everything;
- an identifier you hold cannot be looked up directly.

Failure mode: a negative result logged as a finding. A null result means "not findable under this string, through this route, on this day". Missing public metadata is never, by itself, a finding.

Minimum record per search: string as sent, route, UTC timestamp, total reported, and what was done about the ignored filter.

Then a manufacturer, authorised representative, importer or notified body can repeat the search rather than trust the sentence.

#EUDAMED #UDI #MDR

---
Footnotes (source verification)

[1] CO-CLM-0017 (qualified, observation), registry text: "On the public EUDAMED device API in September 2026, ClinicOps observed that the riskClass= and legislation= query parameters were ignored (totals unchanged), that the same unfiltered query returned different totalElements values minutes apart, that trade-name search is an unanchored substring match, that no 'has an SS(C)P' filter and no Basic UDI-DI lookup exist…" Source record read on `main` (6edb5b2) this run, `website/research-sscp-public-record-scan.md` l.57 ("The `riskClass=` and `legislation=` query parameters are ignored by the public API (totals unchanged)"; "EUDAMED has no 'has an SS(C)P' filter and no Basic UDI-DI lookup") and l.59: "A zero-result trade-name search is not proof of absence. It means 'not findable under the trade name as printed'; the search is an unanchored substring match." Limitations carried: point-in-time observed behaviour, not a published service contract (said in the post); counts approximate; no full-register coverage implied. The deep-offset boundary (also in CO-CLM-0017) is deliberately not mentioned, because it did not reproduce in the 9 September 2026 canary run (see the registry's canary observation claim).
[2] "Missing public metadata is never, by itself, a finding" restates the repository non-negotiable and CLAIM_RULES rule 5; it is an editorial rule, not a regulatory claim. The "minimum record" list is an editorial method derived from the observations above and from the 13 Oct 2026 research-note draft on extract provenance (PR #102); it is not a Commission position.

Not asserted: how the label-vs-registered trade-name case arises in any specific registration (illustration only), and anything about how the API behaves today.

Date guard: CO-CLM-0017 review_after 2026-12-31.
