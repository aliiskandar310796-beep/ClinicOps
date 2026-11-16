from __future__ import annotations

import argparse
import json
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ops_common import (
    USER_AGENT,
    UnsafeXMLError,
    safe_parse_xml,
    strip_ns,
)

BASE_URL = "https://clinicops.dk/"
DOMAIN = "clinicops.dk"
TIMEOUT_SECONDS = 15
REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_SITEMAP = REPO_ROOT / "docs" / "sitemap.xml"

# Published GitHub Pages apex addresses (GitHub Docs: "Managing a custom domain
# for your GitHub Pages site").
GITHUB_PAGES_IPS = frozenset(
    {"185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"}
)
MIN_CERT_DAYS = 14
SITEMAP_CEILING = 48  # tests/test_strategic_invariants.py
DKIM_SELECTORS = ("selector1", "selector2")  # Microsoft 365 custom-domain selectors
DOH_URL = "https://dns.google/resolve"


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
    Target("/services", 200, "<title>Solution: Regulatory Change Integrity Review | ClinicOps</title>"),
    Target(
        "/denmark-market-access",
        200,
        "<title>Denmark Reference: Clinical Trial and Device Study Routes | ClinicOps</title>",
    ),
    Target(
        "/integrity-gate",
        200,
        "<title>Regulatory Integrity Review for MedTech | ClinicOps</title>",
    ),
    Target(
        "/assessment-intake",
        200,
        "<title>Scope a ClinicOps Review | ClinicOps</title>",
    ),
    Target("/tools", 200, "<title>Tools: Integrity Scanner and Evidence Utilities | ClinicOps</title>"),
    Target(
        "/identifier-check",
        200,
        "<title>EUDAMED Identifier Check | ClinicOps</title>",
    ),
    Target(
        "/readiness-score",
        200,
        "<title>Transition Readiness Score | ClinicOps</title>",
    ),
    Target(
        "/transition-map-sample/",
        200,
        "ClinicOps Class III Transition Map — Sanitized Sample",
    ),
    Target(
        "/expert-network",
        200,
        "<title>Working with partners | ClinicOps</title>",
    ),
    Target(
        "/expert-network-interest",
        200,
        "<title>Specialist Expression of Interest | ClinicOps</title>",
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
        "Monthly monitoring of the public EUDAMED record",
    ),
    Target("/clinical-operations-workflow-map", 200, "<title>Clinical operations workflow map | ClinicOps</title>"),
    Target("/ecoa-workflow", 200, "<title>eCOA workflow map from decision to close-out | ClinicOps</title>"),
    Target("/da/", 200, "<title>ClinicOps | "),
    Target("/feed.xml", 200, "<feed xmlns=\"http://www.w3.org/2005/Atom\""),
    Target("/regulatory-dates.ics", 200, "BEGIN:VCALENDAR"),
    Target("/llms.txt", 200, "ClinicOps"),
    Target("/downloads/clinicops-terminology-governance-v1.0.csv", 200, "Change log"),
    Target(
        "/about",
        200,
        "<title>About ClinicOps | EU MedTech Regulatory Data Integrity</title>",
    ),
    Target(
        "/authorised-representative-portfolio-intelligence",
        200,
        "<title>EU Authorised Representative Portfolio Intelligence | ClinicOps</title>",
    ),
    Target(
        "/change-surface-mapper",
        200,
        "<title>Change Surface Mapper | ClinicOps</title>",
    ),
    Target(
        "/class-iii-transition",
        200,
        "<title>Class III and Implantable MDR Transition Intelligence | ClinicOps</title>",
    ),
    Target(
        "/contact",
        200,
        "<title>Contact ClinicOps | EU MedTech Regulatory Data Integrity</title>",
    ),
    Target(
        "/eu-mdr-regulatory-integrity",
        200,
        "<title>EU MDR Regulatory Data Integrity for Global MedTech | ClinicOps</title>",
    ),
    Target(
        "/eudamed-transition",
        200,
        "<title>EUDAMED registration date 28 Nov 2026: work plan | ClinicOps</title>",
    ),
    Target(
        "/evidence-change-control-pack",
        200,
        "<title>Regulatory Change Integrity Review | ClinicOps</title>",
    ),
    Target(
        "/integrity-scanner",
        200,
        "<title>Regulatory Integrity Scanner | ClinicOps</title>",
    ),
    Target(
        "/use-cases",
        200,
        "<title>Use Cases: EUDAMED, SS(C)P, AR Portfolios, Denmark | ClinicOps</title>",
    ),
    Target(
        "/integrity-check",
        200,
        "<title>Free Regulatory Change Integrity Check | ClinicOps</title>",
    ),
    Target(
        "/integrity-economics",
        200,
        "<title>Regulatory Change Review Cost Calculator | ClinicOps</title>",
    ),
    Target(
        "/medical-device-document-control",
        200,
        "<title>Medical Device Regulatory Document Control | ClinicOps</title>",
    ),
    Target(
        "/primary-sources",
        200,
        "<title>Primary Public Sources | ClinicOps</title>",
    ),
    Target(
        "/regulatory-change-impact",
        200,
        "<title>Regulatory Change Impact Mapper | ClinicOps</title>",
    ),
    Target(
        "/regulatory-intelligence",
        200,
        "<title>EU Medical Device Regulatory Intelligence | ClinicOps</title>",
    ),
    Target(
        "/research",
        200,
        "<title>Research & Methodology | ClinicOps</title>",
    ),
    Target(
        "/specimen-register/",
        200,
        "<title>Interactive Regulatory Integrity Specimen Register | ClinicOps</title>",
    ),
    Target(
        "/sscp-operations",
        200,
        "<title>SS(C)P operations explained: who does what | ClinicOps</title>",
    ),
    Target(
        "/technical-file-consistency",
        200,
        "<title>Technical File Consistency Check | ClinicOps</title>",
    ),
    Target("/sitemap.xml", 200, "https://clinicops.dk/assessment-intake"),
    Target("/robots.txt", 200, "Sitemap: https://clinicops.dk/sitemap.xml"),
    Target(
        "/__clinicops_healthcheck_missing__.html",
        404,
        "That page moved or never existed.",
    ),
    Target("/.well-known/security.txt", 200, "Contact: mailto:info@clinicops.dk"),
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


