from __future__ import annotations

from .contracts import SignalIntent, StrategyContext


class XauUsdM5MeanReversionStrategy:
    def __init__(self, max_spread: float = 30.0, min_confidence: float = 0.55):
        self.max_spread = max_spread
        self.min_confidence = min_confidence

    def evaluate(self, feature_row: dict[str, float | str | None], context: StrategyContext) -> SignalIntent:
        close = float(feature_row["close"])
        atr = float(feature_row.get("atr") or 1.0)
        if context.news_blackout:
            return SignalIntent("NO_TRADE", 0.0, {"blocked": "NEWS_BLACKOUT"})
        if context.spread > self.max_spread:
            return SignalIntent("NO_TRADE", 0.0, {"blocked": "SPREAD"})
        if context.regime in {"High Volatility Trend", "News Shock", "UNCERTAIN"}:
            return SignalIntent("NO_TRADE", 0.0, {"blocked": "REGIME", "regime": context.regime})

        rsi = float(feature_row.get("rsi") or 50)
        zscore = float(feature_row.get("zscore") or 0)
        lower = float(feature_row.get("bb_lower") or close)
        upper = float(feature_row.get("bb_upper") or close)
        wick_bottom = float(feature_row.get("wick_bottom_ratio") or 0)
        wick_top = float(feature_row.get("wick_top_ratio") or 0)

        if close <= lower and rsi <= 35 and zscore <= -1.0 and wick_bottom >= 0.25:
            return SignalIntent("BUY", 0.7, {"setup": "LOWER_BAND_REVERSION"}, close - 1.5 * atr, close + 2.5 * atr)
        if close >= upper and rsi >= 65 and zscore >= 1.0 and wick_top >= 0.25:
            return SignalIntent("SELL", 0.7, {"setup": "UPPER_BAND_REVERSION"}, close + 1.5 * atr, close - 2.5 * atr)
        return SignalIntent("NO_TRADE", 0.2, {"blocked": "NO_SETUP"})

