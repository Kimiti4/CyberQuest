from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from cyberquest.main import create_app


def test_liveness_does_not_depend_on_database() -> None:
    client = TestClient(create_app())
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_fails_closed_without_database_configuration() -> None:
    client = TestClient(create_app())
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "database_not_configured"


def test_readiness_checks_database_connectivity() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    app = create_app("sqlite+pysqlite:///:memory:")
    app.state.engine = engine
    response = TestClient(app).get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    engine.dispose()
