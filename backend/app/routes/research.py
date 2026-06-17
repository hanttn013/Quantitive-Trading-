from fastapi import APIRouter

from .. import repository
from ..engines.backtest import CostModel, run_backtest
from ..engines.data.fixtures import xauusd_m5_fixture
from ..schemas import AIModel, BacktestSummary

router = APIRouter(prefix="/api", tags=["research"])


@router.get("/models", response_model=list[AIModel])
def get_models() -> list[AIModel]:
    return repository.models()


@router.get("/strategies")
def get_strategies() -> list[dict[str, object]]:
    return [
        {
            "id": "strat-xau-mr-m5",
            "name": "XAUUSD M5 Mean Reversion",
            "status": "Draft",
            "symbol": "XAUUSD",
            "timeframe": "M5",
            "gate": "Requires OOS + WFO + Paper",
        },
        {
            "id": "strat-liquidity-sweep",
            "name": "ML Liquidity Sweep Classifier",
            "status": "Design",
            "symbol": "XAUUSD",
            "timeframe": "M5",
            "gate": "Requires labels and cost-aware validation",
        },
        {
            "id": "strat-hmm-switch",
            "name": "HMM Regime Strategy Switch",
            "status": "Design",
            "symbol": "XAUUSD",
            "timeframe": "M15",
            "gate": "Requires regime stability analysis",
        },
    ]


@router.get("/backtests/summary", response_model=BacktestSummary)
def get_backtest_summary() -> BacktestSummary:
    result = run_backtest(xauusd_m5_fixture(160), cost_model=CostModel(spread_points=2.0, commission_per_lot=3.5, slippage_points=0.2))
    fallback = repository.backtest_summary()
    metrics = result.metrics
    return BacktestSummary(
        config=fallback.config,
        equity_curve=[
            {"label": str(point["label"]), "equity": float(point["equity"]), "drawdown": float(point["drawdown"])}
            for point in result.equity_curve[-24:]
        ],
        results=[
            {"label": "Net Profit", "value": f"${metrics['net_profit']:.2f}", "tone": "pos" if metrics["net_profit"] >= 0 else "neg"},
            {"label": "Profit Factor", "value": f"{metrics['profit_factor']:.2f}", "tone": "default"},
            {"label": "Trades", "value": str(int(metrics["trades"])), "tone": "default"},
            {"label": "Win Rate", "value": f"{metrics['win_rate'] * 100:.1f}%", "tone": "default"},
            {"label": "Cost", "value": f"${sum(result.cost_breakdown.values()):.2f}", "tone": "warn"},
            {"label": "Expectancy", "value": f"${metrics['expectancy']:.2f}", "tone": "default"},
        ],
    )


@router.get("/backtests/{backtest_id}")
def get_backtest(backtest_id: str) -> dict[str, object]:
    return {"id": backtest_id, "status": "Completed", "summary": get_backtest_summary(), "source": "engine"}


@router.get("/backtests/{backtest_id}/progress")
def get_backtest_progress(backtest_id: str) -> dict[str, object]:
    return {"id": backtest_id, "status": "Completed", "progress": 100}
