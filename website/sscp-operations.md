<!-- claim-use: website -->
<!-- claim-ids: CO-CLM-0001,CO-CLM-0009,CO-CLM-0012,CO-CLM-0018,CO-CLM-0019 -->

# SS(C)P operations: plain explainer

Rewritten 2026-11-16 (plenum lens 18/31/33): the page was a sales page; it is now a plain explainer. Dates come only from registered claims allowed for website use.

## SEO title

SS(C)P operations explained: who does what | ClinicOps

## Meta description

A plain explainer: what a summary of safety and clinical performance (SS(C)P) is, who draws it up and who uploads and validates it in EUDAMED, the dates that apply, and where ClinicOps stops.

## H1

SS(C)P operations explained: what it is and who does what

## Intro

An SS(C)P is a manufacturer's summary of safety and clinical performance. The page says what it is, who does which part, which dates apply, and where ClinicOps stops. It covers MDR Article 32 only.

## What it is

Under MDR Article 32(1), the manufacturer draws up the summary for implantable devices and class III devices, subject to the Article 32 exclusions. [CO-CLM-0001] The summary must include the identification of the device, including the Basic UDI-DI (Article 32(2)(a)). [CO-CLM-0012]

## Who does what

- Manufacturer: draws up the SS(C)P. Under the operating model in MDCG 2026-4, uploads the master version and its translations to EUDAMED. [CO-CLM-0009]
- Notified body: under the same model, indicates which SS(C)P is validated by ticking the box for the relevant Basic UDI-DI(s). [CO-CLM-0009]
- ClinicOps: none of these roles. On request, compares the records that describe the same device and lists where they differ.

MDCG 2026-4 is a non-binding position paper tied to the new EUDAMED functionality; check current Production behaviour before relying on it operationally. Other roles, such as authorised representatives and importers, are not covered.

## Dates

Both dates come from MDCG 2026-4 rev.1 (October 2026). The first is a plan; the second is a recommendation, not a statutory deadline.

- December 2026: planned Production deployment in EUDAMED of the revised SS(C)P operating model, after a planned Playground deployment in July 2026. Plans, not evidence that the functionality is available. [CO-CLM-0018]
- 27 March 2027: for devices placed on the market before mandatory use of the UDI/Devices module, manufacturers "should" upload SS(C)Ps as soon as possible and no later than this date. [CO-CLM-0019]

Rules as of 16 November 2026. Next review by 31 January 2027.

## Boundary

ClinicOps does not draw up, validate or approve an SS(C)P, holds no manufacturer, authorised-representative or notified-body role, and does not decide whether a record is correct. A missing public field is not a finding of non-compliance. Where records differ, ClinicOps lists the difference for the responsible person to resolve.

## Internal implementation notes

- URL slug: `/sscp-operations` (unchanged).
- One H1 only.
- Do not render claim IDs publicly.
- Title is pinned in `scripts/check_live_site.py`; change both together.
