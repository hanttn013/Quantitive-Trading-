from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_session, make_engine
from app.main import create_app


def client_with_db():
    root = Path("backend/.test-tmp")
    root.mkdir(exist_ok=True)
    engine = make_engine(f"sqlite:///{root / f'data-routes-{uuid4().hex}.db'}")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    app = create_app()

    def override_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    return TestClient(app)


def test_fixture_ingest_creates_dataset_version_quality_report_and_bars():
    client = client_with_db()

    created = client.post("/api/data/fixtures/xauusd-m5").json()
    versions = client.get("/api/data/dataset-versions").json()
    report = client.get(f"/api/data/dataset-versions/{created['dataset_version_id']}/quality-report").json()
    bars = client.get(f"/api/data/dataset-versions/{created['dataset_version_id']}/bars").json()

    assert created["status"] == "VALIDATED"
    assert versions[0]["row_count"] == 120
    assert report["status"] == "VALID"
    assert len(bars) == 120
