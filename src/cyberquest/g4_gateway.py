"""Temporary G4 exposure gateway for the synthetic Phishing Detective demo API.

This module is **not** production infrastructure. It exists only for the
CQ-00.7.1-G4 acceptance window: a short-lived, narrowly scoped reverse proxy
that sits between a temporary HTTPS tunnel and the local FastAPI demo service.

Controls implemented here (per the approved G4 plan and the G7.1 review):

* Route and method allowlist - only the two demo routes are forwarded.
* Explicit request body limit (16 KiB by default) applied before forwarding.
* Separate GET and POST rate limits keyed by the TCP peer address. When the
  gateway is reached through a single tunnel connector, every request arrives
  from the same loopback peer, so each limit applies to the tunnel as a whole,
  not per remote end user.
* Explicit connect/read timeouts for the upstream call.
* Minimal operational logging: no bodies, no headers, no client address.
* No arbitrary outbound access: the upstream origin must be a structurally
  valid plain-HTTP URL on a loopback IP literal (127.0.0.1 or ::1).
* Mandatory HTTPS-edge enforcement: the tunnel edge must report that the client
  connection used HTTPS (`X-Forwarded-Proto: https`, cross-checked against
  `CF-Visitor`). There is no opt-out flag.
* Loopback-only bind: the gateway always listens on 127.0.0.1; the bind address
  is not operator-configurable.
* Upstream failures surface as an explicit gateway error, never a false success.

Run it with::

    python -m cyberquest.g4_gateway --upstream http://127.0.0.1:8000 --port 8080
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Iterable
from urllib.parse import urlsplit

import httpx

LOGGER = logging.getLogger("cyberquest.g4_gateway")

#: The gateway never binds to anything except the IPv4 loopback address.
GATEWAY_BIND_HOST = "127.0.0.1"

#: The only upstream hosts accepted: loopback IP literals, never DNS names.
LOOPBACK_HOSTS: frozenset[str] = frozenset({"127.0.0.1", "::1"})

#: The only routes the gateway will forward. Paths must match exactly.
ALLOWED_ROUTES: frozenset[tuple[str, str]] = frozenset(
    {
        ("GET", "/v1/demo/missions/phishing-detective"),
        ("POST", "/v1/demo/missions/phishing-detective/assessment"),
    }
)

#: Paths served by the allowlist; a wrong method on these returns 405.
ALLOWED_PATHS: frozenset[str] = frozenset(path for _, path in ALLOWED_ROUTES)

#: The method allowed on each allowlisted path.
ALLOWED_METHOD_BY_PATH: dict[str, str] = {path: method for method, path in ALLOWED_ROUTES}

DEFAULT_MAX_BODY_BYTES = 16 * 1024
DEFAULT_GET_RATE_PER_MINUTE = 60
DEFAULT_POST_RATE_PER_MINUTE = 10
DEFAULT_UPSTREAM_TIMEOUT_SECONDS = 10.0
MAX_RESPONSE_BYTES = 256 * 1024

#: Client headers that are never forwarded upstream.
STRIPPED_REQUEST_HEADERS = frozenset(
    {
        "authorization",
        "cf-visitor",
        "cookie",
        "proxy-authorization",
        "x-api-key",
        "x-forwarded-for",
        "x-forwarded-host",
        "x-forwarded-port",
        "x-forwarded-proto",
        "x-real-ip",
    }
)

FORWARDED_REQUEST_HEADERS = frozenset({"accept", "content-type"})

#: Edge-supplied headers that describe the scheme the client actually used.
FORWARDED_PROTO_HEADER = b"x-forwarded-proto"
CF_VISITOR_HEADER = b"cf-visitor"

RATE_LIMITED_METHODS = ("GET", "POST")


def validate_upstream_base_url(url: str) -> str:
    """Validate and normalise the loopback upstream origin.

    Structural validation only: the URL must be plain HTTP to a loopback IP
    literal (``127.0.0.1`` or ``::1``) with no user information, path, query or
    fragment. DNS names such as ``localhost`` are rejected because their
    resolution is not controlled by this code.
    """
    if not isinstance(url, str) or not url:
        raise ValueError("upstream URL is empty")
    if url != url.strip() or any(character.isspace() for character in url):
        raise ValueError("upstream URL must not contain whitespace")
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise ValueError(f"upstream URL is not structurally valid: {exc}") from exc
    if parts.scheme.lower() != "http":
        raise ValueError("upstream URL must use plain http (TLS terminates at the tunnel edge)")
    if parts.username is not None or parts.password is not None or "@" in parts.netloc:
        raise ValueError("upstream URL must not contain user information")
    hostname = parts.hostname or ""
    if hostname not in LOOPBACK_HOSTS:
        raise ValueError("upstream URL host must be a loopback IP literal (127.0.0.1 or ::1)")
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("upstream URL port must be between 1 and 65535")
    if parts.path not in ("", "/"):
        raise ValueError("upstream URL must not contain a path")
    if parts.query or parts.fragment or "?" in url or "#" in url:
        raise ValueError("upstream URL must not contain a query or fragment")
    host_part = f"[{hostname}]" if ":" in hostname else hostname
    netloc = f"{host_part}:{port}" if port is not None else host_part
    return f"http://{netloc}"


@dataclass
class GatewayConfig:
    """Operational limits for the temporary gateway."""

    upstream_base_url: str
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES
    get_rate_per_minute: int = DEFAULT_GET_RATE_PER_MINUTE
    post_rate_per_minute: int = DEFAULT_POST_RATE_PER_MINUTE
    upstream_timeout_seconds: float = DEFAULT_UPSTREAM_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        self.upstream_base_url = validate_upstream_base_url(self.upstream_base_url)


@dataclass
class RateLimiter:
    """In-memory sliding window rate limiter keyed by source address."""

    limit_per_minute: int
    window_seconds: float = 60.0
    _hits: dict[str, deque[float]] = field(default_factory=dict)

    def check(self, key: str) -> bool:
        """Record a request for ``key``; return False when the limit is exceeded."""
        now = time.monotonic()
        window_start = now - self.window_seconds
        hits = self._hits.setdefault(key, deque())
        while hits and hits[0] < window_start:
            hits.popleft()
        if len(hits) >= self.limit_per_minute:
            return False
        hits.append(now)
        return True

    def remaining(self, key: str) -> int:
        hits = self._hits.get(key)
        if not hits:
            return self.limit_per_minute
        return max(0, self.limit_per_minute - len(hits))


class ExposureGateway:
    """ASGI application that proxies only the allowlisted demo routes."""

    def __init__(
        self,
        config: GatewayConfig,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.config = config
        self._transport = transport
        self._limiters = {
            method: RateLimiter(
                limit_per_minute=(
                    config.get_rate_per_minute if method == "GET" else config.post_rate_per_minute
                )
            )
            for method in RATE_LIMITED_METHODS
        }

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self._send_json(send, 404, {"detail": {"code": "not_found"}}, "rejected")
            return

        method: str = scope.get("method", "GET").upper()
        path: str = scope.get("path", "")
        started = time.monotonic()
        client = scope.get("client") or ("unknown", 0)
        source_key = str(client[0])

        if not self._forwarded_https(scope):
            await self._send_json(
                send,
                403,
                {"detail": {"code": "https_required"}},
                "rejected",
                started=started,
                method=method,
                path=path,
            )
            return

        if method not in RATE_LIMITED_METHODS:
            await self._reject_non_allowlisted(method, path, send, started)
            return

        limiter = self._limiters[method]
        if not limiter.check(source_key):
            await self._send_json(
                send,
                429,
                {"detail": {"code": "rate_limited"}},
                "rate_limited",
                extra={"retry_after_seconds": 60},
            )
            return

        if (method, path) not in ALLOWED_ROUTES:
            await self._reject_non_allowlisted(method, path, send, started)
            return

        body = await self._read_body(receive)
        if body is None:
            await self._send_json(
                send,
                413,
                {"detail": {"code": "request_too_large"}},
                "rejected",
                extra={"limit_bytes": self.config.max_body_bytes},
            )
            return

        await self._forward(method, path, body, scope, send, started)

    @staticmethod
    def _forwarded_https(scope) -> bool:
        """Check the scheme the tunnel edge reports for the client connection.

        Fail-closed and always enforced: every ``X-Forwarded-Proto`` value must
        be exactly ``https``, and ``CF-Visitor`` must not report a cleartext
        scheme. The gateway is bound to loopback, so the edge header is the
        only evidence of the client's scheme; a missing header is treated as
        cleartext.
        """
        protos = [
            value
            for name, value in scope.get("headers", [])
            if name.lower() == FORWARDED_PROTO_HEADER
        ]
        if not protos or any(value.strip().lower() != b"https" for value in protos):
            return False
        visitors = [
            value for name, value in scope.get("headers", []) if name.lower() == CF_VISITOR_HEADER
        ]
        if any(b'"scheme":"http"' in value.replace(b" ", b"").lower() for value in visitors):
            return False
        return True

    async def _read_body(self, receive) -> bytes | None:
        """Read the request body, returning None when it exceeds the limit."""
        limit = self.config.max_body_bytes
        chunks: list[bytes] = []
        total = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return b""
            if message["type"] != "http.request":
                continue
            chunk = message.get("body", b"")
            total += len(chunk)
            if total > limit:
                return None
            chunks.append(chunk)
            if not message.get("more_body", False):
                break
        return b"".join(chunks)

    async def _forward(self, method, path, body, scope, send, started) -> None:
        headers = {
            name: value
            for name, value in scope.get("headers", [])
            if name.decode("latin-1").lower() in FORWARDED_REQUEST_HEADERS
        }
        url = f"{self.config.upstream_base_url.rstrip('/')}{path}"
        try:
            async with httpx.AsyncClient(
                transport=self._transport,
                timeout=self.config.upstream_timeout_seconds,
                follow_redirects=False,
            ) as client:
                response = await client.request(method, url, content=body, headers=headers)
        except httpx.TimeoutException:
            await self._send_json(
                send, 504, {"detail": {"code": "upstream_timeout"}}, "upstream_timeout"
            )
            return
        except httpx.HTTPError:
            await self._send_json(
                send, 502, {"detail": {"code": "upstream_unavailable"}}, "upstream_unavailable"
            )
            return

        payload = response.content[:MAX_RESPONSE_BYTES]
        await self._send_json(
            send,
            response.status_code,
            payload,
            "forwarded",
            content_type=response.headers.get("content-type", "application/json"),
            started=started,
            method=method,
            path=path,
        )

    async def _reject_non_allowlisted(self, method, path, send, started) -> None:
        if path in ALLOWED_PATHS:
            allowed_method = ALLOWED_METHOD_BY_PATH[path]
            await self._send_json(
                send,
                405,
                {"detail": {"code": "method_not_allowed"}},
                "rejected",
                extra={"allow": allowed_method},
                started=started,
                method=method,
                path=path,
            )
            return
        await self._send_json(
            send,
            404,
            {"detail": {"code": "not_found"}},
            "rejected",
            started=started,
            method=method,
            path=path,
        )

    async def _send_json(
        self,
        send,
        status_code: int,
        payload,
        outcome: str,
        *,
        content_type: str = "application/json",
        extra: dict | None = None,
        started: float | None = None,
        method: str | None = None,
        path: str | None = None,
    ) -> None:
        if isinstance(payload, (dict, list)):
            body = json.dumps(payload).encode("utf-8")
        elif isinstance(payload, str):
            body = payload.encode("utf-8")
        else:
            body = bytes(payload)
        headers = [(b"content-type", content_type.encode("latin-1"))]
        if extra and "retry_after_seconds" in extra:
            headers.append((b"retry-after", str(extra["retry_after_seconds"]).encode("latin-1")))
        if extra and "allow" in extra:
            headers.append((b"allow", str(extra["allow"]).encode("latin-1")))
        await send({"type": "http.response.start", "status": status_code, "headers": headers})
        await send({"type": "http.response.body", "body": body})
        self._log(outcome, method, path, status_code, started)

    def _log(self, outcome: str, method: str | None, path: str | None, status: int, started) -> None:
        duration_ms = int((time.monotonic() - started) * 1000) if started else 0
        LOGGER.info(
            "gateway_request method=%s path=%s status=%s duration_ms=%s outcome=%s",
            method or "-",
            path or "-",
            status,
            duration_ms,
            outcome,
        )


def create_gateway_app(
    upstream_base_url: str,
    *,
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
    get_rate_per_minute: int = DEFAULT_GET_RATE_PER_MINUTE,
    post_rate_per_minute: int = DEFAULT_POST_RATE_PER_MINUTE,
    upstream_timeout_seconds: float = DEFAULT_UPSTREAM_TIMEOUT_SECONDS,
    transport: httpx.AsyncBaseTransport | None = None,
) -> ExposureGateway:
    """Build the gateway application used by the G4 tunnel and by tests."""
    config = GatewayConfig(
        upstream_base_url=upstream_base_url,
        max_body_bytes=max_body_bytes,
        get_rate_per_minute=get_rate_per_minute,
        post_rate_per_minute=post_rate_per_minute,
        upstream_timeout_seconds=upstream_timeout_seconds,
    )
    return ExposureGateway(config, transport=transport)


async def _health_app(scope, receive, send) -> None:
    """Loopback-only health endpoint for the gateway process itself."""
    body = json.dumps({"status": "ok"}).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def _serve_health(port: int) -> None:
    import uvicorn

    config = uvicorn.Config(_health_app, host="127.0.0.1", port=port, log_level="warning")
    await uvicorn.Server(config).serve()


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Temporary G4 exposure gateway.")
    parser.add_argument(
        "--upstream",
        required=True,
        help=(
            "Origin URL of the local FastAPI demo service. Must be plain http to a "
            "loopback IP literal (127.0.0.1 or ::1), with no userinfo, path, query or fragment."
        ),
    )
    parser.add_argument("--port", type=int, default=8080, help="Bind port for the gateway.")
    parser.add_argument("--max-body-bytes", type=int, default=DEFAULT_MAX_BODY_BYTES)
    parser.add_argument("--get-rate-per-minute", type=int, default=DEFAULT_GET_RATE_PER_MINUTE)
    parser.add_argument("--post-rate-per-minute", type=int, default=DEFAULT_POST_RATE_PER_MINUTE)
    parser.add_argument(
        "--health-port",
        type=int,
        default=0,
        help="Optional loopback port for a gateway health endpoint.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        app = create_gateway_app(
            args.upstream,
            max_body_bytes=args.max_body_bytes,
            get_rate_per_minute=args.get_rate_per_minute,
            post_rate_per_minute=args.post_rate_per_minute,
        )
    except ValueError as exc:
        raise SystemExit(f"Refusing to start: {exc}") from exc
    LOGGER.info(
        "gateway_start upstream=%s bind=%s:%s max_body_bytes=%s get_rate=%s post_rate=%s "
        "https_edge=enforced",
        app.config.upstream_base_url,
        GATEWAY_BIND_HOST,
        args.port,
        args.max_body_bytes,
        args.get_rate_per_minute,
        args.post_rate_per_minute,
    )
    if args.health_port:
        asyncio.run(_run_with_health(app, args))
    else:
        import uvicorn

        uvicorn.run(app, host=GATEWAY_BIND_HOST, port=args.port, log_level="warning")
    return 0


async def _run_with_health(app, args) -> None:
    import uvicorn

    health_task = asyncio.create_task(_serve_health(args.health_port))
    server = uvicorn.Server(
        uvicorn.Config(app, host=GATEWAY_BIND_HOST, port=args.port, log_level="warning")
    )
    with contextlib.suppress(asyncio.CancelledError):
        await server.serve()
    health_task.cancel()


if __name__ == "__main__":  # pragma: no cover - operational entry point
    raise SystemExit(main())
