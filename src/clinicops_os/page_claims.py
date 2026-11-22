"""Claim gate over the HTML that is actually served.

Pages declare the registry claims they rely on with paired comments:

    <!-- claim-use: website -->
    <!-- claim-ids: CO-CLM-0004, CO-CLM-0020 -->

A page may carry several pairs; every pair is read. Every id found anywhere in
a served file must be declared and must pass the registry gate for the declared
use. A ratchet lists pages that name a regulation but declare no claims.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .claim_registry import RegistryClaim

DECLARATION_RE = re.compile(r"<!--\s*claim-(use|ids):\s*([^>]*?)\s*-->", re.IGNORECASE)
REF_RE = re.compile(r"CO-CLM-\d{4}")
# A research note is a published use; it is only allowed on the research pages.
PAGE_USES = ("website", "research-note")
RESEARCH_PREFIX = "docs/research/"

# Names of regulations and guidance sets. Case-sensitive on purpose: the
# acronyms are matched as written, so ordinary words never hit.
REGULATION_RE = re.compile(
    r"\b(?:MDR|IVDR|EUDAMED|CTIS|MDCG|GVP|ICH|GCP|FDA|CTR)\b"
    r"|Regulation \(EU\)|Directive \d|Directive \(EU\)|Implementing Regulation"
)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
STYLE_RE = re.compile(r"<style\b.*?</style>", re.DOTALL | re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
BODY_RE = re.compile(r"<body\b", re.IGNORECASE)
UNGOVERNED_SKIP = {"docs/404.html"}


@dataclass(frozen=True)
class Declaration:
    use: str | None
    ids: tuple[str, ...]


def parse_declarations(text: str) -> list[Declaration]:
    """Every claim-use / claim-ids pair in document order."""
    declarations: list[Declaration] = []
    pending: str | None = None
    for match in DECLARATION_RE.finditer(text):
        kind, value = match.group(1).lower(), match.group(2).strip()
        if kind == "use":
            if pending is not None:
                declarations.append(Declaration(pending, ()))
            pending = value.lower()
        else:
            ids = tuple(item.strip() for item in value.split(",") if item.strip())
            declarations.append(Declaration(pending, ids))
            pending = None
    if pending is not None:
        declarations.append(Declaration(pending, ()))
    return declarations


def declared_ids(text: str) -> set[str]:
    return {claim_id for decl in parse_declarations(text) for claim_id in decl.ids}


def iter_public_files(root: Path) -> Iterator[Path]:
    docs = root / "docs"
    yield from sorted(docs.rglob("*.html"))
    yield from sorted((docs / "assets").glob("*-data.js"))


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _gate(
    claim_ids: tuple[str, ...],
    use: str,
    by_id: dict[str, RegistryClaim],
    as_of: date,
    label: str,
) -> list[str]:
    problems: list[str] = []
    for claim_id in claim_ids:
        claim = by_id.get(claim_id)
        if claim is None:
            problems.append(f"{label}: {claim_id}: not found in registry")
            continue
        for reason in claim.gate(use, as_of):
            problems.append(f"{label}: {claim_id}: {reason}")
    return problems


def scan_text(
    rel: str,
    text: str,
    registry: list[RegistryClaim],
    as_of: date,
    *,
    uses: tuple[str, ...] | None = PAGE_USES,
    research_prefix: str = RESEARCH_PREFIX,
) -> list[str]:
    """Gate one file. `uses` limits the claim-use values a file may declare (None
    accepts any registry use, as the markdown pipeline always did) and
    `research_prefix` is where research-note use is allowed."""
    by_id = {claim.claim_id: claim for claim in registry}
    referenced = set(REF_RE.findall(text))
    declarations = parse_declarations(text)
    problems: list[str] = []

    if rel.endswith(".js"):
        problems.extend(_gate(tuple(sorted(referenced)), "website", by_id, as_of, rel))
        return problems

    if not declarations:
        if referenced:
            problems.append(
                f"{rel}: cites {', '.join(sorted(referenced))} but declares no claim-use "
                "or claim-ids"
            )
        return problems

    declared: set[str] = set()
    for decl in declarations:
        if decl.use is None or not decl.ids:
            problems.append(f"{rel}: claim-use and claim-ids metadata must appear together")
            continue
        declared.update(decl.ids)
        if uses is not None and decl.use not in uses:
            problems.append(f"{rel}: unsupported claim-use {decl.use!r}")
            continue
        if decl.use == "research-note" and not rel.startswith(research_prefix):
            problems.append(
                f"{rel}: claim-use research-note is only allowed under {research_prefix}"
            )
            continue
        problems.extend(_gate(decl.ids, decl.use, by_id, as_of, rel))

    undeclared = referenced - declared
    if undeclared:
        problems.append(
            f"{rel}: referenced but undeclared claim IDs: {', '.join(sorted(undeclared))}"
        )
    return problems


def scan_public_files(
    root: Path, registry: list[RegistryClaim], *, as_of: date
) -> list[str]:
    problems: list[str] = []
    for path in iter_public_files(root):
        text = path.read_text(encoding="utf-8")
        problems.extend(scan_text(_relative(root, path), text, registry, as_of))
    return problems


def _page_text(html: str) -> str:
    match = BODY_RE.search(html)
    body = html[match.start() :] if match else html
    body = COMMENT_RE.sub(" ", body)
    body = STYLE_RE.sub(" ", body)
    return TAG_RE.sub(" ", body)


def ungoverned_pages(root: Path) -> dict[str, list[str]]:
    """Pages that name a regulation but declare no claim ids (ratchet input)."""
    flagged: dict[str, list[str]] = {}
    for path in sorted((root / "docs").rglob("*.html")):
        rel = _relative(root, path)
        if rel in UNGOVERNED_SKIP:
            continue
        html = path.read_text(encoding="utf-8")
        if declared_ids(html):
            continue
        terms = sorted(set(REGULATION_RE.findall(_page_text(html))))
        if terms:
            flagged[rel] = terms
    return flagged


def read_allowlist(path: Path) -> dict[str, str]:
    allowed: dict[str, str] = {}
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        page, sep, reason = (part.strip() for part in line.partition("|"))
        if not sep or not reason:
            raise ValueError(f"{path.name}:{number}: every entry needs a reason after '|'")
        allowed[page] = reason
    return allowed
