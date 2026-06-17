import pytest

from backend.app.adapters.brokers import SimulatedBrokerAdapter
from backend.app.engines.execution import AutoTradeRuntime, Mt5LiveDisabledError


def test_live_mt5_is_disabled_by_default():
    runtime = AutoTradeRuntime(SimulatedBrokerAdapter())
    with pytest.raises(Mt5LiveDisabledError):
        runtime.start(mode="Live")


def test_simulated_broker_and_emergency_stop_have_audit_correlation():
    runtime = AutoTradeRuntime(SimulatedBrokerAdapter())
    runtime.start(mode="Paper")
    result = runtime.handle_signal({"environment": "Paper", "volume": 0.1, "confidence": 0.9, "spread": 2.0, "price": 2330.0})
    assert result is not None
    assert result.status == "FILLED"
    event = runtime.emergency_stop(reason="operator test")
    assert runtime.status == "EMERGENCY_STOPPED"
    assert event["correlation_id"].startswith("c-")


def test_reconciliation_reports_unknown_without_blind_retry():
    broker = SimulatedBrokerAdapter()
    broker.orders["x"] = {"status": "UNKNOWN"}
    report = AutoTradeRuntime(broker).reconcile()
    assert report["unknown_orders"] == ["x"]
    assert report["blind_retry"] is False
