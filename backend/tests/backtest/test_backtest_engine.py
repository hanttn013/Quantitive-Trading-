from backend.app.engines.backtest import CostModel, run_backtest
from backend.app.engines.strategies.contracts import SignalIntent


class OneShotBuyStrategy:
    def __init__(self) -> None:
        self.called = False

    def evaluate(self, feature_row, context):
        if self.called:
            return SignalIntent("NO_TRADE", 0.0, {"blocked": "test"})
        self.called = True
        close = float(feature_row["close"])
        return SignalIntent("BUY", 0.9, {"setup": "test"}, stop_loss=close - 10, take_profit=close + 4)


def test_backtest_executes_next_bar_and_costs_reduce_profit():
    bars = [
        {"timestamp": "2026-06-01T00:00:00Z", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1, "spread": 1.0},
        {"timestamp": "2026-06-01T00:05:00Z", "open": 100.5, "high": 105.0, "low": 100.0, "close": 104.0, "volume": 1, "spread": 1.0},
        {"timestamp": "2026-06-01T00:10:00Z", "open": 104.0, "high": 106.0, "low": 103.0, "close": 105.0, "volume": 1, "spread": 1.0},
    ]

    result = run_backtest(
        bars,
        warmup_bars=0,
        max_holding_bars=2,
        strategy=OneShotBuyStrategy(),
        cost_model=CostModel(spread_points=1.0, commission_per_lot=1.0, slippage_points=0.5),
    )

    assert len(result.trades) == 1
    assert result.trades[0].entry_price == 100.5
    assert result.trades[0].exit_reason == "TAKE_PROFIT"
    assert result.metrics["profit_before_cost"] > result.metrics["profit_after_cost"]
    assert result.cost_breakdown["spread"] == 1.0
