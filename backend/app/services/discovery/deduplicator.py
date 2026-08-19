"""Deduplication service checking source URLs and fuzzy title/organization matching."""

from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.opportunity import Opportunity


class DeduplicatorService:
    """Filters duplicate opportunities prior to database insertion."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def filter_duplicates(
        self, candidates: List[Opportunity]
    ) -> Tuple[List[Opportunity], int]:
        """Compares candidate opportunities against database records.

        Returns a tuple of (unique_opportunities_to_insert, duplicate_count).
        """
        if not candidates:
            return [], 0

        # Extract URLs for exact matching
        urls = [c.source_url for c in candidates if c.source_url]
        existing_urls_result = await self.db.execute(
            select(Opportunity.source_url).where(Opportunity.source_url.in_(urls))
        )
        existing_urls = set(existing_urls_result.scalars().all())

        # Extract (title, company_name) pairs for fuzzy matching
        existing_pairs_result = await self.db.execute(
            select(Opportunity.title, Opportunity.company_name)
        )
        existing_pairs = {
            (row.title.lower().strip(), row.company_name.lower().strip())
            for row in existing_pairs_result.all()
        }

        unique_list = []
        duplicates = 0

        for opp in candidates:
            pair = (opp.title.lower().strip(), opp.company_name.lower().strip())
            if opp.source_url in existing_urls or pair in existing_pairs:
                duplicates += 1
                logger.info(
                    "Deduplicated existing opportunity: '%s' at '%s'", opp.title, opp.company_name
                )
            else:
                unique_list.append(opp)
                existing_urls.add(opp.source_url)
                existing_pairs.add(pair)

        return unique_list, duplicates
