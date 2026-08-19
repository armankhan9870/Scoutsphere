"""Abstract OpportunitySource interface and RawOpportunity Pydantic model for pluggable discovery sources."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RawOpportunity(BaseModel):
    """Raw un-normalized opportunity payload fetched from external sources/APIs/mocks."""

    title: str
    organization: str
    opportunity_type: str = "JOB"  # JOB, INTERNSHIP, HACKATHON
    raw_description: str
    skills_found: List[str] = Field(default_factory=list)
    location: str = "Remote"
    is_remote: bool = True
    deadline_str: Optional[str] = None
    apply_url: str
    source_name: str


class OpportunitySource(ABC):
    """Abstract pluggable discovery source interface."""

    @abstractmethod
    async def fetch(
        self, query: str = "", filters: Optional[Dict[str, Any]] = None
    ) -> List[RawOpportunity]:
        """Fetches raw opportunity items matching target query and criteria."""
        pass
