"""Tests for the temporary G4 exposure gateway.

The gateway is temporary test infrastructure for the CQ-00.7.1-G4 acceptance
window. These tests pin the security controls required by the approved plan so
they cannot silently regress.
"""
from __future__ import annotations

import asyncio
import json
import logging

import httpx
import pytest

from cyberquest import g4_gateway
from cyberquest.g4_gateway import (
    DEFAULT_MAX_BODY_BYTES,
    create_gateway_app,
    validate_upstream_base_url,
)

MISSION_PATH = "/v1/demo/missions/phishing-detective"
ASSESSMENT_PATH = "/v1/demo/missions/phishing-detective/assessment"
EDGE_HEADERS = {"X-Forwarded-Proto": "https"}


class RecordingApp:
    """Minimal upstream stand-in that records what the gateway forwarded."""

    def __init__(self, status_code: int = 200, body: dict | None = None) -> None:
        self.status_code = status_code
        self.body = body if body is not None else {"ok": True}
        self.requests: list[httpx.Request] = []

    async def __call__(self, scope, receive, send) -> None:
        body = b""
        while True:
            message = await receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                if not message.get("more_body", False):
                    break
            elif message["type"] == "http.disconnect":
                break
        request = httpx.Request(
            scope["method"], scope["path"], headers=scope.get("headers", []), content=body
        )
        self.requests.append(request)
        payload = json.dumps(self.body).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send({"type": "http.response.body", "body": payload})


def call(gateway, method: str, path: str, *, edge: bool = True, headers=None, **kwargs) -> httpx.Response:
    merged_headers = dict(EDGE_HEADERS) if edge else {}
    if headers:
        merged_headers.update(headers)

    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=gateway)
        async with httpx.AsyncClient(transport=transport, base_url="http://gateway") as client:
            return await client.request(method, path, headers=merged_headers, **kwargs)

    return asyncio.run(run())


def build_gateway(upstream, **kwargs):
    transport = httpx.ASGITransport(app=upstream)
    return create_gateway_app("http://127.0.0.1:8000", transport=transport, **kwargs)


def test_allowed_mission_route_is_forwarded() -> None:
    upstream = RecordingApp(body={"mission_id": "phishing-detective-suspicious-invoice"})
    gateway = build_gateway(upstream)

    response = call(gateway, "GET", MISSION_PATH)

    assert response.status_code == 200
    assert response.json() == {"mission_id": "phishing-detective-suspicious-invoice"}
    assert [request.url.path for request in upstream.requests] == [MISSION_PATH]


def test_allowed_assessment_route_is_forwarded_with_learner_choices_only() -> None:
    upstream = RecordingApp(body={"score": 10})
    gateway = build_gateway(upstream)
    payload = {"selected_indicator_ids": ["sender_domain"], "response_id": "verify_and_report"}

    response = call(gateway, "POST", ASSESSMENT_PATH, json=payload)

    assert response.status_code == 200
    forwarded = json.loads(upstream.requests[0].content)
    assert forwarded == payload


def test_unknown_route_is_rejected_without_reaching_upstream() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream)

    response = call(gateway, "GET", "/health/live")

    assert response.status_code == 404
    assert response.json() == {"detail": {"code": "not_found"}}
    assert upstream.requests == []


def test_interactive_documentation_routes_are_rejected() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream)

    for path in ("/docs", "/redoc", "/openapi.json"):
        response = call(gateway, "GET", path)
        assert response.status_code == 404, path

    assert upstream.requests == []


def test_unsupported_method_on_allowed_path_is_rejected() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream)

    response = call(gateway, "POST", MISSION_PATH, json={})

    assert response.status_code == 405
    assert response.json() == {"detail": {"code": "method_not_allowed"}}
    assert response.headers["allow"] == "GET"
    assert upstream.requests == []


def test_delete_and_put_are_rejected() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream)

    for method in ("DELETE", "PUT", "PATCH"):
        response = call(gateway, method, ASSESSMENT_PATH)
        assert response.status_code == 405, method

    assert upstream.requests == []


