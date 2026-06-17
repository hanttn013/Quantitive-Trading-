from __future__ import annotations

from datetime import datetime


def validate_market_bars(bars: list[dict[str, object]]) -> dict[str, object]:
    issues: list[dict[str, object]] = []
    seen: set[str] = set()
    previous_ts: datetime | None = None

    for index, bar in enumerate(bars):
        timestamp = str(bar.get("timestamp"))
        try:
            current_ts = datetime.fromisoformat(timestamp)
        except ValueError:
            issues.append({"index": index, "code": "INVALID_TIMESTAMP", "timestamp": timestamp})
            current_ts = None

        if timestamp in seen:
            issues.append({"index": index, "code": "DUPLICATE_TIMESTAMP", "timestamp": timestamp})
        seen.add(timestamp)

        if current_ts and previous_ts and current_ts <= previous_ts:
            issues.append({"index": index, "code": "NON_MONOTONIC_TIMESTAMP", "timestamp": timestamp})
        if current_ts:
            previous_ts = current_ts

        high = float(bar.get("high", 0))
        low = float(bar.get("low", 0))
        open_price = float(bar.get("open", 0))
        close = float(bar.get("close", 0))
        spread = float(bar.get("spread", 0))
        volume = float(bar.get("volume", 0))

        if high < low:
            issues.append({"index": index, "code": "HIGH_BELOW_LOW"})
        if high < max(open_price, close) or low > min(open_price, close):
            issues.append({"index": index, "code": "OHLC_INCONSISTENT"})
        if spread < 0:
            issues.append({"index": index, "code": "NEGATIVE_SPREAD"})
        if volume < 0:
            issues.append({"index": index, "code": "NEGATIVE_VOLUME"})

    critical = [issue for issue in issues if issue["code"] != "NON_MONOTONIC_TIMESTAMP"]
    return {
        "status": "VALID" if not issues else "INVALID",
        "row_count": len(bars),
        "critical_issue_count": len(critical),
        "issues": issues,
    }

