"""Skill Gaps API endpoints (/users/{id}/skill-gaps GET, /skill-gaps/analyze POST)."""

import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.nodes.skill_gap_node import run_skill_gap_agent_node
from app.agents.state import ScoutSphereState
from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.skill_gap import SkillGap
from app.models.user import User
from app.repositories.opportunity_repository import OpportunityRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.skill_gap.delta_calculator import compute_skill_delta
from app.services.skill_gap.url_validator import validate_and_flag_resources

router = APIRouter()


@router.get("/users/{user_id}/skill-gaps")
async def get_user_skill_gaps(
    user_id: uuid.UUID,
    opportunity_id: Optional[uuid.UUID] = Query(None, description="Target Opportunity ID"),
    target_role: Optional[str] = Query(None, description="Target Role Title"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieves skill gap report linked to an opportunity or target role."""
    stmt = select(SkillGap).where(SkillGap.user_id == user_id)
    if opportunity_id:
        stmt = stmt.where(SkillGap.opportunity_id == opportunity_id)

    stmt = stmt.order_by(SkillGap.created_at.desc()).limit(1)
    result = await db.execute(stmt)
    gap_record = result.scalar_one_or_none()

    if gap_record:
        return {
            "id": gap_record.id,
            "user_id": gap_record.user_id,
            "opportunity_id": gap_record.opportunity_id,
            "missing_skills": gap_record.missing_skills_json,
            "recommended_resources": gap_record.recommended_resources_json,
            "match_impact_score": gap_record.match_impact_score,
            "created_at": gap_record.created_at,
        }

    # If no stored gap report exists, execute on-demand calculation
    if opportunity_id:
        opp_repo = OpportunityRepository(db)
        opp = await opp_repo.get_by_id(opportunity_id)
        if not opp:
            raise HTTPException(status_code=404, detail="Opportunity not found.")

        resume_repo = ResumeRepository(db)
        active_resume = await resume_repo.get_active_by_user(user_id)
        user_skills = (
            active_resume.parsed_data_json.get("skills", [])
            if active_resume
            else current_user.target_roles
        )

        missing, weak, priority = compute_skill_delta(user_skills, opp.required_skills_json)

        default_resources = validate_and_flag_resources(
            [
                {
                    "skill": sk,
                    "resource_title": f"Official {sk} Documentation & Tutorials",
                    "resource_url": "https://docs.python.org/3/",
                    "resource_type": "Documentation",
                    "estimated_time": "5 hours",
                }
                for sk in priority
            ]
        )

        return {
            "user_id": user_id,
            "opportunity_id": opportunity_id,
            "missing_skills": missing,
            "weak_skills": weak,
            "priority_order": priority,
            "recommended_resources": default_resources,
            "match_impact_score": round(len(priority) * 8.5, 1),
        }

    return {
        "user_id": user_id,
        "target_role": (
            target_role or current_user.target_roles[0]
            if current_user.target_roles
            else "Developer"
        ),
        "missing_skills": [],
        "weak_skills": [],
        "recommended_resources": [],
        "match_impact_score": 0.0,
    }


@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze_skill_gap_now(
    opportunity_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Triggers the Skill Gap Agent node for an opportunity and persists results to skill_gaps table."""
    opp_repo = OpportunityRepository(db)
    opp = await opp_repo.get_by_id(opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    resume_repo = ResumeRepository(db)
    active_resume = await resume_repo.get_active_by_user(current_user.id)
    user_skills = (
        active_resume.parsed_data_json.get("skills", [])
        if active_resume
        else current_user.target_roles
    )

    state: ScoutSphereState = {
        "user_id": str(current_user.id),
        "session_id": str(uuid.uuid4()),
        "current_intent": "analyze_skill_gap",
        "raw_resume_text": active_resume.raw_text if active_resume else "",
        "user_profile": {"skills": user_skills},
        "parsed_profile": {"skills": user_skills},
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": [
            {
                "id": str(opp.id),
                "title": opp.title,
                "company_name": opp.company_name,
                "required_skills_json": opp.required_skills_json,
            }
        ],
        "target_opportunity_id": str(opp.id),
        "matches": None,
        "skill_gap_analysis": None,
        "tailored_resume": None,
        "application_draft": None,
        "chat_query": None,
        "chat_history": [],
        "roadmap_result": None,
        "messages": [],
        "errors": [],
        "next_node": None,
    }

    final_state = await run_skill_gap_agent_node(state)
    analysis = final_state.get("skill_gap_analysis") or {}

    # Persist to skill_gaps database table
    gap_record = SkillGap(
        user_id=current_user.id,
        opportunity_id=opp.id,
        missing_skills_json=analysis.get("missing_skills", []),
        recommended_resources_json=analysis.get("recommended_resources", []),
        match_impact_score=analysis.get("match_impact_score", 0.0),
    )
    db.add(gap_record)
    await db.commit()

    return {
        "message": "Skill gap report generated and persisted successfully.",
        "opportunity_id": opp.id,
        "report": analysis,
    }