def test_oversized_body_is_rejected_before_reaching_upstream() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream, max_body_bytes=64)
    oversized = "x" * 200

    response = call(gateway, "POST", ASSESSMENT_PATH, content=oversized)

    assert response.status_code == 413
    assert response.json() == {"detail": {"code": "request_too_large"}}
    assert upstream.requests == []


def test_default_body_limit_is_sixteen_kibibytes() -> None:
    assert DEFAULT_MAX_BODY_BYTES == 16 * 1024


def test_body_at_the_limit_is_accepted() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream, max_body_bytes=128)
    body = "x" * 128

    response = call(gateway, "POST", ASSESSMENT_PATH, content=body)

    assert response.status_code == 200


def test_post_rate_limit_is_enforced() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream, post_rate_per_minute=2)

    first = call(gateway, "POST", ASSESSMENT_PATH, json={})
    second = call(gateway, "POST", ASSESSMENT_PATH, json={})
    third = call(gateway, "POST", ASSESSMENT_PATH, json={})

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert third.json() == {"detail": {"code": "rate_limited"}}
    assert third.headers["retry-after"] == "60"
    assert len(upstream.requests) == 2


def test_get_and_post_rate_limits_are_separate() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream, get_rate_per_minute=5, post_rate_per_minute=1)

    call(gateway, "POST", ASSESSMENT_PATH, json={})
    limited = call(gateway, "POST", ASSESSMENT_PATH, json={})
    allowed_get = call(gateway, "GET", MISSION_PATH)

    assert limited.status_code == 429
    assert allowed_get.status_code == 200


def test_upstream_connection_failure_is_reported_as_gateway_error() -> None:
    def failing_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    gateway = create_gateway_app(
        "http://127.0.0.1:8000", transport=httpx.MockTransport(failing_handler)
    )

    response = call(gateway, "GET", MISSION_PATH)

    assert response.status_code == 502
    assert response.json() == {"detail": {"code": "upstream_unavailable"}}


def test_upstream_timeout_is_reported_as_gateway_timeout() -> None:
    def timing_out_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timeout", request=request)

    gateway = create_gateway_app(
        "http://127.0.0.1:8000", transport=httpx.MockTransport(timing_out_handler)
    )

    response = call(gateway, "GET", MISSION_PATH)

    assert response.status_code == 504
    assert response.json() == {"detail": {"code": "upstream_timeout"}}


def test_upstream_error_status_is_relayed_and_not_masked_as_success() -> None:
    upstream = RecordingApp(status_code=500, body={"detail": {"code": "internal_error"}})
    gateway = build_gateway(upstream)

    response = call(gateway, "GET", MISSION_PATH)

    assert response.status_code == 500
    assert response.json() == {"detail": {"code": "internal_error"}}


def test_authorization_and_identity_headers_are_not_forwarded() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream)

    call(
        gateway,
        "GET",
        MISSION_PATH,
        headers={
            "Authorization": "Bearer super-secret-token",
            "Cookie": "session=abc",
            "X-Api-Key": "another-secret",
            "Accept": "application/json",
        },
    )

    forwarded = upstream.requests[0]
    assert "authorization" not in forwarded.headers
    assert "cookie" not in forwarded.headers
    assert "x-api-key" not in forwarded.headers
    assert forwarded.headers["accept"] == "application/json"


def test_logs_contain_no_payload_content_or_client_address(
    caplog: pytest.LogCaptureFixture,
) -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream)

    with caplog.at_level(logging.INFO, logger="cyberquest.g4_gateway"):
        call(
            gateway,
            "POST",
            ASSESSMENT_PATH,
            json={"selected_indicator_ids": ["sender_domain"], "response_id": "verify_and_report"},
        )

    record = caplog.text
    assert "selected_indicator_ids" not in record
    assert "sender_domain" not in record
    assert "verify_and_report" not in record
    assert "127.0.0.1" not in record
    assert "method=POST" in record
    assert "path=/v1/demo/missions/phishing-detective/assessment" in record


def test_https_edge_assertion_is_mandatory() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream)

    rejected = call(gateway, "GET", MISSION_PATH, edge=False)

    assert rejected.status_code == 403
    assert rejected.json() == {"detail": {"code": "https_required"}}
    assert upstream.requests == []


