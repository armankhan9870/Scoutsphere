"""Unit test suite for Matching & Ranking Agent monotonicity and LLM call bounds."""

from unittest.mock import AsyncMock

import pytest

from app.models.opportunity import Opportunity
from app.services.matching.hybrid_scorer import calculate_hybrid_score
from app.services.matching.reranker import LLMRerankerService


def test_matching_score_monotonicity() -> None:
    """Asserts that adding matching skills monotonically increases or maintains the fit score."""
    opp = Opportunity(
        title="Python Backend Engineer",
        company_name="TechCorp",
        opportunity_type="JOB",
        description="Python FastAPI PostgreSQL Docker",
        required_skills_json=["Python", "FastAPI", "PostgreSQL", "Docker"],
        location="Remote",
        is_remote=True,
        source_url="https://example.com/job/1",
    )

    profile_low = {"skills": ["Python"], "location_preference": "Remote"}
    profile_mid = {"skills": ["Python", "FastAPI"], "location_preference": "Remote"}
    profile_high = {
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "location_preference": "Remote",
    }

    score_low = calculate_hybrid_score(profile_low, opp, cosine_distance=0.4)["fit_score"]
    score_mid = calculate_hybrid_score(profile_mid, opp, cosine_distance=0.4)["fit_score"]
    score_high = calculate_hybrid_score(profile_high, opp, cosine_distance=0.4)["fit_score"]

    assert score_low <= score_mid
    assert score_mid <= score_high
    assert score_high >= 80.0


@pytest.mark.asyncio
async def test_llm_reranker_call_count_bounded() -> None:
    """Asserts that re-ranking top 20 candidates calls LLMClient.generate exactly ONCE in a single batch."""
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "[]"  # Stub JSON return

    reranker = LLMRerankerService(llm_client=mock_llm)

    # 25 candidates
    candidates = [
        {
            "opportunity_id": f"opp-{i}",
            "title": f"Job {i}",
            "company_name": "Corp",
            "fit_score": 75.0,
        }
        for i in range(25)
    ]

    results = await reranker.rerank_top_candidates(
        user_profile={"skills": ["Python"]}, top_candidates=candidates
    )

    # Must call LLM exactly once
    assert mock_llm.generate.call_count == 1
    # Results must be bounded to top 20
    assert len(results) == 20
