"""Pydantic schemas for UserSettings entity (Create, Update, Read)."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class UserSettingsBase(BaseModel):
    """Base user settings schema."""

    notification_prefs: Dict[str, Any] = {
        "email_alerts": True,
        "match_notifications": True,
        "weekly_digest": False,
    }
    privacy_prefs: Dict[str, Any] = {
        "profile_visibility": "private",
        "allow_data_training": False,
    }
    theme: str = "dark"
    auto_run_agents: bool = False
    preferred_llm_provider: str = "gemini"


class UserSettingsCreate(UserSettingsBase):
    """Schema for creating user settings."""

    user_id: uuid.UUID


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings."""

    notification_prefs: Optional[Dict[str, Any]] = None
    privacy_prefs: Optional[Dict[str, Any]] = None
    theme: Optional[str] = None
    auto_run_agents: Optional[bool] = None
    preferred_llm_provider: Optional[str] = None


class UserSettingsRead(UserSettingsBase):
    """Schema for reading user settings."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
