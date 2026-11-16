"""EUDAMED transition page: one date, a verified-only obligations table, registry ids."""

from __future__ import annotations

import re
from pathlib import Path

from clinicops_os.claim_registry import load_registry
from clinicops_os.page_claims import declared_ids

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "docs" / "eudamed-transition.html").read_text(encoding="utf-8")
REGISTRY = {c.claim_id: c for c in load_registry(ROOT / "research" / "claims.jsonl")}


def _rows() -> list[tuple[str, str, str, str]]:
    table = PAGE.split('id="eudamed-obligations"', 1)[1].split("</table>", 1)[0]
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", table, re.DOTALL):
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.DOTALL)
        rows.append((cells[0], cells[1], cells[2], cells[3]))
    return rows


def test_the_page_gives_one_date_with_the_agreed_wording() -> None:
    assert "28 November 2026 per the Commission's legacy-device transition guidance" in PAGE
    assert "notice published 27 November 2025; mandatory use 28 May 2026; 6-month transition" in PAGE
    assert "Decision (EU) 2025/2371 itself states no calendar date" in PAGE
    assert "28 November 2026 is a Saturday: plan to finish by Friday 27 November 2026" in PAGE
    assert "27 or 28" not in PAGE and "within 12 months" not in PAGE


def test_the_page_declares_every_claim_it_cites() -> None:
    assert {"CO-CLM-0013", "CO-CLM-0020", "CO-CLM-0050", "CO-CLM-0004"} <= declared_ids(PAGE)


def test_table_has_the_seven_obligation_rows() -> None:
    rows = _rows()[1:]
    labels = [re.sub(r"<[^>]+>", "", r[0]) for r in rows]
    assert labels == [
        "Actor registration module",
        "UDI/Device registration module",
        "Notified bodies and certificates module",
        "Market surveillance module",
        "Registration of legacy devices already on the market before mandatory use",
        "Clinical investigations and performance studies module",
        "Vigilance and post-market surveillance module",
    ]


def test_every_row_has_a_source_link_and_a_registry_id_that_backs_it() -> None:
    for obligation, position, source, registry_ids in _rows()[1:]:
        links = re.findall(r'href="(https://[^"]+)"', source)
        assert links, obligation
        ids = re.findall(r"CO-CLM-\d{4}", registry_ids)
        assert ids, obligation
        backed = {url for claim_id in ids for url in REGISTRY[claim_id].sources}
        for claim_id in ids:
            claim = REGISTRY[claim_id]
            assert claim.status.value in {"verified", "qualified"} and "website" in claim.allowed_uses
            assert claim.verified_method == "read-primary", claim_id
        assert backed & set(links), (obligation, links)
        # the primary link of the row must be one of the registered sources
        assert all(link in backed for link in links), (obligation, [l for l in links if l not in backed])


def test_rows_say_only_what_the_registered_claims_say() -> None:
    rows = {re.sub(r"<[^>]+>", "", r[0]): r for r in _rows()[1:]}
    for label in ("Actor registration module", "UDI/Device registration module",
                  "Notified bodies and certificates module", "Market surveillance module"):
        assert "Mandatory to use since 28 May 2026" in rows[label][1]
        assert "28 May 2026" in REGISTRY["CO-CLM-0020"].text
    legacy = rows["Registration of legacy devices already on the market before mandatory use"][1]
    assert "28 November 2026" in legacy and "Friday 27 November 2026" in legacy
    for label in ("Clinical investigations and performance studies module",
                  "Vigilance and post-market surveillance module"):
        position = rows[label][1]
        assert position.startswith("Not yet mandatory") and "gives no date" in position
        assert not re.search(r"\b20\d\d\b", position)
    assert "under analysis" in REGISTRY["CO-CLM-0050"].text and "in development" in REGISTRY["CO-CLM-0050"].text


def test_page_wording_on_the_b_prefix_follows_the_help_page() -> None:
    assert "equivalent of the Basic UDI-DI" in PAGE
    assert "stands in place of" not in PAGE
