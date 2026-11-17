"""External verification for the temporary G4 HTTPS endpoint.

Runs the acceptance checks from the approved CQ-00.7.1-G4 plan against a
publicly reachable HTTPS endpoint, from outside the development machine.

Usage::

    CYBERQUEST_G4_BASE_URL=https://<temporary-host> python scripts/verify_g4_endpoint.py

Optional environment variables:

- ``CYBERQUEST_G4_BASE_URL``  - base URL of the temporary HTTPS endpoint.
- ``CYBERQUEST_G4_REPORT``    - path for a machine-readable JSON report.
- ``CYBERQUEST_G4_RATE_BURST``- number of POST requests used for the rate-limit
  check (default 12).

The script never prints tunnel credentials and never writes them anywhere.
It exits non-zero if any check fails.
"""
from __future__ import annotations

import json
import os
import socket
import ssl
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from urllib.parse import urlparse

MISSION_PATH = "/v1/demo/missions/phishing-detective"
ASSESSMENT_PATH = "/v1/demo/missions/phishing-detective/assessment"
TIMEOUT_SECONDS = 20


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str
    evidence: dict = field(default_factory=dict)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects so cleartext fallback cannot be masked by a redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        return None


def build_opener() -> urllib.request.OpenerDirector:
    context = ssl.create_default_context()
    return urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=context),
        NoRedirect(),
    )


def request(opener, url, method="GET", payload=None, headers=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    all_headers = {"Accept": "application/json"}
    if data is not None:
        all_headers["Content-Type"] = "application/json"
    if headers:
        all_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=all_headers, method=method)
    try:
        with opener.open(req, timeout=TIMEOUT_SECONDS) as response:
            body = response.read()
            return response.status, body, dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers)
    except Exception as error:  # network-level failure
        return None, str(error).encode("utf-8"), {}


def check_https_only(base_url: str) -> CheckResult:
    parsed = urlparse(base_url)
    passed = parsed.scheme == "https" and bool(parsed.hostname)
    return CheckResult(
        "https_scheme_required",
        passed,
        f"base URL scheme is {parsed.scheme!r}",
        {"scheme": parsed.scheme, "host": parsed.hostname},
    )


def check_tls_chain(host: str, port: int) -> CheckResult:
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT_SECONDS) as sock:
            with context.wrap_socket(sock, server_hostname=host) as tls:
                cert = tls.getpeercert()
                cipher = tls.cipher()
    except Exception as error:
        return CheckResult("tls_chain_and_hostname_valid", False, f"TLS handshake failed: {error}")
    issuer = dict(x[0] for x in cert.get("issuer", [])).get("organizationName", "unknown")
    subject_alt = [value for key, value in cert.get("subjectAltName", []) if key == "DNS"]
    return CheckResult(
        "tls_chain_and_hostname_valid",
        True,
        f"TLS handshake succeeded with {issuer}; SAN {subject_alt}",
        {"issuer": issuer, "subject_alt_names": subject_alt, "cipher": cipher[0] if cipher else None},
    )


def check_invalid_hostname_rejected(base_url: str) -> CheckResult:
    parsed = urlparse(base_url)
    alias = f"invalid-{parsed.hostname}.example"
    opener = build_opener()
    status, _, _ = request(opener, f"https://{alias}{MISSION_PATH}")
    rejected = status is None or status >= 400
    return CheckResult(
        "invalid_hostname_rejected",
        rejected,
        f"hostname {alias} was rejected (status={status})",
        {"alias": alias, "status": status},
    )


def check_http_fallback_rejected(base_url: str) -> CheckResult:
    parsed = urlparse(base_url)
    cleartext_url = f"http://{parsed.netloc}{MISSION_PATH}"
    opener = build_opener()
    status, body, _ = request(opener, cleartext_url)
    leaked = False
    if status == 200:
        try:
            leaked = json.loads(body).get("mission_id") == "phishing-detective-suspicious-invoice"
        except Exception:
            leaked = False
    return CheckResult(
        "http_fallback_rejected",
        not leaked,
        f"cleartext request did not return mission content (status={status})",
        {"status": status},
    )


def check_mission_retrieval(opener, base_url: str) -> CheckResult:
    status, body, _ = request(opener, f"{base_url}{MISSION_PATH}")
    try:
        mission = json.loads(body)
    except Exception:
        return CheckResult("mission_retrieval", False, f"non-JSON response (status={status})")
    passed = (
        status == 200
        and mission.get("mission_id") == "phishing-detective-suspicious-invoice"
        and mission.get("version") == 1
        and len(mission.get("indicators", [])) == 8
        and all(item.get("guidance") for item in mission.get("indicators", []))
    )
    return CheckResult(
        "mission_retrieval",
        passed,
        f"status={status} mission_id={mission.get('mission_id')} indicators={len(mission.get('indicators', []))}",
        {"status": status, "mission_id": mission.get("mission_id")},
    )


def submit(opener, base_url: str, payload: dict):
    return request(opener, f"{base_url}{ASSESSMENT_PATH}", method="POST", payload=payload)


