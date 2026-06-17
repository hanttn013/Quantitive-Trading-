from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class BrokerOrderResult:
    broker_order_id: str | None
    status: str
    filled_volume: float
    average_fill_price: float | None
    raw: dict[str, object]


class BrokerAdapter(Protocol):
    def place_order(self, order: dict[str, object]) -> BrokerOrderResult:
        ...

    def reconcile(self) -> dict[str, object]:
        ...
