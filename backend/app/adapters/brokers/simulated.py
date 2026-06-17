from __future__ import annotations

from uuid import uuid4

from .base import BrokerOrderResult


class SimulatedBrokerAdapter:
    def __init__(self) -> None:
        self.orders: dict[str, dict[str, object]] = {}

    def place_order(self, order: dict[str, object]) -> BrokerOrderResult:
        order_id = f"sim-{uuid4().hex[:8]}"
        price = float(order.get("price", 0.0))
        volume = float(order.get("volume", 0.0))
        record = {**order, "broker_order_id": order_id, "status": "FILLED"}
        self.orders[order_id] = record
        return BrokerOrderResult(order_id, "FILLED", volume, price, {"simulated": True})

    def reconcile(self) -> dict[str, object]:
        unknown = [order_id for order_id, order in self.orders.items() if order.get("status") == "UNKNOWN"]
        return {"open_orders": len(self.orders), "unknown_orders": unknown, "blind_retry": False}
