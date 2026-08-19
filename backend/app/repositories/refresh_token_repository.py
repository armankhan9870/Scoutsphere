"""RefreshTokenRepository for auth session tokens management."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Data access repository for RefreshToken entity."""

    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def create_token(
        self,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> RefreshToken:
        """Create and store a new refresh token record."""
        token_obj = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address,
        )
        return await self.create(token_obj)

    async def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Fetch active token record by hash."""
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke_token(self, token_hash: str) -> bool:
        """Revoke a single token by setting revoked_at timestamp."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> int:
        """Revoke all active tokens for a given user."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        result = await self.db.execute(stmt)
        return result.rowcount

    async def cleanup_expired(self) -> int:
        """Delete all expired or revoked token records."""
        now = datetime.now(timezone.utc)
        stmt = delete(RefreshToken).where(
            (RefreshToken.expires_at <= now) | (RefreshToken.revoked_at.isnot(None))
        )
        result = await self.db.execute(stmt)
        return result.rowcount
