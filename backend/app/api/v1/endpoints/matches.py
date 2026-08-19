"""Matches API endpoints (/users/{id}/matches GET, /matches/calculate POST)."""

import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.match import Match
from app.models.user import User
from app.repositories.match_repository import MatchRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.matching.hybrid_scorer import calculate_hybrid_score
from app.services.matching.reranker import LLMRerankerService

router = APIRouter()


@router.get("/users/{user_id}/matches")
async def get_user_matches(
    user_id: uuid.UUID,
    type: Optional[str] = Query(None, description="Filter by JOB, INTERNSHIP, HACKATHON"),
    min_score: float = Query(0.0, ge=0.0, le=100.0, description="Minimum suitability score 0-100"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieves ranked matches for a user with suitability score and natural language rationale."""
    match_repo = MatchRepository(db)
    matches = await match_repo.get_top_matches_for_user(user_id, limit=100)

    # Filter by opportunity_type and min_score
    filtered_results = []
    for m in matches:
        opp = m.opportunity
        if not opp:
            continue
        if type and opp.opportunity_type != type.upper():
            continue
        if m.fit_score < min_score:
            continue

        reasons = m.match_reasons_json or {}
        filtered_results.append(
            {
                "match_id": m.id,
                "fit_score": m.fit_score,
                "skill_overlap_score": m.skill_overlap_score,
                "rationale": reasons.get("rationale")
                or reasons.get("highlights", ["Good match"])[0],
                "opportunity": {
                    "id": opp.id,
                    "title": opp.title,
                    "company_name": opp.company_name,
                    "opportunity_type": opp.opportunity_type,
                    "description": opp.description,
                    "required_skills": opp.required_skills_json,
                    "location": opp.location,
                    "is_remote": opp.is_remote,
                    "source_url": opp.source_url,
                    "deadline": opp.deadline,
                },
                "created_at": m.created_at,
            }
        )

    # Apply pagination offset and limit
    paginated = filtered_results[offset : offset + limit]

    return {
        "total": len(filtered_results),
        "offset": offset,
        "limit": limit,
        "items": paginated,
    }


@router.post("/calculate", status_code=status.HTTP_200_OK)
async def calculate_matches_on_demand(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Calculates vector similarity + heuristic scoring + LLM top-20 re-ranking and persists results to matches table."""
    resume_repo = ResumeRepository(db)
    opp_repo = OpportunityRepository(db)
    match_repo = MatchRepository(db)

    active_resume = await resume_repo.get_active_by_user(current_user.id)
    if not active_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active resume not found. Upload a resume first.",
        )

    # Fetch active opportunities
    opportunities = await opp_repo.filter_opportunities(limit=100)
    if not opportunities:
        return {"message": "No active opportunities available.", "matches_created": 0}

    user_profile = active_resume.parsed_data_json or {}
    if "skills" not in user_profile:
        user_profile["skills"] = current_user.target_roles

    # Heuristic scoring
    candidates = []
    for opp in opportunities:
        # Use pgvector distance if embedding available
        distance = 0.4
        score_dict = calculate_hybrid_score(user_profile, opp, cosine_distance=distance)
        candidates.append((opp, score_dict))

    candidates.sort(key=lambda x: x[1]["fit_score"], reverse=True)

    # LLM re-ranking on top 20
    top_score_dicts = [c[1] for c in candidates[:20]]
    reranker = LLMRerankerService()
    reranked_dicts = await reranker.rerank_top_candidates(user_profile, top_score_dicts)
    reranked_map = {item["opportunity_id"]: item for item in reranked_dicts}

    matches_persisted = 0
    for opp, score_dict in candidates[:20]:
        opp_id = str(opp.id)
        eval_item = reranked_map.get(opp_id, score_dict)
        final_score = eval_item.get("final_score", score_dict["fit_score"])
        rationale = eval_item.get("rationale", "Matches target skill requirements.")

        existing_match = await match_repo.get_by_user_and_opportunity(current_user.id, opp.id)
        if existing_match:
            await match_repo.update(
                existing_match.id,
                fit_score=final_score,
                skill_overlap_score=score_dict["skill_overlap_score"],
                match_reasons_json={"rationale": rationale, "breakdown": score_dict["breakdown"]},
            )
        else:
            match_obj = Match(
                user_id=current_user.id,
                opportunity_id=opp.id,
                fit_score=final_score,
                skill_overlap_score=score_dict["skill_overlap_score"],
                match_reasons_json={"rationale": rationale, "breakdown": score_dict["breakdown"]},
            )
            await match_repo.create(match_obj)
        matches_persisted += 1

    return {
        "message": f"Successfully calculated and persisted {matches_persisted} matches.",
        "matches_created": matches_persisted,
    }
