"""UserSettingsRepository for user configuration and preferences."""

import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_settings import UserSettings
from app.repositories.base import BaseRepository


class UserSettingsRepository(BaseRepository[UserSettings]):
    """Data access repository for UserSettings entity."""

    def __init__(self, db: AsyncSession):
        super().__init__(UserSettings, db)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[UserSettings]:
        """Fetch settings by user UUID."""
        result = await self.db.execute(select(UserSettings).where(UserSettings.user_id == user_id))
        return result.scalar_one_or_none()

    async def create_default(self, user_id: uuid.UUID) -> UserSettings:
        """Create default settings record for a user if absent."""
        existing = await self.get_by_user_id(user_id)
        if existing:
            return existing
        settings_obj = UserSettings(user_id=user_id)
        return await self.create(settings_obj)

    async def update_settings(self, user_id: uuid.UUID, **kwargs: Any) -> Optional[UserSettings]:
        """Update settings fields for a given user."""
        existing = await self.get_by_user_id(user_id)
        if not existing:
            existing = await self.create_default(user_id)

        for key, val in kwargs.items():
            if hasattr(existing, key) and val is not None:
                setattr(existing, key, val)

        await self.db.flush()
        await self.db.refresh(existing)
        return existing
