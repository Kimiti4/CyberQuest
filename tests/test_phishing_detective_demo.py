from fastapi.testclient import TestClient

from cyberquest.main import create_app


client = TestClient(create_app())


def test_demo_mission_is_fictional_and_versioned() -> None:
    response = client.get("/v1/demo/missions/phishing-detective")
    assert response.status_code == 200
    mission = response.json()
    assert mission["mission_id"] == "phishing-detective-suspicious-invoice"
    assert mission["version"] == 1
    assert ".example" in mission["email"]["from_address"]
    assert "fictional training simulation" in mission["simulation_notice"].lower()
    assert "correct_indicator_ids" not in mission
    assert len(mission["indicators"]) == 8


def test_server_scores_submission_and_never_awards_xp_or_mastery() -> None:
    response = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        json={
            "selected_indicator_ids": [
                "sender_domain", "reply_to_mismatch", "urgency_pressure",
                "unexpected_invoice", "unverified_link",
            ],
            "response_id": "verify_and_report",
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["score"] == 10
    assert result["xp_awarded"] == 0
    assert result["competency_awarded"] is False
    assert result["persistence"] == "not_saved"
    assert result["learning_status"] == "practice_feedback_only"


def test_wrong_answers_receive_deterministic_feedback() -> None:
    response = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        json={
            "selected_indicator_ids": ["sender_domain", "unexpected_invoice"],
            "response_id": "click_and_pay",
        },
    )
    result = response.json()
    assert result["score"] == 2
    assert result["missed_indicators"] == [
        "reply_to_mismatch", "unverified_link", "urgency_pressure"
    ]
    assert result["response_correct"] is False


def test_unknown_indicator_is_rejected() -> None:
    response = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        json={"selected_indicator_ids": ["invented"], "response_id": "verify_and_report"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "unknown_indicator"


def test_duplicate_and_extra_submission_fields_are_rejected() -> None:
    duplicate = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        json={
            "selected_indicator_ids": ["sender_domain", "sender_domain"],
            "response_id": "verify_and_report",
        },
    )
    extra = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        json={
            "selected_indicator_ids": [],
            "response_id": "verify_and_report",
            "xp": 999999,
        },
    )
    assert duplicate.status_code == 422
    assert extra.status_code == 422


def test_forged_score_mastery_and_competency_fields_are_rejected() -> None:
    forged_fields = {
        "score": 10,
        "mastery": "expert",
        "competency_awarded": True,
        "persistence": "saved",
    }
    for field, value in forged_fields.items():
        response = client.post(
            "/v1/demo/missions/phishing-detective/assessment",
            json={
                "selected_indicator_ids": [],
                "response_id": "verify_and_report",
                field: value,
            },
        )
        assert response.status_code == 422
        assert response.json()["detail"][0]["type"] == "extra_forbidden"
        assert "xp_awarded" not in response.json()


def test_incomplete_submission_is_scored_but_never_awarded() -> None:
    response = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        json={"selected_indicator_ids": [], "response_id": "verify_and_report"},
    )
    result = response.json()
    assert response.status_code == 200
    assert result["score"] == 5
    assert result["response_correct"] is True
    assert result["missed_indicators"] == [
        "reply_to_mismatch", "sender_domain", "unexpected_invoice",
        "unverified_link", "urgency_pressure",
    ]
    assert result["xp_awarded"] == 0
    assert result["competency_awarded"] is False
    assert result["persistence"] == "not_saved"


def test_malformed_json_is_rejected() -> None:
    response = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        content=b"{not valid json",
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "json_invalid"


def test_oversized_request_body_is_rejected_without_echoing_payload() -> None:
    payload = (
        b'{"selected_indicator_ids":[],"response_id":"verify_and_report","padding":"'
        + b"a" * (64 * 1024)
        + b'"}'
    )
    response = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        content=payload,
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json() == {"detail": {"code": "request_too_large"}}
    assert len(response.content) < 1024


def test_submission_bounds_are_enforced() -> None:
    response = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        json={
            "selected_indicator_ids": ["a", "b", "c", "d", "e", "f", "g", "h", "i"],
            "response_id": "verify_and_report",
        },
    )
    assert response.status_code == 422


def test_unknown_response_is_rejected() -> None:
    response = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        json={"selected_indicator_ids": [], "response_id": "invented_response"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "unknown_response"


def test_neutral_facts_are_not_scored_as_warning_indicators() -> None:
    response = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        json={
            "selected_indicator_ids": [
                "sender_domain", "reply_to_mismatch", "urgency_pressure",
                "unexpected_invoice", "unverified_link", "invoice_reference",
                "team_greeting", "business_hours",
            ],
            "response_id": "verify_and_report",
        },
    )
    result = response.json()
    assert result["score"] == 7
    assert result["incorrect_selections"] == [
        "business_hours", "invoice_reference", "team_greeting"
    ]


def test_feedback_distinguishes_neutral_facts_from_missed_warning_signs() -> None:
    response = client.post(
        "/v1/demo/missions/phishing-detective/assessment",
        json={
            "selected_indicator_ids": ["invoice_reference"],
            "response_id": "verify_and_report",
        },
    )
    feedback = {item["indicator_id"]: item for item in response.json()["feedback"]}
    assert feedback["invoice_reference"]["is_warning_sign"] is False
    assert feedback["invoice_reference"]["selected"] is True
    assert feedback["invoice_reference"]["identified"] is False
    assert feedback["sender_domain"]["is_warning_sign"] is True
    assert feedback["sender_domain"]["selected"] is False
