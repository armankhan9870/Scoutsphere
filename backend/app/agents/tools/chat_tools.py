"""Tools provided to Chatbot / Roadmap Agent for grounded database queries."""

import json
from typing import List

from app.services.rag.roadmap_knowledge import get_curated_roadmap


def tool_search_opportunities(query: str) -> str:
    """Tool: Searches opportunity listings."""
    return json.dumps(
        [
            {
                "title": "AI/ML Research Intern",
                "company": "Google DeepMind",
                "type": "INTERNSHIP",
                "skills": ["Python", "PyTorch", "LangChain"],
            },
            {
                "title": "Associate AI Systems Engineer",
                "company": "ScoutSphere Inc",
                "type": "JOB",
                "skills": ["Python", "FastAPI", "LangGraph", "PostgreSQL"],
            },
        ]
    )


def tool_get_my_skill_gaps(candidate_skills: List[str]) -> str:
    """Tool: Evaluates missing skills for ML and AI roles."""
    user_skills_lower = {s.lower() for s in candidate_skills}
    gaps = []
    if "pytorch" not in user_skills_lower:
        gaps.append("PyTorch")
    if "langgraph" not in user_skills_lower:
        gaps.append("LangGraph")
    if "kubernetes" not in user_skills_lower:
        gaps.append("Kubernetes")

    return json.dumps(
        {
            "missing_skills": gaps,
            "recommendation": "Focus on PyTorch for model training and LangGraph for multi-agent workflows.",
        }
    )


def tool_get_my_applications(total_apps: int) -> str:
    """Tool: Retrieves candidate application pipeline stats."""
    return json.dumps(
        {
            "total_applications": total_apps,
            "active_pipeline": "1 Applied, 1 Interviewing",
        }
    )


def tool_get_role_roadmap(role: str) -> str:
    """Tool: Fetches structured role roadmap milestones."""
    roadmap = get_curated_roadmap(role)
    return json.dumps(roadmap)
