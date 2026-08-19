"""AuthAuditLogRepository for recording and auditing security events."""

import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_audit_log import AuthAuditLog
from app.repositories.base import BaseRepository


class AuthAuditLogRepository(BaseRepository[AuthAuditLog]):
    """Data access repository for AuthAuditLog entity."""

    def __init__(self, db: AsyncSession):
        super().__init__(AuthAuditLog, db)

    async def log_event(
        self,
        event: str,
        user_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthAuditLog:
        """Record an authentication or security audit event."""
        log_obj = AuthAuditLog(
            user_id=user_id,
            event=event,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await self.create(log_obj)

    async def get_by_user_id(self, user_id: uuid.UUID, limit: int = 50) -> Sequence[AuthAuditLog]:
        """Fetch audit log records for a given user ordered by newest first."""
        result = await self.db.execute(
            select(AuthAuditLog)
            .where(AuthAuditLog.user_id == user_id)
            .order_by(AuthAuditLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def list_recent_logs(self, limit: int = 100) -> Sequence[AuthAuditLog]:
        """List global recent security audit events."""
        result = await self.db.execute(
            select(AuthAuditLog).order_by(AuthAuditLog.created_at.desc()).limit(limit)
        )
        return result.scalars().all()
