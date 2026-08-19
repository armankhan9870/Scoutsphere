"""UserSessionRepository for managing device login sessions and token hash rotation."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_session import UserSession
from app.repositories.base import BaseRepository


class UserSessionRepository(BaseRepository[UserSession]):
    """Data access repository for UserSession entities."""

    def __init__(self, db: AsyncSession):
        super().__init__(UserSession, db)

    async def create_session(
        self,
        user_id: uuid.UUID,
        device_info: str = "Web Browser",
        ip_address: str = "127.0.0.1",
        token_hash: str = "",
    ) -> UserSession:
        """Creates a new active login session for a user."""
        session = UserSession(
            user_id=user_id,
            device_info=device_info or "Web Browser",
            ip_address=ip_address or "127.0.0.1",
            token_hash=token_hash,
            is_active=True,
            last_active=datetime.now(timezone.utc),
        )
        return await self.create(session)

    async def get_by_id(self, session_id: uuid.UUID) -> Optional[UserSession]:
        """Fetch session by session ID."""
        result = await self.db.execute(select(UserSession).where(UserSession.id == session_id))
        return result.scalar_one_or_none()

    async def update_token_hash(self, session_id: uuid.UUID, new_token_hash: str) -> None:
        """Rotates the active refresh token hash and updates last_active timestamp."""
        await self.db.execute(
            update(UserSession)
            .where(UserSession.id == session_id)
            .values(
                token_hash=new_token_hash,
                last_active=datetime.now(timezone.utc),
            )
        )
        await self.db.commit()

    async def get_user_sessions(self, user_id: uuid.UUID) -> List[UserSession]:
        """Retrieve all sessions for a user, ordered by last active timestamp."""
        result = await self.db.execute(
            select(UserSession)
            .where(UserSession.user_id == user_id)
            .order_by(UserSession.last_active.desc())
        )
        return list(result.scalars().all())

    async def revoke_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Revokes a specific session belonging to user_id."""
        result = await self.db.execute(
            update(UserSession)
            .where(UserSession.id == session_id, UserSession.user_id == user_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return (result.rowcount or 0) > 0

    async def revoke_all_user_sessions(self, user_id: uuid.UUID) -> int:
        """Revokes ALL active sessions for a user (triggered on token reuse detection or logout-all)."""
        result = await self.db.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id, UserSession.is_active.is_(True))
            .values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount or 0
