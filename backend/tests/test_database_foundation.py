from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models import AppMetadata
from app.db.session import get_session, make_engine
from app.errors import AppError, install_error_handlers


def workspace_db_url(name: str) -> str:
    root = Path("backend/.test-tmp")
    root.mkdir(exist_ok=True)
    return f"sqlite:///{root / f'{name}-{uuid4().hex}.db'}"


def test_database_tables_can_be_created_and_queried():
    engine = make_engine(workspace_db_url("foundation"))
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

    with SessionLocal() as session:
        session.add(AppMetadata(key="schema", value="created"))
        session.commit()
        value = session.scalar(select(AppMetadata.value).where(AppMetadata.key == "schema"))

    assert value == "created"
    assert "app_metadata" in Base.metadata.tables


def test_fastapi_can_inject_database_session():
    engine = make_engine(workspace_db_url("dependency"))
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

    def override_session():
        with SessionLocal() as session:
            yield session

    app = FastAPI()
    app.dependency_overrides[get_session] = override_session

    @app.get("/probe")
    def probe(session: Session = Depends(get_session)):
        session.add(AppMetadata(key="probe", value="ok"))
        session.commit()
        return {"value": session.get(AppMetadata, "probe").value}

    response = TestClient(app).get("/probe")

    assert response.status_code == 200
    assert response.json() == {"value": "ok"}


def test_structured_app_error_response():
    app = FastAPI()
    install_error_handlers(app)

    @app.get("/error")
    def error():
        raise AppError(code="TEST_ERROR", message="structured", status_code=409)

    response = TestClient(app).get("/error")

    assert response.status_code == 409
    assert response.json() == {"error": {"code": "TEST_ERROR", "message": "structured"}}
