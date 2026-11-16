"""Shared, stdlib-only helpers for the ops-watch and regulatory-watch automation.

Two things live here so both watchers behave the same way:

* ``safe_parse_xml``: parse untrusted XML (a regulator feed, our own live
  sitemap) without ever expanding entities.
* ``GitHubIssues``: a very small GitHub REST client used only to open, update,
  comment on and close Issues. It never touches repository contents, so no
  watcher can edit a claim, stamp or page.

CI code only. Nothing here is imported by the public site.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any

MAX_XML_BYTES = 2_000_000
USER_AGENT = "ClinicOps-Ops-Watch/1.0 (+https://clinicops.dk/contact; low-frequency read-only monitor)"

_DANGEROUS_XML = re.compile(rb"<!\s*(DOCTYPE|ENTITY)", re.IGNORECASE)


class UnsafeXMLError(ValueError):
    """Raised when a document is oversized or declares a DTD or entities."""


def safe_parse_xml(payload: bytes | str) -> ET.Element:
    """Parse XML, refusing any DOCTYPE/ENTITY declaration and oversized input.

    ElementTree does not resolve external entities, but internal entity
    expansion ("billion laughs") is still possible, and a feed or sitemap has no
    legitimate reason to carry a DTD.
    """
    data = payload.encode("utf-8") if isinstance(payload, str) else payload
    if len(data) > MAX_XML_BYTES:
        raise UnsafeXMLError(f"XML larger than {MAX_XML_BYTES} bytes")
    if _DANGEROUS_XML.search(data):
        raise UnsafeXMLError("XML declares a DOCTYPE or ENTITY; refusing to parse")
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise UnsafeXMLError(f"XML parse error: {exc}") from exc


def strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


class GitHubError(RuntimeError):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(f"GitHub API {status}: {message}")
        self.status = status


class GitHubIssues:
    """Issues-only GitHub REST client (token from the workflow, never printed)."""

    def __init__(self, repo: str, token: str, api_url: str = "https://api.github.com") -> None:
        self.repo = repo
        self._token = token
        self.api_url = api_url.rstrip("/")

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        url = f"{self.api_url}/repos/{self.repo}{path}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self._token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        req.add_header("User-Agent", USER_AGENT)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
        except urllib.error.HTTPError as exc:
            raise GitHubError(exc.code, exc.read().decode("utf-8", "replace")[:300]) from exc
        return json.loads(body) if body else None


def ensure_label(api: Any, name: str, color: str, description: str) -> None:
    try:
        api.request("POST", "/labels", {"name": name, "color": color, "description": description})
    except GitHubError as exc:
        if exc.status != 422:  # 422 = label already exists
            raise


def list_issues(api: Any, label: str, state: str = "open", limit_pages: int = 3) -> list[dict[str, Any]]:
    """Issues (never pull requests) carrying ``label``."""
    found: list[dict[str, Any]] = []
    for page in range(1, limit_pages + 1):
        batch = api.request(
            "GET", f"/issues?labels={label}&state={state}&per_page=100&page={page}"
        )
        if not batch:
            break
        found.extend(i for i in batch if "pull_request" not in i)
        if len(batch) < 100:
            break
    return found
