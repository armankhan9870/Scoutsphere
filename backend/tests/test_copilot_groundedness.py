"""Automated test suite verifying Application CoPilot grounded suggestions and human-approval persistence requirements."""

import uuid

import pytest

from app.services.copilot_service import CopilotService
from app.services.tailoring.fact_checker import FactCheckerService


@pytest.mark.asyncio
async def test_copilot_suggestions_grounded_in_profile():
    """Verify generated suggestions map strictly to candidate profile facts without hallucinated claims."""
    service = CopilotService()

    user_profile = {
        "full_name": "Alex Rivera",
        "email": "alex.rivera@example.com",
        "phone": "+1 (555) 019-2834",
        "location": "San Francisco, CA",
        "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL"],
        "education": [{"degree": "B.S. Computer Science", "institution": "State University"}],
        "experience": [{"role": "Software Engineer", "company": "TechCorp"}],
    }

    target_fields = [
        {"id": "f_name", "label": "Full Name", "type": "text"},
        {"id": "f_email", "label": "Email Address", "type": "text"},
        {"id": "f_skills", "label": "Technical Stack", "type": "textarea"},
        {
            "id": "f_why",
            "label": "Why do you want to join our engineering team?",
            "type": "textarea",
        },
    ]

    suggestions = service.generate_suggestions(
        fields=target_fields,
        user_profile=user_profile,
        job_context={"title": "Senior AI Engineer", "company_name": "ScoutSphere"},
    )

    assert len(suggestions) == 4

    name_sug = next(s for s in suggestions if s["field_id"] == "f_name")
    assert name_sug["suggested_value"] == "Alex Rivera"
    assert name_sug["is_grounded"] is True

    email_sug = next(s for s in suggestions if s["field_id"] == "f_email")
    assert email_sug["suggested_value"] == "alex.rivera@example.com"
    assert email_sug["is_grounded"] is True

    skills_sug = next(s for s in suggestions if s["field_id"] == "f_skills")
    assert "Python" in skills_sug["suggested_value"]
    assert "FastAPI" in skills_sug["suggested_value"]
    assert skills_sug["is_grounded"] is True

    # Run fact checker
    fact_checker = FactCheckerService()
    for sug in suggestions:
        is_valid, _ = fact_checker.verify_tailored_resume(
            user_profile, {"value": sug["suggested_value"]}
        )
        assert is_valid is True, f"Suggestion for {sug['field_label']} failed fact-checking"


@pytest.mark.asyncio
async def test_approval_flow_required_before_persistence(db_session):
    """Verify suggestions are NOT persisted until human user explicitly approves ('Use this' / accepted)."""
    service = CopilotService()
    app_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Step 1: Query logs prior to human approval -> Must be empty
    initial_logs = await service.get_application_copilot_logs(db_session, app_id)
    assert (
        len(initial_logs) == 0
    ), "No suggestions should be persisted before explicit human approval"

    # Step 2: Human explicitly accepts 2 fields and rejects 1 field
    approved_answers = [
        {
            "field_id": "f_name",
            "field_label": "Full Name",
            "field_type": "text",
            "suggested_answer": "Alex Rivera",
            "final_answer": "Alex Rivera",
            "status": "accepted",
            "grounded_sources": "Profile -> Personal Info",
        },
        {
            "field_id": "f_email",
            "field_label": "Email Address",
            "field_type": "text",
            "suggested_answer": "alex.rivera@example.com",
            "final_answer": "alex.rivera@example.com",
            "status": "accepted",
            "grounded_sources": "Profile -> Verified Email",
        },
        {
            "field_id": "f_why",
            "field_label": "Motivation",
            "field_type": "textarea",
            "suggested_answer": "Raw suggestion text",
            "final_answer": "",
            "status": "rejected",
            "grounded_sources": "Grounded Model",
        },
    ]

    persisted_logs = await service.persist_human_approvals(
        db=db_session,
        application_id=app_id,
        user_id=user_id,
        approved_answers=approved_answers,
    )

    assert len(persisted_logs) == 3

    # Verify persisted log statuses match human decisions
    accepted = [log_item for log_item in persisted_logs if log_item.status == "accepted"]
    rejected = [log_item for log_item in persisted_logs if log_item.status == "rejected"]

    assert len(accepted) == 2
    assert len(rejected) == 1
    assert accepted[0].final_answer == "Alex Rivera"

    # Query DB logs to ensure persistence succeeded
    stored_logs = await service.get_application_copilot_logs(db_session, app_id)
    assert len(stored_logs) == 3
