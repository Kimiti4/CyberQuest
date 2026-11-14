"""CYBERQUEST API application factory."""
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from starlette.responses import JSONResponse

from cyberquest.demo import router as demo_router

MAX_REQUEST_BODY_BYTES = 64 * 1024


class RequestTooLarge(Exception):
    """Raised when a request body exceeds the configured limit."""


class RequestBodyLimitMiddleware:
    """Reject oversized HTTP bodies before route parsing."""

    def __init__(self, app, max_body_bytes: int = MAX_REQUEST_BODY_BYTES):
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        content_length = headers.get(b"content-length")
        if content_length is not None:
            try:
                length = int(content_length)
            except ValueError:
                length = None
            if length is not None and length > self.max_body_bytes:
                await self._reject(scope, receive, send)
                return

        received = 0
        response_started = False

        async def limited_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_body_bytes:
                    raise RequestTooLarge
            return message

        async def tracked_send(message):
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, tracked_send)
        except RequestTooLarge:
            if response_started:
                raise
            await self._reject(scope, receive, send)

    @staticmethod
    async def _reject(scope, receive, send) -> None:
        response = JSONResponse(
            status_code=413,
            content={"detail": {"code": "request_too_large"}},
        )
        await response(scope, receive, send)


def create_app(database_url: str | None = None) -> FastAPI:
    """Create the API; readiness fails closed when the database is not configured."""
    app = FastAPI(
        title="CYBERQUEST API",
        version="0.2.0",
        description="Foundation API with a stateless synthetic Phishing Detective demo.",
    )
    app.add_middleware(RequestBodyLimitMiddleware)
    app.state.database_url = database_url
    app.state.engine = create_engine(database_url, pool_pre_ping=True) if database_url else None
    app.include_router(demo_router)

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
            raise HTTPException(
                status_code=503, detail={"code": "database_unavailable"}
            ) from exc
        return {"status": "ok"}

    return app


app = create_app()
