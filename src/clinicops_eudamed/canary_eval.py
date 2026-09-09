from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CanaryFinding:
    severity: str
    page: int | None
    message: str


def _by_page(snapshot: dict[str, object]) -> dict[int, dict[str, object]]:
    probes = snapshot.get("probes")
    if not isinstance(probes, list):
        return {}
    result: dict[int, dict[str, object]] = {}
    for probe in probes:
        if not isinstance(probe, dict):
            continue
        page = probe.get("page")
        if isinstance(page, int):
            result[page] = probe
    return result


def evaluate_snapshot(
    baseline: dict[str, object],
    latest: dict[str, object],
) -> list[CanaryFinding]:
    """Compare bounded canary behavior without treating API counts as a contract."""
    findings: list[CanaryFinding] = []

    if baseline.get("endpoint") != latest.get("endpoint"):
        findings.append(
            CanaryFinding("error", None, "canary endpoint changed from the reviewed baseline")
        )
        return findings

    expected = _by_page(baseline)
    observed = _by_page(latest)

    for page, prior in sorted(expected.items()):
        current = observed.get(page)
        if current is None:
            findings.append(CanaryFinding("error", page, "expected probe is missing"))
            continue

        prior_ok = prior.get("ok") is True
        current_ok = current.get("ok") is True
        if current_ok != prior_ok:
            severity = "error" if page == 0 and not current_ok else "warning"
            findings.append(
                CanaryFinding(
                    severity,
                    page,
                    f"reachability changed: baseline ok={prior_ok}, latest ok={current_ok}",
                )
            )

        prior_items = prior.get("returned_items")
        current_items = current.get("returned_items")
        if (
            current_ok
            and prior_ok
            and isinstance(prior_items, int)
            and isinstance(current_items, int)
            and current_items != prior_items
        ):
            findings.append(
                CanaryFinding(
                    "warning",
                    page,
                    f"returned item count changed: baseline {prior_items}, latest {current_items}",
                )
            )

    return findings


def has_errors(findings: list[CanaryFinding]) -> bool:
    return any(item.severity == "error" for item in findings)
