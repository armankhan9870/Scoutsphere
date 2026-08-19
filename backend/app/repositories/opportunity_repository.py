"""OpportunityRepository for filtering opportunities and executing pgvector cosine distance search."""

from typing import List, Optional, Sequence, Tuple

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import Opportunity
from app.repositories.base import BaseRepository


class OpportunityRepository(BaseRepository[Opportunity]):
    """Data access repository for Opportunity entities with pgvector similarity search."""

    def __init__(self, db: AsyncSession):
        super().__init__(Opportunity, db)

    async def get_by_source_url(self, source_url: str) -> Optional[Opportunity]:
        """Fetch an opportunity by its unique source URL."""
        result = await self.db.execute(
            select(Opportunity).where(Opportunity.source_url == source_url)
        )
        return result.scalar_one_or_none()

    async def filter_opportunities(
        self,
        opportunity_type: Optional[str] = None,
        is_remote: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Opportunity]:
        """Filter opportunities by type, remote status, and text search."""
        stmt = select(Opportunity)

        if opportunity_type:
            stmt = stmt.where(Opportunity.opportunity_type == opportunity_type.upper())
        if is_remote is not None:
            stmt = stmt.where(Opportunity.is_remote == is_remote)

        if search_query:
            term = f"%{search_query}%"
            stmt = stmt.where(
                or_(
                    Opportunity.title.ilike(term),
                    Opportunity.company_name.ilike(term),
                    Opportunity.description.ilike(term),
                )
            )

        stmt = stmt.order_by(Opportunity.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def search_by_vector(
        self,
        query_vector: List[float],
        opportunity_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Tuple[Opportunity, float]]:
        """Executes pgvector cosine similarity search against opportunities table.

        Returns a list of tuples: (Opportunity, cosine_distance_score).
        Cosine distance ranges from 0.0 (identical) to 2.0 (opposite). Similarity = 1 - distance.
        """
        # pgvector cosine_distance operator is `cosine_distance` or `<=>`
        stmt = select(
            Opportunity,
            Opportunity.embedding.cosine_distance(query_vector).label("distance"),
        ).where(Opportunity.embedding.is_not(None))

        if opportunity_type:
            stmt = stmt.where(Opportunity.opportunity_type == opportunity_type.upper())

        stmt = stmt.order_by("distance").limit(limit)
        result = await self.db.execute(stmt)
        return [(row.Opportunity, float(row.distance)) for row in result.all()]
