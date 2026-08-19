"""Pydantic v2 Input and Output schemas for Resume Analysis Agent."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SkillItem(BaseModel):
    """Extracted skill item with category and proficiency."""

    name: str
    category: str = "General"
    proficiency_estimate: str = "Intermediate"


class ExperienceItem(BaseModel):
    """Extracted work experience item."""

    company: str
    role: str
    duration: str
    summary: str
    highlights: List[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    """Extracted education record."""

    institution: str
    degree: str
    year: str
    gpa: Optional[str] = None


class ProjectItem(BaseModel):
    """Extracted project item."""

    title: str
    description: str
    tech_stack: List[str] = Field(default_factory=list)


class ResumeAnalysisInput(BaseModel):
    """Input payload to Resume Analysis Agent."""

    raw_resume_text: str
    user_profile: Optional[Dict[str, Any]] = None


class ResumeAnalysisOutput(BaseModel):
    """Parsed structured resume profile schema."""

    skills: List[SkillItem]
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    years_experience: float = 0.0
    career_interests: List[str] = Field(default_factory=list)
    strengths_summary: str
