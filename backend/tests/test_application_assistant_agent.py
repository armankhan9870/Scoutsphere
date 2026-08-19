"""Unit test suite for Application Assistant Agent draft generation, editing, and submission logging."""

import pytest

from app.agents.nodes.application_assistant_node import run_application_assistant_node
from app.agents.state import ScoutSphereState


@pytest.mark.asyncio
async def test_application_draft_generation() -> None:
    """Verifies that Application Assistant Node generates cover letter and pre-filled form fields."""
    user_profile = {
        "full_name": "Alex Rivera",
        "email": "student@scoutsphere.ai",
        "skills": [{"name": "Python"}, {"name": "FastAPI"}],
    }
    opportunity = {
        "title": "Associate AI Systems Engineer",
        "company_name": "ScoutSphere Inc",
        "description": "Build multi-agent AI systems with FastAPI and PostgreSQL.",
    }

    state: ScoutSphereState = {
        "user_id": "user-app-1",
        "session_id": "session-app-1",
        "current_intent": "draft_application",
        "raw_resume_text": "",
        "user_profile": user_profile,
        "parsed_profile": user_profile,
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": [opportunity],
        "target_opportunity_id": None,
        "matches": None,
        "skill_gap_analysis": None,
        "tailored_resume": None,
        "application_draft": None,
        "chat_query": "Passionate about AI agents.",
        "chat_history": [],
        "roadmap_result": None,
        "messages": [],
        "errors": [],
        "next_node": None,
    }

    result_state = await run_application_assistant_node(state)
    draft = result_state["application_draft"]

    assert draft is not None
    assert "cover_letter" in draft
    assert "form_fields" in draft
    assert draft["form_fields"]["full_name"] == "Alex Rivera"
    assert "ScoutSphere Inc" in draft["cover_letter"] or "Hiring Team" in draft["cover_letter"]
