<!-- claim-use: website -->
<!-- claim-ids: CO-CLM-0001,CO-CLM-0004 -->

# ClinicOps homepage — canonical deployment pack

Status: ready for browser-assisted implementation on clinicops.dk. This file is the canonical homepage copy until replaced by a newer validated version.

## SEO title

EUDAMED Transition Work Plans for MedTech | ClinicOps

## Meta description

Evidence-backed EUDAMED portfolio screening and human-reviewed transition work plans for EU MedTech manufacturers, authorised representatives and regulatory partners.

## Hero

### Turn EUDAMED transition evidence into an actionable work plan.

ClinicOps helps EU MedTech manufacturers, authorised representatives and regulatory partners map class III and implantable portfolios, separate legacy and MDR registration paths, reconcile identifiers, prioritise transition evidence, and organise SS(C)P and market-language work.

**Primary CTA:** Request a portfolio transition map

**Secondary CTA:** Check an EUDAMED identifier

**Trust line:** Danish domain. EU-wide regulatory operations scope.

Small-print qualifier: Public-register screening is an evidence input, not a compliance determination or a full-register audit.

## Problem

### The hard part is not finding another data point. It is deciding what needs action first.

Portfolio teams often have to reconcile public EUDAMED records with certificate timing, manufacturer-controlled evidence, Basic UDI-DI information, SS(C)P operations and target-market document requirements.

ClinicOps turns that fragmented evidence into a prioritised work queue while keeping machine-detected signals separate from human regulatory judgement.

## Offer

### Class III Transition Map

For a supplied or publicly screenable portfolio, ClinicOps can produce:

- registration-path and actor-role segmentation;
- transition / certificate timing queue where evidence is available;
- identifier and Basic UDI-DI reconciliation questions;
- SS(C)P evidence and workflow questions;
- market-language document-control questions;
- explicit unresolved evidence gaps;
- a human-reviewed action plan.

The deliverable is a work plan, not an allegation that a manufacturer is non-compliant.

**CTA:** Scope a small pilot

## Free front door

### EUDAMED Identifier Check

Use the free local browser tool to screen an identifier structure, including B-prefixed legacy-style EUDAMED DI signals and common SRN actor-role shapes.

The tool does not verify current actor status, device responsibility or compliance. A B-prefix is useful for structural screening but does not by itself establish a device's full regulatory or SS(C)P state. [CO-CLM-0004]

**CTA:** Open Identifier Check

## Why ClinicOps

### Machine breadth. Human judgement. Evidence that survives review.

ClinicOps is built around a simple operating model:

1. capture the signal;
2. classify the evidence;
3. preserve actor-role and duty-holder context;
4. block unsupported claims;
5. prioritise the work;
6. deliver a human-reviewed action plan.

Under MDR Article 32, the manufacturer is the duty holder for drawing up the SSCP for applicable implantable and class III devices, subject to the Article 32 exclusions. ClinicOps preserves that duty-holder context instead of flattening the workflow into generic document checking. [CO-CLM-0001]

## Best fit

ClinicOps is designed for:

- authorised representatives managing multiple manufacturer portfolios;
- manufacturers with class III / implantable transition workload;
- regulatory consultancies that need a white-label evidence and work-plan layer;
- teams entering Denmark or other EU markets where document-language operations must be coordinated.

## Explore the workflow

Create focused landing pages rather than loading every search intent onto the homepage:

- `/eudamed-transition` — portfolio transition screening and work planning;
- `/sscp-operations` — SS(C)P evidence, translation and operational handoffs;
- `/authorised-representative-portfolio-intelligence` — partner / white-label portfolio layer;
- `/denmark-medtech-language-review` — Danish IFU, labelling and market-language consistency work.

The homepage should link to all four and remain the broad conversion page.

## What ClinicOps does not promise

- no end-to-end public-register audit claim when API reachability is incomplete;
- no compliance allegation from a missing public link alone;
- no automatic conversion of an observed system pattern into law;
- no replacement for notified-body, legal or manufacturer-controlled evidence where those inputs are required.

## Closing CTA

### Start with one portfolio, not a platform project.

Send a small portfolio export or discuss the workflow first. ClinicOps will identify what can be screened reproducibly, what evidence is missing, and where human regulatory judgement is actually needed.

**Primary CTA:** Request a portfolio transition map

**Secondary CTA:** Check an identifier

## GoDaddy implementation notes

- Replace the current broad `Independent review of EUDAMED records, Basic UDI-DI, SS(C)P and Danish IFUs` hero with the transition-work-plan hero above.
- Keep Danish capability visible, but do not make the English homepage read as Denmark-only.
- Keep the free Identifier Check as the low-friction entry point and the Class III Transition Map as the paid judgement layer.
- Move long legal/rules material away from the main conversion flow where GoDaddy page structure permits; link to focused supporting pages instead.
- Keep one H1 only. Use descriptive H2s for offer, free tool, best fit, evidence boundaries and contact.
- Use the exact SEO title and meta description above in GoDaddy SEO settings.
- Do not publish internal claim IDs in the rendered website; they are editorial traceability markers only.
- Before deployment, run the repository claim gate and the content-claim-reference validator.
