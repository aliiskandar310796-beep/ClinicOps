# Learning hub: resilient marketing plan (2026-11-18)

Status: proposal for the owner. Nothing here is sent, posted or scheduled. Every outbound step needs the owner's approval under the standing rules (POST GATE, outreach-law addendum, DO_NOT_CONTACT, VERIFIED_PROFILE_FACTS).

Page: `/learn` (hub), with `/ecoa` (eCOA hub and 12-minute video) as the first complete learning area.

## 1. What this has to achieve

The hub is a trust asset, not a traffic goal. Following the Client Acquisition Engine, success is a qualified conversation that starts from something the person already used: a question that names a pattern, a scope request that starts from a tool, or a referral that quotes a page.

Leading signals (weekly): topic requests received, questions received, scope-form submissions that started from a learning page, search queries and pages (Search Console), feed subscriptions if the host exposes them.
Lagging signals (monthly): qualified conversations, bounded paid reviews, referrals that name a page.

Not targets: impressions, followers, video views, email list size.

## 2. What "resilient" means here

A plan is resilient if losing any one channel, platform, tool or person does not stop it. The design choices:

1. **Own the surface.** Every external touch points at a page on clinicops.dk that works without JavaScript services, accounts or third parties. Site, transcripts, feed, calendar, `llms.txt` and sitemap are the durable core. They cost almost nothing to keep alive (static files, build-less).
2. **Content that ages slowly and says when it was read.** Pages carry read dates and next-review dates, so staleness is visible and fixable rather than silent. The feed publishes corrections. This is the moat: regulated buyers distrust unsourced material, and most competing content is unsourced.
3. **More than one way to be found.** Search and AI answer engines (structure, transcripts, chapters, `VideoObject`), professional network (LinkedIn, within the POST GATE), partner and referral channels (ARs, consultancies, eCOA vendors, language-service providers), and direct (feed, calendar, bookmarks). No channel should carry more than about half of qualified conversations; review quarterly.
4. **No dependency on a platform's algorithm or terms.** Social is a distribution layer pointing home. The video is self-hosted; a YouTube copy is optional later and never canonical.
5. **Cheap to run alone.** One spoke per two to three weeks is the pace a solo practice can hold. Agents draft and check; the owner approves anything outward. A plan that needs daily posting fails the first busy month.
6. **Privacy-clean by design.** No cookies, no third-party embeds, no email capture. This matches the audience (regulated, data-protection aware) and removes a whole class of legal and breach risk. The cost is thinner measurement, handled in section 6.

## 3. Audiences (hypotheses to test, not facts)

| Audience | Where they start | First useful object | Next step |
| --- | --- | --- | --- |
| Sponsor or CRO clinical operations (eCOA, vendor oversight) | Search for a step, a licence or a language problem | 12-minute video, workflow map | Burden estimator, workbench, scope request |
| eCOA vendors, language-service providers | Referral, partner page | COA types, lead-time planner, terminology template | Partner conversation (written scope, one accountable owner) |
| Device manufacturers and authorised representatives | Search for SS(C)P or registration questions | SS(C)P explainer, registration work plan | Integrity scanner, research method, scoped review |
| Entrants and operators in Denmark and the Nordics | Search in English; later Nordic-language queries | Denmark reference, Nordic eCOA context, DHPC checker | Question or scope request |

Check each against the specialization gate before building more: the hub is clinical operations and Nordic life science, which is adjacent to the flagship (EU MedTech regulatory data integrity). Keep device-record material visible in the hub so the flagship is not displaced.

## 4. Content architecture

```text
Hub (/learn)
 -> Area hub (/ecoa)                       pillar: complete, dated, sourced
     -> Spokes (workflow, types, Nordic)   reference pages with source registers
     -> Tools (browser-only)               proof objects: the work on the reader's own data
     -> Video (12 min)                     the way in; chapters deep-link to spokes
         -> Atoms                          one chapter, one figure, one source-labelled finding
```

Rules for every new learning page: official source opened and dated; what was not established stated; claims registered or the page declared claim-free; synthesis labelled as such; no client names; synthetic voice disclosed; page has one clear next step.

### Candidate next areas (rank by topic requests, not by guess)

Candidates only; none is committed, and none goes on the site as "coming soon" (unkept dates cost trust).
1. eCOA in Sweden, Norway, Finland, Iceland: per-country authority and language points where sources were read.
2. Language and licensing: from licence request to approved translation, with the lead-time planner as the worked example.
3. Device-record reconciliation for Nordic distributors: what changes in the record when one thing changes.
4. A 90-second teaser cut of the video (for the hub and for LinkedIn).
5. A deeper cut per phase of the workflow (Prepare, Build, Test, Run, Close) if the chapters show demand.

Intake for topics is the pre-filled topic request on `/learn`: the questions people actually send decide the order.

## 5. Channels and guardrails

