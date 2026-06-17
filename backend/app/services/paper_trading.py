from __future__ import annotations

from dataclasses import dataclass

from .risk import RiskDecision, evaluate_order


@dataclass(frozen=True)
class PaperOrder:
    signal_id: str
    status: str
    risk_decision: RiskDecision
    journal: dict[str, object]


def process_paper_signal(signal: dict[str, object], *, margin_level: float = 500.0) -> PaperOrder:
    risk = evaluate_order(
        environment="Paper",
        volume=float(signal.get("volume", 0.1)),
        margin_level=margin_level,
        spread_points=float(signal.get("spread", 2.0)),
        confidence=float(signal.get("confidence", 0.0)),
    )
    status = "FILLED" if risk.decision in {"APPROVE", "MODIFY"} else "REJECTED"
    return PaperOrder(
        signal_id=str(signal.get("id", "signal-paper")),
        status=status,
        risk_decision=risk,
        journal={"source": "paper_trading", "status": status, "risk": risk.checks},
    )
