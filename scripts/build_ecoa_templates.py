"""Build the static ClinicOps template downloads under docs/downloads/.

Standard library only: the XLSX files are written by a small OOXML writer, so
no new dependency is needed and the output is byte-for-byte deterministic
(fixed zip timestamps, fixed document properties, no shared state).

    python scripts/build_ecoa_templates.py          # write the files
    python scripts/build_ecoa_templates.py --check  # fail if committed files differ

Files built:
  clinicops-ecoa-uat-template-v1.0.xlsx          T1, adapted from a CC BY 4.0 paper
  clinicops-terminology-governance-v1.0.xlsx     one printed page (A4 landscape)
  clinicops-terminology-governance-v1.0.csv      the same form as plain CSV

Both templates are blank: they hold no user data and need no account or email.
"""

from __future__ import annotations

import argparse
import csv
import io
import math
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "downloads"

VERSION = "1.0"
DATE = "2026-11-16"
LICENCE_NAME = "Creative Commons Attribution 4.0 International (CC BY 4.0)"
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
BANNER = "Template, not a compliance determination."

UAT_FILE = f"clinicops-ecoa-uat-template-v{VERSION}.xlsx"
TERM_XLSX = f"clinicops-terminology-governance-v{VERSION}.xlsx"
TERM_CSV = f"clinicops-terminology-governance-v{VERSION}.csv"

PAPER_CITATION = (
    "Gordon S, Crager J, Howry C, Barsdorf AI, Cohen J, Crescioni M, Dahya B, Delong P, "
    "Knaus C, Reasner DS, Vallow S, Zarzar K, Eremenco S, on behalf of the Electronic "
    "Patient-Reported Outcome (ePRO) Consortium and the PRO Consortium. Best Practice "
    "Recommendations: User Acceptance Testing for Systems Designed to Collect Clinical "
    "Outcome Assessment Data Electronically. Therapeutic Innovation & Regulatory Science "
    "2022;56(3):442-453. doi:10.1007/s43441-021-00363-z"
)
PAPER_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC8964567"
DKMA_URL = (
    "https://laegemiddelstyrelsen.dk/en/licensing/licensing-of-medicines/"
    "spcs,-package-leaflets-and-labelling/"
    "linguistic-proofreading-of-product-information-for-centrally-authorised-medicinal-products/"
)

# ---------------------------------------------------------------------------
# Minimal XLSX writer
# ---------------------------------------------------------------------------

# Style ids (cellXfs index) used by the sheets below.
S_DEFAULT, S_TITLE, S_HEADER, S_WRAP, S_BANNER, S_INPUT, S_BOLD, S_LABEL, S_CELL = range(9)


@dataclass
class Cell:
    value: str
    style: int = S_WRAP


@dataclass
class Sheet:
    name: str
    widths: list[float]
    rows: list[list[Cell | str | None]] = field(default_factory=list)
    merges: list[str] = field(default_factory=list)
    validations: list[tuple[str, list[str]]] = field(default_factory=list)  # (sqref, items)
    freeze_row: int = 0  # rows above this stay visible (0 = none)
    landscape: bool = True
    fit_one_page: bool = False
    footer: str = ""


