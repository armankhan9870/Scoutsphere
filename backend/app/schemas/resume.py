"""Pydantic schemas for resume upload and profile parsing responses."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    """Response payload returned immediately after uploading a resume."""

    id: uuid.UUID
    file_path: Optional[str] = None
    is_active: bool
    message: str = "Resume uploaded successfully and marked active."
    created_at: datetime


class ResumeResponse(BaseModel):
    """Detailed resume record response."""

    id: uuid.UUID
    user_id: uuid.UUID
    file_path: Optional[str] = None
    parsed_data_json: Dict[str, Any]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
