"""CYBERQUEST API application factory."""

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def create_app(database_url: str | None = None) -> FastAPI:
    """Create the API; readiness fails closed when the database is not configured."""
    app = FastAPI(
        title="CYBERQUEST API",
        version="0.1.0",
        description="Initial backend foundation; learner endpoints are not implemented.",
    )
    app.state.database_url = database_url
    app.state.engine = (
        create_engine(database_url, pool_pre_ping=True)
        if database_url
        else None
    )

    @app.get("/health/live", tags=["Health"])
    def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["Health"])
    def ready() -> dict[str, str]:
        engine: Engine | None = app.state.engine
        if engine is None:
            raise HTTPException(status_code=503, detail={"code": "database_not_configured"})
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except Exception as exc:
            # Do not expose connection strings, credentials or driver internals.
            raise HTTPException(
                status_code=503,
                detail={"code": "database_unavailable"},
            ) from exc
        return {"status": "ok"}

    return app


app = create_app()