def col_letter(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def _clean(text: str) -> str:
    # XML 1.0 forbids most control characters; keep tab, newline.
    return "".join(ch for ch in text if ch in "\n\t" or ord(ch) >= 32)


def _estimate_height(cells: list[Cell | str | None], widths: list[float], spans: dict[int, int]) -> float | None:
    longest = 1
    for idx, cell in enumerate(cells):
        if cell is None:
            continue
        value = cell.value if isinstance(cell, Cell) else cell
        if not value:
            continue
        width = sum(widths[idx : idx + spans.get(idx, 1)])
        per_line = max(int(width * 1.05), 8)
        lines = sum(max(1, math.ceil(len(part) / per_line)) for part in value.split("\n"))
        longest = max(longest, lines)
    return None if longest == 1 else round(15.0 * longest + 2, 1)


def sheet_xml(sheet: Sheet) -> str:
    spans: dict[int, dict[int, int]] = {}
    for ref in sheet.merges:
        start, end = ref.split(":")
        row = int("".join(ch for ch in start if ch.isdigit()))
        c0 = _col_index(start)
        c1 = _col_index(end)
        spans.setdefault(row, {})[c0] = c1 - c0 + 1

    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    out.append('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">')
    out.append('<sheetPr><pageSetUpPr fitToPage="1"/></sheetPr>')
    last_col = col_letter(len(sheet.widths) - 1)
    out.append(f'<dimension ref="A1:{last_col}{max(len(sheet.rows), 1)}"/>')
    if sheet.freeze_row:
        out.append(
            '<sheetViews><sheetView workbookViewId="0">'
            f'<pane ySplit="{sheet.freeze_row}" topLeftCell="A{sheet.freeze_row + 1}" '
            'activePane="bottomLeft" state="frozen"/>'
            f'<selection pane="bottomLeft" activeCell="A{sheet.freeze_row + 1}" sqref="A{sheet.freeze_row + 1}"/>'
            "</sheetView></sheetViews>"
        )
    else:
        out.append('<sheetViews><sheetView workbookViewId="0"/></sheetViews>')
    out.append('<sheetFormatPr defaultRowHeight="15"/>')
    out.append("<cols>")
    for idx, width in enumerate(sheet.widths, start=1):
        out.append(f'<col min="{idx}" max="{idx}" width="{width}" customWidth="1"/>')
    out.append("</cols>")
    out.append("<sheetData>")
    for r_idx, cells in enumerate(sheet.rows, start=1):
        height = _estimate_height(cells, sheet.widths, spans.get(r_idx, {}))
        attrs = f' ht="{height}" customHeight="1"' if height else ""
        out.append(f'<row r="{r_idx}"{attrs}>')
        for c_idx, cell in enumerate(cells):
            if cell is None:
                continue
            if isinstance(cell, str):
                cell = Cell(cell)
            ref = f"{col_letter(c_idx)}{r_idx}"
            if cell.value == "":
                out.append(f'<c r="{ref}" s="{cell.style}"/>')
            else:
                out.append(
                    f'<c r="{ref}" s="{cell.style}" t="inlineStr"><is>'
                    f'<t xml:space="preserve">{escape(_clean(cell.value))}</t></is></c>'
                )
        out.append("</row>")
    out.append("</sheetData>")
    if sheet.merges:
        out.append(f'<mergeCells count="{len(sheet.merges)}">')
        out.extend(f'<mergeCell ref="{ref}"/>' for ref in sheet.merges)
        out.append("</mergeCells>")
    if sheet.validations:
        out.append(f'<dataValidations count="{len(sheet.validations)}">')
        for sqref, items in sheet.validations:
            joined = ",".join(items)
            assert len(joined) <= 255 and all("," not in item and '"' not in item for item in items)
            out.append(
                '<dataValidation type="list" allowBlank="1" showErrorMessage="1" '
                f'sqref="{sqref}"><formula1>"{escape(joined)}"</formula1></dataValidation>'
            )
        out.append("</dataValidations>")
    out.append('<pageMargins left="0.5" right="0.5" top="0.6" bottom="0.6" header="0.3" footer="0.3"/>')
    orientation = "landscape" if sheet.landscape else "portrait"
    if sheet.fit_one_page:
        out.append(f'<pageSetup paperSize="9" orientation="{orientation}" fitToWidth="1" fitToHeight="1"/>')
    else:
        out.append(f'<pageSetup paperSize="9" orientation="{orientation}" fitToWidth="1" fitToHeight="0"/>')
    if sheet.footer:
        out.append(f'<headerFooter><oddFooter>&amp;L{escape(sheet.footer)}&amp;RPage &amp;P of &amp;N</oddFooter></headerFooter>')
    out.append("</worksheet>")
    return "".join(out)


def _col_index(ref: str) -> int:
    letters = "".join(ch for ch in ref if ch.isalpha())
    index = 0
    for ch in letters:
        index = index * 26 + (ord(ch) - 64)
    return index - 1


STYLES_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<fonts count="4">'
    '<font><sz val="11"/><name val="Calibri"/><family val="2"/></font>'
    '<font><b/><sz val="11"/><name val="Calibri"/><family val="2"/></font>'
    '<font><b/><sz val="14"/><name val="Calibri"/><family val="2"/></font>'
    '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/><family val="2"/></font>'
    "</fonts>"
    '<fills count="6">'
    '<fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FF1F4E5F"/><bgColor indexed="64"/></patternFill></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/><bgColor indexed="64"/></patternFill></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FFF2F7F8"/><bgColor indexed="64"/></patternFill></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FFE7E6E6"/><bgColor indexed="64"/></patternFill></fill>'
    "</fills>"
    '<borders count="2">'
    "<border><left/><right/><top/><bottom/><diagonal/></border>"
    '<border><left style="thin"><color rgb="FFBFBFBF"/></left><right style="thin"><color rgb="FFBFBFBF"/></right>'
    '<top style="thin"><color rgb="FFBFBFBF"/></top><bottom style="thin"><color rgb="FFBFBFBF"/></bottom><diagonal/></border>'
    "</borders>"
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="9">'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
    '<xf numFmtId="0" fontId="3" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
    '<xf numFmtId="0" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
    '<xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
    '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
    '<xf numFmtId="0" fontId="1" fillId="5" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
    "</cellXfs>"
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    "</styleSheet>"
)


