# Discovery interview guide (30 minutes)

Status: internal operator script. No interview has taken place. Keep names, notes and recordings out of this repository; record only what the ledger columns allow (see `discovery_ledger.csv`, `evidence_rules.md`).

## Purpose

Find out whether EU-market medical-device teams repeatedly spend real time and money reconciling an approved regulatory change across EUDAMED/UDI data, SS(C)P, certificates, labels, IFUs and controlled documents, and whether anyone owns and funds that problem. The aim is to learn, not to sell. A polite conversation is not evidence of demand.

Boundary to state if asked: ClinicOps compares regulated information and structures review work. A machine-detected signal is not a qualified determination. It does not make regulatory, legal, clinical or safety determinations.

## Ground rules: do not pitch

1. Do not describe ClinicOps, the review, the scanner or pricing until minute 25, and only if the person asks or the problem is confirmed.
2. Do not show a demo, specimen or tool during the interview.
3. Do not ask for a commitment, a pilot, a file or a follow-up meeting before the wrap-up.
4. Do not tell the person they have a problem, a gap or a compliance risk. Do not comment on their real portfolio or registrations.
5. Do not ask for confidential documents or patient-identifiable data.
6. Do not claim customers, results, testimonials or prior conversations.
7. Record only what they say happened. Mark opinions and hypotheticals as such.
8. If the person is a Danish-domiciled organisation contact who arrived through a warm or inbound route, follow the same rules; never cold-contact them.
9. Ask consent before taking notes. If they decline, do not record.

## Questions to avoid

- "Would you use / buy a tool that...?" (hypothetical, invites politeness)
- "Do you think this is a problem?" / "Is X important to you?"
- "How much would you pay?" (ask about current spend instead)
- Leading questions naming EUDAMED, SS(C)P or Class III before they do.
- Compliments fishing: "Does that sound useful?"
- Feature or roadmap questions: "What would you want it to do?"

## Structure

### 0-3 min: frame and consent
"Thanks for the time. I am a solo founder researching how regulatory teams handle changes to approved product information. I am not selling anything today. May I take brief notes? Nothing you say will be shared or attributed."

### 3-8 min: role and context
- What is your role, and what does your team look after (devices, markets, clients)?
- Walk me through the last time an approved regulatory change had to be reflected in other records. What was the change?

### 8-18 min: past behaviour, cost, workaround
- What happened first, and who was involved? Which systems and documents did you touch?
- How did you find out what else needed updating? How did you know when it was done?
- How long did it take, and how many people? What did it displace?
- Did anything turn out to be out of step afterwards? What happened then?
- How often does this happen: last quarter, last year?
- What do you use today (spreadsheets, RIM, QMS, consultants, in-house scripts)? What is annoying about it?
- Have you tried to improve it? What did you try, and what happened?

### 18-24 min: ownership and budget path
- Who owns this work? Who decides how it is done?
- Has money or time been spent on it in the last 12 months (tools, consultants, headcount)? Roughly how much, if you can say?
- If a fix were worth doing, how would that be approved? Who signs, and what budget line?
- What else competes for that budget right now?

### 24-28 min: only if asked, or the problem is confirmed
One sentence: "I am testing a human-reviewed service that reconciles an approved change against the records you supply and returns an exception list; your qualified team decides." Then ask: "What would make that a non-starter?"

### 28-30 min: wrap-up
- Who else should I speak to about this? (Ask for a name, not an endorsement.)
- May I contact you once more if I learn something relevant? Note yes/no exactly.
- Thank them. Do not push for a meeting.

## After the call (same day)
1. Write one ledger row (see `discovery_ledger.csv`), stating only what was said.
2. Assign an outcome and ladder level using `evidence_rules.md`; when unsure, choose the lower level.
3. Update `hypotheses.md` evidence status only with reference to ledger ids.
