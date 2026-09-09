from __future__ import annotations

from pathlib import Path

AGENT_DIR = Path(".github/agents")
REQUIRED_FILES = {
    "portfolio-operator.agent.md",
    "regulatory-evidence-steward.agent.md",
    "release-sentinel.agent.md",
}
REQUIRED_KEYS = {"name", "description", "tools"}


def _parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing opening YAML frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing closing YAML frontmatter delimiter")

    front = text[4:end].splitlines()
    body = text[end + 5 :]
    data: dict[str, object] = {}
    current_list: str | None = None

    for line in front:
        if line.startswith("  - ") and current_list:
            values = data.setdefault(current_list, [])
            if isinstance(values, list):
                values.append(line[4:].strip())
            continue
        current_list = None
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        data[key] = value
        if not value:
            data[key] = []
            current_list = key

    return data, body


def main() -> int:
    files = {path.name: path for path in AGENT_DIR.glob("*.agent.md")}
    missing = sorted(REQUIRED_FILES - files.keys())
    findings: list[str] = [f"missing required agent profile: {name}" for name in missing]

    for name, path in sorted(files.items()):
        try:
            frontmatter, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            findings.append(f"{name}: {exc}")
            continue

        absent = sorted(REQUIRED_KEYS - frontmatter.keys())
        if absent:
            findings.append(f"{name}: missing frontmatter keys: {', '.join(absent)}")

        tools = frontmatter.get("tools")
        if not isinstance(tools, list) or not tools:
            findings.append(f"{name}: tools must be a non-empty YAML list")

        if "AGENT_STATE.md" not in body:
            findings.append(f"{name}: body must instruct the agent to read AGENT_STATE.md")

    if findings:
        for finding in findings:
            print(f"[error] {finding}")
        return 2

    print(f"Agent profiles: {len(files)} valid; required ClinicOps agents present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