def build_xlsx(sheets: list[Sheet], *, title: str, subject: str, description: str) -> bytes:
    """Return the bytes of an XLSX workbook. Deterministic for identical input."""
    names = [s.name for s in sheets]
    assert len(set(names)) == len(names) and all(len(n) <= 31 for n in names)

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        + "".join(
            f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            for i in range(1, len(sheets) + 1)
        )
        + '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        "</Types>"
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        "</Relationships>"
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
        + "".join(
            f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>' for i, name in enumerate(names, start=1)
        )
        + "</sheets></workbook>"
    )
    wb_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(
            f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
            for i in range(1, len(sheets) + 1)
        )
        + f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        "</Relationships>"
    )
    core = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        f"<dc:title>{escape(title)}</dc:title><dc:subject>{escape(subject)}</dc:subject>"
        "<dc:creator>ClinicOps</dc:creator><cp:keywords>template; CC BY 4.0</cp:keywords>"
        f"<dc:description>{escape(description)}</dc:description><cp:lastModifiedBy>ClinicOps</cp:lastModifiedBy>"
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{DATE}T00:00:00Z</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{DATE}T00:00:00Z</dcterms:modified>'
        "</cp:coreProperties>"
    )
    app = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
        "<Application>ClinicOps template builder</Application>"
        f"<AppVersion>{VERSION}</AppVersion></Properties>"
    )

    parts: list[tuple[str, str]] = [
        ("[Content_Types].xml", content_types),
        ("_rels/.rels", root_rels),
        ("docProps/core.xml", core),
        ("docProps/app.xml", app),
        ("xl/workbook.xml", workbook),
        ("xl/_rels/workbook.xml.rels", wb_rels),
        ("xl/styles.xml", STYLES_XML),
    ]
    parts.extend((f"xl/worksheets/sheet{i}.xml", sheet_xml(s)) for i, s in enumerate(sheets, start=1))

    buffer = io.BytesIO()
    # ZIP_STORED, not DEFLATED: deflate output varies with the zlib build, so a committed
    # file built on one Python would differ byte-for-byte from the same build on another.
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as archive:
        for name, text in parts:
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o644 << 16
            info.create_system = 3
            archive.writestr(info, text.encode("utf-8"))
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Shared blocks
# ---------------------------------------------------------------------------

def banner_row(width: int, extra: str = "") -> list[Cell | str | None]:
    text = BANNER + (" " + extra if extra else "")
    return [Cell(text, S_BANNER)] + [Cell("", S_BANNER)] * (width - 1)


def licence_lines(*, adapted: bool) -> list[tuple[str, str]]:
    lines = [
        ("Version and date", f"Version {VERSION}, {DATE}. Blank template: it holds no data and needs no account."),
        ("Licence", (f"{LICENCE_NAME}. You may share and adapt it, including commercially, if you give credit and "
                    f"indicate changes. Licence text: {LICENCE_URL}")),
        ("Credit line", "ClinicOps (clinicops.dk), template version " + VERSION + ", " + DATE + "."),
    ]
    if adapted:
        lines += [
            ("Source paper (CC BY 4.0)", PAPER_CITATION + ". (c) The Author(s) 2022. Licensed under CC BY 4.0. " + PAPER_URL),
            ("Changes made", ("ClinicOps turned the paper's recommendations (roles, documents, test-script contents, "
                             "findings categories, approval) into a spreadsheet skeleton: reorganised and shortened, in "
                             "ClinicOps wording. The example test steps are ClinicOps examples, not taken from the paper. "
                             "The authors and the consortia have not reviewed or endorsed this template.")),
        ]
    return lines


# ---------------------------------------------------------------------------
# T1: eCOA UAT script skeleton, findings log and approval form
# ---------------------------------------------------------------------------

FINDING_CATEGORIES = [
    "System issue",
    "Application or software bug",
    "Design change",
    "Enhancement",
    "Script error",
]
FINDING_IMPACT = ["Blocks go-live", "Can be deferred", "Not assessed yet"]
FINDING_DECISION = [
    "Fix before go-live",
    "Defer to post go-live release plan",
    "Script corrected",
    "Not accepted",
    "Open",
]
FINDING_STATUS = ["Open", "Fixed and awaiting re-test", "Closed", "Deferred"]
YES_NO_NA = ["Yes", "No", "Not needed"]
PASS_FAIL = ["Pass", "Fail", "Not run"]


