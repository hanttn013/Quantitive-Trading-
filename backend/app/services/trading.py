from __future__ import annotations

from uuid import uuid4

from .risk import evaluate_order


def draft_order(payload: dict[str, object]) -> dict[str, object]:
    return {
        "draft_id": f"draft-{uuid4().hex[:8]}",
        "status": "DRAFT",
        "payload": payload,
        "next": "SIMULATE",
    }


def simulate_order(payload: dict[str, object]) -> dict[str, object]:
    volume = float(payload.get("volume", 0.05))
    entry = float(payload.get("entry", 2336.10))
    sl = float(payload.get("sl", 2329.50))
    tp = float(payload.get("tp", 2342.80))
    risk_amount = abs(entry - sl) * volume * 100
    reward_amount = abs(tp - entry) * volume * 100

    decision = evaluate_order(
        environment=str(payload.get("environment", "Paper")),
        volume=volume,
        margin_level=float(payload.get("margin_level", 842)),
        spread_points=float(payload.get("spread_points", 4.2)),
        confidence=float(payload.get("confidence", 0.78)),
    )

    return {
        "simulation_id": f"sim-{uuid4().hex[:8]}",
        "status": "SIMULATED",
        "risk_amount": round(risk_amount, 2),
        "reward_amount": round(reward_amount, 2),
        "estimated_slippage_points": 0.8,
        "risk_decision": decision.__dict__,
    }


def confirm_order(payload: dict[str, object]) -> dict[str, object]:
    simulation = simulate_order(payload)
    decision = simulation["risk_decision"]
    if decision["decision"] == "REJECT":
        return {
            "order_id": None,
            "status": "REJECTED",
            "correlation_id": f"c-{uuid4().hex[:6]}",
            "risk_decision": decision,
        }

    return {
        "order_id": f"ord-{uuid4().hex[:8]}",
        "status": "EXECUTED" if payload.get("environment") != "Live" else "LIVE_CONFIRMATION_RECORDED",
        "correlation_id": f"c-{uuid4().hex[:6]}",
        "filled_volume": decision["approved_volume"],
        "risk_decision": decision,
    }


def reject_order(payload: dict[str, object]) -> dict[str, object]:
    return {
        "status": "REJECTED_BY_USER",
        "correlation_id": f"c-{uuid4().hex[:6]}",
        "reason": payload.get("reason", "User rejected order"),
    }


def emergency_stop(payload: dict[str, object]) -> dict[str, object]:
    close_positions = bool(payload.get("close_positions", True))
    return {
        "status": "PARTIAL_STOP" if close_positions else "OK",
        "correlation_id": f"c-{uuid4().hex[:6]}",
        "actions": {
            "pause_all_agents": True,
            "block_new_orders": True,
            "cancel_pending_orders": True,
            "close_all_positions": close_positions,
            "disconnect_execution_bridge": bool(payload.get("disconnect_execution_bridge", False)),
            "monitoring_only_mode": True,
        },
        "reason": payload.get("reason", "Emergency stop requested"),
        "audit": "PENDING_BROKER_CONFIRMATION" if close_positions else "OK",
    }

