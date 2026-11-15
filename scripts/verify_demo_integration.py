"""Live integration check for FastAPI -> Next.js server-side demo proxy."""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = os.environ.get("CYBERQUEST_WEB_BASE_URL", "http://127.0.0.1:3000")


def get_json(path: str) -> dict:
    with urlopen(f"{BASE}{path}", timeout=5) as response:
        assert response.status == 200
        return json.loads(response.read())


def post_json(path: str, payload: dict) -> tuple[int, dict]:
    request = Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


mission = get_json("/api/demo/mission")
assert mission["mission_id"] == "phishing-detective-suspicious-invoice"
assert mission["version"] == 1
assert len(mission["indicators"]) == 8

perfect_status, perfect = post_json(
    "/api/demo/assessment",
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
assert perfect_status == 200
assert perfect["score"] == 10
assert perfect["xp_awarded"] == 0
assert perfect["competency_awarded"] is False
assert perfect["persistence"] == "not_saved"

false_positive_status, false_positive = post_json(
    "/api/demo/assessment",
    {
        "selected_indicator_ids": [
            "sender_domain",
            "reply_to_mismatch",
            "urgency_pressure",
            "unexpected_invoice",
            "unverified_link",
            "invoice_reference",
            "team_greeting",
            "business_hours",
        ],
        "response_id": "verify_and_report",
    },
)
assert false_positive_status == 200
assert false_positive["score"] == 7
assert len(false_positive["incorrect_selections"]) == 3
assert any(
    item["indicator_id"] == "invoice_reference"
    and item["is_warning_sign"] is False
    and item["selected"] is True
    for item in false_positive["feedback"]
)

invalid_status, invalid = post_json(
    "/api/demo/assessment",
    {"selected_indicator_ids": [], "response_id": "verify_and_report", "xp": 999999},
)
assert invalid_status == 422
assert isinstance(invalid.get("detail"), list)
assert invalid["detail"][0]["type"] == "extra_forbidden"

print("CQ-00.7 FastAPI -> Next.js demo integration: PASS")