def uat_sheets() -> list[Sheet]:
    sheets: list[Sheet] = []

    # 1. Read me
    w = [26.0, 96.0]
    readme = Sheet("Read me", w, footer=f"ClinicOps eCOA UAT template v{VERSION} | CC BY 4.0")
    readme.rows.append(banner_row(2, "The sponsor or its designee writes, approves and runs the real scripts. "
                                     "ClinicOps does not run, validate or sign off user acceptance testing."))
    readme.merges.append("A1:B1")
    readme.rows.append([Cell("eCOA user acceptance testing (UAT): script skeleton, findings log and approval form", S_TITLE)])
    readme.rows.append([Cell("What this is", S_LABEL), Cell(
        "A blank skeleton for the sponsor-led acceptance cycle of an electronic clinical outcome assessment (eCOA) "
        "system. It gives you the documents a UAT cycle usually produces: a test plan, a test script with a step grid, "
        "a single findings log, a summary report and an approval form. Its structure follows the recommendations in "
        "the source paper named on the last sheet. It is not a standard, and using it does not make a study compliant "
        "with anything.", S_CELL)])
    readme.rows.append([Cell("How to use it", S_LABEL), Cell(
        "1. Fill in the Test plan sheet.\n"
        "2. Copy the Test script sheet once per script. Replace the example rows (they are marked EX-) with steps "
        "taken from your own specification, so that every step has an expected result you can check.\n"
        "3. Have the script approved by the person your plan names before anyone runs it.\n"
        "4. Run the scripts in the UAT environment. Log every finding in one Findings log, whoever found it.\n"
        "5. After each round, merge duplicates, agree what is fixed and what is deferred, and re-test fixed items.\n"
        "6. Complete the Summary and approval sheet. Keep these documents with the study records, as your plan states.", S_CELL)])
    readme.rows.append([Cell("Rules the paper gives that this skeleton builds in", S_LABEL), Cell(
        "UAT is not run in the Production environment.\n"
        "The eCOA provider's own staff do not execute the UAT.\n"
        "The sponsor or designee writes the plan and scripts, and scripts are approved before they are executed.\n"
        "If any step fails because of the system, the device or the configuration, the whole test case fails and is "
        "repeated after the provider confirms a fix.\n"
        "Findings go into one log and are consolidated after each round, with duplicates removed.\n"
        "A design change or an enhancement needs the sponsor and the provider to agree, because it can carry risk and cost.\n"
        "A deferred item needs both parties to agree and a communication plan to the study team.\n"
        "The paper advises planning for at least a 2-week cycle with several rounds; it does not give a fixed length.\n"
        "UAT is not complete until the approval form is signed.", S_CELL)])
    readme.rows.append([Cell("What it does not do", S_LABEL), Cell(
        "It does not write your scripts, decide what your study must test, or say what a pass is for your protocol. "
        "It does not replace the provider's own system testing, a validation plan or your quality system. "
        "Example rows show the shape of a step; they are not a complete test set.", S_CELL)])
    for label, text in licence_lines(adapted=True)[:3]:
        readme.rows.append([Cell(label, S_LABEL), Cell(text, S_CELL)])
    sheets.append(readme)

    # 2. Test plan
    w = [30.0, 62.0, 62.0]
    plan = Sheet("Test plan", w, freeze_row=2, footer=f"ClinicOps eCOA UAT template v{VERSION} | CC BY 4.0")
    plan.rows.append(banner_row(3))
    plan.merges.append("A1:C1")
    plan.rows.append([Cell("Section", S_HEADER), Cell("What to record", S_HEADER), Cell("Your entry", S_HEADER)])
    plan_rows = [
        ("Study and system", "Study identifier. eCOA system name and software version under test. Instruments and languages in scope."),
        ("Objectives", "What this UAT is meant to show: that the configured system works as the agreed requirements say."),
        ("Scope: in", ("Study-specific functions to be tested with formal scripts (for example visit schedule, skip logic, "
                      "completion windows, alarms and reminders, instrument versions and languages, portal roles, data export).")),
        ("Scope: out", ("What is not tested here and who covers it (for example the provider's own system testing). "
                       "Ad hoc testing may add to scripted testing; any issue it finds is tested formally in the next round.")),
        ("Risk assessment", "Which functions carry most risk to the data or to the participant, and how that sets test depth."),
        ("Environments", ("Name the environment used for UAT and how it differs from Production. UAT is not run in Production. "
                         "Changes after go-live pass through development, test and UAT before Production.")),
        ("Devices", ("Provisioned devices and, if own devices are allowed, the makes, models and operating-system versions "
                    "to test, taken from the provider's minimum requirements.")),
        ("Roles: sponsor or designee", "Who writes the plan and scripts, picks and trains testers, executes, writes the summary report, signs the approval form."),
        ("Roles: provider", ("Who provides the UAT environment and tester training, analyses findings, holds the debrief and releases the system. "
                            "Provider staff do not execute the UAT.")),
        ("Testers", "Names and functions (for example clinical operations, monitoring, data management, biostatistics) and how each was trained."),
        ("Methods", ("Positive tests (valid entries behave as specified), negative tests (invalid entries give the specified message), "
                    "boundary tests (values at and just past each limit). Say where each applies.")),
        ("Schedule", ("Planned rounds, dates, debrief meetings and the date the approval form is due. The source paper recommends planning "
                     "for at least a 2-week cycle with several rounds.")),
        ("Findings handling", ("How findings are logged (one log), who consolidates after each round, who decides fix, defer or reject, "
                              "and how a deferral is agreed and communicated.")),
        ("Approval criteria", ("What must be true before the approval form is signed (for example no open item that blocks go-live; every "
                              "deferred item agreed and communicated). Write your own; this template sets none.")),
        ("Documents and records", "Test plan, scripts, findings log, summary report and approval form: where each is kept with the study records."),
        ("Plan approved by", "Name, role, signature and date."),
    ]
    for label, prompt in plan_rows:
        plan.rows.append([Cell(label, S_LABEL), Cell(prompt, S_CELL), Cell("", S_INPUT)])
    sheets.append(plan)

    # 3. Test script
    w = [11.0, 7.0, 22.0, 22.0, 44.0, 44.0, 30.0, 12.0, 26.0]
    script = Sheet("Test script", w, freeze_row=0, footer=f"ClinicOps eCOA UAT template v{VERSION} | CC BY 4.0")
    script.rows.append(banner_row(9, "Copy this sheet once per script."))
    script.merges.append("A1:I1")
    header_block = [
        ("Script ID and title", ""),
        ("Document history", "Version, date, author, what changed."),
        ("UAT objective(s)", "What this script shows."),
        ("Prerequisites", "Environment, software version, test accounts, devices, test data and any earlier script that must pass first."),
        ("Pre-execution approval", "Approver name, role, signature, date. The script is approved before anyone executes it."),
        ("Execution", "Executed by, date, signature. Record the software version, environment and device used."),
        ("Overall test result", "If any step fails because of the system, device or configuration, the whole test case fails."),
    ]
    for label, hint in header_block:
        row_no = len(script.rows) + 1
        # label spans A:C, hint spans D:F, entry spans G:I
        script.rows.append([Cell(label, S_LABEL), Cell("", S_LABEL), Cell("", S_LABEL),
                            Cell(hint, S_CELL), Cell("", S_CELL), Cell("", S_CELL),
                            Cell("", S_INPUT), Cell("", S_INPUT), Cell("", S_INPUT)])
        script.merges += [f"A{row_no}:C{row_no}", f"D{row_no}:F{row_no}", f"G{row_no}:I{row_no}"]
        if label == "Overall test result":
            script.validations.append((f"G{row_no}", PASS_FAIL))
    script.rows.append([Cell("", S_DEFAULT)])
    grid_header_row = len(script.rows) + 1
    script.rows.append([Cell(h, S_HEADER) for h in (
        "Test case", "Step", "Component", "Requirement reference", "Action (what the tester does)",
        "Expected result", "Actual result", "Pass or fail", "Comment or findings log ID")])
    examples = [
        ("EX-01", "Study-specific application: visit schedule", "Spec: visit schedule", [
            ("Create a test participant and assign the first scheduled visit.",
             "The first visit offers the assessments in the order the specification gives."),
            ("Open the assessment before the visit window opens.",
             "Entry is not offered, or the system behaves as the specification states."),
            ("Open the assessment on the first and the last day of the window.",
             "Entry is offered on both days."),
        ]),
        ("EX-02", "Study-specific application: entry checks", "Spec: edit checks", [
            ("Enter a value inside the allowed range.", "Accepted and saved as entered."),
            ("Enter a value just outside the allowed range.", "The specified message appears; the value is not saved."),
            ("Enter a value at each limit of the range.", "Accepted at both limits."),
        ]),
        ("EX-03", "Study-specific application: alarms and reminders", "Spec: reminders", [
            ("Set the device to the time a reminder is due.", "The reminder appears at the specified time, in the specified language."),
            ("Leave the assessment incomplete past its completion window.", "The missed entry is handled as the specification states."),
        ]),
        ("EX-04", "Instrument version and language", "Spec: instrument list", [
            ("Open each instrument in each language on the list.",
             "Displayed version, wording, response options and recall period match the approved version and language."),
        ]),
        ("EX-05", "System portal", "Spec: user roles", [
            ("Sign in as each role the specification names.", "Each role sees what the specification gives it, and nothing else."),
        ]),
        ("EX-06", "Data export", "Spec: data transfer", [
            ("Enter known test values, then export a test dataset.",
             "Exported values equal the entered values, in the fields and formats of the data transfer specification."),
        ]),
        ("EX-07", "Own-device range", "Provider device list", [
            ("Run the core script on each make, model and operating-system version on the provider's list.",
             "Same result on every device in the range."),
        ]),
        ("EX-08", "Date, time and time zone", "Spec: visit windows", [
            ("Change the device date, time or time zone and open a scheduled assessment.",
             "Windows and timestamps behave as the specification states."),
        ]),
    ]
    for case_id, component, ref, steps in examples:
        for number, (action, expected) in enumerate(steps, start=1):
            script.rows.append([
                Cell(case_id, S_CELL), Cell(str(number), S_CELL), Cell(component, S_CELL), Cell(ref, S_CELL),
                Cell(action, S_CELL), Cell(expected, S_CELL), Cell("", S_INPUT), Cell("", S_INPUT), Cell("", S_INPUT)])
    first_data = grid_header_row + 1
    for _ in range(12):
        script.rows.append([Cell("", S_INPUT) for _ in range(9)])
    last_data = len(script.rows)
    script.validations.append((f"H{first_data}:H{last_data}", ["Pass", "Fail"]))
    sheets.append(script)

    # 4. Findings log
    w = [9.0, 12.0, 7.0, 12.0, 40.0, 16.0, 22.0, 18.0, 14.0, 24.0, 20.0, 18.0, 28.0, 20.0, 14.0]
    log = Sheet("Findings log", w, freeze_row=3, footer=f"ClinicOps eCOA UAT template v{VERSION} | CC BY 4.0")
    log.rows.append(banner_row(15, "One log for all testers. Consolidate after each round and remove duplicates."))
    log.merges.append("A1:O1")
    log.rows.append([Cell(
        "Category guide (from the source paper): a system issue is critical and takes priority. A design change or an enhancement "
        "needs full-team review and agreement between sponsor and provider. A script error is corrected in the script. "
        "A deferred item needs both parties to agree and a communication plan.", S_WRAP)] + [None] * 14)
    log.merges.append("A2:O2")
    log.rows.append([Cell(h, S_HEADER) for h in (
        "ID", "Date found", "Round", "Test case and step", "Description", "Found by", "Category",
        "Impact on go-live", "Owner", "Cost or timeline impact", "Decision", "Both parties agreed",
        "Communication plan or note (required for a deferral)", "Status", "Duplicate of")])
    log.rows.append([
        Cell("EX-F1", S_CELL), Cell("", S_CELL), Cell("1", S_CELL), Cell("EX-02 step 2", S_CELL),
        Cell("Example only: a value just outside the range was saved without a message.", S_CELL),
        Cell("", S_CELL), Cell("Application or software bug", S_CELL), Cell("Blocks go-live", S_CELL),
        Cell("Provider", S_CELL), Cell("", S_CELL), Cell("Fix before go-live", S_CELL), Cell("Not needed", S_CELL),
        Cell("", S_CELL), Cell("Fixed and awaiting re-test", S_CELL), Cell("", S_CELL)])
    log.rows.append([
        Cell("EX-F2", S_CELL), Cell("", S_CELL), Cell("1", S_CELL), Cell("EX-04 step 1", S_CELL),
        Cell("Example only: a tester asks for a different screen layout.", S_CELL),
        Cell("", S_CELL), Cell("Enhancement", S_CELL), Cell("Can be deferred", S_CELL),
        Cell("Sponsor and provider", S_CELL), Cell("", S_CELL), Cell("Defer to post go-live release plan", S_CELL), Cell("Yes", S_CELL),
        Cell("Example: plan reference, who tells sites, when.", S_CELL), Cell("Deferred", S_CELL), Cell("", S_CELL)])
    first = len(log.rows) + 1
    for _ in range(40):
        log.rows.append([Cell("", S_INPUT) for _ in range(15)])
    last = len(log.rows)
    log.validations += [
        (f"G{first - 2}:G{last}", FINDING_CATEGORIES),
        (f"H{first - 2}:H{last}", FINDING_IMPACT),
        (f"K{first - 2}:K{last}", FINDING_DECISION),
        (f"L{first - 2}:L{last}", YES_NO_NA),
        (f"N{first - 2}:N{last}", FINDING_STATUS),
    ]
    sheets.append(log)

    # 5. Summary and approval
    w = [34.0, 80.0]
    summ = Sheet("Summary and approval", w, footer=f"ClinicOps eCOA UAT template v{VERSION} | CC BY 4.0")
    summ.rows.append(banner_row(2))
    summ.merges.append("A1:B1")
    summ.rows.append([Cell("UAT summary report", S_TITLE)])
    for label, hint in (
        ("Study, system and software version tested", ""),
        ("Environment and devices used", ""),
        ("Rounds run and dates", ""),
        ("Test cases run, passed, failed", "Enter the counts from your executed scripts."),
        ("Findings by category", "System issue, application or software bug, design change, enhancement, script error: counts from the findings log."),
        ("Items fixed and re-tested", ""),
        ("Open items at approval", "List each with its decision. A deferred item needs both parties' agreement and a communication plan."),
        ("Known issues not fixed before launch", "List them so the study team can see them. Check whether the data management review plan and the site monitoring plan need to change."),
        ("Debrief held (date and attendees)", ""),
        ("Summary written by", "Name, role, date."),
    ):
        summ.rows.append([Cell(label, S_LABEL), Cell(hint, S_INPUT)])
    summ.rows.append([Cell("", S_DEFAULT)])
    summ.rows.append([Cell("UAT approval form", S_TITLE)])
    summ.rows.append([Cell(
        "The source paper advises that UAT should not be considered complete until this form is signed. State what you are approving: "
        "the system and version above, tested against the approved requirements, with the open items listed above.", S_WRAP), None])
    summ.merges.append(f"A{len(summ.rows)}:B{len(summ.rows)}")
    for label in (
        "Approval statement (your wording)",
        "Sponsor or designee: name, role, signature, date",
        "eCOA provider representative: name, role, signature, date",
        "Other approvers your plan names: name, role, signature, date",
        "Where the signed form is kept",
    ):
        summ.rows.append([Cell(label, S_LABEL), Cell("", S_INPUT)])
    sheets.append(summ)

    # 6. Checklist
    w = [6.0, 100.0, 22.0]
    chk = Sheet("Checklist", w, freeze_row=2, footer=f"ClinicOps eCOA UAT template v{VERSION} | CC BY 4.0")
    chk.rows.append(banner_row(3))
    chk.merges.append("A1:C1")
    chk.rows.append([Cell("#", S_HEADER), Cell("Reminder", S_HEADER), Cell("Done (date, initials)", S_HEADER)])
    for i, text in enumerate([
        "The test plan names who writes and approves scripts, who tests, and who signs the approval form.",
        "UAT runs in the UAT environment, never in Production.",
        "No provider staff execute the UAT. Testers have been trained.",
        "Every script was approved before it was executed, and the software version is recorded for each run.",
        "A failed step because of system, device or configuration fails the whole test case; it is repeated after the provider confirms a fix.",
        "All findings are in one log. Duplicates were removed after each round.",
        "Each design change or enhancement was reviewed by sponsor and provider together.",
        "Each deferred item has both parties' agreement and a communication plan to the study team.",
        "The data management review plan and the site monitoring plan were checked against the known issues.",
        "Fixed items were re-tested in the UAT environment before approval.",
        "The summary report lists open items and known issues not fixed before launch.",
        "The approval form is signed, and the plan, scripts, findings log, summary and form are kept with the study records.",
    ], start=1):
        chk.rows.append([Cell(str(i), S_CELL), Cell(text, S_CELL), Cell("", S_INPUT)])
    sheets.append(chk)

    # 7. Licence, sources, changes
    w = [26.0, 96.0]
    lic = Sheet("Licence, sources, changes", w, footer=f"ClinicOps eCOA UAT template v{VERSION} | CC BY 4.0")
    lic.rows.append(banner_row(2))
    lic.merges.append("A1:B1")
    lic.rows.append([Cell("Licence, sources and changes", S_TITLE)])
    for label, text in licence_lines(adapted=True):
        lic.rows.append([Cell(label, S_LABEL), Cell(text, S_CELL)])
    lic.rows.append([Cell("Not endorsed", S_LABEL), Cell(
        "This template is not endorsed by the paper's authors, the ePRO Consortium, the PRO Consortium, Critical Path Institute "
        "or any regulator. It does not claim that following it satisfies any regulation or guideline.", S_CELL)])
    lic.rows.append([Cell("Change log", S_LABEL), Cell(f"{VERSION} ({DATE}): first release.", S_CELL)])
    lic.rows.append([Cell("Feedback", S_LABEL), Cell(
        "Spotted an error or want a field added? Write to info@clinicops.dk. No sign-up is needed to use this file.", S_CELL)])
    sheets.append(lic)
    return sheets