# ---------------------------------------------------------------------------
# Weekly "full" checks (DNS, TLS expiry, sitemap, security.txt).
#
# Enabled only with --full so the post-deploy smoke in pages.yml keeps its
# original meaning (is the freshly deployed site up?). The weekly Ops Watch job
# runs --full: it is a drift alarm for the things GitHub Pages cannot tell us.
# ---------------------------------------------------------------------------

OK, WARN, FAIL = "ok", "warn", "fail"


@dataclass(frozen=True)
class Finding:
    severity: str  # "ok" | "warn" | "fail"
    check: str
    message: str


class DnsLookupError(RuntimeError):
    """The DoH service itself failed (not a statement about our records)."""


# A lookup takes (name, rtype) and returns the answer data strings of that type.
Lookup = Callable[[str, str], list[str]]

_RTYPE_CODES = {"A": 1, "CNAME": 5, "TXT": 16, "AAAA": 28}


def clean_txt(data: str) -> str:
    """DoH may quote TXT data, splitting long records into several quoted chunks."""
    chunks = re.findall(r'"((?:[^"\\]|\\.)*)"', data)
    return "".join(chunks) if chunks else data


def parse_doh_answers(payload: dict, rtype: str) -> list[str]:
    status = payload.get("Status")
    if status == 3:  # NXDOMAIN
        return []
    if status != 0:
        raise DnsLookupError(f"DoH status {status}")
    code = _RTYPE_CODES[rtype]
    out = []
    for answer in payload.get("Answer") or []:
        if answer.get("type") != code:
            continue
        data = str(answer.get("data", ""))
        out.append(clean_txt(data) if rtype == "TXT" else data.rstrip("."))
    return out


def doh_lookup(name: str, rtype: str) -> list[str]:
    """Public DNS-over-HTTPS JSON lookup (dns.google). CI use only."""
    query = urllib.parse.urlencode({"name": name, "type": rtype})
    req = urllib.request.Request(f"{DOH_URL}?{query}")
    req.add_header("Accept", "application/dns-json")
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise DnsLookupError(f"{name} {rtype}: {exc}") from exc
    return parse_doh_answers(payload, rtype)


