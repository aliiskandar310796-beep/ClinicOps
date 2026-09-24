# ClinicOps skills

Versioned home for ClinicOps' own agent skills (open Agent Skills format: a folder per skill, each with a `SKILL.md` carrying YAML front-matter with `name` + `description`).

## Add a skill
1. `skills/<skill-name>/SKILL.md` (kebab-case folder name).
2. Front-matter: `name` (kebab-case) and `description` (one line, ≤1024 chars, says when to use it).
3. Body: the instructions.
4. Push — CI (`.github/workflows/validate-skills.yml`) validates format on every change to `skills/**`.

Only ClinicOps' OWN skills belong here — not the Anthropic-provided packs. `_example/` is a template; copy it.
