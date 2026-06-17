from __future__ import annotations

from datetime import datetime, timedelta, timezone


def xauusd_m5_fixture(count: int = 120) -> list[dict[str, object]]:
    start = datetime(2026, 6, 1, 8, 0, tzinfo=timezone.utc)
    price = 2330.0
    bars: list[dict[str, object]] = []
    for i in range(count):
        drift = 0.45 if i % 11 < 6 else -0.35
        open_price = price
        close = round(open_price + drift, 2)
        high = round(max(open_price, close) + 0.7, 2)
        low = round(min(open_price, close) - 0.7, 2)
        bars.append(
            {
                "timestamp": (start + timedelta(minutes=5 * i)).isoformat(),
                "open": round(open_price, 2),
                "high": high,
                "low": low,
                "close": close,
                "volume": 500 + i,
                "spread": 2.0,
            }
        )
        price = close
    return bars

