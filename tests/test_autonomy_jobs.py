from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from clinicops_os.autonomy import jobs
from clinicops_os.autonomy.jobs import (
    JobSpecError,
    common_header,
    get_job,
    list_jobs,
    parse_front_matter,
    render,
)

ROOT = Path(__file__).resolve().parents[1]
JOBS_DIR = ROOT / "autonomy" / "jobs"
EXPECTED_SLUGS = {
    "t0-monitor",
    "t0-research",
    "t0-verification",
    "t0-termbase",
    "t0-eudamed",
    "t0-seo-content",
    "t0-pipeline",
    "t0-invoice",
    "t0-backup",
    "t0-evening",
    "t0-watchdog",
}


def test_all_eleven_jobs_parse_with_unique_slugs() -> None:
    specs = list_jobs(JOBS_DIR)
    assert {spec.slug for spec in specs} == EXPECTED_SLUGS
    assert len(specs) == 11
    for spec in specs:
        assert spec.tier == 0
        assert spec.cron.startswith("CRON_TZ=Europe/Madrid ")
        assert spec.cadence_minutes > 0 and spec.min_expected_duration_seconds > 0
        assert spec.outputs and "01_LOGS" in spec.outputs
        assert spec.notifications in {"none", "email", "push+email"}


def test_stdlib_front_matter_agrees_with_pyyaml_on_every_job_file() -> None:
    for path in jobs.job_files(JOBS_DIR):
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        reference = yaml.safe_load(text.split("---\n")[1])
        assert meta == reference, path.name
        assert body == text.split("\n---\n", 1)[1].lstrip("\n"), path.name


def test_render_prepends_common_header_and_strips_front_matter() -> None:
    header = common_header(JOBS_DIR)
    assert not header.startswith("# ")
    assert header.startswith("You are an unattended **Tier-0 job**")
    assert "## Kill switch" in header

    for slug in sorted(EXPECTED_SLUGS):
        prompt = render(slug, JOBS_DIR)
        assert prompt.startswith(header), slug
        assert "\n---\n" not in prompt and "slug:" not in prompt, slug
        assert "cadence_minutes" not in prompt, slug
        assert "# Job:" in prompt, slug
        assert prompt.endswith("\n")
        body = get_job(slug, JOBS_DIR).body
        assert prompt == header + "\n" + body


def test_cron_minutes_are_jittered_away_from_the_hour_and_half_hour() -> None:
    for spec in list_jobs(JOBS_DIR):
        minute = spec.cron.split()[1]
        assert minute.isdigit(), spec.slug
        assert int(minute) not in {0, 30}, spec.slug


def test_unknown_slug_and_missing_directory_raise() -> None:
    with pytest.raises(JobSpecError, match="unknown job slug"):
        get_job("t0-nope", JOBS_DIR)
    with pytest.raises(JobSpecError, match="jobs directory not found"):
        list_jobs(ROOT / "autonomy" / "absent")


def test_parser_handles_scalars_inline_lists_and_block_lists() -> None:
    text = (
        "---\n"
        "name: \"Quoted: with colon\"\n"
        "slug: 'single ''quoted'''\n"
        "count: 42\n"
        "ratio: 0.5\n"
        "flag: true\n"
        "nothing: null\n"
        "bare: plain text # trailing comment\n"
        "inline: [\"a, b\", \"c\"]\n"
        "loose: [x, 'y', 3]\n"
        "block:\n"
        "  - first\n"
        "  - \"second\"\n"
        "empty: []\n"
        "# a comment line\n"
        "---\n"
        "\n"
        "# Body\n"
        "text\n"
    )
    meta, body = parse_front_matter(text)
    assert meta == {
        "name": "Quoted: with colon",
        "slug": "single 'quoted'",
        "count": 42,
        "ratio": 0.5,
        "flag": True,
        "nothing": None,
        "bare": "plain text",
        "inline": ["a, b", "c"],
        "loose": ["x", "y", 3],
        "block": ["first", "second"],
        "empty": [],
    }
    assert body == "# Body\ntext\n"


@pytest.mark.parametrize(
    ("text", "fragment"),
    [
        ("no front matter\n", "missing opening"),
        ("---\nname: x\n", "missing closing"),
        ("---\nname: x\nname: y\n---\n", "duplicate key"),
        ("---\njunk line\n---\n", "expected 'key: value'"),
        ("---\nouter:\n  inner: 1\n---\n", "nested mappings"),
        ("---\nlist: [a, b\n---\n", "unterminated inline list"),
    ],
)
def test_parser_rejects_malformed_front_matter(text: str, fragment: str) -> None:
    with pytest.raises(JobSpecError, match=fragment):
        parse_front_matter(text)


def test_load_job_requires_metadata_and_body(tmp_path: Path) -> None:
    (tmp_path / "_COMMON_HEADER.md").write_text("# Title\nheader text\n", encoding="utf-8")
    bad = tmp_path / "bad.md"
    bad.write_text("---\nname: x\nslug: bad\n---\nbody\n", encoding="utf-8")
    with pytest.raises(JobSpecError, match="front matter missing"):
        list_jobs(tmp_path)

    bad.write_text(
        "---\nname: x\nslug: bad\ntier: 0\ncron: \"1 2 * * *\"\ncadence_minutes: abc\n"
        "min_expected_duration_seconds: 1\noutputs: [a]\nnotifications: none\n---\nbody\n",
        encoding="utf-8",
    )
    with pytest.raises(JobSpecError, match="cadence_minutes must be an integer"):
        list_jobs(tmp_path)

    bad.write_text(
        "---\nname: x\nslug: bad\ntier: 0\ncron: \"1 2 * * *\"\ncadence_minutes: 1\n"
        "min_expected_duration_seconds: 1\noutputs: [a]\nnotifications: none\n---\n\n",
        encoding="utf-8",
    )
    with pytest.raises(JobSpecError, match="job body is empty"):
        list_jobs(tmp_path)


def test_duplicate_slugs_across_files_are_rejected(tmp_path: Path) -> None:
    (tmp_path / "_COMMON_HEADER.md").write_text("# Title\nheader text\n", encoding="utf-8")
    for name in ("one.md", "two.md"):
        (tmp_path / name).write_text(
            "---\nname: " + name + "\nslug: same\ntier: 0\ncron: \"1 2 * * *\"\ncadence_minutes: 1\n"
            "min_expected_duration_seconds: 1\noutputs: [a]\nnotifications: none\n---\nbody\n",
            encoding="utf-8",
        )
    with pytest.raises(JobSpecError, match="duplicate slug"):
        list_jobs(tmp_path)


def test_common_header_requires_title_line(tmp_path: Path) -> None:
    (tmp_path / "_COMMON_HEADER.md").write_text("no title here\n", encoding="utf-8")
    with pytest.raises(JobSpecError, match="no H1 title"):
        common_header(tmp_path)
    with pytest.raises(JobSpecError, match="common header not found"):
        common_header(tmp_path / "absent")


def test_cli_list_and_render(capsys: pytest.CaptureFixture[str]) -> None:
    assert jobs.main(["list", "--jobs-dir", str(JOBS_DIR)]) == 0
    out = capsys.readouterr().out
    assert "11 job specifications" in out and "t0-watchdog" in out

    assert jobs.main(["render", "t0-evening", "--jobs-dir", str(JOBS_DIR)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("You are an unattended **Tier-0 job**")
    assert "# Job: Evening summary" in out

    assert jobs.main(["render", "t0-nope", "--jobs-dir", str(JOBS_DIR)]) == 2
    assert jobs.main([]) == 2
    assert jobs.main(["bogus"]) == 2
