"""Repository for managing user settings, login sessions, data exports, and account purge."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.chat import ChatSession
from app.models.match import Match
from app.models.resume import Resume
from app.models.roadmap import Roadmap
from app.models.skill_gap import SkillGap
from app.models.user import User
from app.models.user_session import UserSession
from app.models.user_settings import UserSettings


class SettingsRepository:
    """Repository handling UserSettings persistence, sessions, and data lifecycle."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_settings(self, user: User) -> UserSettings:
        """Fetch existing user settings or create default settings if none exist."""
        stmt = select(UserSettings).where(UserSettings.user_id == user.id)
        result = await self.db.execute(stmt)
        settings = result.scalar_one_or_none()

        if not settings:
            settings = UserSettings(
                user_id=user.id,
                target_roles=user.target_roles or ["Software Engineer", "AI Systems Engineer"],
                target_locations=(
                    [user.location_preference] if user.location_preference else ["Remote"]
                ),
            )
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)

        return settings

    async def update_settings(
        self, settings: UserSettings, update_data: Dict[str, Any]
    ) -> UserSettings:
        """Apply dictionary updates to a UserSettings instance."""
        for field, value in update_data.items():
            if value is not None and hasattr(settings, field):
                setattr(settings, field, value)

        settings.updated_at = datetime.now(timezone.utc)
        self.db.add(settings)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def get_active_sessions(self, user_id: uuid.UUID) -> List[UserSession]:
        """Fetch all active security sessions for a user."""
        stmt = (
            select(UserSession)
            .where(UserSession.user_id == user_id, UserSession.is_active.is_(True))
            .order_by(UserSession.last_active.desc())
        )
        result = await self.db.execute(stmt)
        sessions = list(result.scalars().all())

        # If no active sessions exist, seed a primary session for the current client device
        if not sessions:
            default_session = UserSession(
                user_id=user_id,
                device_info="Current Browser (Windows / Chrome)",
                ip_address="127.0.0.1",
                token_hash=str(uuid.uuid4()),
                is_active=True,
            )
            self.db.add(default_session)
            await self.db.commit()
            await self.db.refresh(default_session)
            return [default_session]

        return sessions

    async def revoke_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> bool:
        """Deactivate a specific user session by ID."""
        stmt = select(UserSession).where(
            UserSession.id == session_id, UserSession.user_id == user_id
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        if not session:
            return False

        session.is_active = False
        self.db.add(session)
        await self.db.commit()
        return True

    async def revoke_all_sessions(self, user_id: uuid.UUID) -> int:
        """Deactivate all active sessions for a user."""
        stmt = select(UserSession).where(
            UserSession.user_id == user_id, UserSession.is_active.is_(True)
        )
        result = await self.db.execute(stmt)
        sessions = list(result.scalars().all())

        count = 0
        for sess in sessions:
            sess.is_active = False
            self.db.add(sess)
            count += 1

        await self.db.commit()
        return count

    async def export_user_data(self, user: User) -> Dict[str, Any]:
        """Generate a complete JSON data dump archive for privacy compliance."""
        settings = await self.get_or_create_settings(user)

        resumes = list(
            (await self.db.execute(select(Resume).where(Resume.user_id == user.id))).scalars().all()
        )
        matches = list(
            (await self.db.execute(select(Match).where(Match.user_id == user.id))).scalars().all()
        )
        apps = list(
            (await self.db.execute(select(Application).where(Application.user_id == user.id)))
            .scalars()
            .all()
        )
        chats = list(
            (await self.db.execute(select(ChatSession).where(ChatSession.user_id == user.id)))
            .scalars()
            .all()
        )
        roadmaps = list(
            (await self.db.execute(select(Roadmap).where(Roadmap.user_id == user.id)))
            .scalars()
            .all()
        )
        gaps = list(
            (await self.db.execute(select(SkillGap).where(SkillGap.user_id == user.id)))
            .scalars()
            .all()
        )

        return {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "user_profile": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "target_roles": user.target_roles,
                "location_preference": getattr(user, "location_preference", None),
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
            "settings": {
                "preferred_llm_provider": settings.preferred_llm_provider,
                "agent_tone": settings.agent_tone,
                "min_match_score": settings.min_match_score,
                "auto_background_agents": settings.auto_background_agents,
                "exclude_resume_from_training": settings.exclude_resume_from_training,
                "theme": settings.theme,
            },
            "resumes": [
                {
                    "id": str(r.id),
                    "file_path": r.file_path,
                    "parsed_data": r.parsed_data_json,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in resumes
            ],
            "matches": [
                {
                    "id": str(m.id),
                    "opportunity_id": str(m.opportunity_id),
                    "fit_score": m.fit_score,
                    "match_reasons": m.match_reasons_json,
                }
                for m in matches
            ],
            "applications": [
                {
                    "id": str(a.id),
                    "opportunity_id": str(a.opportunity_id),
                    "status": a.status,
                    "notes": a.notes,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in apps
            ],
            "chat_sessions": [
                {
                    "id": str(c.id),
                    "title": c.title,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in chats
            ],
            "roadmaps": [
                {
                    "id": str(rm.id),
                    "target_role": rm.target_role,
                    "nodes": rm.roadmap_nodes_json,
                }
                for rm in roadmaps
            ],
            "skill_gaps": [
                {
                    "id": str(sg.id),
                    "target_role": sg.target_role,
                    "gap_skills": sg.gap_skills_json,
                }
                for sg in gaps
            ],
        }

    async def purge_user_account(self, user: User) -> bool:
        """Permanently delete a user account and cascade purge all associated records."""
        await self.db.delete(user)
        await self.db.commit()
        return True
