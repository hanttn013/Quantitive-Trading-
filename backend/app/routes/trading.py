from fastapi import APIRouter

from .. import repository
from ..services import trading
from ..schemas import Position

router = APIRouter(prefix="/api", tags=["trading"])


@router.get("/positions", response_model=list[Position])
def get_positions() -> list[Position]:
    return repository.positions()


@router.get("/orders")
def get_orders() -> dict[str, object]:
    return {
        "open": repository.positions(),
        "pending": [],
        "closed_summary": "42 closed trades in the last 24h.",
        "rejected": [{"code": "ORDER_BLOCKED", "reason": "margin_level", "detail": "114% < 150%"}],
        "ai_suggestions": 3,
    }


@router.post("/orders/draft")
def create_order_draft(payload: dict[str, object]) -> dict[str, object]:
    return trading.draft_order(payload)


@router.post("/orders/simulate")
def simulate_order(payload: dict[str, object]) -> dict[str, object]:
    return trading.simulate_order(payload)


@router.post("/orders/confirm")
def confirm_order(payload: dict[str, object]) -> dict[str, object]:
    return trading.confirm_order(payload)


@router.post("/orders/reject")
def reject_order(payload: dict[str, object]) -> dict[str, object]:
    return trading.reject_order(payload)


@router.post("/emergency-stop")
def emergency_stop(payload: dict[str, object]) -> dict[str, object]:
    return trading.emergency_stop(payload)