def test_https_edge_assertion_has_no_opt_out() -> None:
    with pytest.raises(TypeError):
        create_gateway_app("http://127.0.0.1:8000", require_forwarded_https=False)


def test_forwarded_https_is_accepted_when_the_edge_reports_https() -> None:
    upstream = RecordingApp(body={"mission_id": "phishing-detective-suspicious-invoice"})
    gateway = build_gateway(upstream)

    response = call(
        gateway, "GET", MISSION_PATH, headers={"X-Forwarded-Proto": "https"}
    )

    assert response.status_code == 200
    assert [request.url.path for request in upstream.requests] == [MISSION_PATH]


def test_forwarded_http_is_rejected_when_the_edge_reports_cleartext() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream)

    response = call(gateway, "GET", MISSION_PATH, headers={"X-Forwarded-Proto": "http"})

    assert response.status_code == 403
    assert response.json() == {"detail": {"code": "https_required"}}
    assert upstream.requests == []


def test_cf_visitor_scheme_is_checked_as_well() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream)

    response = call(
        gateway,
        "GET",
        MISSION_PATH,
        headers={
            "X-Forwarded-Proto": "https",
            "CF-Visitor": '{"scheme":"http"}',
        },
    )

    assert response.status_code == 403
    assert upstream.requests == []


def test_forwarded_protocol_headers_are_not_forwarded_upstream() -> None:
    upstream = RecordingApp()
    gateway = build_gateway(upstream)

    call(
        gateway,
        "GET",
        MISSION_PATH,
        headers={
            "X-Forwarded-Proto": "https",
            "X-Forwarded-Host": "public-host.example",
            "CF-Visitor": '{"scheme":"https"}',
        },
    )

    forwarded = upstream.requests[0]
    assert "x-forwarded-proto" not in forwarded.headers
    assert "x-forwarded-host" not in forwarded.headers
    assert "cf-visitor" not in forwarded.headers


def test_upstream_url_validation_accepts_loopback_ip_literals() -> None:
    assert validate_upstream_base_url("http://127.0.0.1:8000") == "http://127.0.0.1:8000"
    assert validate_upstream_base_url("HTTP://127.0.0.1:8000") == "http://127.0.0.1:8000"
    assert validate_upstream_base_url("http://[::1]:8000/") == "http://[::1]:8000"


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1:8000",
        "ftp://127.0.0.1:8000",
        "http://localhost:8000",
        "http://example.com:8000",
        "http://127.0.0.1.evil.example:8000",
        "http://127.0.0.1:8000@evil.example",
        "http://user:pass@127.0.0.1:8000",
        "http://2130706433:8000",
        "http://127.0.0.1:0",
        "http://127.0.0.1:99999",
        "http://127.0.0.1:8000/v1",
        "http://127.0.0.1:8000?debug=1",
        "http://127.0.0.1:8000#fragment",
        "http:// 127.0.0.1:8000",
    ],
)
def test_upstream_url_validation_rejects_non_loopback_or_non_structural_values(url: str) -> None:
    with pytest.raises(ValueError):
        validate_upstream_base_url(url)
    with pytest.raises(ValueError):
        create_gateway_app(url)


def test_main_refuses_an_invalid_upstream() -> None:
    with pytest.raises(SystemExit) as excinfo:
        g4_gateway.main(["--upstream", "http://localhost:8000"])

    assert "loopback IP literal" in str(excinfo.value)


def test_gateway_bind_host_is_not_configurable() -> None:
    with pytest.raises(SystemExit):
        g4_gateway._parse_args(["--upstream", "http://127.0.0.1:8000", "--host", "0.0.0.0"])


def test_gateway_always_binds_loopback(monkeypatch: pytest.MonkeyPatch) -> None:
    import uvicorn

    captured: dict[str, object] = {}

    def fake_run(app, *, host: str, port: int, log_level: str) -> None:
        captured.update(host=host, port=port, log_level=log_level)

    monkeypatch.setattr(uvicorn, "run", fake_run)

    assert g4_gateway.main(["--upstream", "http://127.0.0.1:8000", "--port", "8099"]) == 0
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 8099
