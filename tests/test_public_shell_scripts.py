from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": ""},
    )


def test_public_shell_has_no_drift() -> None:
    result = _run("harmonize_public_shell.py", "--check")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 changed" in result.stdout


def test_llms_txt_is_current() -> None:
    result = _run("render_llms_txt.py", "--check")
    assert result.returncode == 0, result.stdout + result.stderr


def test_llms_txt_lists_every_sitemap_url() -> None:
    import re

    sitemap = (ROOT / "docs" / "sitemap.xml").read_text(encoding="utf-8")
    llms = (ROOT / "docs" / "llms.txt").read_text(encoding="utf-8")
    urls = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    assert urls
    assert [url for url in urls if url not in llms] == []
