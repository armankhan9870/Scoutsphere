"""Pydantic schemas for User entity (Create, Update, Read)."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.user_profile import UserProfileBase, UserProfileRead, UserProfileUpdate


class UserBase(BaseModel):
    """Base schema for user fields."""

    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    is_active: bool = True
    email_verified: bool = False


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr
    password: Optional[str] = None
    full_name: str
    phone: Optional[str] = None
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    target_roles: List[str] = []
    location_preference: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user details."""

    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    email_verified: Optional[bool] = None
    password: Optional[str] = None
    target_roles: Optional[List[str]] = None
    location_preference: Optional[str] = None


class UserRead(UserBase):
    """Schema for reading user details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    token_version: int = 1
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None
    target_roles: List[str] = []
    location_preference: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    google_id: Optional[str] = None
    has_password: bool = True


# Backward-compatibility aliases
UserResponse = UserRead

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "UserResponse",
    "UserProfileUpdate",
    "UserProfileRead",
    "UserProfileBase",
]
