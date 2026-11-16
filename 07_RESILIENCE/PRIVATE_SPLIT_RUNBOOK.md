# Private split runbook: sales, prospect, strategy and operations material out of the public repository

Prepared 2026-11-16 (plenum lens 30 item 3, lens 33). Status: preparation only. **Nothing in this runbook has been executed.** No visibility change, history rewrite, force-push, deletion or push to another repository has been made. Every command below is for the founder (or a session he explicitly approves) to run, one case at a time, because `00_STATE/GOVERNANCE_BOUNDARIES.md` reserves git-history rewrite and repository-settings changes for his case-by-case approval.

Read-only tooling that backs this runbook: `scripts/private_split_manifest.py` (classifies every tracked path, lists dependencies, proves the public set builds alone) and `tests/test_private_split_manifest.py`.

## 1. Why this exists

The repository `aliiskandar310796-beep/clinicops` is **public**, with GitHub Pages enabled (GitHub REST, read-only, 2026-11-16: `private: false`, `visibility: public`, `has_pages: true`, 0 forks, 0 stars, 0 watchers, 0 tags or releases, 30 branches, 142 pull requests of which 26 were open that day, 492 commits on `main`). AGENTS.md says client, prospect, mailbox and credential data stay out of the public repo, and copilot-instructions rules 8 and 15 say real account and prospect working sets stay private. Today the tracked tree still contains, for example, a 46-row named target-account list with the role to approach (`sales/target_accounts_2026-09-23.csv`), outreach drafts, a discovery ledger, a pipeline file, the service ladder, strategy documents and the resilience plans. Everything in git history is readable by anyone, including files deleted later.

A scan of the current tree for credentials (API-key, token, password and private-key patterns) found none outside documentation text and tool references. **History was not scanned**: run a secret scanner over a mirror clone first (step P5).

## 2. Inventory (from the manifest script)

Run `python scripts/private_split_manifest.py` for the live numbers. On 2026-11-16 (`origin/main` a5bcf2b): 544 tracked paths, **109 private** (55 certain, 54 judgement for the founder to confirm), **435 public**, 0 unclassified. Historical paths that matched a private rule: 115 (`--list private-history`); two historical paths match no rule and need a human look (`__invalid__` and `x` look like junk).

| Private rule | Files | Confidence |
|---|---:|---|
| `sales/` | 18 | certain |
| `revenue/` | 6 | certain |
| `05_CLIENT_DELIVERY/` | 7 | certain |
| `01_STRATEGY/` | 4 | certain |
| `04_GROWTH/` | 11 | certain |
| `07_RESILIENCE/` | 5 | certain |
| `content/drafts/` | 3 | certain |
| `research/economic-validation/` | 1 | certain |
| `offers/` | 3 | judgement |
| `research/market/`, `research/drafts/` | 2 + 2 | judgement |
| `00_STATE/`, `AGENT_STATE.md` | 6 + 1 | judgement |
| `03_OPERATIONS/` (except two synthetic `*.example.json`) | 17 | judgement |
| `06_AGENTS/`, `BUILD_NOTES/`, `experiments/` | 6 + 4 + 1 | judgement |
| `01_PRODUCT/`, `02_PRODUCTS/`, `05_INTELLIGENCE/` | 5 + 1 + 1 | judgement |
| `COLLABORATION.md`, `VALIDATION_AND_SCALABILITY_GATES.md` | 1 + 1 | judgement |
| `website/` plans: `visibility-plan.md`, `CLINICOPS_DK_DEPLOYMENT_PLAN.md`, `denmark-medtech-language-review.md` | 3 | judgement |

Stays public (must): `docs/` (the served site), `website/` page sources, `research/` (claims registry, corrections, primary-source reviews, canary baseline), `data/`, `src/`, `tests/`, `scripts/`, `e2e/`, `qa/`, `examples/` (sanitized fixtures), `skills/`, `design/`, `agents/fleet.json`, `autonomy/`, `.github/`, `.claude/`, `AGENTS.md`, `CLAIM_RULES.md`, `README.md`, `PRIMARY_SOURCES.md`, `CHANGELOG.md`, packaging files.

### Founder decisions on the judgement rows (edit `RULES` in the script, then re-run)

