from datetime import UTC, datetime

import pytest
import requests

from clinicops_eudamed import canary


class FakeResponse:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {"content": [{"id": 1}, {"id": 2}], "totalElements": 123}


def test_probe_success_contract(monkeypatch):
    monkeypatch.setattr(canary.requests, "get", lambda *args, **kwargs: FakeResponse())
    result = canary.probe(7, page_size=50, timeout=1)
    assert result.page == 7
    assert result.ok
    assert result.status_code == 200
    assert result.returned_items == 2
    assert result.total_elements == 123
    assert result.error is None


def test_probe_transport_failure_is_captured(monkeypatch):
    def fail(*args, **kwargs):
        raise requests.Timeout("timed out")

    monkeypatch.setattr(canary.requests, "get", fail)
    result = canary.probe(32_000, timeout=1)
    assert not result.ok
    assert result.returned_items is None
    assert "Timeout" in (result.error or "")


def test_snapshot_contract_is_explicitly_non_audit():
    sample = canary.Probe(0, 50, True, 200, 0.25, 50, 1000, None)
    captured = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    snapshot = canary.build_snapshot([sample], captured_at=captured)
    assert snapshot["captured_at_utc"] == "2026-09-09T10:00:00+00:00"
    assert "do not establish full-register coverage" in snapshot["interpretation"]
    assert snapshot["probes"][0]["page"] == 0


def test_snapshot_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        canary.build_snapshot(
            [],
            # noqa: DTZ001 — intentionally construct a naive timestamp to test rejection.
            captured_at=datetime(2026, 9, 9, 10, 0),
        )
