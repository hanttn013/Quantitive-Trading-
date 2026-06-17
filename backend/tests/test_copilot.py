from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_copilot_health_does_not_expose_api_key():
    response = client.get("/api/copilot/health")

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "DeepSeek"
    assert "api_key" not in body
    assert "DEEPSEEK_API_KEY" not in str(body)


def test_copilot_chat_uses_safe_fallback_without_secret():
    response = client.post("/api/copilot/chat", json={"message": "Why hasnt the agent bought yet?"})

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "DeepSeek"
    assert body["reply"]
    assert "sk-" not in str(body)


def test_copilot_command_confirm_is_auditable():
    response = client.post("/api/copilot/commands/confirm", json={"action": "Close 50% XAUUSD position"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CONFIRMED"
    assert body["correlation_id"].startswith("c-")
