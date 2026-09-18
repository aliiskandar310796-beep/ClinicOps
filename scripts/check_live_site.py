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


# Markers are stable page-identity strings (title/canonical fragments), not
# promotional sentences: copy changes should not break the health check unless
# the page's identity actually changed.
TARGETS = (
    Target("/", 200, "<title>ClinicOps | "),
    Target("/services.html", 200, "<title>Solution | ClinicOps</title>"),
    Target(
        "/denmark-market-access.html",
        200,
        "<title>Denmark Market Access | ClinicOps</title>",
    ),
    Target(
        "/integrity-gate.html",
        200,
        "<title>Regulatory Integrity Review for MedTech | ClinicOps</title>",
    ),
    Target(
        "/assessment-intake.html",
        200,
        "<title>Scope a ClinicOps Review | ClinicOps</title>",
    ),
    Target("/tools.html", 200, "<title>Tools & Evidence | ClinicOps</title>"),
    Target(
        "/identifier-check.html",
        200,
        "<title>EUDAMED Identifier Check | ClinicOps</title>",
    ),
    Target(
        "/readiness-score.html",
        200,
        "<title>Transition Readiness Score | ClinicOps</title>",
    ),
    Target(
        "/transition-map-sample/",
        200,
        "ClinicOps Class III Transition Map — Sanitized Sample",
    ),
    Target(
        "/expert-network.html",
        200,
        "<title>Independent Expert Network | ClinicOps</title>",
    ),
    Target("/privacy-notice/", 200, "<title>Privacy Notice | ClinicOps</title>"),
    Target(
        "/research/sscp-public-record-scan/",
        200,
        "The published SS(C)P and the public EUDAMED record",
    ),
    Target(
        "/research/eudamed-watch/",
        200,
        "Continuous monitoring of the public EUDAMED record",
    ),
    Target(
        "/about.html",
        200,
        "<title>About ClinicOps | Danish-Led, EU-Wide Clinical Operations</title>",
    ),
    Target(
        "/authorised-representative-portfolio-intelligence.html",
        200,
        "<title>EU Authorised Representative Portfolio Intelligence | ClinicOps</title>",
    ),
    Target(
        "/change-surface-mapper.html",
        200,
        "<title>Change Surface Mapper | ClinicOps</title>",
    ),
    Target(
        "/class-iii-transition.html",
        200,
        "<title>Class III and Implantable MDR Transition Intelligence | ClinicOps</title>",
    ),
    Target(
        "/contact.html",
        200,
        "<title>Contact ClinicOps | Danish-Led, EU-Wide Clinical Operations</title>",
    ),
    Target(
        "/eu-mdr-regulatory-integrity.html",
        200,
        "<title>EU MDR Regulatory Data Integrity for Global MedTech | ClinicOps</title>",
    ),
    Target(
        "/eudamed-transition.html",
        200,
        "<title>EUDAMED Transition Work Plans for MedTech | ClinicOps</title>",
    ),
    Target(
        "/evidence-change-control-pack.html",
        200,
        "<title>Regulatory Change Integrity Review | ClinicOps</title>",
    ),
    Target(
        "/integrity-scanner.html",
        200,
        "<title>Regulatory Integrity Scanner | ClinicOps</title>",
    ),
    Target(
        "/use-cases.html",
        200,
        "<title>Use Cases | ClinicOps</title>",
    ),
    Target(
        "/integrity-check.html",
        200,
        "<title>Free Regulatory Change Integrity Check | ClinicOps</title>",
    ),
    Target(
        "/integrity-economics.html",
        200,
        "<title>Regulatory Change Review Cost Calculator | ClinicOps</title>",
    ),
    Target(
        "/medical-device-document-control.html",
        200,
        "<title>Medical Device Regulatory Document Control | ClinicOps</title>",
    ),
    Target(
        "/primary-sources.html",
        200,
        "<title>Primary Public Sources | ClinicOps</title>",
    ),
    Target(
        "/regulatory-change-impact.html",
        200,
        "<title>Regulatory Change Impact Mapper | ClinicOps</title>",
    ),
    Target(
        "/regulatory-intelligence.html",
        200,
        "<title>EU Medical Device Regulatory Intelligence | ClinicOps</title>",
    ),
    Target(
        "/research.html",
        200,
        "<title>Research & Methodology | ClinicOps</title>",
    ),
    Target(
        "/specimen-register/",
        200,
        "<title>Interactive Regulatory Integrity Specimen Register | ClinicOps</title>",
    ),
    Target(
        "/sscp-operations.html",
        200,
        "<title>SS(C)P Operations and Evidence Workflows | ClinicOps</title>",
    ),
    Target(
        "/technical-file-consistency.html",
        200,
        "<title>Technical File Consistency Check | ClinicOps</title>",
    ),
    Target("/sitemap.xml", 200, "https://clinicops.dk/assessment-intake.html"),
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
