from __future__ import annotations


def label_regime(state_statistics: dict[str, float], confidence: float) -> tuple[str, float]:
    if confidence < 0.55:
        return "UNCERTAIN", confidence
    volatility = state_statistics.get("volatility", 0.0)
    trend = state_statistics.get("trend_strength", 0.0)
    avg_return = state_statistics.get("average_return", 0.0)
    spread = state_statistics.get("average_spread", 0.0)
    if spread > 20 or volatility > 3.0:
        return "News Shock", confidence
    if abs(trend) < 0.25 and volatility < 1.5:
        return "Low Volatility Sideway", confidence
    if trend > 0.5 and avg_return > 0:
        return "Bull Trend", confidence
    if trend < -0.5 and avg_return < 0:
        return "Bear Trend", confidence
    return "High Volatility Trend", confidence

