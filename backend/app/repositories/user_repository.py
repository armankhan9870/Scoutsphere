"""UserRepository for user accounts, credentials, and session management."""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import _USER_TRANSIENT_STORE, User, UserSkill
from app.repositories.base import BaseRepository
from app.repositories.user_profile_repository import UserProfileRepository


class UserRepository(BaseRepository[User]):
    """Data access repository for User entity with async CRUD methods."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_id(self, id: uuid.UUID) -> Optional[User]:
        """Fetch a single record by primary key UUID with profile loaded."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.profile), selectinload(User.settings))
            .where(User.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user record by email address (citext match) with profile loaded."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.profile), selectinload(User.settings))
            .where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def get_by_oauth(self, provider: str, oauth_id: str) -> Optional[User]:
        """Fetch a user record by OAuth provider and OAuth ID."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.profile), selectinload(User.settings))
            .where(User.oauth_provider == provider, User.oauth_id == oauth_id)
        )
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Fetch a user record by Google OAuth ID."""
        return await self.get_by_oauth("google", google_id)

    async def get_by_email_verification_token(self, token_hash: str) -> Optional[User]:
        """Fetch a user record by email verification token hash."""
        for uid, data in _USER_TRANSIENT_STORE.items():
            if data.get("email_verification_token_hash") == token_hash:
                return await self.get_by_id(uid)
        return None

    async def get_by_password_reset_token(self, token_hash: str) -> Optional[User]:
        """Fetch a user record by password reset token hash."""
        for uid, data in _USER_TRANSIENT_STORE.items():
            if data.get("password_reset_token_hash") == token_hash:
                return await self.get_by_id(uid)
        return None

    async def get_with_skills(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a user with eagerly loaded skills."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.user_skills).selectinload(UserSkill.skill))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_with_relations(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a user with profile and settings eagerly loaded."""
        return await self.get_by_id(user_id)

    async def update(self, id: uuid.UUID, **kwargs: Any) -> Optional[User]:
        """Update user record and delegate profile specific attributes to UserProfile."""
        profile_keys = {
            "target_roles",
            "location_preference",
            "bio",
            "preferred_locations",
            "remote_preference",
            "education",
            "current_status",
            "avatar_url",
        }
        profile_updates = {k: kwargs.pop(k) for k in list(kwargs.keys()) if k in profile_keys}

        if kwargs:
            stmt = update(User).where(User.id == id).values(**kwargs)
            await self.db.execute(stmt)

        if profile_updates:
            prof_repo = UserProfileRepository(self.db)
            if "location_preference" in profile_updates:
                loc = profile_updates.pop("location_preference")
                if loc and "preferred_locations" not in profile_updates:
                    profile_updates["preferred_locations"] = [loc]
            await prof_repo.create_or_update(id, **profile_updates)

        await self.db.flush()
        self.db.expire_all()
        return await self.get_by_id(id)

    async def increment_token_version(self, user_id: uuid.UUID) -> int:
        """Increment token_version to invalidate all active JWT refresh/access tokens."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(token_version=User.token_version + 1)
            .returning(User.token_version)
        )
        result = await self.db.execute(stmt)
        new_version = result.scalar_one_or_none()
        return new_version or 1

    async def update_last_login(
        self, user_id: uuid.UUID, login_dt: Optional[datetime] = None
    ) -> Optional[User]:
        """Update last_login_at timestamp for a user."""
        dt = login_dt or datetime.now(timezone.utc)
        return await self.update(user_id, last_login_at=dt)
