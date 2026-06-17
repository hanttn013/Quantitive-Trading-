from sqlalchemy.orm import Session

from ..db import models
from ..repositories.domain import DomainRepository, new_id


def seed_demo_data(session: Session) -> dict[str, str]:
    repo = DomainRepository(session)
    dataset_version = repo.create_dataset_with_version(
        name="XAUUSD M5 Demo Dataset",
        source="fixture",
        symbol="XAUUSD",
        timeframe="M5",
    )
    strategy_version = repo.create_strategy_version(
        name="XAUUSD M5 Mean Reversion",
        family="mean_reversion",
        parameters={"rsi_period": 14, "bb_period": 20, "max_spread": 30},
    )
    broker_account = models.BrokerAccount(
        id=new_id("broker"),
        label="Demo Account",
        broker="Simulated",
        server="local",
        account_type="Demo",
        masked_account=".... 0001",
    )
    risk_profile = models.RiskProfile(
        id=new_id("risk"),
        name="Conservative XAUUSD",
        limits={"max_risk_per_trade": 0.005, "max_daily_loss": 300},
        non_overridable=["max_daily_loss"],
    )
    cost_model = models.CostModel(
        id=new_id("cost"),
        name="XAUUSD Fixed Cost Demo",
        config={"spread_points": 2.0, "commission": 3.5, "slippage_points": 1.0},
    )
    session.add_all([broker_account, risk_profile, cost_model])
    session.flush()
    return {
        "dataset_version_id": dataset_version.id,
        "strategy_version_id": strategy_version.id,
        "broker_account_id": broker_account.id,
        "risk_profile_id": risk_profile.id,
        "cost_model_id": cost_model.id,
    }

