from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from time import perf_counter

import requests

ENDPOINT = "https://ec.europa.eu/tools/eudamed/api/devices/udiDiData"


@dataclass(frozen=True)
class Probe:
    page: int
    requested_page_size: int
    ok: bool
    status_code: int | None
    elapsed_seconds: float
    returned_items: int | None
    total_elements: int | None
    error: str | None


def probe(page: int, page_size: int = 50, timeout: float = 25.0) -> Probe:
    """Run one operational reachability probe against the public device route."""
    started = perf_counter()
    try:
        response = requests.get(
            ENDPOINT,
            params={
                "page": page,
                "pageSize": page_size,
                "size": page_size,
                "iso2Code": "en",
                "languageIso2Code": "en",
            },
            timeout=timeout,
            headers={"User-Agent": "ClinicOps-eudamed-canary/0.1"},
        )
        elapsed = perf_counter() - started
        response.raise_for_status()
        data = response.json()
        content = data.get("content") if isinstance(data, dict) else None
        return Probe(
            page=page,
            requested_page_size=page_size,
            ok=True,
            status_code=response.status_code,
            elapsed_seconds=round(elapsed, 3),
            returned_items=len(content) if isinstance(content, list) else None,
            total_elements=data.get("totalElements") if isinstance(data, dict) else None,
            error=None,
        )
    except (requests.RequestException, ValueError) as exc:
        elapsed = perf_counter() - started
        status = getattr(getattr(exc, "response", None), "status_code", None)
        return Probe(
            page=page,
            requested_page_size=page_size,
            ok=False,
            status_code=status,
            elapsed_seconds=round(elapsed, 3),
            returned_items=None,
            total_elements=None,
            error=f"{type(exc).__name__}: {exc}",
        )


def build_snapshot(
    probes: list[Probe],
    *,
    captured_at: datetime | None = None,
) -> dict[str, object]:
    """Build the stable JSON contract used for longitudinal API observations."""
    captured = captured_at or datetime.now(UTC)
    if captured.tzinfo is None:
        raise ValueError("captured_at must be timezone-aware")
    return {
        "captured_at_utc": captured.astimezone(UTC).isoformat(),
        "endpoint": ENDPOINT,
        "interpretation": (
            "Operational reachability canary only. These probes do not establish "
            "full-register coverage, population counts, or regulatory status."
        ),
        "probes": [asdict(item) for item in probes],
    }
