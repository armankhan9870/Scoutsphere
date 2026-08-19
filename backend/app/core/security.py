"""Security utilities for Argon2id password hashing, JWT token generation with rotation/jti, and token hashing."""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import httpx
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core.config import settings
from app.core.logging import logger

ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hashes a plain-text password using Argon2id."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against an Argon2id hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False
    except Exception as e:
        logger.error("Password verification error: %s", str(e))
        return False


def generate_secure_token(length: int = 32) -> str:
    """Generates a cryptographically secure random token string for email verification or password reset."""
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """Computes SHA-256 hex digest of a token string for safe database lookup."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(
    user_id: uuid.UUID,
    session_id: Optional[uuid.UUID] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Creates a signed JWT access token containing the user ID subject, session ID, and 15-minute expiration."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": str(user_id),
        "sid": str(session_id) if session_id else None,
        "exp": expire,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: uuid.UUID,
    session_id: Optional[uuid.UUID] = None,
    jti: Optional[str] = None,
) -> Tuple[str, str]:
    """Creates a signed JWT refresh token with 7-day expiration. Returns (token_string, jti)."""
    token_jti = jti or str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "sid": str(session_id) if session_id else None,
        "exp": expire,
        "type": "refresh",
        "jti": token_jti,
        "iat": datetime.now(timezone.utc),
    }
    encoded_token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_token, token_jti


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and verifies a JWT token string."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        logger.warning("JWT token decoding failed: %s", str(e))
        return None


async def verify_google_id_token(id_token_str: str) -> Optional[Dict[str, Any]]:
    """Verifies a Google OAuth ID token using httpx or returns mock payload for testing."""
    if not id_token_str:
        return None

    if id_token_str.startswith("mock_google_token_"):
        clean_identifier = id_token_str.replace("mock_google_token_", "")
        return {
            "sub": f"google_sub_{clean_identifier}",
            "email": f"{clean_identifier}@gmail.com",
            "name": f"Mock Google User {clean_identifier}",
            "picture": "https://lh3.googleusercontent.com/a/default-user=s96-c",
            "email_verified": True,
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token_str}"
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("email"):
                    return data
    except Exception as e:
        logger.error("Error verifying Google ID token: %s", str(e))
    return None


def send_verification_email_stub(email: str, token: str) -> str:
    """Stubs sending an email verification token link and returns verification URL."""
    verify_url = f"http://localhost:5173/verify-email?token={token}"
    logger.info("[STUB EMAIL] Verification link for %s: %s", email, verify_url)
    return verify_url


def send_password_reset_email_stub(email: str, token: str) -> str:
    """Stubs sending a password reset token link and returns reset URL."""
    reset_url = f"http://localhost:5173/reset-password?token={token}"
    logger.info("[STUB EMAIL] Password reset link for %s: %s", email, reset_url)
    return reset_url
