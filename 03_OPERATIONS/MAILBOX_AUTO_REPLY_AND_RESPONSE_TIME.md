# Mailbox auto-reply, response time and enquiry commitments

Status: DRAFT, written 2026-11-16 from plenum lens 19 (conversion path). Text only. Nothing here is an integration: the founder pastes the auto-reply into the Microsoft 365 automatic-reply setting of `info@clinicops.dk` and `support@clinicops.dk` once the commitments below are confirmed. Defaults are pending his OK.

## 1. Commitments the public site now makes (confirm or change)

These are promises about future behaviour, not regulatory claims, so they do not belong in `research/claims.jsonl`. They are listed here in registry style so each has one owner, one place it is stated and one thing that must be true for it to stay honest.

| ID | Commitment | Stated at | Default | What must be true | Founder decision |
|---|---|---|---|---|---|
| CM-01 | Questions and scope requests get a reply within three working days, Spanish and Danish public holidays excluded | `docs/contact.html` lede; this auto-reply | 3 working days | Oldest unanswered enquiry is checked every Monday (10 minutes, private, not published). If a number the founder can keep is different, change it in both places | Accept 3 days or give another number |
| CM-02 | A dated away line replaces the default when ClinicOps is travelling | `docs/contact.html` `#away` (hidden by default) | hidden | Founder removes `hidden` and sets the date before leaving, restores `hidden` on return. A stale away line is worse than none | Accept the procedure |
| CM-03 | The reply names the public source if a public source answers the question; otherwise it says what a scope would look like | `docs/contact.html` Ask block | on | Replies actually do this | Accept |
| CM-04 | ClinicOps does not forward a question or add the sender to a mailing list | `docs/contact.html` Ask block | on | No newsletter or list exists (none does; the privacy notice says no marketing list is kept) | Accept |
| CM-05 | Enquiries that do not lead to an engagement are deleted twelve months after last contact | `docs/privacy-notice/index.html` section 7 | 12 months | A calendar reminder runs a quarterly deletion pass over both mailboxes | Accept 12 months or give another number, and set the reminder |
| CM-06 | Questions and corrections go to `support@clinicops.dk`; scope requests go to `info@clinicops.dk` | `docs/contact.html`, `docs/research.html`, tool pages | on | Both mailboxes exist, are monitored and share one auto-reply | Accept the two-inbox split |

Not promised anywhere, on purpose: any "within 24 hours" or "same day" reply; anonymity (an email address identifies the sender); a fixed price; a booking link; a follow-up sequence.

## 2. Auto-reply, English

Subject: `Received: <original subject>` (Microsoft 365 adds the prefix; leave the default if it differs)

> Thanks, your message arrived. A reply follows within three working days, Spanish and Danish public holidays excluded. If ClinicOps is away, the date is shown at clinicops.dk/contact.
>
> Please do not send patient-identifiable data or confidential files by email. A secure route is agreed first.
>
> This is an automatic acknowledgement. It is not advice and not an offer. How your message is handled: clinicops.dk/privacy-notice/

## 3. Auto-reply, Danish (use for senders writing in Danish, or add under the English text)

> Tak, din besked er modtaget. Du får svar inden for tre hverdage, dog ikke på spanske og danske helligdage. Hvis ClinicOps er bortrejst, står datoen på clinicops.dk/contact.
>
> Send ikke patientidentificerbare oplysninger eller fortrolige filer pr. e-mail. En sikker fremgangsmåde aftales først.
>
> Dette er en automatisk kvittering, ikke rådgivning og ikke et tilbud. Sådan behandles din besked: clinicops.dk/privacy-notice/

Rules for this text: transactional only, no promotion, no link other than the contact and privacy pages, no mention of any named party. An automatic acknowledgement to an inbound message is not marketing; keep it that way.

## 4. Away line procedure (`docs/contact.html`)

1. Find `<p class="away" id="away" hidden>`.
2. Remove `hidden`, replace `[date]` with the return date and the `datetime` attribute with the same date as `YYYY-MM-DD`.
3. Commit as "Away until <date>". Reverse on return (put `hidden` back, reset the placeholder).
4. Update the Microsoft 365 automatic reply to name the same date.

## 5. Weekly check (private, never published)

Monday, 10 minutes: find the oldest enquiry without a reply in `info@` and `support@`. If it is older than three working days, answer it first. Do not publish the check or any reply-rate figure; a published figure would need evidence.

## 6. Reading the funnel without analytics

Signals available from the mailbox alone: count of emails per subject prefix (`Question:` from the Ask block, `ClinicOps scope` from the scope brief and the info@ link), the `Source`/`Campaign`/`Segment` lines inside a brief body, and a monthly manual tally. Report only to the founder. No analytics script is to be added.
