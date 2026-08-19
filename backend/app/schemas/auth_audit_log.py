"""Pydantic schemas for AuthAuditLog entity (Create, Read)."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuthAuditLogCreate(BaseModel):
    """Schema for recording an authentication audit event."""

    user_id: Optional[uuid.UUID] = None
    event: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuthAuditLogRead(BaseModel):
    """Schema for reading an audit log record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    event: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
