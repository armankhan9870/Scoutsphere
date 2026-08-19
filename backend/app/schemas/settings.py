"""Pydantic schemas for user settings, security sessions, and account management."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserSettingsResponse(BaseModel):
    """Pydantic schema for retrieving user settings and preferences."""

    id: uuid.UUID
    user_id: uuid.UUID

    # Account
    full_name: str
    email: str
    pending_new_email: Optional[str] = None

    # Career Preferences
    target_roles: List[str] = Field(default_factory=list)
    target_industries: List[str] = Field(default_factory=list)
    target_locations: List[str] = Field(default_factory=list)
    work_style: str = "remote"
    min_salary: Optional[int] = None
    opportunity_types: List[str] = Field(default_factory=lambda: ["internship", "job", "hackathon"])

    # Discovery Preferences
    discovery_frequency: str = "daily"
    source_filters: Dict[str, Any] = Field(default_factory=dict)

    # Matching Preferences
    min_match_score: int = 70
    auto_hide_low_score: bool = False

    # Resume & Cover Letter Defaults
    default_resume_template: str = "modern_clean"
    cover_letter_tone: str = "conversational"
    auto_tailor_high_matches: bool = False

    # AI / Agent Preferences
    preferred_llm_provider: str = "gemini"
    agent_tone: str = "exploratory"
    auto_background_agents: bool = False

    # Notifications
    notify_high_matches: bool = True
    notify_deadlines: bool = True
    notify_status_changes: bool = True
    notify_weekly_digest: bool = True
    email_notifications_enabled: bool = False

    # Privacy & Data Controls
    exclude_resume_from_training: bool = False

    # Appearance
    theme: str = "light"
    layout_density: str = "comfortable"

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    """Pydantic schema for updating user settings and preferences."""

    # Account
    full_name: Optional[str] = None

    # Career Preferences
    target_roles: Optional[List[str]] = None
    target_industries: Optional[List[str]] = None
    target_locations: Optional[List[str]] = None
    work_style: Optional[str] = None
    min_salary: Optional[int] = None
    opportunity_types: Optional[List[str]] = None

    # Discovery Preferences
    discovery_frequency: Optional[str] = None
    source_filters: Optional[Dict[str, Any]] = None

    # Matching Preferences
    min_match_score: Optional[int] = None
    auto_hide_low_score: Optional[bool] = None

    # Resume & Cover Letter Defaults
    default_resume_template: Optional[str] = None
    cover_letter_tone: Optional[str] = None
    auto_tailor_high_matches: Optional[bool] = None

    # AI / Agent Preferences
    preferred_llm_provider: Optional[str] = None
    agent_tone: Optional[str] = None
    auto_background_agents: Optional[bool] = None

    # Notifications
    notify_high_matches: Optional[bool] = None
    notify_deadlines: Optional[bool] = None
    notify_status_changes: Optional[bool] = None
    notify_weekly_digest: Optional[bool] = None
    email_notifications_enabled: Optional[bool] = None

    # Privacy & Data Controls
    exclude_resume_from_training: Optional[bool] = None

    # Appearance
    theme: Optional[str] = None
    layout_density: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """Schema for updating user account password."""

    current_password: str
    new_password: str = Field(..., min_length=6)


class ChangeEmailRequest(BaseModel):
    """Schema for initiating email change verification flow."""

    new_email: EmailStr


class EmailVerificationRequest(BaseModel):
    """Schema for confirming email change verification code."""

    verification_code: str


class UserSessionResponse(BaseModel):
    """Schema for active security login sessions."""

    id: uuid.UUID
    device_info: str
    ip_address: str
    is_active: bool
    last_active: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class DataExportResponse(BaseModel):
    """Schema for complete JSON dump data export."""

    export_timestamp: datetime
    user_profile: Dict[str, Any]
    settings: Dict[str, Any]
    resumes: List[Dict[str, Any]]
    matches: List[Dict[str, Any]]
    applications: List[Dict[str, Any]]
    chat_sessions: List[Dict[str, Any]]
    roadmaps: List[Dict[str, Any]]
    skill_gaps: List[Dict[str, Any]]
