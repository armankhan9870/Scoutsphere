"""End-to-end integration test executing full master orchestrator pipeline against a fresh candidate user."""

import uuid

import pytest

from app.agents.orchestrator import run_full_onboarding_pipeline
from app.agents.state import ScoutSphereState


@pytest.mark.asyncio
async def test_full_pipeline_execution_end_to_end() -> None:
    """Executes full Master Orchestrator pipeline (Discovery -> Analysis -> Matching -> Skill Gap -> Roadmap) for a fresh test user."""
    fresh_user_id = str(uuid.uuid4())
    raw_resume = (
        "ALEX RIVERA\n"
        "Computer Science Student specializing in Python, FastAPI, PostgreSQL, and Docker.\n"
        "Built REST microservices and async data pipelines."
    )
    opportunities = [
        {
            "id": str(uuid.uuid4()),
            "title": "Associate AI Systems Engineer",
            "company_name": "ScoutSphere Inc",
            "opportunity_type": "JOB",
            "required_skills_json": ["Python", "FastAPI", "LangGraph", "PostgreSQL", "Docker"],
            "location": "Remote",
            "is_remote": True,
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Cloud Infrastructure Intern",
            "company_name": "AWS",
            "opportunity_type": "INTERNSHIP",
            "required_skills_json": ["Docker", "Kubernetes", "Python"],
            "location": "Remote",
            "is_remote": True,
        },
    ]

    initial_state: ScoutSphereState = {
        "user_id": fresh_user_id,
        "session_id": str(uuid.uuid4()),
        "current_intent": "onboarding",
        "raw_resume_text": raw_resume,
        "user_profile": {"target_roles": ["AI Engineer"]},
        "parsed_profile": None,
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": opportunities,
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

    final_state = await run_full_onboarding_pipeline(initial_state)

    # 1. Assert Resume Analysis Output
    assert final_state.get("parsed_profile") is not None
    skills = [
        s.get("name") if isinstance(s, dict) else str(s)
        for s in final_state["parsed_profile"].get("skills", [])
    ]
    assert "Python" in skills or "FastAPI" in skills

    # 2. Assert Matches Output
    matches = final_state.get("matches")
    assert matches is not None
    assert len(matches) >= 1
    assert matches[0]["fit_score"] > 50.0

    # 3. Assert Skill Gap Analysis Output
    gap_analysis = final_state.get("skill_gap_analysis")
    assert gap_analysis is not None
    assert "missing_skills" in gap_analysis
    assert "recommended_resources" in gap_analysis
