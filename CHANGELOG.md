# ClinicOps operating changelog

## 2026-11-14
- Public site made independent of any individual (owner instruction): removed the owner's name, biography, degrees, language list, "I" voice, personal LinkedIn link and Person/founder structured data from all pages; the voice is now "ClinicOps", and research pages are authored by the organisation. The About page now describes how ClinicOps works. Identity stays only where a law or registry requires it: the privacy notice (controller identification), the registered-actor block on the EU authorised representative page, and the contact address. No team, headcount or scale is claimed; the practice is described as small. Validator and tests now enforce the rule.
- Design pass on PR #121 using three published design-engineering rule sets (Emil Kowalski's design-engineering notes, Impeccable's craft floor and detector, Taste's rules for plain static sites): removed the 41 eyebrow/kicker labels above headings (status notes such as "browser-local" and "sanitized prototype" moved to a plain line under the lede), replaced 2px coloured left borders on callouts with a 2px top rule, press feedback `scale(.97)` on buttons, hover effects gated to hover-capable pointers, one strong ease-out curve with named durations (140/180/260 ms), shorter hero entrance (520 ms), disabled states, caret/scrollbar/marker theming, reading measure capped near 70 characters. Impeccable's detector reports no findings on the pages scanned except `cream-palette` and `overused-font` (Fraunces), both kept on purpose: the paper-and-ink palette and Fraunces are the Clinical Ledger identity and are pinned in `design/DESIGN_TOKENS.md`. Not applied from Taste: stock photography, shader/card-loop effects and real-icon sets, because they would add unapproved imagery to a regulatory practice site.
- Proposed site restructure (branch `feat/site-restructure-clinical-operations`, not merged): homepage now "Clinical operations support from Denmark" with three lanes (eCOA, medical device records, Danish language and pharmacovigilance); navigation reorganised; tools page grouped by lane with eCOA first; 24 plain-language copy replacements; decision record `01_STRATEGY/SITE_PROJECT_PID_2026-11-14.md`.
- Added the eCOA Delivery Workbench (`docs/ecoa-delivery-workbench`) as an adjacent, browser-local sanitized prototype: instrument-language plan, protocol-vs-specification schedule comparison, testing skeleton, risk and issue registers, change-surface mapping, tolerances, highlight report; PRINCE2-structured; 18 sources verified against origin on 2026-11-14.
- Added Node rule tests (30), a pytest contract test (9), and a Playwright journey (111 checks) to CI.
- Fixed during testing: calendar-impossible dates (for example 30 February) were accepted by `isoDate`.

## 2026-09-09
- Initialized public GitHub operating repository.
- Encoded 8 Sep headline reversal into standing claim rules and claim guard.
- Added a versioned claim registry with evidence class, allowed use, limitations, review dates and supersession state.
- Added publication-pack generation so approved claims carry their limitations and source ledger into downstream work.
- Added opportunity scoring that rewards evidence, leverage, defensibility and reuse while penalizing risk and maintenance burden.
- Added portfolio transition report generator for AR/manufacturer work-plan screening.
- Added a deterministic sanitized portfolio report fixture and CI drift check.
- Refactored the EUDAMED API canary into a testable module; ordinary CI uses no live EUDAMED network calls.
- Added multi-agent collaboration contract so ChatGPT/Claude/other assistants can coordinate through durable shared state.
- Added the internal Class III Transition Map offer specification and buyer-validation criteria.
- Raised the verified CI baseline to 30 passing tests plus Ruff, claim-registry audit, report-fixture check and public-copy claim gate.
- Isolated GitHub Pages enablement as the single tracked manual deployment dependency in issue #1.

## 2026-09-08
- Corrected initial SS(C)P-linking hypothesis after systematic class III census.
- Reframed commercial thesis from manufacturer diligence gap to legacy-to-MDR transition gap.
- Added API reachability and page-size limitations to publication constraints.
