# eCOA Delivery Workbench: project initiation record (2026-11-14)

Structure follows PRINCE2 (7th edition) project initiation products at the size this prototype warrants. PRINCE2® is a registered trademark of PeopleCert; no accreditation is claimed.

## 1. Specialization gate (AGENTS.md, 2026-09-18)
Question: does this strengthen EU MedTech Regulatory Data Integrity? **Adjacent.** The default for adjacent work is "record as backlog". It was built because the owner instructed it explicitly (2026-11-14, "has to be developed into clinicops.dk"). Decision recorded for the owner to confirm or reverse; the page is labelled a sanitized prototype and is not placed in primary navigation.

## 2. Business case
- Reason: eCOA delivery is where Danish-language and change-control work meets sponsor timelines; the owner wants a credible, inspectable method artefact for that work.
- Expected benefits (not yet evidenced): inbound qualified conversations; a method he can apply on a real design-partner study. Neither is measured today.
- Dis-benefits and risks: dilution of the integrity positioning; maintenance burden; a "tool" being read as a validated system. Mitigation: boundary text, documented-tool record on the page, no scores, kill condition below.
- Options considered: do nothing; write an article only; build the prototype (chosen, smallest option that is inspectable); build a hosted multi-user system (rejected: privacy contract, YAGNI, no validation).

## 3. Tolerances
Time: one stage, released when CI is green. Cost: no new dependencies, no new services. Scope: browser-local, one page, three scripts. Quality: all contract tests, axe WCAG 2.2 AA, no console errors. Risk: no unverifiable regulatory statement on the page. Benefits: review at the kill dates. Sustainability: no runtime network, no storage, no build step.

## 4. Product descriptions (quality criteria)
| Product | Quality criteria | Check |
|---|---|---|
| Rule core `ecoa-workbench-core.js` | Deterministic, no DOM, no network; rules as documented on the page | Node tests QA01–QA14, QA18 |
| Content `ecoa-workbench-data.js` | Every item has basis and registered source; no pre-filled ratings or targets | Node QA15–QA17; pytest |
| Page and script | Local only; text-only rendering of imported data; accessible; reflows 320–1440 px | pytest; Playwright |
| Source register | Each source opened at origin and dated; context-only sources say so | verification pass 2026-11-14; QA16 |

## 5. QA validation matrix (33 passes)
18 rule-family passes (Node, `tests/ecoa_workbench.test.cjs`): product status, not-applicable handling, out-of-sequence completion, due dates, plan summary, schedule comparison, Danish-letter normalisation, schedule parsing, exposure matrix, change-rule integrity, change impact merge, surface closure, script skeleton, script input refusal, testing-area shape, findings and exit hold, checklist completion, tolerance status and completion counts (QA01–QA18, with the export-safety, workspace-validation, prototype-pollution, report and content-integrity families inside the numbering).
9 contract passes (pytest, `tests/test_ecoa_workbench_contract.py`): identity and boundary, banned claims and names, DOM-id contract, tab/panel pairing, source registry, browser-local and no dynamic code, cross-site registration, fictional example, no pre-filled ratings.
6 browser passes (Playwright, `e2e/ecoa_workbench_journey.mjs`, 111 checks): full functional journey on all tabs with keyboard navigation; hostile import and export safety; network and storage privacy; reflow at 320/390/768/1024/1440 px; axe WCAG 2.2 AA in light and dark at mobile and desktop on every tab; resilience (forced colours, no JavaScript, 200% text, print).
Existing site-wide gates (metadata, links, professional claims, sitemap, shell, llms.txt, claim gate, privacy contract, site acceptance, performance) also run on the new page.

## 6. Known gaps (do not claim past these)
- No real study has used it; no design-partner feedback. Checklists and the change-surface table are ClinicOps method.
- PRINCE2 official practice names verified only through secondary syllabi; EU DCT paper version and several DOIs verified at origin on 2026-11-14 but may change.
- FDA guidance items are context only, not mapped.
- `validate_content_claims.py website` fails on this branch and on `main`: claim reviews CO-CLM-0005/0008/0009 expired on 2026-10-31. Not caused by this work; needs the owner's claim review.

## 7. Kill condition and review dates
See `02_PRODUCTS/PRODUCT_REGISTRY.md`: 2027-02-14 usage check; 2027-05-14 design-partner check.
