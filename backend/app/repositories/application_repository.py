"""ApplicationRepository for application status pipeline management and history audit logging."""

import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application, ApplicationStatusHistory
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    """Data access repository for Application entities."""

    def __init__(self, db: AsyncSession):
        super().__init__(Application, db)

    async def get_user_applications(
        self, user_id: uuid.UUID, status: Optional[str] = None
    ) -> Sequence[Application]:
        """Fetch applications for a user, optionally filtered by pipeline status."""
        stmt = (
            select(Application)
            .options(
                selectinload(Application.opportunity), selectinload(Application.status_history)
            )
            .where(Application.user_id == user_id)
        )
        if status:
            stmt = stmt.where(Application.status == status.upper())

        stmt = stmt.order_by(Application.updated_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_status(
        self, application_id: uuid.UUID, new_status: str, notes: Optional[str] = None
    ) -> Optional[Application]:
        """Updates application status and creates an immutable status history audit log."""
        app_obj = await self.get_by_id(application_id)
        if not app_obj:
            return None

        app_obj.status = new_status.upper()
        if notes:
            app_obj.notes = notes

        # Log audit history
        history_entry = ApplicationStatusHistory(
            application_id=application_id,
            status=new_status.upper(),
            notes=notes,
        )
        self.db.add(history_entry)
        await self.db.flush()
        await self.db.refresh(app_obj)
        return app_obj
