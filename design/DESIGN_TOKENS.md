# ClinicOps design tokens (canonical)

Status: ACTIVE — "Clinical Ledger" system (2026-09 redesign), superseding the original teal/Geist
"ledger" tokens this file previously described. These tokens are implemented in the single
`:root` block in `docs/site.css` (light) and its `@media(prefers-color-scheme:dark)` override
(dark); every public page inherits them with zero per-page hardcoding. This file names them so
every surface (site, Scanner, SVG illustrations, reports, future Figma library, charts) uses the
same vocabulary. When a Figma library is created, it mirrors this file — Figma never forks the
values.

## Color (light / dark)

| Token | Light | Dark | Use |
|---|---|---|---|
| --bg | #f7f5f0 | #16130f | page background (warm paper, not white/near-black) |
| --surface | #ffffff | #1e1a13 | cards, panels |
| --surface-2 | #efebe1 | #241f17 | callouts, table heads, secondary panels |
| --text | #1b1912 | #ede8de | body text (ink, not pure black) |
| --muted | #6b6455 | #a79e8c | secondary text |
| --border | #e2dccb | #362f23 | hairlines |
| --border-strong | #cbc2aa | #4a4131 | stronger rules (rail dividers, `.closing.band`) |
| --control | #8b8371 | #6e6553 | form control borders |
| --accent | #33396b | #8b93d6 | brand, links, CTAs — ink indigo |
| --accent-strong | #23274a | #a9afe3 | hover/active states |
| --accent-contrast | #ffffff | #12142b | text on solid `--accent` fills |
| --accent-soft | #e7e8f2 | #23264a | accent wash |
| --secondary | #b5502a | #e08a5f | terracotta — sparing use only, never a status colour |

## Status semantics (never color alone — always paired with the status word)

| Status | Token | Light | Dark |
|---|---|---|---|
| aligned | --ok | #2f6d4f | #7fd9a8 |
| mismatch signal / conflicting evidence | --hold | #b23a2e | #f0897a |
| missing evidence / requires qualified review / unresolved | --warn | #a6741a | #e3b15c |
| not applicable | --muted | as above | as above |

## Type, spacing, shape

Three self-hosted type families, each doing one job (`docs/assets/fonts/`, no third-party
requests — Google Fonts and similar remain off-limits for this privacy-first audience):

- `--font-display`: Fraunces (variable weight 500–700, optical size pinned at 36 to halve the file; the
  full opsz axis cost ~45 KB on the mobile critical path) — h1–h4 only. A serif reads as an
  authored, archival document rather than software chrome; this is the single biggest visual
  break from the prior Geist-everywhere system.
- `--font`: Public Sans (variable) — body copy, UI, nav.
- `--mono`: IBM Plex Mono — identifiers, labels, status words, tabular numbers, list counters.

Radii: `--r` 6px, `--r-sm` 4px (cards, controls). No pill/999px radii. Spacing rhythm uses
`clamp()` fluid values rather than a fixed px scale — see `docs/site.css` for the exact
clamp ranges per section type (hero, `.rail`, `.closing`). Shadows avoided (`--shadow:none`);
borders and the accent rule (`.rail::before`, left-border cards) carry structure instead.

## Visual character

Calm · precise · archival — a printed regulatory dossier, not a software dashboard. Warm
paper/ink neutrals, one primary accent (ink indigo) and one secondary accent (terracotta, used
sparingly and never as a status colour). No gradients-as-decoration, no AI-glow imagery, no fake
metrics. Diagrams as code (inline SVG with these tokens, Mermaid/Graphviz for internal docs);
real product screenshots only (Playwright, sanitized fixtures); evidence figures only from real
data under figure governance.

## History

The system this file described before 2026-09 (Inter font stack, teal `--accent`, near-white/
near-black neutrals) was never actually implemented in `docs/site.css` — it documented an
intended direction that the shipped teal/Geist system (see `FRONTEND_REDESIGN_BRIEF.md`) had
already diverged from. That mismatch between "canonical" docs and shipped code is exactly the
kind of drift this repo's own tooling exists to catch elsewhere; keep this file in sync with
`docs/site.css` when either changes; when a copy resolution is needed, `docs/site.css` is the
implementation and its own header comment names the design-language version it ships.
