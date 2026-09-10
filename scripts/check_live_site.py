from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from urllib.parse import urljoin, urlparse

import requests

BASE_URL = "https://clinicops.dk/"
TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class Target:
    path: str
    expected_status: int
    marker: str


@dataclass(frozen=True)
class Result:
    path: str
    status: int
    final_url: str
    marker_found: bool


TARGETS = (
    Target("/", 200, "Turn EUDAMED transition evidence into an actionable work plan."),
    Target("/tools.html", 200, "Free intelligence tools"),
    Target("/readiness-score.html", 200, "Transition Readiness Score"),
    Target(
        "/transition-map-sample/",
        200,
        "ClinicOps Class III Transition Map — Sanitized Sample",
    ),
    Target("/sitemap.xml", 200, "https://clinicops.dk/transition-map-sample/"),
    Target("/robots.txt", 200, "Sitemap: https://clinicops.dk/sitemap.xml"),
    Target(
        "/__clinicops_healthcheck_missing__.html",
        404,
        "That page moved or never existed.",
    ),
)


def check_target(session: requests.Session, target: Target) -> Result:
    url = urljoin(BASE_URL, target.path.lstrip("/"))
    response = session.get(url, timeout=TIMEOUT_SECONDS, allow_redirects=True)
    final = urlparse(response.url)

    if final.scheme != "https":
        raise RuntimeError(f"{target.path}: final URL is not HTTPS: {response.url}")
    if final.hostname not in {"clinicops.dk", "www.clinicops.dk"}:
        raise RuntimeError(f"{target.path}: unexpected final host: {final.hostname}")
    if response.status_code != target.expected_status:
        raise RuntimeError(
            f"{target.path}: HTTP {response.status_code}, expected {target.expected_status}"
        )

    marker_found = target.marker in response.text
    if not marker_found:
        raise RuntimeError(f"{target.path}: expected content marker not found")

    return Result(
        path=target.path,
        status=response.status_code,
        final_url=response.url,
        marker_found=marker_found,
    )


def main() -> None:
    results: list[Result] = []
    failures: list[str] = []
    with requests.Session() as session:
        session.headers["User-Agent"] = "ClinicOps-Ops-Watch/1.0"
        for target in TARGETS:
            try:
                results.append(check_target(session, target))
            except requests.RequestException as exc:
                failures.append(f"{target.path}: request failed: {exc}")
            except RuntimeError as exc:
                failures.append(str(exc))

    print(
        json.dumps(
            {
                "base_url": BASE_URL,
                "results": [asdict(result) for result in results],
                "failures": failures,
            },
            indent=2,
        )
    )
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
