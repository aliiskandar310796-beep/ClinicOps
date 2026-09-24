#!/usr/bin/env python3
"""Dependency-free validator for the Agent Skills format. Exits 1 on any failure."""
import os, re, sys

ROOT = os.path.join(os.path.dirname(__file__))
errors = []
found = 0
for name in sorted(os.listdir(ROOT)):
    d = os.path.join(ROOT, name)
    if not os.path.isdir(d) or name.startswith('.'):
        continue
    sk = os.path.join(d, "SKILL.md")
    if not os.path.isfile(sk):
        errors.append(f"{name}/: no SKILL.md")
        continue
    found += 1
    text = open(sk, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        errors.append(f"{name}/SKILL.md: missing YAML front-matter (--- fences)")
        continue
    fm = m.group(1)
    nm = re.search(r"^name:\s*(.+)$", fm, re.M)
    ds = re.search(r"^description:\s*(.+)$", fm, re.M)
    if not nm or not nm.group(1).strip():
        errors.append(f"{name}/SKILL.md: missing 'name'")
    elif not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", nm.group(1).strip()):
        errors.append(f"{name}/SKILL.md: name must be kebab-case")
    if not ds or not ds.group(1).strip():
        errors.append(f"{name}/SKILL.md: missing 'description'")
    elif len(ds.group(1).strip()) > 1024:
        errors.append(f"{name}/SKILL.md: description >1024 chars")

if errors:
    print("SKILL validation FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"SKILL validation passed ({found} skill(s)).")