1. **AGENT_STATE.md and 00_STATE/**: private by default, but AGENTS.md and eight agent profiles tell every agent to read `AGENT_STATE.md` first. Either move them and re-point those instructions (section 4, item 8), or flip the rule to public (they hold policy, not names).
2. **autonomy/**: kept public because code, tests, CODEOWNERS and `autonomy-gate.yml` read it and it holds no names. If moved, `/autonomy/...` CODEOWNERS lines and the workflow paths must be re-pointed too.
3. **offers/, research/market/, research/drafts/**: private until a page or report is published; published content belongs under `docs/`, `website/` or `research/`.
4. **03_OPERATIONS/ and 06_AGENTS/**: internal engines and protocols. Moving them does not affect the public product.
5. **data/proof_public.json** stays public by design but carries the founder's name and role. That is a brand decision (D1/D4), not a split decision.

## 3. Three ways to do it, and what each costs

| | Option A: split in place | Option B: make the whole repo private | Option C: swap (old repo private, new public repo from filtered history) |
|---|---|---|---|
| What happens | Private set copied with history to a new private repo; private set removed from the public repo and its history rewritten; force-push | Change visibility of the existing repo to private | New public repo gets only the public set (with its filtered history); the existing repo is made private afterwards |
| Rewrites public history | Yes (force-push, every SHA changes) | No | No (a new repo, new SHAs; the old repo untouched) |
| Past exposure removed | Mostly: needs GitHub Support for cached views and PR refs; clones and forks stay exposed | Repo URL stops being readable; clones and caches stay | Same as B for the old URL; the new public repo never contained the private set |
| Public site | Unchanged (same repo, same Pages) | **Breaks on Free**: Pages is unpublished automatically; needs a paid plan | Moves to the new repo: Pages, secrets, domain re-point (downtime risk) |
| Public research and tamper-evident history | Kept (history rewritten once, disclosed) | Lost: research, claims registry and history are no longer publicly verifiable | Kept in the new repo, history restarts from the filtered copy |
| Open PRs, branches, Actions logs | Break (all SHAs change); close or merge first | Kept (private) | Left behind in the old private repo |
| GitHub cost | 0 | Paid plan needed (see section 7) | 0 |
| Effort | 4-8 h plus Support wait | 30 min plus plan change plus Pages re-publish | 3-5 h plus DNS wait |
| Pairs with lens 30 item 8 (org with two owners) | Separate step later | Separate | **Yes**: create the new public repo under the organisation and the account name leaves public DNS |

Recommendation (founder decides): **Option C if the organisation move is wanted soon, otherwise Option A. Option B only if the public research record is no longer wanted**, because it removes the very trail the site promises ("a page is not quietly edited") and needs a paid plan to keep the site up. All three share the same preparation (section 5, P0-P6).

## 4. Dependencies: what references the private set, and how public CI keeps passing

Produced by `python scripts/private_split_manifest.py --deps` and checked by running the whole public CI list in a copy with the private set removed (`--verify-public-build`: site contract scripts, claim audits, ruff, node rule tests, full `pytest`). With the four moved tests ignored, the public copy passes everything. The items below are the complete list found.

| # | Where | What it does with the private set | Action so CI keeps passing |
|---|---|---|---|
| 1 | `.github/workflows/ci.yml` lines 39-42 | `clinicops-sales-swarm sales/global-sales-swarm.json` plus three greps (33 cells, 99 leads, SWARM READY) | Remove the step from public CI. Run it in the private repo's overlay CI (below). The unit tests for the engine (`tests/test_sales_swarm.py`) build their own cells in code and stay public. |
| 2 | `.github/workflows/ci.yml` line 110 | `claim_gate.py ... offers sales research content` | Drop `offers sales` from the arguments. The gate already tolerates missing directories (verified: exit 0 in the temp copy). Run the gate on those directories in private CI too. |
| 3 | `tests/test_commercial_activation_gate.py`, `tests/test_delegation_proof_contract.py`, `tests/test_pilot_operator_contract.py` | Assert the content of `sales/` pilot, delegation and activation documents | Move these three files to the private repo (they test the private documents, and fail with `FileNotFoundError` without them). |
| 4 | `tests/test_expansion_lane_contract.py` | Asserts `04_GROWTH/expansion_lanes.json` | Move to the private repo. |
| 5 | `tests/test_expert_network.py::test_public_example_roster_is_synthetic` | Reads `03_OPERATIONS/expert_network/roster.example.json` | The two synthetic `*.example.json` files are kept public by an explicit rule. Cleaner: move them to `examples/expert_network/` and change one path in the test (small PR before the split). |
| 6 | `.github/workflows/economic-validation.yml`, `outcome-control.yml`, `risk-control.yml` | `paths:` filters naming `03_OPERATIONS/**`, `06_AGENTS/**` and two protocol files | Delete those filter lines (the code and example paths in the same filters stay). The workflows themselves run on public examples. |
| 7 | `scripts/audit_claim_references.py` | Default targets include `offers/` and `sales/` (resolves `CO-CLM` ids in markdown); skips missing directories | Public run is unaffected. Private overlay CI runs it over the private directories so claim ids there stay checked. |
| 8 | `AGENTS.md`, `.github/copilot-instructions.md`, `README.md` (11 references), `CHANGELOG.md`, eight `.github/agents/*.agent.md` profiles, `autonomy/rules.json:62`, `autonomy/README.md:36`, `autonomy/jobs/seo-content.md:17,23`, `agents/fleet.json:324`, docstrings in `src/clinicops_os/dry_run.py`, `human_review_gate.py`, `economic_validation.py`, tests `test_positioning_contract.py` and `test_strategic_invariants.py`, `e2e/xlsx_xss_journey.mjs:7`, `examples/*.json` `artifact:` strings | Text mentions of private documents (no runtime read; the temp-copy run passes with them dangling) | Re-point or reword in the prep PR. Copilot or any agent working in the public repo will no longer be able to open the private documents; point them at the private repo, or keep AGENT_STATE.md public (decision 1). |
| 9 | `scripts/pipeline_report.py` | Default paths `sales/discovery/discovery_ledger.csv` and `revenue/pipeline/pipeline.csv`; returns empty if absent | No CI impact. The script's real use is private; move it with the data if wanted. |
| 10 | `.github/CODEOWNERS` | Names only `autonomy/rules.json`, `autonomy/jobs/`, `.github/workflows/` | Unchanged under the default classification. |
| 11 | Claude scheduled tasks (claude.ai side, not in the repo) | Jobs under `autonomy/jobs/` read `main` and open pull requests, some against private-bound paths (`00_STATE`, `content/drafts`, `research/market`) | Re-point those tasks' repository and paths in claude.ai after the split. Founder action; cannot be done from the repo. |

False positives the scanner reports and that need no action: `src/clinicops_os/experiments.py:79` (a JSON key named "experiments"), `src/clinicops_os/outcome_control.py:18` (the outcome class "revenue"), `economic_validation.py:356` ("revenue/hour" in a message).

**Overlay CI for the private repo** (sketch for review; not added to `.github/`): the private repo's workflow checks out the public repo at `main` into the workspace, checks out the private repo into `_private/`, copies `_private/*` over the workspace at the same paths, then runs the moved tests, `clinicops-sales-swarm sales/global-sales-swarm.json` with the same three greps, and `python scripts/audit_claim_references.py` and `python scripts/claim_gate.py sales offers content research`. Nothing moves in the public product; the private files are simply tested against the public code that already exists.

```yaml
# private repo: .github/workflows/overlay-ci.yml (sketch)
name: Overlay CI
on: [push, pull_request]
jobs:
  overlay:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with: { repository: <owner>/clinicops, path: . }          # public repo, no token needed
      - uses: actions/checkout@v7
        with: { path: _private }                                  # this private repo
      - run: cp -r _private/. . && rm -rf _private/.git
      - uses: actions/setup-python@v7
        with: { python-version: '3.12' }
      - run: pip install -e .[dev]
      - run: python -m pytest -q tests/test_commercial_activation_gate.py tests/test_delegation_proof_contract.py tests/test_pilot_operator_contract.py tests/test_expansion_lane_contract.py
      - run: clinicops-sales-swarm sales/global-sales-swarm.json | tee /tmp/swarm.json && grep -q '"status": "SWARM READY"' /tmp/swarm.json
      - run: python scripts/audit_claim_references.py && python scripts/claim_gate.py sales offers content research
```

## 5. Option A: exact steps (split in place)

Run on a trusted machine with `git` 2.30+ and `git-filter-repo` 2.47 or newer (the version GitHub's guide requires for `--sensitive-data-removal`). `<owner>` is `aliiskandar310796-beep`. Replace placeholders; run nothing you have not read.

**P0. Approval and decisions.** Founder approves the history rewrite in writing (this repo's rule). Settle the five judgement decisions in section 2 and edit `RULES` in `scripts/private_split_manifest.py` accordingly.

**P1. Freeze.** Merge or close every open pull request (26 on 2026-11-16) and delete stale branches. A rewrite changes every SHA, so open PRs and builder branches (`plenum/*`) cannot survive it. Create `autonomy/HALT.md` on `main` (the documented kill switch) so no scheduled job opens a PR mid-rewrite; remove it afterwards.

**P2. Domain safety (one-off, also needed for B and C).** Verify the custom domain for GitHub Pages (a `_github-pages-challenge-<owner>` TXT record), so nobody else can claim `clinicops.dk` if Pages is ever unpublished or the repo moves. Lens 30 could not confirm it is set.

**P3. Backup.**
```
git clone --mirror https://github.com/<owner>/clinicops.git clinicops-backup.git
git -C clinicops-backup.git bundle create ../clinicops-pre-split.bundle --all
```
Keep both offline. This is also the only way back.

**P4. Prerequisites.** `git filter-repo --version` (2.47 or newer); `gh auth status`.

**P5. Enumerate paths and scan history for secrets.**
```
git clone --no-local clinicops-backup.git work-scan && cd work-scan
python scripts/private_split_manifest.py --strict                 # exit 0 required
python scripts/private_split_manifest.py --list private-history > ../private-paths.txt
wc -l ../private-paths.txt                                         # 115 on 2026-11-16
gitleaks detect --log-opts="--all"                                 # or trufflehog git file://. ; neither is installed here
```
Review the stderr "historic paths matching no rule" list and add rules. If the scanner finds a real credential, **revoke or rotate it first** (GitHub's guidance: rotate first; a rotated secret may make the rewrite unnecessary for that item).

**P6. Prep PR on the public repo (merge before the rewrite).** CI independence changes from section 4 items 1, 2, 5, 6, 8. Merge it, then confirm `python scripts/private_split_manifest.py --verify-public-build` passes on updated `main`.

**1. Create the private repo.**
```
gh repo create <owner>/clinicops-private --private --description "ClinicOps private working set"
```
(or in the web UI). Do not enable Pages.

**2. Copy the private set with its history into the private repo.**
```
git clone --no-local clinicops-backup.git work-private && cd work-private
git filter-repo --paths-from-file ../private-paths.txt             # keeps ONLY these paths, with their history
git remote add origin git@github.com:<owner>/clinicops-private.git
git push -u origin main
```
Check: `git ls-files | wc -l` equals the private file count; `git log --oneline | wc -l` is plausible; `git ls-files | grep -E '^(docs|src|tests)/'` prints nothing. Push only `main`; do not push `refs/pull/*`. Add the overlay CI workflow (section 4) and `AGENTS.md` for the private repo.

**3. Remove the private set from the public repo's history.**
```
git clone --no-local clinicops-backup.git work-public && cd work-public
git filter-repo --sensitive-data-removal --invert-paths --paths-from-file ../private-paths.txt
```
`--paths-from-file` takes exact paths, one per line, so renamed or deleted files must be in the list (that is what `--list private-history` is for). If filter-repo refuses because the clone is not fresh, that is expected: always start from a fresh clone. Keep the printed first-changed-commit SHAs (also in `.git/filter-repo/commit-map`) for step 7.
Verify in `work-public`:
```
for d in sales revenue offers 01_STRATEGY 04_GROWTH 05_CLIENT_DELIVERY 07_RESILIENCE; do git log --all --oneline -- $d | wc -l; done   # all 0
git ls-files | wc -l                                                                                                                  # 435 (or your final public count)
python scripts/private_split_manifest.py --verify-public-build                                                                       # runs against the rewritten tree
```

**4. Force-push.** Pull-request refs cannot be pushed; that is expected.
```
git remote add origin git@github.com:<owner>/clinicops.git
git push origin --force --mirror
```
Per GitHub's guide this overwrites all branches and tags and rejects `refs/pull/*` (read-only). If other refs are rejected, branch protection is on: disable it for the push and re-enable it. Then dispatch CI and Pages, and run the Ops Watch workflow to confirm the live site is unchanged.

**5. Rotate anything sensitive.** From P5: anything a scanner found, rotated before the rewrite. Not credentials and not rotated by default: `EUDAMED_WATCHLIST` and `EUDAMED_HMAC_KEY` live in Actions secrets, not in the repository; rotating the HMAC key changes every snapshot key and breaks diff continuity, so rotate it only if it was exposed. Treat the named-account list, outreach drafts and pipeline as **exposed since their first push**: rewriting history shortens the exposure, it does not undo it.

**6. Pull-request quotations.** 142 pull requests exist. Private material may be quoted in PR titles, bodies, comments or diffs. List the PRs whose diffs touched private paths:
```
for n in $(gh api "repos/<owner>/clinicops/pulls?state=all&per_page=100" --paginate --jq '.[].number'); do
  gh api "repos/<owner>/clinicops/pulls/$n/files" --paginate --jq '.[].filename' | grep -qE '^(sales|revenue|offers|01_STRATEGY|04_GROWTH|05_CLIENT_DELIVERY|07_RESILIENCE)/' && echo "PR $n"
done
```
Edit or delete quoted text in titles, bodies and comments yourself (GitHub: dereferencing does not remove sensitive data quoted in retained bodies or comments).

**7. Ask GitHub Support to purge cached views and PR references.** Open a ticket (GitHub Support, "Remove sensitive data from a repository") with: repository `<owner>/clinicops`, the number of affected PRs from step 6, the first-changed-commit SHAs from step 3, and a request to remove cached views and dereference or delete those PRs (deleting a PR removes its conversation, reviews and diffs). Support only assists with sensitive data, so describe it as the removal of private commercial and prospect data. Old commits remain reachable by SHA until Support acts.

**8. Check forks and clones.** `gh api repos/<owner>/clinicops/forks --jq length` (0 on 2026-11-16; repeat before and after). You cannot remove data from other people's clones or from a fork that contains the commits (GitHub contacts no fork owners for you). Any collaborator or tool with a clone must delete it and re-clone (rebase, not merge, anything built on the old history). Also check search engines and archives for cached copies of `github.com/<owner>/clinicops/blob/...` private paths and request removal where possible.

**9. Re-point.** Section 4 items 1-2, 5-6 and 8 if not already in the prep PR; the claude.ai scheduled tasks (item 11); AGENTS.md pointers; your Obsidian vault links if they point at repo paths.

**10. Retire the tooling and re-run.** Remove `scripts/private_split_manifest.py` and `tests/test_private_split_manifest.py` from the public repo (they only make sense before the split; the test module also skips itself inside a public-only copy). This runbook moves with `07_RESILIENCE/` to the private repo. Run a full CI on `main` and the weekly Ops Watch.

Rollback before step 4: delete the local clones; nothing was changed. After step 4: restore from `clinicops-pre-split.bundle` into a new repository (the old repo's PR history and Actions logs cannot be restored by force-push).

## 6. Option B: make the whole repository private instead

Change visibility in Settings, "Danger zone", "Change repository visibility". GitHub states the consequences (docs.github.com, "Setting repository visibility", read 2026-11-16 through a page-summary tool; re-read the page before acting):
- "Any published GitHub Pages site will be automatically unpublished." This applies on GitHub Free; clinicops.dk would stop serving until Pages is re-published on a plan that allows it.
- Pages for private repositories is listed for GitHub Pro, Team and Enterprise, not Free (docs.github.com, "GitHub Pages limits" and "GitHub's plans"). The published site is still public unless you use Enterprise Cloud access control. Check current price and terms.
- "Code scanning will become unavailable unless Code Security is enabled for this repository", so the CodeQL workflow would stop working on a plan without it. "Custom Dependabot alert rules will be disabled unless GitHub Code Security is enabled"; dependency graph and Dependabot alerts remain.
- "Stars and watchers for this repository will be erased" (currently 0), "Current forks will remain public and will be detached" (currently 0 forks), and the repository leaves the GitHub Archive Program.
- Branch protection on private repositories is a paid feature (plans page). It is also not confirmed whether any protection exists now (the API refused to say).
- Public trust: the public claims registry, corrections trail and commit history disappear from public view. The site's promise of dated corrections becomes unverifiable from outside, and lens 30's Zenodo and citation ideas lose their source.
- Domain risk: if Pages is unpublished, `clinicops.dk` points to GitHub with nothing behind it; do P2 first.

**Actions minutes if the repo is private** (GitHub Free personal: 2,000 minutes per month; Pro: 3,000; public repositories are not metered; docs.github.com, "GitHub's plans", read 2026-11-16 through a summary tool). Per-run billed minutes are measured from the 16 Nov 2026 runs (each job rounded up to the minute; Linux 1x). Monthly counts are my assumptions for a normal month of about 15 pushes or pull requests that trigger CI, not measurements.

| Workflow | Trigger | Billed min per run | Runs per month (est.) | Minutes per month (est.) |
|---|---|---:|---:|---:|
| CI (`test` 1 + `scanner-browser` 3) | push and pull_request | 4 (measured) | 30 | 120 |
| CodeQL (two analyses) | push main, PR to main, weekly | 3 (measured) | 23 | 69 |
| Frontend QA | PR touching docs/qa, weekly | 3 (measured) | 14 | 42 |
| Integrity Gate | push and pull_request | 1 (measured) | 30 | 30 |
| Deploy ClinicOps Site (Pages) | after CI on main | 2 (measured) | 8 | 16 |
| Ops Watch (live-site + evidence freshness) | weekly | 3 (measured before the extension; about 3-4 after) | 4.3 | 13-17 |
| Regulatory Watch (new) | weekly | 1 (estimate) | 4.3 | 5 |
| E2E Scanner Journey | weekly | 4 (estimate, not measured) | 4.3 | 17 |
| OSV Scan | weekly | 2 (estimate, not measured) | 4.3 | 9 |
| EUDAMED Watch | monthly | 2 (estimate; timeout 20) | 1 | 2 |
| Autonomy Gate, Economic Validation, Outcome Control, Risk Control, Validate skills | push/PR on path filters | 1 each (estimate) | about 10 in total | 10 |
| **Total (normal month)** | | | | **about 335-340** |

A normal month fits inside 2,000. A build wave does not: on 2026-11-16 alone CI ran 28 times (about 112 billed minutes) while parallel builders were pushing, so a wave of a few days can exceed the monthly allowance. Dependabot update runs also use Actions minutes on private repositories (not verified here). Under Options A and C the public repository stays unmetered and only the (small) private overlay CI is billed.

## 7. Option C: swap (old repository becomes private, new public repository from filtered history)

1. P0-P5 as above. In P5 also produce `public-paths.txt`: `python scripts/private_split_manifest.py --list public`.
2. Create the new public repository (under the organisation if the lens 30 item 8 move is happening: two owners, hardware keys). Do not enable Pages yet.
3. Fresh clone of the backup, `git filter-repo --paths-from-file ../public-paths.txt` (keeps only public paths and their history; also needs historical public paths, so add `git log --all --name-only --format= | sort -u` entries that classify public), push `main` only.
4. Recreate what does not travel: Actions secrets (`EUDAMED_WATCHLIST`, `EUDAMED_HMAC_KEY`), Pages source (Actions), custom domain (`docs/CNAME` travels), domain verification TXT (P2) for the new owner, branch protection and CODEOWNERS user names, Dependabot settings, issue labels (`ops-watch`, `regulatory-watch`, `monthly-verification`).
5. Run CI and the Pages deploy on the new repo; check `https://<new-owner>.github.io/<repo>/` or the Pages preview before touching DNS.
6. DNS at the registrar: point the `www` CNAME to the new `<owner>.github.io` (the apex A records stay the four Pages addresses). GitHub does not redirect Pages on transfer or rename, so do this in one sitting, then re-run Ops Watch.
7. Only after the live site is confirmed on the new repo: make the old repository private (its Pages site unpublishes automatically; that is intended now) and move the private set into `clinicops-private` as in Option A step 2, or simply keep the old repo as the private one and delete nothing.
8. Update `check_live_site.py`, `CODEOWNERS`, README links and the claude.ai scheduled tasks to the new repository.

## 8. What stays the same under every option

- Nothing here changes the published site content, the claims registry or any regulatory statement.
- The four moved tests and the sales-swarm contract keep running somewhere (private overlay CI) instead of disappearing.
- The honest limit: data that has already been public cannot be recalled. The aim is to stop further exposure, remove what GitHub controls, and know what remains.
