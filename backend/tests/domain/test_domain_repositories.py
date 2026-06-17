from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import (
    AutoTradeSession,
    BacktestRun,
    Dataset,
    DatasetVersion,
    RiskDecision,
    Signal,
    StrategyVersion,
)
from app.db.session import make_engine
from app.repositories import DomainRepository, ImmutableEntityError
from app.seeds.demo import seed_demo_data


def make_session():
    root = Path("backend/.test-tmp")
    root.mkdir(exist_ok=True)
    engine = make_engine(f"sqlite:///{root / f'domain-{uuid4().hex}.db'}")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)()


def test_required_domain_tables_exist():
    required_tables = {
        "datasets",
        "dataset_versions",
        "market_bars",
        "market_ticks",
        "economic_events",
        "data_quality_reports",
        "feature_definitions",
        "feature_sets",
        "strategies",
        "strategy_versions",
        "models",
        "model_versions",
        "training_runs",
        "rl_training_runs",
        "backtest_runs",
        "walk_forward_folds",
        "risk_profiles",
        "strategy_deployments",
        "auto_trade_sessions",
        "signals",
        "risk_decisions",
        "live_orders",
        "positions",
        "trading_journal",
        "audit_logs",
    }

    assert required_tables.issubset(Base.metadata.tables)


def test_repository_persists_dataset_and_strategy_version():
    with make_session() as session:
        repo = DomainRepository(session)
        dataset_version = repo.create_dataset_with_version(name="Demo", source="fixture", symbol="XAUUSD", timeframe="M5")
        strategy_version = repo.create_strategy_version(name="MR", family="mean_reversion", parameters={"rsi": 14})
        session.commit()

        assert session.get(DatasetVersion, dataset_version.id).dataset.symbol == "XAUUSD"
        assert session.get(Dataset, dataset_version.dataset_id).name == "Demo"
        assert session.get(StrategyVersion, strategy_version.id).parameters == {"rsi": 14}


def test_strategy_version_becomes_immutable_after_deployment():
    with make_session() as session:
        repo = DomainRepository(session)
        strategy_version = repo.create_strategy_version(name="MR", family="mean_reversion", parameters={"rsi": 14})
        repo.deploy_strategy_version(strategy_version.id)

        with pytest.raises(ImmutableEntityError):
            repo.update_strategy_parameters(strategy_version.id, {"rsi": 21})


def test_demo_seed_stores_data_in_database():
    with make_session() as session:
        ids = seed_demo_data(session)
        session.commit()

        assert session.get(DatasetVersion, ids["dataset_version_id"]) is not None
        assert session.get(StrategyVersion, ids["strategy_version_id"]) is not None


def test_core_trading_entities_are_persistable():
    with make_session() as session:
        ids = seed_demo_data(session)
        deployment = __import__("app.db.models", fromlist=["StrategyDeployment"]).StrategyDeployment(
            id="dep-test",
            strategy_version_id=ids["strategy_version_id"],
            broker_account_id=ids["broker_account_id"],
            mode="PAPER",
            status="ACTIVE",
        )
        session.add(deployment)
        session.flush()
        auto_session = AutoTradeSession(id="ats-test", deployment_id=deployment.id, status="RUNNING", state={})
        signal = Signal(id="sig-test", deployment_id=deployment.id, action="BUY", confidence=0.7, reason={}, status="CREATED")
        session.add_all([auto_session, signal])
        session.flush()
        decision = RiskDecision(id="rd-test", signal_id=signal.id, decision="APPROVE", original_volume=0.1, approved_volume=0.1, checks={})
        session.add(decision)
        run = BacktestRun(id="bt-test", backtest_config_id="missing-later", status="QUEUED", metrics={})
        session.add(run)

        assert session.get(RiskDecision, "rd-test").decision == "APPROVE"
