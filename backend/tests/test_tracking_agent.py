"""Unit test suite for Tracking Agent state transitions and pipeline stats calculation."""

import uuid
from datetime import datetime, timedelta, timezone

from app.models.application import Application
from app.models.opportunity import Opportunity
from app.services.tracking.tracking_service import (
    calculate_pipeline_stats,
    is_valid_state_transition,
)


def test_state_transition_validation() -> None:
    """Verifies valid lifecycle state transitions and rejects illegal skips."""
    assert is_valid_state_transition("SAVED", "DRAFTING") is True
    assert is_valid_state_transition("SAVED", "APPLIED") is True
    assert is_valid_state_transition("DRAFTING", "APPLIED") is True
    assert is_valid_state_transition("APPLIED", "INTERVIEWING") is True
    assert is_valid_state_transition("INTERVIEWING", "OFFER") is True

    # Invalid transitions
    assert is_valid_state_transition("SAVED", "OFFER") is False
    assert is_valid_state_transition("REJECTED", "INTERVIEWING") is False


def test_pipeline_stats_calculation() -> None:
    """Verifies counts per status, response rate %, and stale follow-up detection."""
    now = datetime.now(timezone.utc)
    old_date = now - timedelta(days=16)

    opp = Opportunity(
        id=uuid.uuid4(),
        title="Software Intern",
        company_name="TechCorp",
        opportunity_type="INTERNSHIP",
        description="Desc",
        source_url="https://example.com/job/stats",
    )

    apps = [
        Application(id=uuid.uuid4(), status="SAVED", opportunity=opp, updated_at=now),
        Application(id=uuid.uuid4(), status="APPLIED", opportunity=opp, updated_at=now),
        Application(
            id=uuid.uuid4(), status="APPLIED", opportunity=opp, updated_at=old_date
        ),  # Stale
        Application(id=uuid.uuid4(), status="INTERVIEWING", opportunity=opp, updated_at=now),
        Application(id=uuid.uuid4(), status="OFFER", opportunity=opp, updated_at=now),
    ]

    stats = calculate_pipeline_stats(apps)

    assert stats["total_applications"] == 5
    assert stats["counts_by_status"]["SAVED"] == 1
    assert stats["counts_by_status"]["APPLIED"] == 2
    assert stats["counts_by_status"]["INTERVIEWING"] == 1
    assert stats["counts_by_status"]["OFFER"] == 1

    # Responded = 2 (INTERVIEWING + OFFER), Evaluated = 4 (APPLIED:2 + INTERVIEWING:1 + OFFER:1) -> 2/4 = 50.0%
    assert stats["response_rate_percentage"] == 50.0
    assert len(stats["stale_followup_nudges"]) == 1
    assert stats["stale_followup_nudges"][0]["days_inactive"] >= 16
