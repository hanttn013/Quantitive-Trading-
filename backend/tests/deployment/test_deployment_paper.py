from backend.app.services.deployment import evaluate_deployment_gates
from backend.app.services.paper_trading import process_paper_signal


def test_positive_profit_alone_cannot_enter_live():
    result = evaluate_deployment_gates({"profit_factor": 2.0, "trades": 100}, "LIVE")
    assert not result.allowed
    assert "OOS_REQUIRED" in result.failures
    assert "PAPER_TRADING_REQUIRED" in result.failures


def test_trading_invalid_model_fails_deployment_gate():
    result = evaluate_deployment_gates(
        {
            "oos_passed": True,
            "walk_forward_passed": True,
            "leakage_valid": True,
            "profit_factor": 1.5,
            "trades": 80,
            "paper_approved": True,
            "model_status": "PREDICTIVELY_VALID/TRADING_INVALID",
        },
        "LIVE",
    )
    assert not result.allowed
    assert "MODEL_TRADING_INVALID" in result.failures


def test_paper_trading_generates_risk_decision_and_journal():
    order = process_paper_signal({"id": "sig-1", "volume": 0.2, "confidence": 0.8, "spread": 2.0})
    assert order.status == "FILLED"
    assert order.risk_decision.decision == "APPROVE"
    assert order.journal["source"] == "paper_trading"
