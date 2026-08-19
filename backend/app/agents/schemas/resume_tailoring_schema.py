"""Pydantic v2 schemas for Resume Tailoring Agent."""

from typing import List

from pydantic import BaseModel, Field


class TailoredSkill(BaseModel):
    name: str
    category: str = "General"


class TailoredExperience(BaseModel):
    company: str
    role: str
    duration: str
    highlights: List[str] = Field(default_factory=list)


class TailoredProject(BaseModel):
    title: str
    description: str
    tech_stack: List[str] = Field(default_factory=list)


class TailoredResumeOutput(BaseModel):
    target_role: str
    summary: str
    skills: List[TailoredSkill]
    experience: List[TailoredExperience] = Field(default_factory=list)
    projects: List[TailoredProject] = Field(default_factory=list)
