from fastapi import APIRouter

from .. import repository
from ..schemas import Agent, Metric, PortfolioSummary, RiskMonitor

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard/metrics", response_model=list[Metric])
def get_dashboard_metrics() -> list[Metric]:
    return repository.dashboard_metrics()


@router.get("/agents", response_model=list[Agent])
def get_agents() -> list[Agent]:
    return repository.agents()


@router.get("/risk/monitor", response_model=RiskMonitor)
def get_risk_monitor() -> RiskMonitor:
    return repository.risk_monitor()


@router.get("/portfolio", response_model=PortfolioSummary)
def get_portfolio() -> PortfolioSummary:
    return repository.portfolio()
