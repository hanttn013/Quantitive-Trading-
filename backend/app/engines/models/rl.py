from __future__ import annotations


def default_rl_schemas() -> dict[str, object]:
    return {
        "observation": {"fields": ["ohlc", "spread", "atr", "rsi", "regime", "open_risk"]},
        "action": {"enum": ["HOLD", "BUY", "SELL", "CLOSE"], "requires_risk_decision": True},
        "reward": {"components": ["net_profit", "drawdown_penalty", "transaction_cost_penalty", "overtrading_penalty"]},
    }


def assert_rl_action_requires_risk(action_schema: dict[str, object]) -> None:
    if action_schema.get("requires_risk_decision") is not True:
        raise PermissionError("RL action path must go through RiskDecision")
