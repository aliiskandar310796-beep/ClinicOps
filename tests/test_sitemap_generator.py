"""render_sitemap.py: git-derived lastmod, shallow-clone fallback, hreflang."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("render_sitemap", ROOT / "scripts" / "render_sitemap.py")
render_sitemap = importlib.util.module_from_spec(_spec)
sys.modules["render_sitemap"] = render_sitemap
_spec.loader.exec_module(render_sitemap)

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}
HAS_GIT = shutil.which("git") is not None


def _page(canonical: str, lang: str = "en", extra: str = "") -> str:
    return (
        f'<!doctype html><html lang="{lang}"><head><title>t</title>'
        f'<link rel="canonical" href="{canonical}">{extra}</head><body></body></html>'
    )


@pytest.fixture
def site(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    (docs / "da").mkdir(parents=True)
    (docs / "index.html").write_text(_page("https://clinicops.dk/"), encoding="utf-8")
    (docs / "tool.html").write_text(_page("https://clinicops.dk/tool"), encoding="utf-8")
    (docs / "da" / "tool.html").write_text(_page("https://clinicops.dk/da/tool", "da"), encoding="utf-8")
    (docs / "hidden.html").write_text(
        _page("https://clinicops.dk/hidden", extra='<meta name="robots" content="noindex,follow">'),
        encoding="utf-8",
    )
    monkeypatch.setattr(render_sitemap, "ROOT", tmp_path)
    monkeypatch.setattr(render_sitemap, "DOCS", docs)
    monkeypatch.setattr(render_sitemap, "SITEMAP", docs / "sitemap.xml")
    monkeypatch.setattr(render_sitemap, "HREFLANG_PAIRS", tmp_path / "hreflang_pairs.json")
    return tmp_path


def _write_pairs(site: Path, pairs: list[dict]) -> None:
    (site / "hreflang_pairs.json").write_text(json.dumps({"pairs": pairs}), encoding="utf-8")


def _render(site: Path) -> str:
    pages = render_sitemap.discover_pages()
    groups = render_sitemap.load_hreflang_groups()
    render_sitemap.validate_hreflang_groups(groups, pages)
    lastmods = {page.url: "2026-01-02" for page in pages}
    return render_sitemap.render([p.url for p in pages], lastmods, render_sitemap.alternates_for(groups))


# --- hreflang: empty and populated ------------------------------------------


def test_empty_pair_map_emits_no_hreflang_and_no_xhtml_namespace(site) -> None:
    _write_pairs(site, [])
    xml = _render(site)
    assert "xhtml" not in xml and "hreflang" not in xml
    root = ElementTree.fromstring(xml)
    locs = [n.text for n in root.findall("sm:url/sm:loc", NS)]
    assert "https://clinicops.dk/hidden" not in locs
    assert all(re.search(r"<lastmod>2026-01-02</lastmod>", xml) for _ in locs)


def test_missing_pair_file_is_the_same_as_empty(site) -> None:
    assert render_sitemap.load_hreflang_groups() == []


def test_populated_pair_is_self_referencing_reciprocal_with_english_x_default(site) -> None:
    _write_pairs(site, [{"en": "https://clinicops.dk/tool", "da": "https://clinicops.dk/da/tool"}])
    xml = _render(site)
    root = ElementTree.fromstring(xml)
    by_loc = {
        node.find("sm:loc", NS).text: [
            (link.get("hreflang"), link.get("href")) for link in node.findall("x:link", NS)
        ]
        for node in root.findall("sm:url", NS)
    }
    expected = [
        ("en", "https://clinicops.dk/tool"),
        ("da", "https://clinicops.dk/da/tool"),
        ("x-default", "https://clinicops.dk/tool"),
    ]
    assert by_loc["https://clinicops.dk/tool"] == expected  # self-referencing
    assert by_loc["https://clinicops.dk/da/tool"] == expected  # reciprocal, same set
    assert by_loc["https://clinicops.dk/"] == []  # unpaired pages untouched
    assert 'xmlns:xhtml="http://www.w3.org/1999/xhtml"' in xml


@pytest.mark.parametrize(
    ("pairs", "message"),
    [
        ([{"da": "https://clinicops.dk/da/tool", "sv": "https://clinicops.dk/tool"}], "must include 'en'"),
        ([{"en": "https://clinicops.dk/tool"}], "at least two"),
        ([{"en": "https://clinicops.dk/tool", "EU": "https://clinicops.dk/da/tool"}], "invalid language code"),
        ([{"en": "https://clinicops.dk/tool", "da": "https://clinicops.dk/hidden"}], "not an indexable sitemap page"),
        ([{"en": "https://clinicops.dk/tool", "da": "https://clinicops.dk/missing"}], "not an indexable sitemap page"),
        ([{"en": "https://clinicops.dk/tool", "da": "https://clinicops.dk/tool"}], "same URL"),
        ([{"en": "https://clinicops.dk/da/tool", "da": "https://clinicops.dk/tool"}], "expected"),
        (
            [
                {"en": "https://clinicops.dk/tool", "da": "https://clinicops.dk/da/tool"},
                {"en": "https://clinicops.dk/", "da": "https://clinicops.dk/da/tool"},
            ],
            "already belongs",
        ),
    ],
)
def test_invalid_pair_declarations_fail_the_build(site, pairs, message) -> None:
    _write_pairs(site, pairs)
    with pytest.raises(SystemExit, match=message):
        _render(site)


def test_committed_pair_map_is_valid_against_the_real_site() -> None:
    data = json.loads((ROOT / "data" / "hreflang_pairs.json").read_text(encoding="utf-8"))
    assert isinstance(data["pairs"], list)
    sitemap = (ROOT / "docs" / "sitemap.xml").read_text(encoding="utf-8")
    # Initially empty: an English-only site carries no hreflang at all.
    assert bool(data["pairs"]) == ("hreflang" in sitemap)


# --- lastmod -----------------------------------------------------------------


def _git(cwd: Path, *args: str, date: str | None = None) -> None:
    env = {"PATH": os.environ["PATH"], "HOME": str(cwd), "GIT_CONFIG_NOSYSTEM": "1"}
    if date:
        env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"] = date
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, env=env)


@pytest.mark.skipif(not HAS_GIT, reason="git not installed")
def test_lastmod_is_the_utc_date_of_the_last_commit_touching_the_page(site) -> None:
    _git(site, "init", "-q", "-b", "main")
    _git(site, "config", "user.email", "t@example.invalid")
    _git(site, "config", "user.name", "t")
    _git(site, "add", "-A")
    _git(site, "commit", "-qm", "first", date="2026-03-01T23:30:00+00:00")
    (site / "docs" / "tool.html").write_text(_page("https://clinicops.dk/tool", extra="<!-- v2 -->"), encoding="utf-8")
    _git(site, "commit", "-qam", "edit tool", date="2026-04-05T10:00:00+00:00")

    pages = render_sitemap.discover_pages()
    assert render_sitemap.history_is_complete() is True
    lastmods = render_sitemap.compute_lastmods(pages)
    assert lastmods["https://clinicops.dk/tool"] == "2026-04-05"
    assert lastmods["https://clinicops.dk/"] == "2026-03-01"
    # deterministic: same history, same bytes
    assert render_sitemap.compute_lastmods(pages) == lastmods

    # an uncommitted edit counts as modified today
    (site / "docs" / "index.html").write_text(_page("https://clinicops.dk/", extra="<!-- dirty -->"), encoding="utf-8")
    assert render_sitemap.compute_lastmods(pages)["https://clinicops.dk/"] == render_sitemap._today()


def test_shallow_or_gitless_checkout_keeps_recorded_lastmod_and_dates_new_pages_today(site, monkeypatch) -> None:
    monkeypatch.setattr(render_sitemap, "history_is_complete", lambda: False)
    monkeypatch.setattr(render_sitemap, "_is_dirty", lambda path: path.name == "index.html")
    render_sitemap.SITEMAP.write_text(
        render_sitemap.render(
            ["https://clinicops.dk/", "https://clinicops.dk/tool"],
            {"https://clinicops.dk/": "2025-12-24", "https://clinicops.dk/tool": "2025-12-25"},
        ),
        encoding="utf-8",
    )
    lastmods = render_sitemap.compute_lastmods(render_sitemap.discover_pages())
    assert lastmods["https://clinicops.dk/tool"] == "2025-12-25"  # clean: keep recorded
    assert lastmods["https://clinicops.dk/"] == render_sitemap._today()  # modified: today
    assert lastmods["https://clinicops.dk/da/tool"] == render_sitemap._today()  # new: today


def test_shallow_check_validates_lastmod_shape(site, monkeypatch) -> None:
    monkeypatch.setattr(render_sitemap, "history_is_complete", lambda: False)
    urls = [p.url for p in render_sitemap.discover_pages()]
    render_sitemap.SITEMAP.write_text(render_sitemap.render(urls, {u: "2026-01-02" for u in urls}), encoding="utf-8")
    assert set(render_sitemap._check_recorded_lastmods(urls)) == set(urls)
    render_sitemap.SITEMAP.write_text(render_sitemap.render(urls, {u: "2999-01-01" for u in urls}), encoding="utf-8")
    with pytest.raises(SystemExit, match="future"):
        render_sitemap._check_recorded_lastmods(urls)
    render_sitemap.SITEMAP.write_text(render_sitemap.render(urls), encoding="utf-8")
    with pytest.raises(SystemExit, match="no valid <lastmod>"):
        render_sitemap._check_recorded_lastmods(urls)


def test_committed_sitemap_has_a_wellformed_lastmod_for_every_url() -> None:
    root = ElementTree.fromstring((ROOT / "docs" / "sitemap.xml").read_text(encoding="utf-8"))
    nodes = root.findall("sm:url", NS)
    assert nodes
    for node in nodes:
        mod = node.find("sm:lastmod", NS)
        assert mod is not None and re.fullmatch(r"\d{4}-\d{2}-\d{2}", mod.text or ""), node.find("sm:loc", NS).text
