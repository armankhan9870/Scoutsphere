"""Hybrid scoring service combining vector similarity, skill overlap %, and remote/location heuristics."""

from typing import Any, Dict

from app.models.opportunity import Opportunity
from app.services.matching.skill_matcher import calculate_skill_overlap


def calculate_hybrid_score(
    user_profile: Dict[str, Any],
    opportunity: Opportunity,
    cosine_distance: float = 0.5,
) -> Dict[str, Any]:
    """Calculates baseline composite match score (0 to 100).

    Components:
    1. Vector Similarity Score (0 - 40 pts)
    2. Skill Overlap Score (0 - 45 pts)
    3. Location & Preference Fit (0 - 15 pts)
    """
    # 1. Vector similarity (cosine distance 0.0=identical, 2.0=opposite)
    sim = max(0.0, 1.0 - (cosine_distance / 2.0))
    vector_pts = sim * 40.0

    # 2. Skill overlap
    user_skills = [
        s.get("name") if isinstance(s, dict) else s for s in user_profile.get("skills", [])
    ]
    required_skills = opportunity.required_skills_json or []
    overlap_ratio, matching_skills, missing_skills = calculate_skill_overlap(
        user_skills, required_skills
    )
    skill_pts = overlap_ratio * 45.0

    # 3. Location preference fit
    location_pref = (user_profile.get("location_preference") or "remote").lower()
    location_pts = 0.0
    if "remote" in location_pref and opportunity.is_remote:
        location_pts = 15.0
    elif opportunity.location and location_pref in opportunity.location.lower():
        location_pts = 10.0
    else:
        location_pts = 5.0

    total_score = round(min(100.0, max(0.0, vector_pts + skill_pts + location_pts)), 1)

    return {
        "opportunity_id": str(opportunity.id),
        "title": opportunity.title,
        "company_name": opportunity.company_name,
        "opportunity_type": opportunity.opportunity_type,
        "fit_score": total_score,
        "skill_overlap_score": round(overlap_ratio, 2),
        "matching_skills": matching_skills,
        "missing_skills": [s for s in required_skills if s not in matching_skills],
        "breakdown": {
            "vector_pts": round(vector_pts, 1),
            "skill_pts": round(skill_pts, 1),
            "location_pts": round(location_pts, 1),
        },
    }