def check_valid_assessment(opener, base_url: str) -> CheckResult:
    status, body, _ = submit(
        opener,
        base_url,
        {
            "selected_indicator_ids": [
                "sender_domain",
                "reply_to_mismatch",
                "urgency_pressure",
                "unexpected_invoice",
                "unverified_link",
            ],
            "response_id": "verify_and_report",
        },
    )
    try:
        result = json.loads(body)
    except Exception:
        return CheckResult("valid_assessment", False, f"non-JSON response (status={status})")
    passed = (
        status == 200
        and result.get("score") == 10
        and result.get("xp_awarded") == 0
        and result.get("competency_awarded") is False
        and result.get("persistence") == "not_saved"
        and all(item.get("guidance") for item in result.get("feedback", []))
        and len(result.get("feedback", [])) == 8
    )
    return CheckResult(
        "valid_assessment",
        passed,
        f"status={status} score={result.get('score')} persistence={result.get('persistence')}",
        {"status": status, "score": result.get("score")},
    )


def check_incorrect_assessment(opener, base_url: str) -> CheckResult:
    status, body, _ = submit(
        opener,
        base_url,
        {
            "selected_indicator_ids": ["sender_domain", "invoice_reference"],
            "response_id": "click_and_pay",
        },
    )
    try:
        result = json.loads(body)
    except Exception:
        return CheckResult("incorrect_assessment", False, f"non-JSON response (status={status})")
    passed = (
        status == 200
        and isinstance(result.get("score"), int)
        and result["score"] < 10
        and len(result.get("incorrect_selections", [])) > 0
        and result.get("xp_awarded") == 0
    )
    return CheckResult(
        "incorrect_assessment",
        passed,
        f"status={status} score={result.get('score')} incorrect={result.get('incorrect_selections')}",
        {"status": status, "score": result.get("score")},
    )


def check_unknown_route_rejected(opener, base_url: str) -> CheckResult:
    status, _, _ = request(opener, f"{base_url}/health/live")
    rejected = status is not None and status >= 400
    return CheckResult(
        "unknown_route_rejected", rejected, f"status={status}", {"status": status}
    )


def check_unsupported_method_rejected(opener, base_url: str) -> CheckResult:
    status, _, _ = request(opener, f"{base_url}{MISSION_PATH}", method="DELETE")
    rejected = status is not None and status >= 400
    return CheckResult(
        "unsupported_method_rejected", rejected, f"status={status}", {"status": status}
    )


def check_oversized_request_rejected(opener, base_url: str) -> CheckResult:
    oversized = {"selected_indicator_ids": ["x" * 20000], "response_id": "verify_and_report"}
    status, _, _ = request(opener, f"{base_url}{ASSESSMENT_PATH}", method="POST", payload=oversized)
    rejected = status is not None and status >= 400
    return CheckResult(
        "oversized_request_rejected", rejected, f"status={status}", {"status": status}
    )


def check_rate_limit(opener, base_url: str, burst: int) -> CheckResult:
    statuses = []
    for _ in range(burst):
        status, _, _ = submit(
            opener,
            base_url,
            {
                "selected_indicator_ids": ["sender_domain"],
                "response_id": "verify_and_report",
            },
        )
        statuses.append(status)
    throttled = sum(1 for status in statuses if status == 429)
    return CheckResult(
        "excessive_rate_throttled",
        throttled > 0,
        f"{throttled}/{burst} requests throttled with 429",
        {"statuses": statuses},
    )


def main() -> int:
    base_url = (os.environ.get("CYBERQUEST_G4_BASE_URL") or "").strip().rstrip("/")
    if not base_url:
        print("CYBERQUEST_G4_BASE_URL is required", file=sys.stderr)
        return 2
    burst = int(os.environ.get("CYBERQUEST_G4_RATE_BURST", "12"))

    parsed = urlparse(base_url)
    port = parsed.port or 443
    opener = build_opener()

    results = [
        check_https_only(base_url),
        check_tls_chain(parsed.hostname, port),
        check_invalid_hostname_rejected(base_url),
        check_http_fallback_rejected(base_url),
        check_mission_retrieval(opener, base_url),
        check_valid_assessment(opener, base_url),
        check_incorrect_assessment(opener, base_url),
        check_unknown_route_rejected(opener, base_url),
        check_unsupported_method_rejected(opener, base_url),
        check_oversized_request_rejected(opener, base_url),
        check_rate_limit(opener, base_url, burst),
    ]

    for result in results:
        marker = "PASS" if result.passed else "FAIL"
        print(f"[{marker}] {result.name}: {result.detail}")

    report = {
        "base_url_host": parsed.hostname,
        "checks": [
            {
                "name": result.name,
                "passed": result.passed,
                "detail": result.detail,
                "evidence": result.evidence,
            }
            for result in results
        ],
        "all_passed": all(result.passed for result in results),
    }
    report_path = os.environ.get("CYBERQUEST_G4_REPORT")
    if report_path:
        with open(report_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
        print(f"report written to {report_path}")

    print("CQ-00.7.1-G4 endpoint verification: " + ("PASS" if report["all_passed"] else "FAIL"))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
