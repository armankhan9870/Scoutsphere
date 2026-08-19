"""Unit test suite for Skill Gap Agent delta computation, URL validation, and 100% match case."""

import pytest

from app.agents.nodes.skill_gap_node import run_skill_gap_agent_node
from app.agents.state import ScoutSphereState
from app.services.skill_gap.delta_calculator import compute_skill_delta
from app.services.skill_gap.url_validator import validate_and_flag_resources, validate_resource_url


def test_skill_delta_computation() -> None:
    """Verifies that missing skills and weak skills are computed correctly."""
    user_skills = [
        {"name": "Python", "proficiency_estimate": "Advanced"},
        {"name": "FastAPI", "proficiency_estimate": "Intermediate"},
        {"name": "Docker", "proficiency_estimate": "Beginner"},
    ]
    required_skills = ["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL"]

    missing, weak, priority = compute_skill_delta(user_skills, required_skills)

    assert "Kubernetes" in missing
    assert "PostgreSQL" in missing
    assert "Docker" in weak
    assert priority[0] in ["Kubernetes", "PostgreSQL"]


def test_url_validation_and_flagging() -> None:
    """Verifies valid HTTP format checking and domain trust flagging."""
    assert validate_resource_url("https://kubernetes.io/docs/tutorials/") is True
    assert validate_resource_url("invalid_string") is False

    resources = [
        {"resource_url": "https://kubernetes.io/docs/tutorials/", "resource_title": "Trusted Docs"},
        {
            "resource_url": "https://fake-hallucinated-domain-xyz.com/tutorial",
            "resource_title": "Untrusted Link",
        },
    ]

    flagged = validate_and_flag_resources(resources)
    assert flagged[0]["flagged_for_review"] is False
    assert flagged[1]["flagged_for_review"] is True


@pytest.mark.asyncio
async def test_100_percent_skill_match_graceful() -> None:
    """Verifies graceful zero-gap handling when candidate meets 100% of requirements."""
    user_skills = [
        {"name": "Python", "proficiency_estimate": "Advanced"},
        {"name": "FastAPI", "proficiency_estimate": "Advanced"},
        {"name": "Docker", "proficiency_estimate": "Intermediate"},
    ]
    required_skills = ["Python", "FastAPI", "Docker"]

    state: ScoutSphereState = {
        "user_id": "user-100",
        "session_id": "session-100",
        "current_intent": "analyze_gap",
        "raw_resume_text": "",
        "user_profile": {"skills": user_skills},
        "parsed_profile": {"skills": user_skills},
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": [{"required_skills_json": required_skills}],
        "target_opportunity_id": None,
        "matches": None,
        "skill_gap_analysis": None,
        "tailored_resume": None,
        "application_draft": None,
        "chat_query": None,
        "chat_history": [],
        "roadmap_result": None,
        "messages": [],
        "errors": [],
        "next_node": None,
    }

    result_state = await run_skill_gap_agent_node(state)
    analysis = result_state["skill_gap_analysis"]

    assert len(analysis["missing_skills"]) == 0
    assert len(analysis["priority_order"]) == 0
    assert analysis["match_impact_score"] == 0.0
