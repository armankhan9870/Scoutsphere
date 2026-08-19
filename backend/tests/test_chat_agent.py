"""Unit test suite for Career Chatbot dual-intent routing (General Knowledge & Personal Data)."""

import pytest

from app.agents.nodes.chat_node import classify_chat_intent, run_chat_agent_node
from app.agents.state import ScoutSphereState
from app.agents.tools.chat_tools import (
    tool_get_my_skill_gaps,
    tool_get_role_roadmap,
    tool_search_opportunities,
)


def test_chat_tools_selection() -> None:
    """Verifies that RAG tools produce expected JSON output strings."""
    opps = tool_search_opportunities("ML Intern")
    gaps = tool_get_my_skill_gaps(["Python", "FastAPI"])
    roadmap = tool_get_role_roadmap("ML Engineer")

    assert "Google DeepMind" in opps
    assert "PyTorch" in gaps or "LangGraph" in gaps
    assert "Machine Learning Engineer" in roadmap


def test_intent_classification_routing() -> None:
    """Verifies that query intent router distinguishes General Knowledge from Personal Data queries."""
    # General knowledge queries (no personal data indicators)
    gk_queries = [
        "what is AI",
        "what is machine learning",
        "what is the difference between ML and data science",
        "difference between internship and apprenticeship",
        "what does a data analyst do",
        "how does ATS scoring work",
        "what skills does a backend developer need",
    ]
    for q in gk_queries:
        assert classify_chat_intent(q) == "GENERAL_KNOWLEDGE", f"Failed for query: '{q}'"

    # Personal data queries (first-person pronouns & candidate context)
    personal_queries = [
        "what should I apply to next",
        "why is my match score low",
        "what's missing in my resume",
        "what are my skill gaps for backend roles",
        "what applications have I submitted",
    ]
    for q in personal_queries:
        assert classify_chat_intent(q) == "PERSONAL_DATA", f"Failed for query: '{q}'"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,expected_keywords",
    [
        ("what is AI", ["Artificial Intelligence", "computer science", "Machine Learning"]),
        ("what is machine learning", ["Machine Learning", "patterns", "data"]),
        (
            "what is the difference between ML and data science",
            ["Data Science", "Machine Learning", "predictive"],
        ),
        (
            "difference between internship and apprenticeship",
            ["Internship", "Apprenticeship", "short-term"],
        ),
        ("what does a data analyst do", ["Data Analyst", "SQL", "dashboards"]),
        ("how does ATS scoring work", ["Applicant Tracking System", "ATS", "keywords"]),
        ("what skills does a backend developer need", ["Backend Developer", "Databases", "APIs"]),
    ],
)
async def test_general_knowledge_queries(query: str, expected_keywords: list) -> None:
    """Verifies that general knowledge questions answer directly without deflection or forced personal citations."""
    user_skills = [{"name": "Python"}, {"name": "FastAPI"}]
    state: ScoutSphereState = {
        "user_id": "user-chat-gk",
        "session_id": "session-chat-gk",
        "current_intent": "chat",
        "raw_resume_text": "",
        "user_profile": {"skills": user_skills},
        "parsed_profile": {"skills": user_skills},
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": None,
        "target_opportunity_id": None,
        "matches": None,
        "skill_gap_analysis": None,
        "tailored_resume": None,
        "application_draft": None,
        "user_settings": {"preferred_llm_provider": "stub"},
        "chat_query": query,
        "chat_history": [],
        "roadmap_result": None,
        "messages": [],
        "errors": [],
        "next_node": None,
    }

    result_state = await run_chat_agent_node(state)
    chat_history = result_state["chat_history"]

    assert len(chat_history) >= 2
    assistant_reply = chat_history[-1]["content"]

    # Verify complete educational response and keyword inclusion
    for keyword in expected_keywords:
        assert (
            keyword.lower() in assistant_reply.lower()
        ), f"Keyword '{keyword}' missing in reply for '{query}'"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,expected_keywords",
    [
        ("what should I apply to next", ["ScoutSphere Inc", "96% match"]),
        ("why is my match score low", ["match score", "Python"]),
        ("what's missing in my resume", ["PyTorch", "Kubernetes"]),
        ("what are my skill gaps for backend roles", ["Redis", "Kubernetes"]),
        ("what applications have I submitted", ["Python", "FastAPI"]),
    ],
)
async def test_personal_data_queries(query: str, expected_keywords: list) -> None:
    """Verifies that personal/data-grounded questions utilize candidate profile data and tools."""
    user_skills = [{"name": "Python"}, {"name": "FastAPI"}, {"name": "PostgreSQL"}]
    state: ScoutSphereState = {
        "user_id": "user-chat-pd",
        "session_id": "session-chat-pd",
        "current_intent": "chat",
        "raw_resume_text": "",
        "user_profile": {"skills": user_skills},
        "parsed_profile": {"skills": user_skills},
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": None,
        "target_opportunity_id": None,
        "matches": None,
        "skill_gap_analysis": None,
        "tailored_resume": None,
        "application_draft": None,
        "user_settings": {"preferred_llm_provider": "stub"},
        "chat_query": query,
        "chat_history": [],
        "roadmap_result": None,
        "messages": [],
        "errors": [],
        "next_node": None,
    }

    result_state = await run_chat_agent_node(state)
    chat_history = result_state["chat_history"]

    assert len(chat_history) >= 2
    assistant_reply = chat_history[-1]["content"]

    # Verify reply incorporates candidate profile or tool context
    for keyword in expected_keywords:
        assert (
            keyword.lower() in assistant_reply.lower()
        ), f"Keyword '{keyword}' missing in reply for '{query}'"
