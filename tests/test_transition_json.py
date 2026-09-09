import json
from datetime import date

from clinicops_os.transition_report import PortfolioRow, portfolio_payload, render_json


def test_portfolio_payload_is_machine_readable_and_prioritised():
    as_of = date(2026, 9, 9)
    rows = [
        PortfolioRow("MDR Co", "MDR device", "MF", "MDR", danish_market="yes"),
        PortfolioRow(
            "Legacy Co",
            "Legacy device",
            "MF",
            "legacy",
            basic_udi_di="B-123",
            certificate_expiry="2026-10-01",
            danish_market="confirmed",
        ),
    ]

    payload = portfolio_payload(rows, as_of=as_of)
    assert payload["schema_version"] == "1.0"
    assert payload["summary"]["manufacturer_legacy"] == 1
    assert payload["rows"][0]["company"] == "Legacy Co"
    assert payload["rows"][0]["priority_score"] > payload["rows"][1]["priority_score"]
    assert "not a regulatory risk" in payload["interpretation"]


def test_render_json_round_trips_without_losing_caveats():
    row = PortfolioRow(
        "Legacy Co",
        "Device",
        "MF",
        "legacy",
        basic_udi_di="B-123",
        linked_sscp="null",
    )
    rendered = render_json([row], as_of=date(2026, 9, 9))
    payload = json.loads(rendered)

    assert payload["rows"][0]["legacy_screen"] is True
    assert "B-prefix" in payload["rows"][0]["evidence_note"]
    assert "non-compliance" in payload["rows"][0]["evidence_note"]
    assert any("end-to-end EUDAMED audit" in item for item in payload["limitations"])
