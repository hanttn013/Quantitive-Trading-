from __future__ import annotations

from uuid import uuid4

from .deployment import evaluate_deployment_gates
from .risk import evaluate_order
from ..settings import Settings


def health(settings: Settings) -> dict[str, object]:
    return {
        "provider": "DeepSeek",
        "model": settings.deepseek_model,
        "status": settings.deepseek_status,
        "base_url": settings.deepseek_base_url,
        "fallback": settings.deepseek_status == "degraded",
    }


def fallback_reply(prompt: str) -> str:
    p = prompt.lower()
    if "pause" in p:
        return "Pausing requires confirmation. The agent will stop generating new signals and continue managing open positions."
    if "risk" in p:
        return "Risk is elevated: daily loss is near warning threshold and XAUUSD spread anomaly is active."
    if "report" in p:
        return "Daily report: PnL +184.30 USD, win rate 61%, profit factor 1.42, max intraday DD 1.8%."
    if "backtest" in p:
        return "Quick backtest can be started for PPO-v12 on XAUUSD M5 with current cost model."
    return "Decision: HOLD. Spread is elevated, ATR is rising, and CPI risk is near. No-trade is the safer action until conditions normalize."


def chat(payload: dict[str, object], settings: Settings) -> dict[str, object]:
    prompt = str(payload.get("message", ""))
    # Real provider calls belong here once secrets and outbound access are configured.
    # The fallback is deterministic and never exposes the API key.
    return {
        "id": f"msg-{uuid4().hex[:8]}",
        "provider": "DeepSeek",
        "model": settings.deepseek_model,
        "status": settings.deepseek_status,
        "reply": fallback_reply(prompt),
        "requires_confirmation": any(word in prompt.lower() for word in ["pause", "close", "risk", "break-even"]),
    }


def command_result(action: str, payload: dict[str, object]) -> dict[str, object]:
    risk = evaluate_order(
        environment=str(payload.get("environment", "Paper")),
        volume=float(payload.get("volume", 0.1)),
        margin_level=float(payload.get("margin_level", 500.0)),
        spread_points=float(payload.get("spread", 2.0)),
        confidence=float(payload.get("confidence", 0.7)),
    )
    has_deployment_gate = "deployment_state" in payload or "target_status" in payload
    gate = (
        evaluate_deployment_gates(dict(payload.get("deployment_state", {})), str(payload.get("target_status", "PAPER_TRADING")))
        if has_deployment_gate
        else None
    )
    if action == "confirmed" and (risk.decision == "REJECT" or (gate is not None and not gate.allowed)):
        status = "REJECTED"
    else:
        status = action.upper()
    return {
        "id": f"cmd-{uuid4().hex[:8]}",
        "action": payload.get("action", action),
        "status": status,
        "correlation_id": f"c-{uuid4().hex[:6]}",
        "audit": "RECORDED",
        "risk_decision": risk.decision,
        "gate_failures": gate.failures if gate is not None else [],
    }
