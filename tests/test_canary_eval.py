from clinicops_eudamed.canary_eval import evaluate_snapshot, has_errors


def _snapshot(*, page0=True, page30000=True, page32000=True, items=50):
    return {
        "endpoint": "https://ec.europa.eu/tools/eudamed/api/devices/udiDiData",
        "probes": [
            {"page": 0, "ok": page0, "returned_items": items if page0 else None},
            {
                "page": 30000,
                "ok": page30000,
                "returned_items": items if page30000 else None,
            },
            {
                "page": 32000,
                "ok": page32000,
                "returned_items": items if page32000 else None,
            },
        ],
    }


def test_canary_equal_baseline_has_no_findings():
    baseline = _snapshot()
    assert evaluate_snapshot(baseline, _snapshot()) == []


def test_deep_reachability_change_is_warning_not_error():
    findings = evaluate_snapshot(_snapshot(), _snapshot(page32000=False))
    assert len(findings) == 1
    assert findings[0].severity == "warning"
    assert findings[0].page == 32000
    assert not has_errors(findings)


def test_page_zero_loss_is_error():
    findings = evaluate_snapshot(_snapshot(), _snapshot(page0=False))
    assert any(item.severity == "error" and item.page == 0 for item in findings)
    assert has_errors(findings)


def test_total_elements_is_not_treated_as_contract():
    baseline = _snapshot()
    latest = _snapshot()
    baseline["probes"][0]["total_elements"] = 100
    latest["probes"][0]["total_elements"] = 200
    assert evaluate_snapshot(baseline, latest) == []
