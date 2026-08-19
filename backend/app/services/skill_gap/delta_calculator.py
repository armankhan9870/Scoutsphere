"""Skill delta calculator determining missing and weak skills."""

from typing import Any, Dict, List, Tuple


def compute_skill_delta(
    user_skills: List[Any], required_skills: List[str]
) -> Tuple[List[str], List[str], List[str]]:
    """Calculates missing skills, weak skills (Beginner), and priority order.

    Returns a tuple of (missing_skills, weak_skills, priority_order).
    """
    user_skill_map: Dict[str, str] = {}
    for s in user_skills:
        if isinstance(s, dict):
            name = s.get("name", "").strip().lower()
            prof = s.get("proficiency_estimate") or s.get("proficiency_level") or "Intermediate"
            user_skill_map[name] = prof
        elif isinstance(s, str):
            user_skill_map[s.strip().lower()] = "Intermediate"

    missing_skills = []
    weak_skills = []

    for req in required_skills:
        req_clean = req.strip().lower()
        if req_clean not in user_skill_map:
            missing_skills.append(req.strip())
        elif user_skill_map[req_clean].lower() == "beginner":
            weak_skills.append(req.strip())

    # Priority order places missing skills first, followed by weak skills
    priority_order = missing_skills + weak_skills

    return missing_skills, weak_skills, priority_order
