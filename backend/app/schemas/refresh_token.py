"""Pydantic schemas for RefreshToken entity (Create, Read)."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RefreshTokenCreate(BaseModel):
    """Schema for creating a refresh token."""

    user_id: uuid.UUID
    token_hash: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: datetime


class RefreshTokenRead(BaseModel):
    """Schema for reading a refresh token."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    token_hash: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    created_at: datetime