# ---------------------------------------------------------------------------
# Terminology governance template (one page)
# ---------------------------------------------------------------------------

TERM_ANCHOR = (
    "Why a term needs an owner. One example of a stated expectation: the Danish Medicines Agency's page on "
    "linguistic proofreading of product information for centrally authorised medicinal products lists, among the standards it "
    "expects that product information meets, that the choice of words and the use of terminology is consistent, and that the "
    "Danish translation is a faithful translation of the original text. That page covers medicines product information (the page "
    "is dated 3 April 2017; read 16 November 2026). It does not cover medical devices or clinical-trial material, so use it as an "
    "example of a stated expectation, not as a rule for your deliverable. Source: " + DKMA_URL
)

TERM_FORM: list[tuple[str, str, str]] = [
    # (section, field, prompt)
    ("A. Scope", "Document family, device or study", "What this term set covers."),
    ("A. Scope", "Source language and version", "Language and version of the source text the terms are taken from."),
    ("A. Scope", "Target languages", "Languages this term set governs."),
    ("A. Scope", "Glossary and translation memory", ("Where the live glossary and translation memory are, who maintains them and which version applies. "
                                                      "This form governs decisions; it does not replace them.")),
    ("A. Scope", "Which source wins", "Order of authority when sources disagree (for example client glossary, then translation memory, then reference text). Write your own order."),
    ("B. Ownership and approval", "Terminology owner (per language)", "The role that decides a term. One owner per language."),
    ("B. Ownership and approval", "Approver for new or changed terms", "The role that signs off. Say whether the owner may approve their own proposal."),
    ("B. Ownership and approval", "Subject-matter reviewer", "Who checks that the term is correct in the field, and how that person is chosen."),
    ("B. Ownership and approval", "Language provider contact", "Who at the language provider receives term decisions and confirms the glossary was updated."),
    ("B. Ownership and approval", "Escalation", "Who settles a disagreement between owner, reviewer and provider, and within what time."),
    ("C. Term decision (copy for each term)", "Source term", "The term as it appears in the source."),
    ("C. Term decision (copy for each term)", "Approved target term and language", "The term to use, with its language."),
    ("C. Term decision (copy for each term)", "Status", "Proposed, approved or retired."),
    ("C. Term decision (copy for each term)", "Basis", "Why this term: regulator or standard text, instrument developer, client decision, prior approved use."),
    ("C. Term decision (copy for each term)", "Approved by and date", "Name or role, and date."),
    ("C. Term decision (copy for each term)", "Where it is used", "Documents and deliverables that contain the term."),
    ("D. Change impact (copy for each change)", "Old term, new term, reason", "What changes and why."),
    ("D. Change impact (copy for each change)", "Deliverables affected", "Every document, screen, label or file that carries the old term."),
    ("D. Change impact (copy for each change)", "Language versions affected", "Every language version that carries the old term."),
    ("D. Change impact (copy for each change)", "Glossary and memory updated", "Who updated them, and the date."),
    ("D. Change impact (copy for each change)", "Re-review needed", "Which segments or documents are re-translated or re-reviewed, and by whom."),
    ("D. Change impact (copy for each change)", "Approved by and date", "Name or role, and date. Record the version the change takes effect in."),
]


