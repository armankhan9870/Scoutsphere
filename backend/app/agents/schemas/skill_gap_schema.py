"""Pydantic v2 schemas for Skill Gap Agent input and output."""

from typing import List

from pydantic import BaseModel, Field


class RecommendedResource(BaseModel):
    """Single recommended learning resource."""

    skill: str
    resource_title: str
    resource_url: str
    resource_type: str = "Documentation"  # Documentation, Course, Interactive, Tutorial
    estimated_time: str = "4 hours"
    is_valid_url: bool = True
    flagged_for_review: bool = False


class SkillGapOutput(BaseModel):
    """Structured skill gap report schema."""

    missing_skills: List[str] = Field(default_factory=list)
    weak_skills: List[str] = Field(default_factory=list)
    priority_order: List[str] = Field(default_factory=list)
    recommended_resources: List[RecommendedResource] = Field(default_factory=list)
    match_impact_score: float = 0.0  # Estimated fit score boost if skills are acquired
