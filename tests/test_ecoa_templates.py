"""eCOA workflow update, UAT template (T1) and terminology governance template contract.

The downloads are static, blank, ungated files built by scripts/build_ecoa_templates.py with
the standard library only. These tests pin: deterministic builds, the committed files equal the
build, the banner and licence are inside every file, the structure follows the CC BY 4.0 source
paper, no HTML page or sitemap URL appears under docs/downloads, and the workflow page carries
twelve steps with stable anchors and the 'synthesis, not a standard' label.
"""
from __future__ import annotations

import csv
import importlib.util
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_ecoa_templates", ROOT / "scripts" / "build_ecoa_templates.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_ecoa_templates"] = module
    spec.loader.exec_module(module)
    return module


B = _load_builder()
BUILT = B.build_all()


def _sheet_texts(data: bytes) -> dict[str, list[list[str]]]:
    """Sheet name -> rows of cell text, read with the standard library only."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        names = [s.attrib["name"] for s in workbook.find("m:sheets", NS)]
        result = {}
        for index, name in enumerate(names, start=1):
            root = ET.fromstring(archive.read(f"xl/worksheets/sheet{index}.xml"))
            rows = []
            for row in root.find("m:sheetData", NS):
                rows.append(["".join(t.text or "" for t in c.iter("{{{}}}t".format(NS["m"]))) for c in row])
            result[name] = rows
        return result


def _flat(data: bytes) -> str:
    return "\n".join(cell for rows in _sheet_texts(data).values() for row in rows for cell in row)


# ---------------------------------------------------------------- builds


def test_build_is_deterministic_and_committed_files_match() -> None:
    again = B.build_all()
    assert again == BUILT
    for name, data in BUILT.items():
        assert (DOWNLOADS / name).read_bytes() == data, f"{name} is stale; run scripts/build_ecoa_templates.py"


def test_no_html_page_and_no_sitemap_url_under_downloads() -> None:
    assert sorted(p.name for p in DOWNLOADS.iterdir()) == sorted(BUILT)
    assert not list(DOWNLOADS.rglob("*.html"))
    sitemap = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    assert "downloads" not in sitemap
    llms = (DOCS / "llms.txt").read_text(encoding="utf-8")
    assert "downloads/" not in llms


def test_xlsx_is_a_valid_zip_with_fixed_timestamps_and_well_formed_parts() -> None:
    for name in (B.UAT_FILE, B.TERM_XLSX):
        with zipfile.ZipFile(io.BytesIO(BUILT[name])) as archive:
            assert archive.testzip() is None
            assert {i.date_time for i in archive.infolist()} == {(2026, 11, 16, 0, 0, 0)}
            for part in archive.namelist():
                ET.fromstring(archive.read(part))  # raises on malformed XML
            core = archive.read("docProps/core.xml").decode("utf-8")
            assert "2026-11-16T00:00:00Z" in core and "ClinicOps" in core


def test_xlsx_re_reads_with_openpyxl_when_available() -> None:
    openpyxl = pytest.importorskip("openpyxl")  # optional: not a project dependency
    wb = openpyxl.load_workbook(io.BytesIO(BUILT[B.UAT_FILE]))
    assert wb.sheetnames == [
        "Read me", "Test plan", "Test script", "Findings log", "Summary and approval", "Checklist",
        "Licence, sources, changes",
    ]
    assert wb["Findings log"].data_validations.dataValidation
    assert wb.properties.title.startswith("ClinicOps eCOA UAT")
    term = openpyxl.load_workbook(io.BytesIO(BUILT[B.TERM_XLSX]))
    assert term.sheetnames == ["Terminology governance"]


# ------------------------------------------------------------ T1: UAT


def test_every_uat_sheet_opens_with_the_banner() -> None:
    sheets = _sheet_texts(BUILT[B.UAT_FILE])
    assert len(sheets) == 7
    for name, rows in sheets.items():
        assert rows[0][0].startswith("Template, not a compliance determination."), name


def test_uat_file_carries_version_date_sources_and_licence() -> None:
    text = _flat(BUILT[B.UAT_FILE])
    for needle in (
        "Version 1.0, 2026-11-16",
        "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "https://creativecommons.org/licenses/by/4.0/",
        "doi:10.1007/s43441-021-00363-z",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC8964567",
        "Gordon S",
        "(c) The Author(s) 2022",
        "Changes made",
        "not endorsed",
        "ClinicOps (clinicops.dk)",
    ):
        assert needle.lower() in text.lower(), needle
    assert "v1.0" in B.UAT_FILE


def test_uat_structure_follows_the_source_paper() -> None:
    sheets = _sheet_texts(BUILT[B.UAT_FILE])
    log_header = next(row for row in sheets["Findings log"] if row and row[0] == "ID")
    assert "Category" in log_header and "Impact on go-live" in log_header
    categories = {
        "System issue", "Application or software bug", "Design change", "Enhancement", "Script error",
    }
    assert set(B.FINDING_CATEGORIES) == categories
    with zipfile.ZipFile(io.BytesIO(BUILT[B.UAT_FILE])) as archive:
        log_xml = archive.read("xl/worksheets/sheet4.xml").decode("utf-8")
    assert 'type="list"' in log_xml and "System issue,Application or software bug,Design change,Enhancement,Script error" in log_xml
    script_text = "\n".join(c for row in sheets["Test script"] for c in row)
    for field in (
        "Document history", "UAT objective(s)", "Prerequisites", "Pre-execution approval", "Execution",
        "Overall test result", "Pass or fail", "Expected result",
    ):
        assert field in script_text, field
    assert "the whole test case fails" in script_text
    readme = "\n".join(c for row in sheets["Read me"] for c in row)
    assert "never" not in readme.lower() or "Production" in readme
    assert "not run in the Production environment" in readme
    assert "at least a 2-week cycle" in readme and "does not give a fixed length" in readme
    assert "UAT is not complete until the approval form is signed" in readme
    summary = "\n".join(c for row in sheets["Summary and approval"] for c in row)
    assert "UAT approval form" in summary and "should not be considered complete until this form is signed" in summary


def test_uat_file_makes_no_compliance_or_validation_claim() -> None:
    text = _flat(BUILT[B.UAT_FILE]).lower()
    for banned in ("uat-compliant", "validated by clinicops", "certified", "audit-ready", "iso-aligned", "guarantee"):
        assert banned not in text, banned
    assert "does not run, validate or sign off" in text
    # the paper's two-week point is reported as a recommendation, never as a rule
    assert "must plan" not in text and "two-week rule" not in text


# ------------------------------------------------- terminology template


def test_terminology_csv_is_utf8_bom_four_columns_with_notice_and_licence() -> None:
    raw = BUILT[B.TERM_CSV]
    assert raw.startswith(b"\xef\xbb\xbf")
    rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))
    assert rows[0] == ["Section", "Field", "Prompt", "Your entry"]
    assert all(len(r) == 4 for r in rows)
    flat = "\n".join(" ".join(r) for r in rows)
    assert "Template, not a compliance determination." in flat
    assert "CC BY 4.0" in flat or "Creative Commons Attribution 4.0" in flat
    assert "Version 1.0, 2026-11-16" in flat
    sections = {r[0] for r in rows}
    assert {"A. Scope", "B. Ownership and approval"} <= sections
    assert any(s.startswith("C. Term decision") for s in sections) and any(s.startswith("D. Change impact") for s in sections)
    for must in ("Terminology owner", "Approver for new or changed terms", "Language versions affected", "Deliverables affected"):
        assert must in flat


def test_terminology_template_anchor_is_scoped_and_matches_the_claim() -> None:
    claims = {json.loads(line)["id"]: json.loads(line) for line in (ROOT / "research" / "claims.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    claim = claims["CO-CLM-0053"]
    assert claim["status"] == "qualified" and "website" in claim["allowed_uses"]
    assert claim["sources"] == [B.DKMA_URL]
    csv_text = BUILT[B.TERM_CSV].decode("utf-8-sig")
    xlsx_text = _flat(BUILT[B.TERM_XLSX])
    for text in (csv_text, xlsx_text):
        assert B.DKMA_URL in text
        assert "choice of words and the use of terminology is consistent" in text
        assert "It does not cover medical devices or clinical-trial material" in text
        assert "3 April 2017" in text
    # the anchor must not be stretched to devices or trial material
    assert "device manufacturers must" not in csv_text.lower()


def test_terminology_xlsx_is_one_printed_page() -> None:
    with zipfile.ZipFile(io.BytesIO(BUILT[B.TERM_XLSX])) as archive:
        xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert 'fitToPage="1"' in xml and 'fitToWidth="1" fitToHeight="1"' in xml and 'orientation="landscape"' in xml


# ------------------------------------------------- workflow page contract


@pytest.fixture(scope="module")
def page() -> str:
    return (DOCS / "ecoa-workflow.html").read_text(encoding="utf-8")


EXPECTED_IDS = [
    "step-decide", "step-start", "step-align", "step-plan", "step-licences", "step-build", "step-test",
    "step-participant-material", "step-go-live", "step-run", "step-change-transfer", "step-close",
]


def test_page_has_twelve_numbered_steps_with_stable_slug_anchors(page: str) -> None:
    rows = re.findall(r'<tr id="(step-[a-z-]+)"><td class="k">(\d+)</td><th scope="row">([^<]+)</th>', page)
    assert [r[0] for r in rows] == EXPECTED_IDS
    assert [int(r[1]) for r in rows] == list(range(12))
    titles = {r[0]: r[2] for r in rows}
    assert titles["step-decide"] == "Decide and select"
    assert titles["step-change-transfer"] == "Control change and transfer data"
    assert titles["step-close"] == "Close and learn"
    # steps 1 to 9 keep the numbers they had in the ten-stage version
    assert {k: int(n) for k, n, _ in rows if 1 <= int(n) <= 9}["step-test"] == 6
    live = page.split('id="changes"', 1)[0]  # the change log may name the old structure
    assert "Twelve steps" in page and "Ten stages" not in live and "ten stages" not in live.lower()
    ids = re.findall(r'\sid="([^"]+)"', page)
    assert len(ids) == len(set(ids)) and "sources" in ids and "templates" in ids and "changes" in ids


def test_page_is_labelled_synthesis_not_a_standard_and_keeps_the_stamp(page: str) -> None:
    assert "ClinicOps synthesis of published guidance, not a standard" in page
    assert "sources checked 2026-11-16" in page


def test_every_source_row_is_stamped_and_the_vendor_number_is_not_repeated(page: str) -> None:
    register = page.split('id="sources"', 1)[1]
    body = register.split("<tbody>", 1)[1].split("</tbody>", 1)[0]
    rows = re.findall(r"<tr>.*?</tr>", body, flags=re.DOTALL)
    assert len(rows) == 8
    assert all(row.rstrip().endswith("<td>2026-11-16</td></tr>") for row in rows)
    assert 'Last opened' in register
    assert "6 weeks" not in page and "Mapi" not in page and "six weeks" not in page.lower()


def test_page_claims_are_registered_for_website_use(page: str) -> None:
    assert "<!-- claim-use: website -->" in page
    ids = re.search(r"<!-- claim-ids: ([^>]+?) -->", page).group(1)
    declared = {i.strip() for i in ids.split(",")}
    assert declared == {"CO-CLM-0053", "CO-CLM-0054", "CO-CLM-0055"}
    claims = {json.loads(line)["id"]: json.loads(line) for line in (ROOT / "research" / "claims.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    for cid in declared:
        assert claims[cid]["status"] in {"verified", "qualified"}
        assert "website" in claims[cid]["allowed_uses"]
        assert claims[cid]["limitations"], cid
    assert "CC BY 4.0" in claims["CO-CLM-0055"]["claim"]


def test_templates_are_linked_directly_with_version_licence_and_no_gate(page: str) -> None:
    section = page.split('id="templates"', 1)[1].split('id="changes"', 1)[0]
    hrefs = re.findall(r'href="(downloads/[^"]+)"', page)
    assert set(hrefs) == {
        f"downloads/{B.UAT_FILE}", f"downloads/{B.TERM_XLSX}", f"downloads/{B.TERM_CSV}",
    }
    for href in hrefs:
        assert (DOCS / href).is_file()
    assert "no sign-up and no email address asked" in section.lower()
    assert "version 1.0, 2026-11-16" in section and "CC BY 4.0" in section
    assert "not endorsed by the authors" in section
    assert "<form" not in page.lower() and "type=\"email\"" not in page.lower()
    assert "not compliance determinations" in section


def test_mapper_link_and_language_pointer_exist(page: str) -> None:
    step = page.split('id="step-change-transfer"', 1)[1].split("</tr>", 1)[0]
    assert 'href="change-surface-mapper"' in step
    assert "language versions and deliverables moved" in step
    assert "optional language dimension" in page


def test_hub_card_matches_the_new_step_count() -> None:
    hub = (DOCS / "ecoa.html").read_text(encoding="utf-8")
    assert "Twelve steps from the decision to close-out" in hub and "Ten stages" not in hub
