from __future__ import annotations

from dataclasses import dataclass, field

from ..features.indicators import add_core_features
from ..strategies.contracts import StrategyContext
from ..strategies.mean_reversion import XauUsdM5MeanReversionStrategy


@dataclass(frozen=True)
class CostModel:
    spread_points: float = 2.0
    commission_per_lot: float = 7.0
    slippage_points: float = 0.2
    swap_per_trade: float = 0.0
    point_value: float = 1.0

    def round_trip_cost(self, volume: float) -> dict[str, float]:
        return {
            "spread": self.spread_points * self.point_value * volume,
            "commission": self.commission_per_lot * volume,
            "slippage": self.slippage_points * self.point_value * volume,
            "swap": self.swap_per_trade * volume,
        }


@dataclass(frozen=True)
class SimulatedTrade:
    symbol: str
    side: str
    entry_time: str
    exit_time: str
    entry_price: float
    exit_price: float
    volume: float
    gross_pnl: float
    net_pnl: float
    costs: dict[str, float]
    exit_reason: str


@dataclass(frozen=True)
class BacktestResult:
    trades: list[SimulatedTrade]
    equity_curve: list[dict[str, float | str]]
    metrics: dict[str, float]
    cost_breakdown: dict[str, float] = field(default_factory=dict)


def run_backtest(
    bars: list[dict[str, object]],
    *,
    symbol: str = "XAUUSD",
    initial_equity: float = 10000.0,
    volume: float = 1.0,
    warmup_bars: int = 20,
    max_holding_bars: int = 6,
    cost_model: CostModel | None = None,
    strategy: XauUsdM5MeanReversionStrategy | None = None,
) -> BacktestResult:
    cost_model = cost_model or CostModel()
    strategy = strategy or XauUsdM5MeanReversionStrategy()
    featured = add_core_features(bars)
    trades: list[SimulatedTrade] = []
    equity = initial_equity
    equity_curve: list[dict[str, float | str]] = [{"label": "Start", "equity": equity, "drawdown": 0.0}]
    peak = equity
    index = warmup_bars

    while index < len(featured) - 2:
        row = featured[index]
        context = StrategyContext(spread=float(row.get("spread") or cost_model.spread_points))
        signal = strategy.evaluate(row, context)
        if signal.action not in {"BUY", "SELL"}:
            index += 1
            continue

        entry_bar = featured[index + 1]
        entry_price = float(entry_bar["open"])
        stop_loss = float(signal.stop_loss or entry_price)
        take_profit = float(signal.take_profit or entry_price)
        exit_bar = entry_bar
        exit_reason = "TIME_STOP"
        for future in featured[index + 1 : min(len(featured), index + 1 + max_holding_bars)]:
            high = float(future["high"])
            low = float(future["low"])
            exit_bar = future
            if signal.action == "BUY":
                if low <= stop_loss:
                    exit_reason = "STOP_LOSS"
                    break
                if high >= take_profit:
                    exit_reason = "TAKE_PROFIT"
                    break
            else:
                if high >= stop_loss:
                    exit_reason = "STOP_LOSS"
                    break
                if low <= take_profit:
                    exit_reason = "TAKE_PROFIT"
                    break

        exit_price = _exit_price(signal.action, exit_reason, exit_bar, stop_loss, take_profit)
        gross_pnl = _gross_pnl(signal.action, entry_price, exit_price, volume, cost_model.point_value)
        costs = cost_model.round_trip_cost(volume)
        net_pnl = gross_pnl - sum(costs.values())
        equity += net_pnl
        peak = max(peak, equity)
        drawdown = peak - equity
        trades.append(
            SimulatedTrade(
                symbol=symbol,
                side=signal.action,
                entry_time=str(entry_bar["timestamp"]),
                exit_time=str(exit_bar["timestamp"]),
                entry_price=entry_price,
                exit_price=exit_price,
                volume=volume,
                gross_pnl=gross_pnl,
                net_pnl=net_pnl,
                costs=costs,
                exit_reason=exit_reason,
            )
        )
        equity_curve.append({"label": str(exit_bar["timestamp"]), "equity": equity, "drawdown": drawdown})
        index = featured.index(exit_bar) + 1 if exit_bar in featured else index + max_holding_bars

    return BacktestResult(
        trades=trades,
        equity_curve=equity_curve,
        metrics=_metrics(trades, initial_equity, equity),
        cost_breakdown=_sum_costs(trades),
    )


def _exit_price(action: str, reason: str, bar: dict[str, object], stop_loss: float, take_profit: float) -> float:
    if reason == "STOP_LOSS":
        return stop_loss
    if reason == "TAKE_PROFIT":
        return take_profit
    return float(bar["close"])


def _gross_pnl(action: str, entry: float, exit_price: float, volume: float, point_value: float) -> float:
    direction = 1 if action == "BUY" else -1
    return (exit_price - entry) * direction * volume * point_value


def _metrics(trades: list[SimulatedTrade], initial_equity: float, final_equity: float) -> dict[str, float]:
    wins = [trade.net_pnl for trade in trades if trade.net_pnl > 0]
    losses = [trade.net_pnl for trade in trades if trade.net_pnl < 0]
    gross_profit = sum(max(trade.gross_pnl, 0) for trade in trades)
    gross_loss = abs(sum(min(trade.gross_pnl, 0) for trade in trades))
    net_profit = final_equity - initial_equity
    return {
        "net_profit": net_profit,
        "gross_profit": gross_profit,
        "profit_factor": gross_profit / gross_loss if gross_loss else (gross_profit if gross_profit else 0.0),
        "expectancy": net_profit / len(trades) if trades else 0.0,
        "win_rate": len(wins) / len(trades) if trades else 0.0,
        "trades": float(len(trades)),
        "average_win": sum(wins) / len(wins) if wins else 0.0,
        "average_loss": sum(losses) / len(losses) if losses else 0.0,
        "profit_before_cost": sum(trade.gross_pnl for trade in trades),
        "profit_after_cost": net_profit,
    }


def _sum_costs(trades: list[SimulatedTrade]) -> dict[str, float]:
    totals = {"spread": 0.0, "commission": 0.0, "slippage": 0.0, "swap": 0.0}
    for trade in trades:
        for key in totals:
            totals[key] += trade.costs.get(key, 0.0)
    return totals
