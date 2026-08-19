"""Pydantic schemas for UserProfile entity (Create, Update, Read)."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.user_profile import CurrentStatusEnum, RemotePreferenceEnum


class UserProfileBase(BaseModel):
    """Base profile attributes."""

    bio: Optional[str] = None
    target_roles: List[str] = []
    preferred_locations: List[str] = []
    remote_preference: RemotePreferenceEnum = RemotePreferenceEnum.HYBRID
    education: Optional[Dict[str, Any]] = None
    current_status: CurrentStatusEnum = CurrentStatusEnum.STUDENT
    resume_id: Optional[uuid.UUID] = None
    avatar_url: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    """Schema for creating a user profile."""

    user_id: uuid.UUID


class UserProfileUpdate(BaseModel):
    """Schema for updating a user profile."""

    full_name: Optional[str] = None
    bio: Optional[str] = None
    target_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    location_preference: Optional[str] = None
    remote_preference: Optional[RemotePreferenceEnum] = None
    education: Optional[Dict[str, Any]] = None
    current_status: Optional[CurrentStatusEnum] = None
    resume_id: Optional[uuid.UUID] = None
    avatar_url: Optional[str] = None


class UserProfileRead(UserProfileBase):
    """Schema for reading a user profile."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
