from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
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


def main() -> None:
    probes = [probe(0), probe(30_000), probe(32_000)]
    output = {
        "captured_at_utc": datetime.now(UTC).isoformat(),
        "endpoint": ENDPOINT,
        "interpretation": (
            "Operational reachability canary only. These probes do not establish "
            "full-register coverage, population counts, or regulatory status."
        ),
        "probes": [asdict(item) for item in probes],
    }
    path = Path("research/canary/latest.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