**Search and AI answer engines (owned, highest durability).** Done: transcript on the page, `VideoObject`, chapter deep links, sitemap, `llms.txt`. Owner action: confirm Google Search Console ownership and submit the sitemap (needs the owner's account). Keep titles and descriptions literal and specific; avoid clever naming.

**LinkedIn (distribution, not foundation).** From the ClinicOps identity, not the personal one. POST GATE applies to every post: whole value chain, teaches a structure or failure mode, anchored to a real asset, verified at source, shown to the owner before scheduling. At most three posts a week, weekdays 08:30 CEST. Atoms that fit: one chapter plus its source; one figure with its attribution; one catch point from the video with the page link. Never a post that names a vendor's or sponsor's problem.

**Partner and referral channel.** Per the acquisition engine: ARs, regulatory consultancies, eCOA vendors, language-service providers. Value offered: a learning page they can send to their own clients, and a terminology or UAT template (CC BY 4.0) they can reuse. Outbound only under the pacing and dedup rules (all three checks every send, sub-batches of five, plain text, read back the first). Danish-domiciled organisations are never contacted by cold email or LinkedIn DM (markedsføringsloven section 10); they are reached by public posting and by being found.

**Professional communities and events (Nordic).** Participate with useful answers that link to a page only where it fully answers the question. No broadcast posting. Options to evaluate with the owner, none committed: Nordic clinical-operations and regulatory associations, local meetups, a short talk built from the video.

**Video platforms.** YouTube and similar are discovery channels with third-party tracking. Not recommended until the hub has proven demand. If used: upload the same file, description links to the hub, transcript as captions, never the canonical copy. Needs an account created by the owner.

**Email newsletter.** Deliberately absent (the feed and calendar replace it). Reopen only if readers ask; it would need a vendor account, a lawful basis, a privacy-notice change and a change to the page claims "no email list".

## 6. Measurement without tracking

Privacy-friendly analytics is a pending owner decision (needs a vendor account). Until then:
- Search Console (queries, pages, impressions) once ownership is verified.
- Count and classify by hand: topic requests, questions, scope requests, referrals that name a page. Add one optional line to the scope form, "What brought you here?", if it is not there (owner decision; it is a form change).
- Qualitative review monthly: which pages were quoted back in conversations.
- If cookieless analytics is added later, update the privacy notice and the "no tracking" wording on the hub and the feed page first.

## 7. Risk register

| Risk | Early signal | Mitigation |
| --- | --- | --- |
| A regulatory claim is wrong or goes stale | Correction request; source changes | Read dates, next-review dates, claim registry, corrections log, 10-working-day decision rule already published |
| Hub drifts from the flagship | Most conversations are eCOA, few device | Quarterly gate review; keep device material in the hub; record as backlog if adjacent |
| Platform or algorithm change cuts LinkedIn reach | Falling reach with stable search | Social is distribution only; rely on owned surface; no channel above half of conversations |
| Single-person bottleneck | Cadence slips | One spoke per 2-3 weeks; templates; agents draft, owner approves; static site needs no upkeep |
| Synthetic voice reads as impersonal or draws objection | Feedback; low completion | Disclosed on the page; the transcript and chapters stand alone; option to re-record later (a person's own voice, or a licensed professional voice) |
| Marketing-law breach (cold outreach) | Any proposed send to a Danish-domiciled organisation | Hard rule; the Danish rule is in the outreach-law addendum; checks every send |
| Claims about the owner or ClinicOps not in VERIFIED_PROFILE_FACTS | Copy that names credentials, clients, languages or metrics | The hub makes none; keep it that way; check that file before any such line |
| Large binaries bloat the repository | Clone time | Keep videos under about 10 MB; if more are added, move media to release assets or object storage with a documented fallback |
| Competitors copy content | Similar pages appear | Evidence discipline, read dates and corrections are hard to copy; keep the tools and templates as the proof layer |

## 8. Sequence (90 days, with gates)

Gate 0, now: hub live after owner approval; links from `/ecoa` and `/research`.
Weeks 1-2: owner verifies Search Console and submits the sitemap; owner decides the pending items below; teaser cut drafted (owner reviews before use).
Weeks 3-6: one new spoke or area chosen from topic requests; three POST GATE posts drafted from the video chapters, shown to the owner; no posting before approval.
Weeks 7-12: partner conversations under the pacing rules, offering the learning pages and templates; review the signal table.
Gate 1, end of week 12: keep, change or stop each channel by evidence (qualified conversations and topic requests), not by activity.

## 9. Decisions needed from the owner

1. Merge the hub PR (publishes it).
2. Nav: the primary navigation is capped at seven items by a positioning test, so `/learn` is linked from `/ecoa` and `/research`, not the header. Options: swap "Home" for "Learn" (the logo already links home), or leave as is.
3. Danish home page: linking `/learn` from the English home page changes a stamped unit and needs the Danish twin re-translated. Do you want that, or keep the home page unchanged?
4. Search Console ownership and sitemap submission (your account).
5. Privacy-friendly analytics vendor (your account), and whether to add "What brought you here?" to the scope form.
6. Whether to use a YouTube copy later (your account), and whether to replace the synthetic voice later.
7. Which Nordic countries to prioritise after Denmark, and whether any claim about languages or experience may appear (only if listed in VERIFIED_PROFILE_FACTS).
