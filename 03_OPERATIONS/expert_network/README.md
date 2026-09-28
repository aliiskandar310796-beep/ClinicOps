# Expert network data model

This directory contains **public-safe structure only**.

Do not commit a real expert roster here.

Use the schemas/examples to maintain the actual roster in an approved private system.

## Files

- `roster.example.json` — fictional records showing the expected shape.
- `assignment.example.json` — fictional assignment gate.
- `qualification-checklist.md` — human qualification checklist.

Validate locally:

```bash
clinicops-expert-network-validate private-roster.json
clinicops-expert-network-validate private-roster.json private-assignments.json
```

The validator prevents obvious control failures. It does not verify credentials against external registries and does not make legal/professional-scope determinations.
