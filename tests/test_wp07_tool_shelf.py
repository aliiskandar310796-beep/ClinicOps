from __future__ import annotations

import re
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"

# Target by end of Wave 2 is 12 or fewer listed tools; the ceiling ratchets down.
LISTED_TOOL_CEILING = 13
ARCHIVED = ("readiness-score", "integrity-economics")


def _listed_tools() -> set[str]:
    html = (DOCS / "tools.html").read_text(encoding="utf-8")
    main = html.split("<main", 1)[1].split("</main>", 1)[0]
    links = re.findall(r'<a href="([a-z0-9-]+(?:/)?)"', main)
    tool_pages = {p.stem for p in DOCS.glob("*.html")} | {"specimen-register/", "transition-map-sample/"}
    skip = {"specimen-register", "transition-map-sample", "tools", "ecoa", "services", "evidence-change-control-pack", "contact", "about", "assessment-intake"}
    return {l.rstrip("/") for l in links if (l in tool_pages or l.rstrip("/") in tool_pages) and l.rstrip("/") not in skip}


def test_archived_tools_are_not_listed_but_stay_reachable_with_a_note() -> None:
    listed = _listed_tools()
    for slug in ARCHIVED:
        assert slug not in listed, slug
        html = (DOCS / f"{slug}.html").read_text(encoding="utf-8")
        assert "No longer listed." in html, slug


def test_listed_tool_count_stays_under_the_ceiling() -> None:
    assert len(_listed_tools()) <= LISTED_TOOL_CEILING, sorted(_listed_tools())
