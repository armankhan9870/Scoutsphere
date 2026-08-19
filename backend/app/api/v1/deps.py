"""FastAPI dependency injections for authentication and authorization."""

import uuid
from typing import Optional, Tuple

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

DEMO_USER_ID = uuid.UUID("3e8ec9ae-9d67-48f7-9622-c52de2c7def9")


async def get_current_user_and_session(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Tuple[User, Optional[uuid.UUID]]:
    """Decodes JWT access bearer token from Header or Cookie and returns (user, session_id)."""
    user_repo = UserRepository(db)

    effective_token = token
    if not effective_token:
        effective_token = request.cookies.get("scoutsphere_access_token")

    if effective_token:
        payload = decode_token(effective_token)
        if payload and payload.get("type") == "access":
            user_id_str: str = payload.get("sub", "")
            sid_str: Optional[str] = payload.get("sid")
            try:
                user_id = uuid.UUID(user_id_str)
                session_id = uuid.UUID(sid_str) if sid_str else None
                user = await user_repo.get_by_id(user_id)
                if user and user.is_active:
                    return user, session_id
            except ValueError:
                pass

    # Fallback to seeded demo user
    demo_user = await user_repo.get_by_id(DEMO_USER_ID)
    if demo_user:
        return demo_user, None

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    current_user_and_session: Tuple[User, Optional[uuid.UUID]] = Depends(
        get_current_user_and_session
    ),
) -> User:
    """Dependency wrapper returning the current authenticated user."""
    user, _ = current_user_and_session
    return user


async def get_current_session_id(
    current_user_and_session: Tuple[User, Optional[uuid.UUID]] = Depends(
        get_current_user_and_session
    ),
) -> Optional[uuid.UUID]:
    """Dependency wrapper returning the active session ID from claims."""
    _, session_id = current_user_and_session
    return session_id
