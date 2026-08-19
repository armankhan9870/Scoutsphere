"""Unit and integration tests for standalone ATS Analysis module."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.security import create_access_token
from app.models.resume import Resume
from app.models.user import User
from app.services.ats_analyzer import ATSAnalyzer
from tests.fixtures.resume_fixtures import KNOWN_BAD_RESUME, KNOWN_GOOD_RESUME


@pytest.mark.asyncio
async def test_known_bad_resume_scores_low_and_flags_issues():
    """Validates that a known-bad resume receives a low overall score and correctly flags all structural & content issues."""
    analyzer = ATSAnalyzer()
    dummy_id = str(uuid.uuid4())
    result = await analyzer.analyze(dummy_id, KNOWN_BAD_RESUME)

    # 1. Overall Score Verification
    assert (
        result.overall_ats_score < 50.0
    ), f"Expected low ATS score (<50), got {result.overall_ats_score}"

    # 2. Category Sub-scores Verification
    assert (
        result.sub_scores.formatting < 80.0
    ), "Expected low formatting score due to ASCII table borders"
    assert (
        result.sub_scores.section_completeness < 80.0
    ), "Expected section completeness penalty due to missing Education & Summary"
    assert (
        result.sub_scores.quantified_achievements < 50.0
    ), "Expected low quantified achievements score (0 metrics)"
    assert (
        result.sub_scores.action_verbs < 60.0
    ), "Expected action verb penalty due to passive phrases 'worked on', 'responsible for'"
    assert (
        result.sub_scores.length < 60.0
    ), "Expected length penalty due to critically short text (<150 words)"

    # 3. Rule-Based Findings Verification
    rule_findings = result.rule_based_findings
    assert (
        rule_findings["formatting"]["has_tables"] is True
    ), "Rule checker should detect ASCII table grid"
    assert (
        "Education" in rule_findings["sections"]["missing_sections"]
    ), "Rule checker should flag missing Education section"
    assert (
        rule_findings["quantified_achievements"]["quantified_bullets_count"] == 0
    ), "No metrics should be detected"
    assert (
        rule_findings["action_verbs"]["weak_phrase_count"] >= 2
    ), "Weak passive phrases should be flagged"

    # 4. Improvement Suggestions Verification
    suggestions_text = " ".join(result.improvement_suggestions).lower()
    assert "education" in suggestions_text, "Suggestions should recommend adding Education section"
    assert (
        "metric" in suggestions_text
        or "quantit" in suggestions_text
        or "bullet" in suggestions_text
    ), "Suggestions should address metrics"


@pytest.mark.asyncio
async def test_known_good_resume_scores_high():
    """Validates that a well-structured, metric-rich resume achieves a high ATS score."""
    analyzer = ATSAnalyzer()
    dummy_id = str(uuid.uuid4())
    result = await analyzer.analyze(dummy_id, KNOWN_GOOD_RESUME)

    assert (
        result.overall_ats_score >= 80.0
    ), f"Expected high ATS score (>=80), got {result.overall_ats_score}"
    assert result.sub_scores.formatting == 100.0
    assert result.sub_scores.section_completeness == 100.0
    assert result.sub_scores.quantified_achievements >= 80.0
    assert result.sub_scores.action_verbs >= 80.0
    assert result.sub_scores.length >= 80.0


@pytest.mark.asyncio
async def test_ats_analysis_api_endpoint(async_client: AsyncClient, db_session):
    """Integration test verifying POST /api/v1/resumes/{id}/ats-analysis endpoint."""
    # 1. Fetch demo user from fixture setup
    res = await db_session.execute(select(User).where(User.email == "alex.rivera@scoutsphere.ai"))
    user = res.scalar_one()

    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create sample resume record in DB
    resume_id = uuid.uuid4()
    resume = Resume(
        id=resume_id,
        user_id=user.id,
        raw_text=KNOWN_BAD_RESUME,
        file_path="uploads/bad_resume.pdf",
        parsed_data_json={"status": "UPLOADED"},
        is_active=True,
    )
    db_session.add(resume)
    await db_session.commit()

    # 3. Call endpoint POST /api/v1/resumes/{id}/ats-analysis
    response = await async_client.post(
        f"/api/v1/resumes/{resume_id}/ats-analysis",
        headers=headers,
    )

    assert (
        response.status_code == 200
    ), f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()

    assert data["resume_id"] == str(resume_id)
    assert "overall_ats_score" in data
    assert data["overall_ats_score"] < 50.0
    assert "sub_scores" in data
    assert "category_breakdown" in data
    assert "improvement_suggestions" in data
    assert len(data["improvement_suggestions"]) > 0

    # 4. Verify persistence in DB record parsed_data_json
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        db_resume = await session.scalar(select(Resume).where(Resume.id == resume_id))
        assert db_resume is not None
        assert "ats_analysis" in db_resume.parsed_data_json
        assert (
            db_resume.parsed_data_json["ats_analysis"]["overall_ats_score"]
            == data["overall_ats_score"]
        )
