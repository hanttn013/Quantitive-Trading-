from backend.app.services.copilot import command_result


def test_copilot_confirm_cannot_bypass_risk_and_gate():
    result = command_result(
        "confirmed",
        {
            "action": "place_order",
            "environment": "Live",
            "volume": 0.1,
            "margin_level": 50,
            "spread": 2.0,
            "confidence": 0.9,
            "deployment_state": {"profit_factor": 2.0, "trades": 100},
            "target_status": "LIVE",
        },
    )
    assert result["status"] == "REJECTED"
    assert result["risk_decision"] == "REJECT"
    assert "PAPER_TRADING_REQUIRED" in result["gate_failures"]
