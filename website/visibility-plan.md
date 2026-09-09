# ClinicOps.dk visibility deployment plan

Status: implementation-ready. Based on the public clinicops.dk surface reviewed 9 September 2026 and the current ClinicOps commercial thesis.

## Objective

Make clinicops.dk discoverable for a small number of high-intent regulatory-operations searches while preserving evidence discipline and a clear EU-wide commercial posture.

## Current public-site diagnosis

The live homepage is credible and detailed, but it currently asks one URL to carry too many intents at once: EUDAMED/UDI integrity review, Basic UDI-DI, SS(C)P, Danish IFUs, Article 16, vigilance, clinical investigations, confidentiality, pricing and bilingual explanatory material.

That creates three practical problems:

1. Search intent is diffuse: one URL is trying to answer many different queries.
2. Conversion intent is diffuse: the current hero sells a broad integrity review while the strongest ClinicOps wedge is transition portfolio work planning.
3. English and Danish content are repeated on the same long page, increasing length without giving search engines separate focused locale URLs.

A site-specific search on 9 September 2026 did not surface clinicops.dk pages in the search backend used for the audit, even though the homepage itself was publicly crawlable. Treat that as an indexing/discoverability warning to verify in Google Search Console rather than proof of de-indexing.

## Domain strategy

Keep `clinicops.dk` as the live primary domain for now.

A `.dk` country-code domain is a strong Denmark signal. That is useful for Danish trust and Danish-market services, but pan-EU intent should be made explicit in copy and structure.

Compensate by:

- stating EU-wide scope in the English hero and meta description;
- keeping English as the main commercial language for EU-wide services;
- creating focused English landing pages for EU-wide search intent;
- keeping Danish-market content on a dedicated Danish-focused page;
- if a distinct Danish-language site is later needed, prefer an explicit locale path such as `/da/` and use hreflang where the platform permits;
- do not migrate to another primary domain until acquisition evidence shows the ccTLD materially constrains demand.

Optional resilience move later: acquire `clinicops.com` or a suitable `.eu` alternative defensively if available, but do not split authority across two live sites. Redirect any secondary domain to the canonical `.dk` site.

## Canonical positioning

**Category:** MedTech regulatory operations intelligence.

**Core promise:** Turn fragmented EUDAMED and transition evidence into a prioritised, human-reviewed work plan.

**Primary paid offer:** Class III Transition Map / portfolio transition work plan.

**Free front door:** EUDAMED Identifier Check.

**Partner posture:** Evidence reconciliation and prioritisation layer for authorised representatives and regulatory consultancies; not a generic registration-service competitor.

## Recommended site architecture

Homepage `/`
- broad conversion page;
- one H1;
- EU-wide scope immediately visible;
- transition map as primary offer;
- identifier check as free CTA;
- links to focused landing pages.

`/eudamed-transition`
- intent: EUDAMED transition work plan, legacy/MDR portfolio screening, class III transition;
- CTA: request a portfolio map.

`/sscp-operations`
- intent: SS(C)P operations, evidence, translations, Basic UDI-DI handoffs;
- CTA: scope an SS(C)P operations review.

`/authorised-representative-portfolio-intelligence`
- intent: authorised representative portfolio triage, white-label transition support;
- CTA: discuss partner workflow.

`/denmark-medtech-language-review`
- intent: Danish IFU/labelling consistency, in-country review and market-language operations;
- CTA: request a Denmark-market review.

## GoDaddy implementation order

1. Replace homepage SEO title, meta description and hero with `website/homepage-v2.md`.
2. Create the four focused pages from the deployment packs in this directory.
3. Add homepage links to all four pages and cross-link related pages naturally.
4. Ensure only one H1 per page.
5. Add a descriptive page title and meta description to every page.
6. Keep important content as visible text, not only inside images.
7. Keep the primary CTA above the fold and repeat it once near the bottom.
8. Verify canonical URL behavior (`https`, one preferred hostname, no duplicate www/non-www indexing).
9. Verify GoDaddy sitemap/robots behavior and submit the sitemap in Search Console.
10. Request indexing for the homepage and the four focused pages after publication.

## Measurement

Track monthly, not daily:
- indexed pages;
- branded impressions and clicks;
- non-branded impressions for EUDAMED/SS(C)P/AR/Denmark-intent queries;
- landing-page CTR;
- portfolio-map enquiries;
- identifier-check usage;
- qualified calls generated per page.

Do not optimize on rankings alone. A page that ranks but produces no qualified regulatory conversation is not winning.
