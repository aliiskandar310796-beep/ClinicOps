from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INTAKE = DOCS / "assessment-intake.html"

DEEPLINK_RE = re.compile(
    r"assessment-intake\.html\?workstream=([A-Za-z0-9_-]+)"
)
PRESET_RE = re.compile(r'data-preset="([A-Za-z0-9_-]+)"')


def test_every_public_workstream_deeplink_has_an_intake_preset() -> None:
    intake_html = INTAKE.read_text(encoding="utf-8")
    presets = set(PRESET_RE.findall(intake_html))

    assert presets, "assessment intake must declare at least one data-preset"

    deep_links: dict[str, set[str]] = {}
    for page in DOCS.rglob("*.html"):
        html = page.read_text(encoding="utf-8")
        for preset in DEEPLINK_RE.findall(html):
            deep_links.setdefault(preset, set()).add(page.relative_to(ROOT).as_posix())

    assert deep_links, "expected at least one public assessment-intake workstream deep link"

    unsupported = {
        preset: sorted(paths)
        for preset, paths in sorted(deep_links.items())
        if preset not in presets
    }
    assert not unsupported, (
        "public assessment-intake deep links must resolve to declared data-preset values: "
        f"{unsupported}"
    )


def test_intake_preset_identifiers_are_unique() -> None:
    intake_html = INTAKE.read_text(encoding="utf-8")
    presets = PRESET_RE.findall(intake_html)
    assert len(presets) == len(set(presets)), "data-preset identifiers must be unique"


def test_denmark_market_access_deeplink_is_supported() -> None:
    intake_html = INTAKE.read_text(encoding="utf-8")
    assert 'data-preset="denmark-market-access"' in intake_html
    assert "Denmark Market Access &amp; Localisation" in intake_html
