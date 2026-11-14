"""Safe, stateless Phishing Detective demo API.

This module deliberately does not create learner accounts, persist attempts, award XP,
or claim mastery. Submitted answers are untrusted and evaluated on the server.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

router = APIRouter(prefix="/v1/demo", tags=["Demo missions"])
MISSION_PATH = Path(__file__).parent / "content" / "phishing_detective_v1.json"
CORRECT_INDICATORS = frozenset({
    "sender_domain", "reply_to_mismatch", "urgency_pressure",
    "unexpected_invoice", "unverified_link",
})
SAFE_RESPONSE = "verify_and_report"


class Indicator(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    label: str
    category: str


class ResponseOption(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    label: str


class EmailContent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    display_name: str
    from_address: str
    reply_to: str
    subject: str
    received_label: str
    body: list[str]
    displayed_link: str
    attachment_label: str


class MissionContent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: int
    mission_id: str
    version: int
    title: str
    organisation: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    estimated_minutes: int
    simulation_notice: str
    briefing: str
    email: EmailContent
    indicators: list[Indicator]
    response_options: list[ResponseOption]
    learning_objectives: list[str]


class AssessmentSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    selected_indicator_ids: list[str] = Field(max_length=5)
    response_id: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def unique_indicators(self) -> "AssessmentSubmission":
        if len(set(self.selected_indicator_ids)) != len(self.selected_indicator_ids):
            raise ValueError("selected_indicator_ids must be unique")
        return self


def load_mission() -> MissionContent:
    try:
        raw = json.loads(MISSION_PATH.read_text(encoding="utf-8"))
        mission = MissionContent.model_validate(raw)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        # A broken or missing mission must never be served as a successful demo.
        raise RuntimeError("Phishing Detective mission content is invalid") from exc
    if {item.id for item in mission.indicators} != CORRECT_INDICATORS:
        raise RuntimeError("Mission indicator catalogue does not match its assessment rubric")
    if SAFE_RESPONSE not in {item.id for item in mission.response_options}:
        raise RuntimeError("Mission response catalogue does not match its assessment rubric")
    return mission


def public_mission() -> dict:
    return load_mission().model_dump()


def evaluate_submission(submission: AssessmentSubmission) -> dict:
    mission = load_mission()
    known_ids = {item.id for item in mission.indicators}
    unknown_ids = set(submission.selected_indicator_ids) - known_ids
    if unknown_ids:
        raise HTTPException(status_code=422, detail={"code": "unknown_indicator"})
    known_response_ids = {item.id for item in mission.response_options}
    if submission.response_id not in known_response_ids:
        raise HTTPException(status_code=422, detail={"code": "unknown_response"})
    correct_selected = set(submission.selected_indicator_ids) & CORRECT_INDICATORS
    incorrect_selected = set(submission.selected_indicator_ids) - CORRECT_INDICATORS
    indicator_score = max(0, len(correct_selected) - len(incorrect_selected))
    response_correct = submission.response_id == SAFE_RESPONSE
    response_score = 5 if response_correct else 0
    total = indicator_score + response_score

    explanations = [
        {
            "indicator_id": indicator.id,
            "identified": indicator.id in correct_selected,
            "explanation": indicator.label,
        }
        for indicator in mission.indicators
    ]
    return {
        "mission_id": mission.mission_id,
        "mission_version": mission.version,
        "score": total,
        "max_score": 10,
        "indicator_score": indicator_score,
        "response_score": response_score,
        "identified_indicators": sorted(correct_selected),
        "missed_indicators": sorted(CORRECT_INDICATORS - correct_selected),
        "incorrect_selections": sorted(incorrect_selected),
        "response_correct": response_correct,
        "feedback": explanations,
        "response_explanation": (
            "Correct. Verify using a known official channel, then report through the approved process."
            if response_correct else
            "Do not click, pay, reply, or forward the link. Verify independently and report the message."
        ),
        "learning_status": "practice_feedback_only",
        "xp_awarded": 0,
        "competency_awarded": False,
        "persistence": "not_saved",
        "simulation_notice": "This result is practice feedback, not a verified competency or account record.",
    }


@router.get("/missions/phishing-detective")
def get_phishing_detective() -> dict:
    return public_mission()


@router.post("/missions/phishing-detective/assessment")
def assess_phishing_detective(submission: AssessmentSubmission) -> dict:
    return evaluate_submission(submission)
