from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import models
from ..engines.data.validation import validate_market_bars
from .domain import new_id


class DataRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_dataset(self, *, name: str, source: str, symbol: str, timeframe: str, timezone: str = "UTC") -> models.Dataset:
        dataset = models.Dataset(id=new_id("ds"), name=name, source=source, symbol=symbol, timeframe=timeframe, timezone=timezone)
        self.session.add(dataset)
        self.session.flush()
        return dataset

    def create_version_with_bars(self, dataset: models.Dataset, bars: list[dict[str, object]]) -> tuple[models.DatasetVersion, models.DataQualityReport]:
        next_version = len(dataset.versions) + 1
        report_data = validate_market_bars(bars)
        version = models.DatasetVersion(
            id=new_id("dsv"),
            dataset_id=dataset.id,
            version=next_version,
            status="VALIDATED" if report_data["status"] == "VALID" else "INVALID",
            row_count=len(bars),
            start_time=str(bars[0]["timestamp"]) if bars else None,
            end_time=str(bars[-1]["timestamp"]) if bars else None,
        )
        self.session.add(version)
        self.session.flush()
        for bar in bars:
            self.session.add(models.MarketBar(dataset_version_id=version.id, **bar))
        report = models.DataQualityReport(
            id=new_id("dqr"),
            dataset_version_id=version.id,
            status=str(report_data["status"]),
            checks=report_data,
            critical_issue_count=int(report_data["critical_issue_count"]),
        )
        self.session.add(report)
        self.session.flush()
        return version, report

    def get_versions(self) -> list[models.DatasetVersion]:
        return list(self.session.scalars(select(models.DatasetVersion).order_by(models.DatasetVersion.created_at)))

    def get_report(self, version_id: str) -> models.DataQualityReport | None:
        return self.session.scalar(select(models.DataQualityReport).where(models.DataQualityReport.dataset_version_id == version_id))

    def bars_for_version(self, version_id: str) -> list[models.MarketBar]:
        return list(self.session.scalars(select(models.MarketBar).where(models.MarketBar.dataset_version_id == version_id).order_by(models.MarketBar.timestamp)))

