"""Consolidated skill matching and overlap calculation service."""

from typing import Any, List, Tuple


def normalize_skill_name(skill: Any) -> str:
    """Extracts string skill name from dict or string instance and converts to clean lowercase."""
    if isinstance(skill, dict):
        name = skill.get("name") or skill.get("skill") or str(skill)
    else:
        name = str(skill)
    return name.lower().strip()


def calculate_skill_overlap(
    user_skills: List[Any], required_skills: List[str]
) -> Tuple[float, List[str], List[str]]:
    """Calculates skill overlap ratio (0.0 to 1.0), matching skills, and missing skills.

    Consolidates skill matching logic across Job Discovery, Matching, Tailoring, and ATS scoring.
    """
    if not required_skills:
        return 1.0, [normalize_skill_name(s) for s in user_skills], []

    user_skills_clean = {normalize_skill_name(s) for s in user_skills if s}
    matching_skills = []
    missing_skills = []

    for req in required_skills:
        req_clean = req.lower().strip()
        if req_clean in user_skills_clean:
            matching_skills.append(req)
        else:
            missing_skills.append(req)

    overlap_ratio = len(matching_skills) / len(required_skills) if required_skills else 1.0
    return round(overlap_ratio, 4), matching_skills, missing_skills
