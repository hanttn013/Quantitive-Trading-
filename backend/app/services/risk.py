from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RiskDecisionValue = Literal["APPROVE", "MODIFY", "REJECT"]


@dataclass(frozen=True)
class RiskDecision:
    decision: RiskDecisionValue
    original_volume: float
    approved_volume: float
    checks: dict[str, bool]
    rejection_code: str | None = None


def evaluate_order(
    *,
    environment: str,
    volume: float,
    margin_level: float,
    spread_points: float,
    confidence: float,
) -> RiskDecision:
    checks = {
        "environment_known": environment in {"Backtest", "Paper", "Live"},
        "volume_positive": volume > 0,
        "margin_level_ok": margin_level >= 150,
        "spread_ok": spread_points <= 30,
        "confidence_ok": confidence >= 0.55,
    }

    if not all(checks.values()):
        failed = next(name for name, ok in checks.items() if not ok)
        return RiskDecision(
            decision="REJECT",
            original_volume=volume,
            approved_volume=0,
            checks=checks,
            rejection_code=failed.upper(),
        )

    approved_volume = min(volume, 1.0)
    if approved_volume != volume:
        return RiskDecision(
            decision="MODIFY",
            original_volume=volume,
            approved_volume=approved_volume,
            checks=checks,
            rejection_code="MAX_LOT_SIZE",
        )

    return RiskDecision(decision="APPROVE", original_volume=volume, approved_volume=volume, checks=checks)

