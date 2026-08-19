"""Unit tests for SQLAlchemy 2.0 ORM model instantiation and fields."""

from app.models.opportunity import Opportunity
from app.models.user import User


def test_user_model_instantiation() -> None:
    """Verifies that User model initializes with defaults and attributes."""
    user = User(
        email="test@scoutsphere.ai",
        password_hash="hashed_pw",
        full_name="Test User",
        target_roles=["Backend Engineer"],
    )
    assert user.email == "test@scoutsphere.ai"
    assert user.full_name == "Test User"
    assert "Backend Engineer" in user.target_roles


def test_opportunity_model_instantiation() -> None:
    """Verifies Opportunity model field initialization."""
    opp = Opportunity(
        title="Software Intern",
        company_name="Tech Corp",
        opportunity_type="INTERNSHIP",
        description="Great internship opportunity",
        required_skills_json=["Python", "FastAPI"],
        source_url="https://example.com/job/1",
        is_remote=True,
    )
    assert opp.title == "Software Intern"
    assert opp.opportunity_type == "INTERNSHIP"
    assert opp.is_remote is True
    assert "Python" in opp.required_skills_json
