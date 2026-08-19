"""Unit tests for UserRepository and OpportunityRepository operations."""

from app.repositories.opportunity_repository import OpportunityRepository
from app.repositories.user_repository import UserRepository


def test_user_repository_structure() -> None:
    """Smoke test ensuring repository methods bind correctly."""
    assert hasattr(UserRepository, "get_by_email")
    assert hasattr(UserRepository, "get_with_skills")


def test_opportunity_repository_structure() -> None:
    """Smoke test ensuring vector search and filter repository methods exist."""
    assert hasattr(OpportunityRepository, "search_by_vector")
    assert hasattr(OpportunityRepository, "filter_opportunities")
    assert hasattr(OpportunityRepository, "get_by_source_url")
