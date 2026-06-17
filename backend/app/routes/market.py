from fastapi import APIRouter

from .. import repository
from ..schemas import CalendarEvent, FeedIntegrity, MarketQuote

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/watch", response_model=list[MarketQuote])
def get_market_watch() -> list[MarketQuote]:
    return repository.market_watch()


@router.get("/feed-integrity", response_model=list[FeedIntegrity])
def get_feed_integrity() -> list[FeedIntegrity]:
    return repository.feed_integrity()


@router.get("/calendar", response_model=list[CalendarEvent])
def get_calendar() -> list[CalendarEvent]:
    return repository.calendar()


@router.get("/candles")
def get_candles(symbol: str = "XAUUSD", timeframe: str = "M5") -> dict[str, object]:
    candles = []
    price = 2330.0
    for i in range(120):
        drift = 0.4 if i % 9 < 5 else -0.35
        open_price = price
        close = round(open_price + drift, 2)
        high = round(max(open_price, close) + 0.8, 2)
        low = round(min(open_price, close) - 0.8, 2)
        candles.append({"t": i, "o": open_price, "h": high, "l": low, "c": close, "v": 500 + i})
        price = close
    return {"symbol": symbol, "timeframe": timeframe, "candles": candles}

