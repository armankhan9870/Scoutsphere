"""Seed script populating 3 demo users across student, grad, and professional personas with complete profile, settings, refresh token, and audit log entries."""

import asyncio
import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.auth_audit_log import AuthAuditLog
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.models.user_profile import CurrentStatusEnum, RemotePreferenceEnum, UserProfile
from app.models.user_settings import UserSettings

ph = PasswordHasher()


async def seed_users() -> None:
    """Populate database with 3 demo users and associated profile/settings/token/audit entities."""
    print("Starting user seed process...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Define 3 demo users with distinct career personas
        users_payload = [
            {
                "id": uuid.UUID("3e8ec9ae-9d67-48f7-9622-c52de2c7def9"),
                "email": "student@scoutsphere.ai",
                "password": "DemoStudent123!",
                "full_name": "Alex Rivera",
                "phone": "+1-555-0101",
                "email_verified": True,
                "token_version": 1,
                "profile": {
                    "bio": "Senior Computer Science student passionate about async Python backend services, microservices, and agentic AI.",
                    "target_roles": ["Backend Engineer", "AI Developer"],
                    "preferred_locations": ["San Francisco, CA", "Remote"],
                    "remote_preference": RemotePreferenceEnum.REMOTE,
                    "education": {
                        "degree": "B.S. Computer Science",
                        "institution": "Stanford University",
                        "graduation_year": 2026,
                        "gpa": "3.85",
                    },
                    "current_status": CurrentStatusEnum.STUDENT,
                    "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
                },
                "settings": {
                    "notification_prefs": {
                        "email_alerts": True,
                        "match_notifications": True,
                        "weekly_digest": True,
                    },
                    "privacy_prefs": {
                        "profile_visibility": "public",
                        "allow_data_training": False,
                    },
                    "theme": "dark",
                    "auto_run_agents": True,
                    "preferred_llm_provider": "gemini",
                },
                "audit_events": [
                    ("LOGIN_SUCCESS", "192.168.1.10", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"),
                    ("TOKEN_REFRESH", "192.168.1.10", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"),
                ],
            },
            {
                "id": uuid.UUID("5f9fa01b-7a33-4e8c-8822-b91aa3f4e1d2"),
                "email": "grad@scoutsphere.ai",
                "password": "DemoGrad123!",
                "full_name": "Elena Rostova",
                "phone": "+1-555-0202",
                "email_verified": True,
                "token_version": 1,
                "profile": {
                    "bio": "Recent M.S. graduate in Software Engineering focused on full-stack web applications with React, TypeScript, and FastAPI.",
                    "target_roles": ["Full-Stack Engineer", "Frontend Developer"],
                    "preferred_locations": ["New York, NY", "Austin, TX"],
                    "remote_preference": RemotePreferenceEnum.HYBRID,
                    "education": {
                        "degree": "M.S. Software Engineering",
                        "institution": "New York University",
                        "graduation_year": 2025,
                    },
                    "current_status": CurrentStatusEnum.GRAD,
                    "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150",
                },
                "settings": {
                    "notification_prefs": {
                        "email_alerts": True,
                        "match_notifications": True,
                        "weekly_digest": False,
                    },
                    "privacy_prefs": {
                        "profile_visibility": "recruiter_only",
                        "allow_data_training": True,
                    },
                    "theme": "dark",
                    "auto_run_agents": False,
                    "preferred_llm_provider": "groq",
                },
                "audit_events": [
                    (
                        "LOGIN_SUCCESS",
                        "172.16.0.45",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                    ),
                ],
            },
            {
                "id": uuid.UUID("8c29db4e-128b-4b11-9a74-d41ee0f912c3"),
                "email": "pro@scoutsphere.ai",
                "password": "DemoPro123!",
                "full_name": "Marcus Vance",
                "phone": "+1-555-0303",
                "email_verified": True,
                "token_version": 1,
                "profile": {
                    "bio": "Experienced Systems Architect with 8+ years building distributed cloud platforms, pgvector retrieval, and LLM orchestration.",
                    "target_roles": ["Staff AI Systems Architect", "Principal Cloud Engineer"],
                    "preferred_locations": ["Seattle, WA", "Remote"],
                    "remote_preference": RemotePreferenceEnum.REMOTE,
                    "education": {
                        "degree": "B.S. Electrical Engineering & CS",
                        "institution": "MIT",
                        "graduation_year": 2018,
                    },
                    "current_status": CurrentStatusEnum.PROFESSIONAL,
                    "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
                },
                "settings": {
                    "notification_prefs": {
                        "email_alerts": False,
                        "match_notifications": True,
                        "weekly_digest": True,
                    },
                    "privacy_prefs": {
                        "profile_visibility": "private",
                        "allow_data_training": False,
                    },
                    "theme": "light",
                    "auto_run_agents": True,
                    "preferred_llm_provider": "openrouter",
                },
                "audit_events": [
                    ("LOGIN_SUCCESS", "10.0.0.12", "Mozilla/5.0 (X11; Linux x86_64)"),
                    ("PASSWORD_RESET", "10.0.0.12", "Mozilla/5.0 (X11; Linux x86_64)"),
                    ("LOGIN_SUCCESS", "10.0.0.12", "Mozilla/5.0 (X11; Linux x86_64)"),
                ],
            },
        ]

        for u_data in users_payload:
            # Check if user already exists
            from sqlalchemy import select

            existing_res = await session.execute(select(User).where(User.email == u_data["email"]))
            existing_user = existing_res.scalar_one_or_none()

            if existing_user:
                print(f"User {u_data['email']} already exists. Skipping creation.")
                continue

            user_obj = User(
                id=u_data["id"],
                email=u_data["email"],
                hashed_password=ph.hash(u_data["password"]),
                full_name=u_data["full_name"],
                phone=u_data["phone"],
                email_verified=u_data["email_verified"],
                is_active=True,
                token_version=u_data["token_version"],
                last_login_at=datetime.now(timezone.utc),
            )
            session.add(user_obj)
            await session.flush()

            # Profile creation
            prof_data = u_data["profile"]
            profile_obj = UserProfile(
                user_id=user_obj.id,
                bio=prof_data["bio"],
                target_roles=prof_data["target_roles"],
                preferred_locations=prof_data["preferred_locations"],
                remote_preference=prof_data["remote_preference"],
                education=prof_data["education"],
                current_status=prof_data["current_status"],
                avatar_url=prof_data["avatar_url"],
            )
            session.add(profile_obj)

            # Settings creation
            sett_data = u_data["settings"]
            settings_obj = UserSettings(
                user_id=user_obj.id,
                notification_prefs=sett_data["notification_prefs"],
                privacy_prefs=sett_data["privacy_prefs"],
                theme=sett_data["theme"],
                auto_run_agents=sett_data["auto_run_agents"],
                preferred_llm_provider=sett_data["preferred_llm_provider"],
            )
            session.add(settings_obj)

            # Sample Refresh Token
            token_str = f"demo_token_{user_obj.id}_{datetime.now(timezone.utc).timestamp()}"
            token_hash = hashlib.sha256(token_str.encode()).hexdigest()
            refresh_token = RefreshToken(
                user_id=user_obj.id,
                token_hash=token_hash,
                device_info="Chrome 128 / Windows 11",
                ip_address=u_data["audit_events"][0][1],
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
            session.add(refresh_token)

            # Sample Auth Audit Logs
            for event, ip, ua in u_data["audit_events"]:
                audit_log = AuthAuditLog(
                    user_id=user_obj.id,
                    event=event,
                    ip_address=ip,
                    user_agent=ua,
                )
                session.add(audit_log)

            print(
                f"Created demo user: {user_obj.email} ({user_obj.full_name}) - Persona: {prof_data['current_status'].value}"
            )

        await session.commit()
        print("Demo users seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_users())
