"""Unit test suite for Resume & Profile Analysis Agent across 4 varied candidate fixtures."""

import os

import pytest

from app.agents.nodes.resume_analysis_node import run_resume_analysis_node
from app.agents.state import ScoutSphereState
from app.services.skill_normalizer import normalize_skill_name

FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures/resumes"))


def load_fixture(filename: str) -> str:
    """Helper reading text fixture from disk."""
    path = os.path.join(FIXTURES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_skill_normalization() -> None:
    """Verifies canonical normalization mapping for raw skill terms."""
    assert normalize_skill_name("py")[0] == "Python"
    assert normalize_skill_name("postgres db")[0] == "PostgreSQL"
    assert normalize_skill_name("reactjs")[0] == "React"
    assert normalize_skill_name("k8s")[0] == "Kubernetes"


@pytest.mark.asyncio
async def test_junior_dev_fixture_extraction() -> None:
    """Verifies agent extraction quality for Junior Full-Stack Developer resume."""
    raw_text = load_fixture("junior_dev.txt")
    state: ScoutSphereState = {
        "user_id": "test-uuid-1",
        "session_id": "session-1",
        "current_intent": "analyze",
        "raw_resume_text": raw_text,
        "user_profile": {"target_roles": ["Backend Engineer"]},
        "parsed_profile": None,
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": None,
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

    result_state = await run_resume_analysis_node(state)
    parsed = result_state["parsed_profile"]
    embedding = result_state["profile_embedding"]

    assert parsed is not None
    assert embedding is not None
    assert len(embedding) == 384

    extracted_skill_names = [s["name"] for s in parsed["skills"]]
    assert "Python" in extracted_skill_names
    assert "FastAPI" in extracted_skill_names
    assert "PostgreSQL" in extracted_skill_names


@pytest.mark.asyncio
async def test_data_science_fixture_extraction() -> None:
    """Verifies agent extraction quality for Data Science Student resume."""
    raw_text = load_fixture("data_science.txt")
    state: ScoutSphereState = {
        "user_id": "test-uuid-2",
        "session_id": "session-2",
        "current_intent": "analyze",
        "raw_resume_text": raw_text,
        "user_profile": {"target_roles": ["Data Scientist", "AI Engineer"]},
        "parsed_profile": None,
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": None,
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

    result_state = await run_resume_analysis_node(state)
    parsed = result_state["parsed_profile"]

    extracted_skill_names = [s["name"] for s in parsed["skills"]]
    assert "Python" in extracted_skill_names
    assert "PyTorch" in extracted_skill_names or "Pandas" in extracted_skill_names


@pytest.mark.asyncio
async def test_non_cs_transition_fixture_extraction() -> None:
    """Verifies agent extraction quality for Non-CS Career Transitioner resume."""
    raw_text = load_fixture("non_cs_transition.txt")
    state: ScoutSphereState = {
        "user_id": "test-uuid-3",
        "session_id": "session-3",
        "current_intent": "analyze",
        "raw_resume_text": raw_text,
        "user_profile": {"target_roles": ["Web Developer"]},
        "parsed_profile": None,
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": None,
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

    result_state = await run_resume_analysis_node(state)
    parsed = result_state["parsed_profile"]

    extracted_skill_names = [s["name"] for s in parsed["skills"]]
    assert "React" in extracted_skill_names or "JavaScript" in extracted_skill_names


@pytest.mark.asyncio
async def test_mobile_dev_fixture_extraction() -> None:
    """Verifies agent extraction quality for Mobile Developer resume."""
    raw_text = load_fixture("mobile_dev.txt")
    state: ScoutSphereState = {
        "user_id": "test-uuid-4",
        "session_id": "session-4",
        "current_intent": "analyze",
        "raw_resume_text": raw_text,
        "user_profile": {"target_roles": ["Mobile Engineer"]},
        "parsed_profile": None,
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": None,
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

    result_state = await run_resume_analysis_node(state)
    parsed = result_state["parsed_profile"]

    extracted_skill_names = [s["name"] for s in parsed["skills"]]
    assert "Flutter" in extracted_skill_names or "Dart" in extracted_skill_names
