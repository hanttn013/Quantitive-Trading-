from dataclasses import dataclass, field
from typing import Literal


Action = Literal["BUY", "SELL", "NO_TRADE", "CLOSE"]


@dataclass(frozen=True)
class StrategyContext:
    session: str = "London"
    spread: float = 2.0
    news_blackout: bool = False
    regime: str = "Low Volatility Sideway"
    regime_confidence: float = 0.8


@dataclass(frozen=True)
class SignalIntent:
    action: Action
    confidence: float
    reason: dict = field(default_factory=dict)
    stop_loss: float | None = None
    take_profit: float | None = None