def check_dns(
    lookup: Lookup,
    domain: str = DOMAIN,
    dkim_severity: str = WARN,
    attempts: int = 3,
    sleep: Callable[[float], None] = time.sleep,
) -> list[Finding]:
    """DNS drift checks. A lookup-service outage is a warning, never a site failure."""
    findings: list[Finding] = []

    def safe(name: str, rtype: str) -> list[str] | None:
        try:
            return lookup(name, rtype)
        except DnsLookupError as exc:
            findings.append(Finding(WARN, "dns-lookup", f"lookup unavailable, check skipped: {exc}"))
            return None

    # Apex A: must be exactly the GitHub Pages addresses. One early manual
    # lookup (lens 30) returned unrelated addresses that three later lookups did
    # not repeat, so fail only if every one of `attempts` lookups disagrees.
    last: list[str] | None = None
    for attempt in range(attempts):
        answers = safe(domain, "A")
        if answers is None:
            last = None
            break
        last = sorted(answers)
        if last and set(last) <= GITHUB_PAGES_IPS:
            break
        if attempt < attempts - 1:
            sleep(5)
    if last is not None:
        if not last or not set(last) <= GITHUB_PAGES_IPS:
            findings.append(
                Finding(FAIL, "dns-apex-a", f"apex A records {last or 'missing'} are not GitHub Pages addresses")
            )
        elif set(last) != GITHUB_PAGES_IPS:
            missing = sorted(GITHUB_PAGES_IPS - set(last))
            findings.append(Finding(WARN, "dns-apex-a", f"apex A records are GitHub Pages but {missing} missing"))
        else:
            findings.append(Finding(OK, "dns-apex-a", "apex A records are the four GitHub Pages addresses"))

    cname = safe(f"www.{domain}", "CNAME")
    if cname is not None:
        if not cname:
            findings.append(Finding(FAIL, "dns-www-cname", f"www.{domain} has no CNAME record"))
        elif not cname[0].lower().endswith(".github.io"):
            findings.append(Finding(WARN, "dns-www-cname", f"www CNAME points to {cname[0]}, not a github.io host"))
        else:
            findings.append(Finding(OK, "dns-www-cname", "www CNAME present"))

    txt = safe(domain, "TXT")
    if txt is not None:
        spf = [t for t in txt if t.lower().startswith("v=spf1")]
        if len(spf) == 1:
            findings.append(Finding(OK, "dns-spf", "single SPF record present"))
        elif not spf:
            findings.append(Finding(FAIL, "dns-spf", "no SPF record at the apex"))
        else:
            findings.append(Finding(FAIL, "dns-spf", f"{len(spf)} SPF records at the apex (must be exactly one)"))

    dmarc = safe(f"_dmarc.{domain}", "TXT")
    if dmarc is not None:
        records = [t for t in dmarc if t.upper().startswith("V=DMARC1")]
        if records:
            findings.append(Finding(OK, "dns-dmarc", "DMARC record present"))
        else:
            findings.append(Finding(FAIL, "dns-dmarc", f"no DMARC record at _dmarc.{domain}"))

    for selector in DKIM_SELECTORS:
        name = f"{selector}._domainkey.{domain}"
        found = safe(name, "CNAME")
        if found is None:
            continue
        if not found:
            txt_found = safe(name, "TXT") or []
            found = [t for t in txt_found if "v=DKIM1" in t]
        if found:
            findings.append(Finding(OK, f"dns-dkim-{selector}", f"{selector} DKIM record present"))
        else:
            findings.append(
                Finding(
                    dkim_severity,
                    f"dns-dkim-{selector}",
                    f"{name} not published (Microsoft 365 DKIM signing not enabled; founder action)",
                )
            )
    return findings


def fetch_cert_not_after(host: str = DOMAIN, port: int = 443) -> datetime:
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    with (
        socket.create_connection((host, port), timeout=TIMEOUT_SECONDS) as sock,
        ctx.wrap_socket(sock, server_hostname=host) as tls,
    ):
        cert = tls.getpeercert()
    return datetime.fromtimestamp(ssl.cert_time_to_seconds(cert["notAfter"]), tz=UTC)


def check_tls_expiry(
    not_after: datetime | None, now: datetime, min_days: int = MIN_CERT_DAYS, error: str | None = None
) -> Finding:
    if not_after is None:
        return Finding(FAIL, "tls-expiry", f"could not read the TLS certificate: {error}")
    days = (not_after - now).days
    if days <= min_days:
        return Finding(FAIL, "tls-expiry", f"certificate expires in {days} days (limit {min_days}); renewal not happening")
    return Finding(OK, "tls-expiry", f"certificate valid for {days} more days")


def sitemap_locs(xml_text: str) -> list[str]:
    root = safe_parse_xml(xml_text)
    return [
        (el.text or "").strip()
        for el in root.iter()
        if strip_ns(el.tag) == "loc" and (el.text or "").strip()
    ]


