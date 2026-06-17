from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from ..db import models


class ImmutableEntityError(ValueError):
    pass


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:10]}"


class DomainRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_dataset_with_version(self, *, name: str, source: str, symbol: str, timeframe: str) -> models.DatasetVersion:
        dataset = models.Dataset(id=new_id("ds"), name=name, source=source, symbol=symbol, timeframe=timeframe)
        version = models.DatasetVersion(id=new_id("dsv"), dataset=dataset, version=1, status="VALIDATED")
        self.session.add(dataset)
        self.session.add(version)
        self.session.flush()
        return version

    def mark_dataset_version_used(self, version_id: str) -> models.DatasetVersion:
        version = self.session.get(models.DatasetVersion, version_id)
        if version is None:
            raise KeyError(version_id)
        version.immutable = True
        version.status = "USED"
        self.session.flush()
        return version

    def create_strategy_version(self, *, name: str, family: str, parameters: dict) -> models.StrategyVersion:
        strategy = models.Strategy(id=new_id("strat"), name=name, family=family)
        version = models.StrategyVersion(
            id=new_id("stratv"),
            strategy=strategy,
            version=1,
            lifecycle_status="DRAFT",
            parameters=parameters,
            entry_rules={},
            exit_rules={},
        )
        self.session.add(strategy)
        self.session.add(version)
        self.session.flush()
        return version

    def deploy_strategy_version(self, version_id: str) -> models.StrategyVersion:
        version = self.session.get(models.StrategyVersion, version_id)
        if version is None:
            raise KeyError(version_id)
        version.lifecycle_status = "PAPER_TRADING"
        version.immutable = True
        self.session.flush()
        return version

    def update_strategy_parameters(self, version_id: str, parameters: dict) -> models.StrategyVersion:
        version = self.session.get(models.StrategyVersion, version_id)
        if version is None:
            raise KeyError(version_id)
        if version.immutable:
            raise ImmutableEntityError("Deployed StrategyVersion is immutable; create a new version instead.")
        version.parameters = parameters
        self.session.flush()
        return version

