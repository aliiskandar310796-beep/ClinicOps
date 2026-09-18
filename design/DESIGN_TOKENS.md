# ClinicOps design tokens (canonical)

Status: ACTIVE. These tokens are already implemented in `docs/site.css` and the tool pages' inline `:root` blocks; this file names them so every surface (site, Scanner, SVG illustrations, reports, future Figma library, charts) uses the same vocabulary. When a Figma library is created, it mirrors this file — Figma never forks the values.

## Color (light / dark)

| Token | Light | Dark | Use |
|---|---|---|---|
| --bg | #f8f7f4 / #fbfaf8 | #101419 / #11151b | page background |
| --surface | #ffffff | #171d24 | cards, panels |
| --surface2 | #f0eee8 / #f3f1ec | #1d252d | callouts, table heads |
| --text | #17202b / #1c2430 | #e8edf1 | body text |
| --muted | #5e6874 / #5b6572 | #a1aab4 | secondary text |
| --border | #d7dde2 / #d8dee5 | #303943 | borders, rules |
| --accent | #0d6559 / #0f5c52 | #52d7c3 | brand, links, CTAs |
| --soft | #e0f1ed / #e4f2ef | #142b27 | accent wash |

## Status semantics (never color alone — always paired with the status word)

| Status | Token | Light | Dark |
|---|---|---|---|
| aligned | --ok | #157847 | #69d79d |
| mismatch signal / conflicting evidence | --hold | #b03333 | #ff9191 |
| missing evidence / requires qualified review / unresolved | --warn | #a55b00 | #efb05c |
| not applicable | --muted | as above | as above |

## Type, spacing, shape

Font stack: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto. H1 clamp(2rem,5vw,3.2rem), tight letter-spacing (-.04em); eyebrow 0.75rem/800/uppercase/.07em. Radii: 16px panels, 11–13px cards/tables, 9px controls, 999px chips. Spacing rhythm ≈ 9/14/18/22px. Shadows avoided; borders carry structure.

## Visual character

Calm · precise · technical · Scandinavian/European · regulatory · premium without flash. No gradients-as-decoration, no AI-glow imagery, no fake metrics. Diagrams as code (inline SVG with these tokens, Mermaid/Graphviz for internal docs); real product screenshots only (Playwright, sanitized fixtures); evidence figures only from real data under figure governance.