def check_sitemap(live_xml: str, local_xml: str, ceiling: int = SITEMAP_CEILING) -> Finding:
    try:
        live, local = sitemap_locs(live_xml), sitemap_locs(local_xml)
    except UnsafeXMLError as exc:
        return Finding(FAIL, "sitemap", f"sitemap is not safe, well-formed XML: {exc}")
    if len(live) > ceiling:
        return Finding(FAIL, "sitemap", f"live sitemap has {len(live)} URLs, ceiling is {ceiling}")
    if len(live) != len(local):
        extra, gone = sorted(set(live) - set(local)), sorted(set(local) - set(live))
        return Finding(
            FAIL,
            "sitemap",
            f"live sitemap has {len(live)} URLs, docs/sitemap.xml has {len(local)} "
            f"(only live: {extra[:5]}; only repo: {gone[:5]})",
        )
    return Finding(OK, "sitemap", f"{len(live)} URLs, matches docs/sitemap.xml, within ceiling {ceiling}")


def check_security_txt(status: int | None, text: str, today: date) -> Finding:
    # WARN, not FAIL: actions/upload-pages-artifact omits dotfiles/dot-directories
    # (unverified for the pinned v5), so docs/.well-known may need a deploy change
    # before this can pass. Promote to fail once it has been seen passing.
    if status != 200:
        return Finding(WARN, "security-txt", f"/.well-known/security.txt returned {status}")
    fields = {}
    for line in text.splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, value = line.split(":", 1)
            fields.setdefault(key.strip().lower(), value.strip())
    if "contact" not in fields:
        return Finding(WARN, "security-txt", "security.txt has no Contact field")
    expires = fields.get("expires")
    if not expires:
        return Finding(WARN, "security-txt", "security.txt has no Expires field")
    try:
        expiry = datetime.fromisoformat(expires).date()
    except ValueError:
        return Finding(WARN, "security-txt", f"Expires is not an ISO 8601 date: {expires}")
    if expiry < today:
        return Finding(FAIL, "security-txt", f"security.txt expired on {expiry.isoformat()}")
    return Finding(OK, "security-txt", f"security.txt present, expires {expiry.isoformat()}")


def run_full_checks(session: requests.Session, dkim_severity: str = WARN) -> list[Finding]:
    findings = check_dns(doh_lookup, dkim_severity=dkim_severity)

    try:
        findings.append(check_tls_expiry(fetch_cert_not_after(), datetime.now(UTC)))
    except (OSError, ssl.SSLError, KeyError) as exc:
        findings.append(check_tls_expiry(None, datetime.now(UTC), error=str(exc)))

    try:
        live = session.get(urljoin(BASE_URL, "sitemap.xml"), timeout=TIMEOUT_SECONDS)
        findings.append(check_sitemap(live.text, LOCAL_SITEMAP.read_text(encoding="utf-8")))
    except requests.RequestException as exc:
        findings.append(Finding(FAIL, "sitemap", f"could not fetch live sitemap: {exc}"))

    try:
        resp = session.get(urljoin(BASE_URL, ".well-known/security.txt"), timeout=TIMEOUT_SECONDS)
        findings.append(check_security_txt(resp.status_code, resp.text, datetime.now(UTC).date()))
    except requests.RequestException as exc:
        findings.append(Finding(WARN, "security-txt", f"could not fetch security.txt: {exc}"))
    return findings


def build_report(http_failures: list[str], findings: list[Finding], generated: str) -> dict:
    items = [Finding(FAIL, "http", msg) for msg in http_failures] + findings
    return {
        "generated": generated,
        "failures": [asdict(f) for f in items if f.severity == FAIL],
        "warnings": [asdict(f) for f in items if f.severity == WARN],
        "ok": [asdict(f) for f in items if f.severity == OK],
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="also run DNS, TLS expiry, sitemap and security.txt checks")
    parser.add_argument("--report", help="write the machine-readable findings report to this path")
    parser.add_argument("--dkim-severity", choices=(WARN, FAIL), default=WARN)
    args = parser.parse_args(argv)

    results: list[Result] = []
    failures: list[str] = []
    findings: list[Finding] = []
    with requests.Session() as session:
        session.headers["User-Agent"] = "ClinicOps-Ops-Watch/1.0"
        for target in TARGETS:
            try:
                results.append(check_target(session, target))
            except requests.RequestException as exc:
                failures.append(f"{target.path}: request failed: {exc}")
            except RuntimeError as exc:
                failures.append(str(exc))
        if args.full:
            findings = run_full_checks(session, args.dkim_severity)

    report = build_report(failures, findings, datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ"))
    print(
        json.dumps(
            {
                "base_url": BASE_URL,
                "results": [asdict(result) for result in results],
                "failures": failures,
                "findings": report,
            },
            indent=2,
        )
    )
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
