"""System health check endpoint."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db, is_sqlite
from app.core.logging import logger

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Check API and Database Health",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Returns application status, version, and database connectivity state."""
    db_status = "disconnected"
    pgvector_status = "disabled"

    try:
        # Check standard database query
        result = await db.execute(text("SELECT 1;"))
        if result.scalar() == 1:
            db_status = "connected"

        if not is_sqlite:
            # Check pgvector extension availability on PostgreSQL
            vec_check = await db.execute(
                text("SELECT count(*) FROM pg_extension WHERE extname = 'vector';")
            )
            if vec_check.scalar() >= 1:
                pgvector_status = "enabled"
        else:
            pgvector_status = "enabled (sqlite fallback)"
    except Exception as e:
        logger.warning("Database health check fallback warning: %s", str(e), exc_info=True)
        db_status = f"degraded: {str(e)}"

    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "pgvector": pgvector_status,
    }
