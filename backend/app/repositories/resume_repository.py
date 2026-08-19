"""ResumeRepository for storing and querying user resumes and vector embeddings."""

import uuid
from typing import Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    """Data access repository for Resume entities."""

    def __init__(self, db: AsyncSession):
        super().__init__(Resume, db)

    async def get_active_by_user(self, user_id: uuid.UUID) -> Optional[Resume]:
        """Fetch the currently active resume for a specific user."""
        result = await self.db.execute(
            select(Resume)
            .where(Resume.user_id == user_id, Resume.is_active.is_(True))
            .order_by(Resume.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: uuid.UUID) -> Sequence[Resume]:
        """Fetch all resumes belonging to a user."""
        result = await self.db.execute(
            select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
        )
        return result.scalars().all()

    async def get_user_resumes(self, user_id: uuid.UUID) -> Sequence[Resume]:
        """Alias for get_by_user to fetch all user resumes."""
        return await self.get_by_user(user_id)

    async def set_active(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> None:
        """Deactivates all other resumes for a user and sets the target resume as active."""
        await self.db.execute(
            update(Resume).where(Resume.user_id == user_id).values(is_active=False)
        )
        await self.db.execute(update(Resume).where(Resume.id == resume_id).values(is_active=True))