def term_csv() -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(["Section", "Field", "Prompt", "Your entry"])
    writer.writerow(["Notice", "Status", BANNER + " It records who decides a term and what a change touches; it does not decide whether any term is correct.", ""])
    writer.writerow(["Notice", "Version and date", f"Version {VERSION}, {DATE}. Blank template: it holds no data and needs no account.", ""])
    writer.writerow(["Notice", "Licence", f"{LICENCE_NAME}. Share and adapt it, including commercially, with credit and a note of changes. {LICENCE_URL}", ""])
    writer.writerow(["Notice", "Credit line", f"ClinicOps (clinicops.dk), template version {VERSION}, {DATE}. Original ClinicOps work.", ""])
    writer.writerow(["Notice", "Anchor and limits", TERM_ANCHOR, ""])
    for section, name, prompt in TERM_FORM:
        writer.writerow([section, name, prompt, ""])
    writer.writerow(["Change log", f"{VERSION} ({DATE})", "First release.", ""])
    return ("﻿" + buffer.getvalue()).encode("utf-8")


def term_sheet() -> list[Sheet]:
    # One printed page, A4 landscape. Left half: fields. Right half: change block.
    w = [30.0, 52.0, 60.0]
    sheet = Sheet("Terminology governance", w, fit_one_page=True, footer=f"ClinicOps terminology governance template v{VERSION} | CC BY 4.0")
    sheet.rows.append(banner_row(3, "It records who decides a term and what a change touches; it does not decide whether any term is correct."))
    sheet.merges.append("A1:C1")
    sheet.rows.append([Cell("Terminology governance: owner, approval, change impact", S_TITLE)])
    sheet.rows.append([Cell(TERM_ANCHOR.replace(" Source: " + DKMA_URL, ""), S_WRAP), None, None])
    sheet.merges.append("A3:C3")
    sheet.rows.append([Cell("Field", S_HEADER), Cell("What to record", S_HEADER), Cell("Your entry", S_HEADER)])
    current = ""
    for section, name, prompt in TERM_FORM:
        if section != current:
            current = section
            row_no = len(sheet.rows) + 1
            sheet.rows.append([Cell(section, S_BOLD), None, None])
            sheet.merges.append(f"A{row_no}:C{row_no}")
        sheet.rows.append([Cell(name, S_LABEL), Cell(prompt, S_CELL), Cell("", S_INPUT)])
    sheet.rows.append([Cell(
        f"Version {VERSION}, {DATE}. {LICENCE_NAME}: {LICENCE_URL} Credit: ClinicOps (clinicops.dk). Original ClinicOps work. Source for the anchor: {DKMA_URL}",
        S_WRAP), None, None])
    sheet.merges.append(f"A{len(sheet.rows)}:C{len(sheet.rows)}")
    return [sheet]


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_all() -> dict[str, bytes]:
    return {
        UAT_FILE: build_xlsx(
            uat_sheets(),
            title="ClinicOps eCOA UAT script skeleton, findings log and approval form",
            subject=f"Template v{VERSION}, {BANNER} Licence CC BY 4.0",
            description="Blank template adapted from Gordon et al. 2022 (CC BY 4.0). Template, not a compliance determination.",
        ),
        TERM_XLSX: build_xlsx(
            term_sheet(),
            title="ClinicOps terminology governance template",
            subject=f"Template v{VERSION}, {BANNER} Licence CC BY 4.0",
            description="One-page blank template: terminology owner, approval and change impact. Template, not a compliance determination.",
        ),
        TERM_CSV: term_csv(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    built = build_all()
    if args.check:
        stale = [
            name for name, data in built.items()
            if not (OUT_DIR / name).exists() or (OUT_DIR / name).read_bytes() != data
        ]
        if stale:
            print("stale template downloads: " + ", ".join(stale) + "; run `python scripts/build_ecoa_templates.py`")
            return 1
        print("template downloads: OK")
        return 0
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, data in built.items():
        (OUT_DIR / name).write_bytes(data)
        print(f"wrote docs/downloads/{name} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
