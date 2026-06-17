from fastapi import APIRouter

from ..dependencies import DbSession
from ..engines.data.fixtures import xauusd_m5_fixture
from ..repositories.data import DataRepository

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/fixtures/xauusd-m5")
def create_xauusd_fixture(session: DbSession) -> dict[str, object]:
    repo = DataRepository(session)
    dataset = repo.create_dataset(name="XAUUSD M5 Fixture", source="fixture", symbol="XAUUSD", timeframe="M5")
    version, report = repo.create_version_with_bars(dataset, xauusd_m5_fixture())
    session.commit()
    return {
        "dataset_id": dataset.id,
        "dataset_version_id": version.id,
        "status": version.status,
        "row_count": version.row_count,
        "data_quality_report_id": report.id,
    }


@router.get("/dataset-versions")
def list_dataset_versions(session: DbSession) -> list[dict[str, object]]:
    return [
        {
            "id": version.id,
            "dataset_id": version.dataset_id,
            "version": version.version,
            "status": version.status,
            "row_count": version.row_count,
            "immutable": version.immutable,
        }
        for version in DataRepository(session).get_versions()
    ]


@router.get("/dataset-versions/{version_id}/quality-report")
def get_quality_report(version_id: str, session: DbSession) -> dict[str, object]:
    report = DataRepository(session).get_report(version_id)
    if report is None:
        return {"status": "NOT_FOUND", "dataset_version_id": version_id}
    return {
        "id": report.id,
        "dataset_version_id": report.dataset_version_id,
        "status": report.status,
        "critical_issue_count": report.critical_issue_count,
        "checks": report.checks,
    }


@router.get("/dataset-versions/{version_id}/bars")
def get_bars(version_id: str, session: DbSession) -> list[dict[str, object]]:
    return [
        {
            "timestamp": bar.timestamp,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
            "spread": bar.spread,
        }
        for bar in DataRepository(session).bars_for_version(version_id)
    ]

