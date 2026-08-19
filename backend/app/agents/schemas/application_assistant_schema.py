"""Pydantic v2 schemas for Application Assistant Agent input and draft package output."""

from typing import Optional

from pydantic import BaseModel


class ApplicationFormFields(BaseModel):
    """Pre-filled common job portal form fields."""

    full_name: str
    email: str
    phone: Optional[str] = "+1 (555) 019-2834"
    linkedin_url: Optional[str] = "https://linkedin.com/in/alexrivera"
    github_url: Optional[str] = "https://github.com/alexrivera"
    portfolio_url: Optional[str] = "https://alexrivera.dev"
    why_this_role: str
    why_this_company: str
    availability: str = "Immediate / Fall 2026"
    sponsorship_required: bool = False


class ApplicationDraftPackage(BaseModel):
    """Complete application draft package output."""

    cover_letter: str
    form_fields: ApplicationFormFields
    status: str = "DRAFT_READY"
