"""Celery async background tasks for Discovery Agent background fetching."""

import asyncio
from typing import Any, Dict

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.logging import logger
from app.models.application import Application
from app.services.discovery.deduplicator import DeduplicatorService
from app.services.discovery.mock_sources import (
    MockHackathonSource,
    MockInternshipSource,
    MockJobBoardSource,
)
from app.services.discovery.normalizer import normalize_raw_opportunity
from app.services.tracking.tracking_service import calculate_pipeline_stats
from app.worker.celery_app import celery_app


async def _execute_discovery_pipeline() -> Dict[str, Any]:
    """Internal async helper fetching, normalizing, deduplicating, and persisting opportunities."""
    logger.info("Starting background discovery pipeline task...")
    sources = [
        MockJobBoardSource(),
        MockHackathonSource(),
        MockInternshipSource(),
    ]

    all_raw = []
    for s in sources:
        items = await s.fetch()
        all_raw.extend(items)

    candidates = [normalize_raw_opportunity(raw) for raw in all_raw]

    async with AsyncSessionLocal() as session:
        deduper = DeduplicatorService(session)
        unique_opps, duplicate_count = await deduper.filter_duplicates(candidates)

        if unique_opps:
            session.add_all(unique_opps)
            await session.commit()
            logger.info(
                "Successfully persisted %d new unique opportunities to DB (%d duplicates skipped).",
                len(unique_opps),
                duplicate_count,
            )

        return {
            "status": "success",
            "fetched_count": len(all_raw),
            "inserted_count": len(unique_opps),
            "duplicate_count": duplicate_count,
        }


@celery_app.task(name="tasks.run_discovery_job")
def run_discovery_job_task() -> Dict[str, Any]:
    """Celery background task executed periodically by Celery Beat every 6 hours."""
    return asyncio.run(_execute_discovery_pipeline())


async def _execute_tracking_reminders() -> Dict[str, Any]:
    """Scans active applications for stale status entries and upcoming deadline reminders."""
    logger.info("Starting background tracking reminder task...")
    async with AsyncSessionLocal() as session:
        # Scan applications
        result = await session.execute(select(Application))
        all_apps = result.scalars().all()
        stats = calculate_pipeline_stats(list(all_apps))
        return {
            "status": "success",
            "stale_followup_count": len(stats["stale_followup_nudges"]),
            "upcoming_deadlines_count": len(stats["upcoming_deadlines"]),
        }


@celery_app.task(name="tasks.run_tracking_reminders")
def run_tracking_reminder_job_task() -> Dict[str, Any]:
    """Celery periodic task scanning for stale applications and deadline nudges."""
    return asyncio.run(_execute_tracking_reminders())
