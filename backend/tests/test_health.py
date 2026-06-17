from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_app_metadata_and_provider_states():
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "AurumQuant API"
    assert body["version"] == "0.1.0"
    assert body["status"] == "ok"
    assert body["providers"]["deepseek"] in {"configured", "degraded"}
    assert body["providers"]["mt5"] == "mock"
