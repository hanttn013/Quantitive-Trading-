from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_core_read_routes_return_data():
    routes = [
        "/api/context",
        "/api/accounts",
        "/api/dashboard/metrics",
        "/api/agents",
        "/api/risk/monitor",
        "/api/portfolio",
        "/api/positions",
        "/api/orders",
        "/api/models",
        "/api/strategies",
        "/api/backtests/summary",
        "/api/market/watch",
        "/api/market/feed-integrity",
        "/api/market/calendar",
        "/api/market/candles",
        "/api/alerts",
        "/api/audit-logs",
        "/api/integrations",
        "/api/settings/roles",
        "/api/risk/rules",
    ]

    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, route
        assert response.json(), route


def test_read_routes_expose_spec_required_values():
    context = client.get("/api/context").json()
    market = client.get("/api/market/watch").json()
    roles = client.get("/api/settings/roles").json()
    backtest = client.get("/api/backtests/summary").json()

    assert context["environment"] == "Paper"
    assert market[0]["symbol"] == "XAUUSD"
    assert any(role["role"] == "Risk Manager" for role in roles)
    assert backtest["config"]["symbol"] == "XAUUSD"
