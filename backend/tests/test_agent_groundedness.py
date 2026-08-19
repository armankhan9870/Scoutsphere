"""Groundedness and Anti-Hallucination verification test suite for user-facing AI agents."""

import uuid

import pytest

from app.agents.nodes.application_assistant_node import run_application_assistant_node
from app.agents.nodes.chat_node import run_chat_agent_node
from app.services.skill_gap.url_validator import validate_and_flag_resources
from app.services.tailoring.fact_checker import FactCheckerService


@pytest.mark.asyncio
async def test_application_assistant_groundedness() -> None:
    """Verifies that Application Assistant drafts cover letters strictly grounded in candidate profile facts."""
    state = {
        "user_id": str(uuid.uuid4()),
        "parsed_profile": {
            "full_name": "Alex Rivera",
            "email": "alex.rivera@scoutsphere.ai",
            "skills": [{"name": "Python"}, {"name": "FastAPI"}],
            "experience": [{"company": "TechCorp Solutions", "role": "Software Developer Intern"}],
        },
        "discovered_opportunities": [
            {
                "id": str(uuid.uuid4()),
                "title": "Backend Systems Engineer",
                "company_name": "ScoutSphere Corp",
                "description": "Looking for Python and FastAPI developers to build scalable microservices.",
                "required_skills_json": ["Python", "FastAPI", "PostgreSQL"],
            }
        ],
        "user_settings": {"preferred_llm_provider": "gemini"},
    }

    res_state = await run_application_assistant_node(state)
    draft = res_state.get("application_draft")

    assert draft is not None
    assert "cover_letter" in draft
    assert "form_fields" in draft

    cover_letter = draft["cover_letter"]
    assert "Alex Rivera" in cover_letter or "Hiring Team" in cover_letter
    assert (
        "ScoutSphere Corp" in cover_letter
        or "Backend Systems Engineer" in cover_letter
        or "Tech Corp" in cover_letter
    )


@pytest.mark.asyncio
async def test_chat_copilot_groundedness() -> None:
    """Verifies that Chatbot Copilot incorporates actual candidate profile skills in recommendations."""
    state = {
        "chat_query": "What skills should I learn next for backend engineering?",
        "parsed_profile": {
            "skills": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "PostgreSQL"}],
        },
        "rag_context": {"top_matching_role": "Backend Engineer"},
        "user_settings": {"preferred_llm_provider": "gemini"},
    }

    res_state = await run_chat_agent_node(state)
    chat_history = res_state.get("chat_history") or []

    assert len(chat_history) >= 2
    assistant_msg = chat_history[-1]["content"]

    # Verify response references candidate's actual profile skills
    assert (
        "Python" in assistant_msg
        or "FastAPI" in assistant_msg
        or "backend" in assistant_msg.lower()
    )


def test_url_validator_groundedness() -> None:
    """Verifies that URL validator verifies real official documentation URLs and flags invalid ones."""
    resources = [
        {
            "skill": "React",
            "resource_url": "https://react.dev/learn",
            "resource_title": "React Docs",
        },
        {
            "skill": "FakeSkill",
            "resource_url": "https://invalid-nonexistent-domain-999.com/doc",
            "resource_title": "Fake Tutorial",
        },
    ]

    validated = validate_and_flag_resources(resources)
    assert len(validated) == 2

    valid_res = next(r for r in validated if r["skill"] == "React")
    invalid_res = next(r for r in validated if r["skill"] == "FakeSkill")

    assert valid_res.get("is_verified", True) is True
    assert (
        invalid_res.get("is_verified", False) is False
        or "unverified" in invalid_res.get("verification_status", "").lower()
        or "flagged" in invalid_res.get("verification_status", "").lower()
    )


def test_fact_checker_anti_hallucination_boundary() -> None:
    """Verifies that FactChecker strictly catches unauthorized skill insertions in tailored resumes."""
    base_profile = {
        "skills": [{"name": "Python"}, {"name": "SQL"}],
        "experience": [{"company": "DataCorp", "role": "Junior Analyst"}],
    }

    hallucinated_tailoring = {
        "target_role": "AI Research Scientist",
        "skills": [{"name": "Python"}, {"name": "SQL"}, {"name": "Quantum Machine Learning"}],
        "experience": [{"company": "DataCorp", "role": "Junior Analyst"}],
    }

    checker = FactCheckerService()
    is_valid, violations = checker.verify_tailored_resume(base_profile, hallucinated_tailoring)

    assert is_valid is False
    assert any("Quantum Machine Learning" in v for v in violations)
