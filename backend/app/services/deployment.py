from __future__ import annotations

from dataclasses import dataclass


LIFECYCLE = ["DRAFT", "BACKTESTED", "VALIDATED", "PAPER_TRADING", "PAPER_APPROVED", "LIVE_APPROVED", "LIVE", "PAUSED", "RETIRED"]


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    next_status: str | None
    failures: list[str]


def evaluate_deployment_gates(strategy_state: dict[str, object], target: str) -> GateResult:
    failures: list[str] = []
    if target not in LIFECYCLE:
        failures.append("UNKNOWN_TARGET_STATUS")
    if target in {"PAPER_TRADING", "PAPER_APPROVED", "LIVE_APPROVED", "LIVE"}:
        if not strategy_state.get("oos_passed"):
            failures.append("OOS_REQUIRED")
        if not strategy_state.get("walk_forward_passed"):
            failures.append("WALK_FORWARD_REQUIRED")
        if not strategy_state.get("leakage_valid", True):
            failures.append("LEAKAGE_INVALID")
        if float(strategy_state.get("profit_factor", 0.0)) < 1.1:
            failures.append("PROFIT_FACTOR_TOO_LOW")
        if int(strategy_state.get("trades", 0)) < 30:
            failures.append("INSUFFICIENT_TRADES")
    if target in {"LIVE_APPROVED", "LIVE"} and not strategy_state.get("paper_approved"):
        failures.append("PAPER_TRADING_REQUIRED")
    if strategy_state.get("model_status") == "PREDICTIVELY_VALID/TRADING_INVALID":
        failures.append("MODEL_TRADING_INVALID")
    return GateResult(allowed=not failures, next_status=target if not failures else None, failures=failures)
