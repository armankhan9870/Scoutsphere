"""UserProfileRepository for extended user profile data access."""

import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile
from app.repositories.base import BaseRepository


class UserProfileRepository(BaseRepository[UserProfile]):
    """Data access repository for UserProfile entity."""

    def __init__(self, db: AsyncSession):
        super().__init__(UserProfile, db)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        """Fetch profile by user UUID."""
        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        return result.scalar_one_or_none()

    async def create_or_update(self, user_id: uuid.UUID, **profile_data: Any) -> UserProfile:
        """Create a profile if it doesn't exist, or update existing fields."""
        existing = await self.get_by_user_id(user_id)
        if existing:
            for key, val in profile_data.items():
                if hasattr(existing, key) and val is not None:
                    setattr(existing, key, val)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            new_profile = UserProfile(user_id=user_id, **profile_data)
            return await self.create(new_profile)
