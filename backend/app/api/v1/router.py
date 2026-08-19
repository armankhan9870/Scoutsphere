"""Central API router assembling all v1 resource endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    applications,
    auth,
    chat,
    health,
    matches,
    opportunities,
    resumes,
    roadmap,
    settings,
    skill_gaps,
    users,
)

api_router = APIRouter()

# Mount endpoints
api_router.include_router(health.router, tags=["System Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users & Profiles"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["Opportunities"])
api_router.include_router(matches.router, prefix="/matches", tags=["Matches"])
api_router.include_router(skill_gaps.router, prefix="/skill-gaps", tags=["Skill Gaps"])
api_router.include_router(
    applications.router, prefix="/applications", tags=["Applications & Tailoring"]
)
api_router.include_router(chat.router, prefix="/chat", tags=["Career Chatbot"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["Roadmaps"])
api_router.include_router(settings.router, prefix="/settings", tags=["User Settings"])
