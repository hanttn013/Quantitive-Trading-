from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_order_simulation_returns_risk_decision_before_execution():
    response = client.post(
        "/api/orders/simulate",
        json={"environment": "Paper", "volume": 0.05, "margin_level": 842, "spread_points": 4.2, "confidence": 0.78},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SIMULATED"
    assert body["risk_decision"]["decision"] == "APPROVE"
    assert body["risk_amount"] > 0


def test_order_confirm_rejects_when_risk_fails():
    response = client.post(
        "/api/orders/confirm",
        json={"environment": "Live", "volume": 0.05, "margin_level": 114, "spread_points": 4.2, "confidence": 0.78},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REJECTED"
    assert body["risk_decision"]["rejection_code"] == "MARGIN_LEVEL_OK"


def test_emergency_stop_is_safe_and_auditable():
    response = client.post("/api/emergency-stop", json={"reason": "operator test", "close_positions": True})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PARTIAL_STOP"
    assert body["actions"]["block_new_orders"] is True
    assert body["correlation_id"].startswith("c-")
