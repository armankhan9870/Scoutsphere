"""Unit test suite for Discovery Agent sources, normalizer, deduplicator, and worker pipeline."""

import pytest

from app.services.discovery.mock_sources import (
    MockHackathonSource,
    MockInternshipSource,
    MockJobBoardSource,
)
from app.services.discovery.normalizer import normalize_raw_opportunity
from app.worker.tasks import _execute_discovery_pipeline


@pytest.mark.asyncio
async def test_mock_sources_fetch() -> None:
    """Verifies that all pluggable mock sources return structured RawOpportunity items."""
    job_src = MockJobBoardSource()
    hack_src = MockHackathonSource()
    intern_src = MockInternshipSource()

    jobs = await job_src.fetch()
    hacks = await hack_src.fetch()
    interns = await intern_src.fetch()

    assert len(jobs) >= 2
    assert len(hacks) >= 2
    assert len(interns) >= 2

    assert jobs[0].opportunity_type == "JOB"
    assert hacks[0].opportunity_type == "HACKATHON"
    assert interns[0].opportunity_type == "INTERNSHIP"


@pytest.mark.asyncio
async def test_raw_opportunity_normalization() -> None:
    """Verifies that RawOpportunity objects normalize correctly with 384-dim embeddings."""
    job_src = MockJobBoardSource()
    raw_list = await job_src.fetch()
    opp_model = normalize_raw_opportunity(raw_list[0])

    assert opp_model.title == raw_list[0].title
    assert opp_model.company_name == raw_list[0].organization
    assert len(opp_model.required_skills_json) > 0
    assert len(opp_model.embedding) == 384


@pytest.mark.asyncio
async def test_discovery_pipeline_execution() -> None:
    """Verifies end-to-end execution of discovery pipeline."""
    result = await _execute_discovery_pipeline()
    assert result["status"] == "success"
    assert result["fetched_count"] >= 6
    assert "inserted_count" in result
    assert "duplicate_count" in result
