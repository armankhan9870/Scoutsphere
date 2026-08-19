"""Roadmap API endpoints (/users/{id}/roadmap GET, /roadmap/generate POST)."""

import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.roadmap import Roadmap
from app.models.user import User
from app.services.rag.roadmap_knowledge import get_curated_roadmap

router = APIRouter()


@router.get("/users/{user_id}/roadmap")
async def get_user_roadmap(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieves active career roadmap for user."""
    stmt = (
        select(Roadmap)
        .where(Roadmap.user_id == user_id)
        .order_by(Roadmap.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    roadmap = result.scalar_one_or_none()

    if roadmap:
        return {
            "roadmap_id": roadmap.id,
            "user_id": roadmap.user_id,
            "target_role": roadmap.target_role,
            "milestones": roadmap.milestone_nodes_json,
            "created_at": roadmap.created_at,
        }

    # Default fallback roadmap
    target_role = (
        current_user.target_roles[0] if current_user.target_roles else "Machine Learning Engineer"
    )
    default_doc = get_curated_roadmap(target_role)

    return {
        "user_id": user_id,
        "target_role": target_role,
        "milestones": default_doc.get("milestones", []),
    }


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_career_roadmap(
    target_role: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Generates and persists a multi-phase career roadmap based on candidate target role."""
    role = target_role or (
        current_user.target_roles[0] if current_user.target_roles else "Machine Learning Engineer"
    )
    roadmap_doc = get_curated_roadmap(role)

    roadmap_obj = Roadmap(
        user_id=current_user.id,
        target_role=role,
        milestone_nodes_json=roadmap_doc.get("milestones", []),
        skill_requirements_json={"target_role": role},
    )
    db.add(roadmap_obj)
    await db.commit()
    await db.refresh(roadmap_obj)

    return {
        "message": f"Career roadmap for '{role}' generated successfully.",
        "roadmap_id": roadmap_obj.id,
        "target_role": role,
        "milestones": roadmap_obj.milestone_nodes_json,
    }
