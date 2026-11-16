# Atom feed and regulatory-dates calendar

Stage A of the owned-channel plan: two static files, no email list, no form, no third-party service, no personal data.

| File | Generator | Check |
| --- | --- | --- |
| `docs/feed.xml` (Atom 1.0, `https://clinicops.dk/feed.xml`) | `python scripts/render_feed.py` | `--check` in CI |
| `docs/regulatory-dates.ics` (`https://clinicops.dk/regulatory-dates.ics`) | `python scripts/render_ics.py` | `--check` in CI |

Neither file is in the sitemap, neither has an HTML page, and neither is ever published under a `github.io` URL. Feed autodiscovery (`<link rel="alternate" type="application/atom+xml">`) is added to every public page head by `scripts/harmonize_public_shell.py`; `research.html` and `eudamed-transition.html` carry a visible "Subscribe" line.

Shared code is `src/clinicops_os/public_feeds.py`. Both scripts read the registry at build time and take whatever it says.

## What is included, and why only verified

A reader who subscribes acts on what arrives, and a wrong date in a calendar is worse than a wrong paragraph. So the files are fail-closed. A claim is included only if all of these hold:

1. status is `verified` or `qualified` (never `unchecked` or `rejected`);
2. `website` is in its `allowed_uses`;
3. it is not superseded and its `review_after` has not passed (`--as-of YYYY-MM-DD`, default today UTC; on the day a review lapses `--check` fails until a person re-reads the source, or the claim drops out);
4. it has a `last_verified` date (the day a person last read the source), which becomes the feed `updated` time and the calendar "Rules as of" date. Nothing uses the clock for either;
5. at least one indexable page declares it in a `<!-- claim-ids: ... -->` comment, so the feed never carries a statement the site does not.

Anything else is left out. `--report` prints each omitted claim with the reason.

**Feed entries** are (a) claims that pass the rules above, with a stable id `tag:clinicops.dk,2026:claim/CO-CLM-NNNN`, and (b) entries of the dated corrections log in `docs/research.html` (id `tag:clinicops.dk,2026:correction/YYYY-MM-DD-n`). Every entry has a `<category scheme="https://clinicops.dk/claims" term="CO-CLM-NNNN">` registry id, a link to the page, and links to the primary sources. Repository paths and `github.com` links are never published as sources. Each `<li>` of the corrections log names its registry ids as bare numbers in `data-feed-claims="0018,0019"` (bare numbers because the page claim gate counts every full `CO-CLM-` id in a page as a statement the page makes, and a correction can point at a claim that has since been superseded or rejected). An entry that corrects ClinicOps' own self-description, with no registry claim behind it, is marked `data-feed="editorial"`: it stays on the page, carries no ids and is not published in the feed. The build fails if an entry has neither, or if an id is unknown.

**Calendar events** come from the same eligible claims. Each event is one all-day `VEVENT` with a stable UID (`reg-co-clm-NNNN-<key>@clinicops.dk`), `DTSTAMP` and `LAST-MODIFIED` from `last_verified`, a description with the source URL(s), the page, the registry id and "Rules as of", a `URL`, and a `VALARM` 14 days before. Dates are shown exactly as the source states them: there is no weekend roll-forward, and a weekend date says so in its description. Lines are folded at 75 octets (RFC 5545).

## Optional registry fields (additive; nothing breaks if absent)

- `last_verified`: `YYYY-MM-DD`, the day the source was last read. Required for any feed entry or event.
- `ics_events`: list of `{"key": "legacy-deadline", "date": "2026-11-28", "summary": "...", "kind": "deadline", "sequence": 0, "note": "..."}`. `key` (lowercase, digits, hyphens) is part of the UID and must not change; `date` is `YYYY-MM-DD`; `kind` is one of `date` (default), `deadline`, `milestone`, `recommendation`, `planning_rule`; bump `sequence` when you change a published date; `note` is optional extra text.
- `fact_key` plus a date-type `value` (`YYYY-MM-DD`): contributes one event (key `value`) with summary `ics_summary` or the `fact_key`; an optional `kind` (for example `planning_rule`) is honoured. Month-only or free-text values are not dates and are ignored.

A malformed `ics_events` entry fails the build; it is never skipped silently.

## Corrections and withdrawn dates

Correct a date by editing the claim (and `sequence`), and add an entry to the corrections log on the Research page. The calendar has no withdrawal marker yet: a claim that drops out simply disappears from the file, so record the withdrawal in the corrections log.

## Not built (Stage B, gated)

No email digest, subscribe form or processor. Stage B needs an imprint, an updated privacy notice, a chosen EU processor and stored consent text first.
