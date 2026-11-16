# Ops Watch and Regulatory Watch: keep-alive design and what each check means

Written 2026-11-16 (2026-11-16 plenum review, lenses 29 and 30). Applies to `.github/workflows/ops-watch.yml` and `.github/workflows/regulatory-watch.yml`.

## The problem

GitHub disables scheduled workflows in a public repository after 60 days without repository activity. The failure notice goes only to the person who last edited the cron line. A quiet winter would switch both watches off without anyone noticing.

## The choice (no commits to main)

1. **Heartbeat comment.** `scripts/report_ops_issue.py` keeps one open Issue, "Ops Watch heartbeat" (label `ops-watch`), and adds a comment about every 28 days.
2. **Re-enable call.** Each weekly Ops Watch run calls `PUT /repos/{repo}/actions/workflows/{file}/enable` for both workflows (`actions: write`, step marked `continue-on-error`). This is the approach used by public keep-alive actions.
3. **Monthly Issue.** The first Regulatory Watch run of each month opens "Monthly verification YYYY-MM". Step 8 of that checklist is a human look at the Actions tab and the heartbeat.

Rejected: a keep-alive commit to main (breaks the "no commits to main by automation" rule and pollutes history), and a `workflow_dispatch` self-call (a manual dispatch does not run on a disabled schedule, so it cannot prevent the disable).

## What is NOT verified

GitHub's documentation says "repository activity" without defining it. It is not verified that an Issue comment or the enable call resets the 60-day counter. The design therefore also has a human check (35 days: if the heartbeat has no comment in the last 35 days, re-enable both workflows in the Actions tab). If a disable ever happens anyway, the fallback is a `workflow_dispatch` run from the Actions tab, which restarts the schedule.

## What the weekly check reports

| Check | Fails when | Warns when |
|---|---|---|
| HTTP and title markers | any page status or marker differs | |
| `dns-apex-a` | A records include an address outside the four GitHub Pages IPs, or none (3 lookups, all must disagree) | one of the four missing |
| `dns-www-cname` | no CNAME on www | target is not a github.io host |
| `dns-spf` | none, or more than one SPF record | |
| `dns-dmarc` | no DMARC record | |
| `dns-dkim-selector1/2` | only if run with `--dkim-severity fail` | Microsoft 365 selector record not published (founder action in Defender) |
| `tls-expiry` | certificate valid 14 days or less, or unreadable | |
| `sitemap` | live URL count differs from `docs/sitemap.xml`, or exceeds 48 | |
| `security-txt` | `Expires` in the past | missing, or no Contact or Expires |
| `dns-lookup` | | the public DoH service (dns.google) itself failed; DNS checks skipped |

`security-txt` is a warning on purpose: `actions/upload-pages-artifact` is documented to leave out dotfiles and dot-directories, so `docs/.well-known/security.txt` may not reach the live site without a deploy change. Verify after adding the file, then consider promoting it to a failure.

When the DKIM selectors are published, the warning disappears by itself and the Issue closes on the next clean run. After DKIM has been live for a few weeks, run the job with `--dkim-severity fail` (edit the workflow) so a later removal alarms.

## Regulatory Watch in one paragraph

Three official feeds (Commission EUDAMED news RSS, EMA What's new RSS, Danish Medicines Agency news RSS) are read once a week, with robots.txt checked first and an identifying User-Agent. New or changed items open one Issue (label `regulatory-watch`). Nothing is edited or committed. A 403 or 429 opens an Issue and that feed stays paused while the Issue is open; there is no retry. The EUDAMED public API is not polled. `research/regulatory-watch-state.json` is the accepted baseline; accept items into it with `python scripts/regulatory_watch.py apply-update FILE` in a normal PR. Reported items are not re-listed even if the state file is not updated.
