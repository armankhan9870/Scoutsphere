"""Pydantic schemas for authentication requests, responses, and device session tracking."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
    """Registration request payload."""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: str = Field(..., min_length=2)
    target_roles: Optional[List[str]] = Field(default_factory=list)


class LoginRequest(BaseModel):
    """User authentication request payload."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Optional refresh token payload for non-cookie HTTP clients."""

    refresh_token: Optional[str] = None


class TokenResponse(BaseModel):
    """JWT Token pair response object."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 900
    user_id: uuid.UUID
    email: str
    full_name: str
    is_verified: bool = False
    message: Optional[str] = None


class VerifyEmailRequest(BaseModel):
    """Email verification payload."""

    token: str


class ResendVerificationRequest(BaseModel):
    """Payload to trigger resending email verification token."""

    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    """Forgot password request payload."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Password reset payload."""

    token: str
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


class GoogleAuthRequest(BaseModel):
    """Google OAuth ID token payload."""

    credential: str


class UserSessionResponse(BaseModel):
    """Device login session summary."""

    id: uuid.UUID
    device_info: str
    ip_address: str
    last_active: datetime
    created_at: datetime
    is_active: bool
    is_current: bool = False

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """Generic status message payload."""

    message: str
    detail: Optional[str] = None
