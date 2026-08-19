"""MatchRepository for recording and querying user-opportunity fit scores."""

import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.match import Match
from app.repositories.base import BaseRepository


class MatchRepository(BaseRepository[Match]):
    """Data access repository for Match entities."""

    def __init__(self, db: AsyncSession):
        super().__init__(Match, db)

    async def get_by_user_and_opportunity(
        self, user_id: uuid.UUID, opportunity_id: uuid.UUID
    ) -> Optional[Match]:
        """Fetch existing match record for a user and opportunity."""
        result = await self.db.execute(
            select(Match).where(Match.user_id == user_id, Match.opportunity_id == opportunity_id)
        )
        return result.scalar_one_or_none()

    async def get_top_matches_for_user(
        self, user_id: uuid.UUID, limit: int = 10
    ) -> Sequence[Match]:
        """Fetch top ranked matches for a user sorted by fit_score descending."""
        result = await self.db.execute(
            select(Match)
            .options(selectinload(Match.opportunity))
            .where(Match.user_id == user_id)
            .order_by(Match.fit_score.desc())
            .limit(limit)
        )
        return result.scalars().all()
