from __future__ import annotations

from statistics import mean, pstdev


def add_core_features(bars: list[dict[str, float | str]], period: int = 20) -> list[dict[str, float | str | None]]:
    rows: list[dict[str, float | str | None]] = []
    closes = [float(bar["close"]) for bar in bars]
    for index, bar in enumerate(bars):
        window = closes[max(0, index - period + 1) : index + 1]
        avg = mean(window)
        std = pstdev(window) if len(window) > 1 else 0.0
        prev_close = closes[index - 1] if index else closes[index]
        high = float(bar["high"])
        low = float(bar["low"])
        open_price = float(bar["open"])
        close = float(bar["close"])
        body = abs(close - open_price)
        candle_range = max(high - low, 1e-9)
        wick_top = high - max(open_price, close)
        wick_bottom = min(open_price, close) - low
        enriched = {
            **bar,
            "ema20": _ema(closes[: index + 1], 20),
            "ema50": _ema(closes[: index + 1], 50),
            "bb_mid": avg,
            "bb_upper": avg + 2 * std,
            "bb_lower": avg - 2 * std,
            "zscore": (close - avg) / std if std else 0.0,
            "atr": _atr(bars[max(0, index - 13) : index + 1]),
            "rsi": _rsi(closes[max(0, index - 14) : index + 1]),
            "body_ratio": body / candle_range,
            "wick_top_ratio": wick_top / candle_range,
            "wick_bottom_ratio": wick_bottom / candle_range,
            "return": (close - prev_close) / prev_close if prev_close else 0.0,
        }
        rows.append(enriched)
    return rows


def _ema(values: list[float], period: int) -> float:
    alpha = 2 / (period + 1)
    ema = values[0]
    for value in values[1:]:
        ema = alpha * value + (1 - alpha) * ema
    return ema


def _atr(bars: list[dict[str, float | str]]) -> float:
    ranges = [float(bar["high"]) - float(bar["low"]) for bar in bars]
    return mean(ranges) if ranges else 0.0


def _rsi(values: list[float]) -> float:
    if len(values) < 2:
        return 50.0
    gains = []
    losses = []
    for previous, current in zip(values, values[1:], strict=False):
        delta = current - previous
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))
    avg_gain = mean(gains) if gains else 0.0
    avg_loss = mean(losses) if losses else 0.0
    if avg_loss == 0:
        return 100.0 if avg_gain else 50.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

