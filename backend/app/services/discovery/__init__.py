"""Export module for Discovery Agent services."""

from app.services.discovery.base_source import OpportunitySource, RawOpportunity
from app.services.discovery.deduplicator import DeduplicatorService
from app.services.discovery.mock_sources import (
    MockHackathonSource,
    MockInternshipSource,
    MockJobBoardSource,
)
from app.services.discovery.normalizer import normalize_raw_opportunity

__all__ = [
    "OpportunitySource",
    "RawOpportunity",
    "MockJobBoardSource",
    "MockHackathonSource",
    "MockInternshipSource",
    "normalize_raw_opportunity",
    "DeduplicatorService",
]
