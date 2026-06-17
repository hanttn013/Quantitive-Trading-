from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from ...adapters.brokers.base import BrokerAdapter, BrokerOrderResult
from ...services.risk import evaluate_order


class Mt5LiveDisabledError(PermissionError):
    pass


@dataclass
class AutoTradeRuntime:
    broker: BrokerAdapter
    mt5_live_enabled: bool = False
    status: str = "STOPPED"
    audit: list[dict[str, object]] = field(default_factory=list)

    def start(self, *, mode: str) -> None:
        if mode == "Live" and not self.mt5_live_enabled:
            raise Mt5LiveDisabledError("Live MT5 execution is disabled by default")
        self.status = "RUNNING"

    def handle_signal(self, signal: dict[str, object]) -> BrokerOrderResult | None:
        decision = evaluate_order(
            environment=str(signal.get("environment", "Paper")),
            volume=float(signal.get("volume", 0.0)),
            margin_level=float(signal.get("margin_level", 500.0)),
            spread_points=float(signal.get("spread", 2.0)),
            confidence=float(signal.get("confidence", 0.0)),
        )
        if decision.decision == "REJECT":
            self.audit.append({"action": "ORDER_REJECTED", "correlation_id": _correlation_id(), "reason": decision.rejection_code})
            return None
        result = self.broker.place_order({**signal, "volume": decision.approved_volume})
        self.audit.append({"action": "ORDER_SENT", "correlation_id": _correlation_id(), "status": result.status})
        return result

    def emergency_stop(self, *, reason: str) -> dict[str, object]:
        self.status = "EMERGENCY_STOPPED"
        event = {"action": "EMERGENCY_STOP", "correlation_id": _correlation_id(), "reason": reason}
        self.audit.append(event)
        return event

    def reconcile(self) -> dict[str, object]:
        return self.broker.reconcile()


def _correlation_id() -> str:
    return f"c-{uuid4().hex[:10]}"
