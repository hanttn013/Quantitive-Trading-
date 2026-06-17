from __future__ import annotations

from typing import Literal


SweepLabel = Literal["positive", "negative", "neutral"]


def label_liquidity_sweep(future_path: list[float], entry: float, take_profit: float, stop_loss: float) -> SweepLabel:
    for price in future_path:
        if entry <= take_profit:
            if price >= take_profit:
                return "positive"
            if price <= stop_loss:
                return "negative"
        else:
            if price <= take_profit:
                return "positive"
            if price >= stop_loss:
                return "negative"
    return "neutral"

