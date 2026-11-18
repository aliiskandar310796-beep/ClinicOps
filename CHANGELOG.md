# ClinicOps operating changelog

## 2026-11-18 – eCOA learning hub: narrated walkthrough

- `ecoa` now opens with a "Start here" block: a 12 min 27 s narrated walkthrough of the twelve workflow steps, self-hosted (`docs/assets/video/ecoa-12-steps.mp4`, about 10 MB, 1280x720, poster alongside), `preload="none"`, no third-party player, no cookies, no network call until play. Chapter list seeks the video (`docs/assets/ecoa-video.js`, no network) and links each chapter to its step on `ecoa-workflow`; full transcript in a `<details>` block; `VideoObject` JSON-LD; "A suggested learning path" replaces "How the pieces work together". `ecoa-workflow` gains a "Prefer to watch?" link.
- The narration is a synthetic voice (local open-source TTS), disclosed on the page. One imagined study, not a client, runs through it. Labelled a ClinicOps synthesis, not a standard.

## 2026-11-16 – eCOA workflow map: twelve steps, templates, language dimension

- `ecoa-workflow` updated in place from ten stages to twelve steps (0 to 11): new step 0 (decide and select) and new step 10 (control change and transfer data); the former step 10 is now step 11, steps 1 to 9 keep their numbers. Rows carry slug anchors (`#step-test`). Labelled a ClinicOps synthesis of published guidance, not a standard. The source register gained a "last opened" column; all eight sources were reopened on 2026-11-16. Claims `CO-CLM-0053` to `CO-CLM-0055` added (renumbered from 0050 to 0052 at integration, where registry-stamps already used those ids) for the statements the new rows and templates rely on.
- Change Surface Mapper: optional "language versions and deliverables affected" input (`docs/assets/change-surface-core.js`, `tests/change_surface.test.cjs`); the brief and JSON gain the field only when it is used.
- Static template downloads in `docs/downloads/` (not pages, not in the sitemap, no email gate), built deterministically by `scripts/build_ecoa_templates.py` with the standard library only: eCOA UAT script skeleton, findings log and approval form (XLSX, adapted from a CC BY 4.0 paper); terminology governance template (one-page XLSX and CSV). Both CC BY 4.0, version 1.0.

## 2026-11-14 – COA and eCOA section

- New pages: `ecoa` (hub, now the eCOA navigation target), `coa-types`, `ecoa-workflow`, `coa-nordic`. Each carries a source register with the date opened and how much of each source was read; items that could not be verified are listed as open questions, not stated.
- Three new free browser-local tools: COA type finder and inventory (`coa-type-finder`), licence and translation lead-time planner (`ecoa-lead-time-planner`), visit and diary burden estimator (`ecoa-visit-burden`). Core rules live in `docs/assets/coa-*-core.js` with 31 Node tests; no network, no storage, formula-safe CSV.
- Sitemap ceiling 40 to 48 (decision D8 in the PID). One vendor the owner excluded is removed from the PID source list and appears nowhere.

## 2026-11-14 – Display font

- Headline font changed from Fraunces to Source Serif 4. Fraunces drew a hooked J/j and a looped ampersand that read as odd; Source Serif 4 keeps the warmth with ordinary letterforms. Self-hosted, OFL licence included.

## 2026-11-14 – Living colour and a rebuilt homepage

- Colour now follows the segment: eCOA teal, device cobalt, Danish coral, with a calm petrol-ink base. A page or band takes its segment ink through `data-seg`; status colours still pair colour with a word. All pairs checked at 4.5:1 or better in light and dark.
- Homepage rebuilt: three doors in the first screen, one full-width colour field per segment, a fictional example plan, a tools index, a four-step project flow and a dark closing band. Plainer copy throughout.
- Flow: a header line fills as you read and changes colour with the segment you are in (`assets/flow.js`; CSS scroll timeline where supported, small script elsewhere; reduced motion respected).
- Other pages get the shared colour system, segment headline ink and the new tokens; their copy and structure are not rewritten in this change.

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
