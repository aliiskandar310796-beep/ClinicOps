from __future__ import annotations

from pathlib import Path

PAGE = Path("docs/change-surface-mapper.html")

REQUIRED_MARKERS = (
    'id="workstream"',
    'id="change-title"',
    'id="source-ref"',
    'id="change-summary"',
    'id="surfaces"',
    'id="download"',
    'id="scope"',
    'schema_version:"1.0"',
    '"regulatory-integrity"',
    'trialops',
    'qualityops',
    '"clinical-ai"',
    'labops',
    '"clinic-ops"',
    '"medical-content"',
    'evidence-change-control-pack.html',
    'assessment-intake.html',
    'Nothing has been sent or uploaded.',
)

FORBIDDEN_NETWORK_MARKERS = (
    "fetch(",
    "XMLHttpRequest",
    "WebSocket",
    "sendBeacon",
    "google-analytics",
    "gtag(",
    "segment.com",
    "mixpanel",
)


def main() -> int:
    text = PAGE.read_text(encoding="utf-8")
    findings: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            findings.append(f"missing mapper contract marker: {marker}")

    for marker in FORBIDDEN_NETWORK_MARKERS:
        if marker in text:
            findings.append(f"browser-local mapper contains forbidden network/telemetry marker: {marker}")

    if '<form id="mapper"' not in text or "action=" in text.split('<form id="mapper"', 1)[1].split(">", 1)[0]:
        findings.append("mapper form must not declare a network form action")

    if "compliance" not in text.lower() or "qualified" not in text.lower():
        findings.append("mapper must preserve explicit professional decision boundary")

    if findings:
        for finding in findings:
            print(f"[error] {finding}")
        return 2

    print("Change Surface Mapper contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
