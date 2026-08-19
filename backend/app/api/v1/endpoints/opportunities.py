"""Opportunities API endpoints (/search, /discover)."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.opportunity_repository import OpportunityRepository
from app.worker.tasks import _execute_discovery_pipeline

router = APIRouter()


@router.get("", response_model=Dict[str, Any])
@router.get("/", response_model=Dict[str, Any])
@router.get("/search", response_model=Dict[str, Any])
async def search_opportunities(
    query: Optional[str] = Query(None, description="Search term"),
    type: Optional[str] = Query(None, description="JOB, INTERNSHIP, HACKATHON"),
    is_remote: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Searches and filters job, internship, and hackathon opportunities."""
    repo = OpportunityRepository(db)
    try:
        items = await repo.filter_opportunities(
            opportunity_type=type,
            is_remote=is_remote,
            search_query=query,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        print("ERROR IN SEARCH OPPORTUNITIES:", str(e))
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    return {
        "count": len(items),
        "offset": offset,
        "limit": limit,
        "items": [
            {
                "id": str(o.id),
                "title": o.title,
                "company_name": o.company_name,
                "opportunity_type": o.opportunity_type,
                "description": o.description,
                "required_skills": o.required_skills_json or [],
                "required_skills_json": o.required_skills_json or [],
                "location": o.location or "Remote",
                "is_remote": o.is_remote,
                "source_url": o.source_url,
                "deadline": o.deadline.isoformat() if o.deadline else None,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in items
        ],
    }


@router.post("/discover", status_code=status.HTTP_200_OK)
async def trigger_discovery_now(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Manually triggers the Discovery Agent job to fetch, normalize, deduplicate, and persist new listings."""
    result = await _execute_discovery_pipeline()
    return {
        "message": "Discovery refresh job executed successfully.",
        "details": result,
    }
