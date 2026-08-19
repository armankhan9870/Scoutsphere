"""Pydantic schemas for standalone ATS Analysis module."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ATSCategoryScore(BaseModel):
    """Detailed category evaluation breakdown."""

    score: float = Field(..., ge=0.0, le=100.0, description="Category score from 0 to 100")
    status: str = Field(..., description="Evaluation status: Good, Needs Improvement, Critical")
    details: List[str] = Field(
        default_factory=list, description="Specific findings for this category"
    )


class ATSSubScores(BaseModel):
    """Per-category sub-scores (0-100)."""

    formatting: float = Field(..., ge=0.0, le=100.0)
    section_completeness: float = Field(..., ge=0.0, le=100.0)
    quantified_achievements: float = Field(..., ge=0.0, le=100.0)
    action_verbs: float = Field(..., ge=0.0, le=100.0)
    keyword_density: float = Field(..., ge=0.0, le=100.0)
    length: float = Field(..., ge=0.0, le=100.0)


class ATSAnalysisResponse(BaseModel):
    """Response schema returned by POST /resumes/{id}/ats-analysis."""

    resume_id: uuid.UUID
    overall_ats_score: float = Field(
        ..., ge=0.0, le=100.0, description="Overall ATS readiness score (0-100)"
    )
    sub_scores: ATSSubScores
    category_breakdown: Dict[str, ATSCategoryScore]
    rule_based_findings: Dict[str, Any]
    improvement_suggestions: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True
