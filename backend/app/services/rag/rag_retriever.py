"""RAG Retriever fetching candidate profile, skills, top matches, and roadmap knowledge."""

import uuid
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.application_repository import ApplicationRepository
from app.repositories.match_repository import MatchRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.rag.roadmap_knowledge import get_curated_roadmap


class RAGRetriever:
    """Retrieves grounded user database context and vector knowledge for conversational agent."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_rag_context(self, user_id: uuid.UUID, query: str) -> Dict[str, Any]:
        """Gathers active resume skills, top opportunity matches, applications, and curated roadmap context."""
        resume_repo = ResumeRepository(self.db)
        match_repo = MatchRepository(self.db)
        app_repo = ApplicationRepository(self.db)

        active_resume = await resume_repo.get_active_by_user(user_id)
        top_matches = await match_repo.get_top_matches_for_user(user_id, limit=5)
        user_apps = await app_repo.get_user_applications(user_id)

        parsed_data = active_resume.parsed_data_json if active_resume else {}
        user_skills = [
            s.get("name") if isinstance(s, dict) else str(s) for s in parsed_data.get("skills", [])
        ]

        matches_summary = [
            {
                "title": m.opportunity.title if m.opportunity else "Role",
                "company": m.opportunity.company_name if m.opportunity else "Company",
                "fit_score": m.fit_score,
            }
            for m in top_matches
        ]

        roadmap_doc = get_curated_roadmap(query)

        return {
            "candidate_skills": user_skills,
            "years_experience": parsed_data.get("years_experience", 1.0),
            "top_matches": matches_summary,
            "total_applications": len(user_apps),
            "relevant_roadmap_knowledge": roadmap_doc,
        }
