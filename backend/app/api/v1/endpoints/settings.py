"""Settings API endpoints (/settings GET/PUT, security sessions, privacy export, purge)."""

import random
import string
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.core.logging import logger
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.settings_repository import SettingsRepository
from app.schemas.settings import (
    ChangeEmailRequest,
    ChangePasswordRequest,
    EmailVerificationRequest,
    UserSessionResponse,
    UserSettingsResponse,
    UserSettingsUpdate,
)

router = APIRouter()


@router.get("", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettingsResponse:
    """Fetch current user's preferences, settings, and agent configs."""
    repo = SettingsRepository(db)
    settings = await repo.get_or_create_settings(current_user)

    return UserSettingsResponse(
        id=settings.id,
        user_id=settings.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        pending_new_email=settings.pending_new_email,
        target_roles=settings.target_roles,
        target_industries=settings.target_industries,
        target_locations=settings.target_locations,
        work_style=settings.work_style,
        min_salary=settings.min_salary,
        opportunity_types=settings.opportunity_types,
        discovery_frequency=settings.discovery_frequency,
        source_filters=settings.source_filters,
        min_match_score=settings.min_match_score,
        auto_hide_low_score=settings.auto_hide_low_score,
        default_resume_template=settings.default_resume_template,
        cover_letter_tone=settings.cover_letter_tone,
        auto_tailor_high_matches=settings.auto_tailor_high_matches,
        preferred_llm_provider=settings.preferred_llm_provider,
        agent_tone=settings.agent_tone,
        auto_background_agents=settings.auto_background_agents,
        notify_high_matches=settings.notify_high_matches,
        notify_deadlines=settings.notify_deadlines,
        notify_status_changes=settings.notify_status_changes,
        notify_weekly_digest=settings.notify_weekly_digest,
        email_notifications_enabled=settings.email_notifications_enabled,
        exclude_resume_from_training=settings.exclude_resume_from_training,
        theme=settings.theme,
        layout_density=settings.layout_density,
        created_at=settings.created_at,
        updated_at=settings.updated_at,
    )


@router.put("", response_model=UserSettingsResponse)
async def update_user_settings(
    update_data: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettingsResponse:
    """Update user settings and agent automation dials."""
    repo = SettingsRepository(db)
    settings = await repo.get_or_create_settings(current_user)

    # Update full_name on User model if supplied
    data = update_data.model_dump(exclude_unset=True)
    if "full_name" in data and data["full_name"]:
        current_user.full_name = data.pop("full_name")
        db.add(current_user)

    updated_settings = await repo.update_settings(settings, data)

    # Keep target_roles synced on user model if updated
    if "target_roles" in data and data["target_roles"]:
        current_user.target_roles = data["target_roles"]
        db.add(current_user)

    await db.commit()

    return UserSettingsResponse(
        id=updated_settings.id,
        user_id=updated_settings.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        pending_new_email=updated_settings.pending_new_email,
        target_roles=updated_settings.target_roles,
        target_industries=updated_settings.target_industries,
        target_locations=updated_settings.target_locations,
        work_style=updated_settings.work_style,
        min_salary=updated_settings.min_salary,
        opportunity_types=updated_settings.opportunity_types,
        discovery_frequency=updated_settings.discovery_frequency,
        source_filters=updated_settings.source_filters,
        min_match_score=updated_settings.min_match_score,
        auto_hide_low_score=updated_settings.auto_hide_low_score,
        default_resume_template=updated_settings.default_resume_template,
        cover_letter_tone=updated_settings.cover_letter_tone,
        auto_tailor_high_matches=updated_settings.auto_tailor_high_matches,
        preferred_llm_provider=updated_settings.preferred_llm_provider,
        agent_tone=updated_settings.agent_tone,
        auto_background_agents=updated_settings.auto_background_agents,
        notify_high_matches=updated_settings.notify_high_matches,
        notify_deadlines=updated_settings.notify_deadlines,
        notify_status_changes=updated_settings.notify_status_changes,
        notify_weekly_digest=updated_settings.notify_weekly_digest,
        email_notifications_enabled=updated_settings.email_notifications_enabled,
        exclude_resume_from_training=updated_settings.exclude_resume_from_training,
        theme=updated_settings.theme,
        layout_density=updated_settings.layout_density,
        created_at=updated_settings.created_at,
        updated_at=updated_settings.updated_at,
    )


@router.post("/account/password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Change account password."""
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password.")

    current_user.password_hash = hash_password(payload.new_password)

    db.add(current_user)
    await db.commit()

    logger.info("User %s changed their password successfully.", current_user.id)
    return {"message": "Password changed successfully."}


@router.post("/account/email/request")
async def request_email_change(
    payload: ChangeEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Initiate email change flow and log verification code (stubbed interface)."""
    if payload.new_email == current_user.email:
        raise HTTPException(status_code=400, detail="New email is identical to current email.")

    repo = SettingsRepository(db)
    settings = await repo.get_or_create_settings(current_user)

    code = "".join(random.choices(string.digits, k=6))
    settings.pending_new_email = payload.new_email
    settings.email_verification_code = code
    db.add(settings)
    await db.commit()

    # Stubbed Email Dispatch Log
    logger.info(
        "[STUBBED EMAIL DISPATCH] Verification code '%s' sent to '%s' for user '%s'.",
        code,
        payload.new_email,
        current_user.id,
    )

    return {
        "message": f"Verification code sent to {payload.new_email}. (Demo Code: {code})",
        "pending_email": payload.new_email,
        "verification_code_demo": code,
    }


@router.post("/account/email/verify")
async def verify_email_change(
    payload: EmailVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Confirm email change verification code and update user email."""
    repo = SettingsRepository(db)
    settings = await repo.get_or_create_settings(current_user)

    if not settings.pending_new_email or not settings.email_verification_code:
        raise HTTPException(status_code=400, detail="No pending email change request found.")

    if payload.verification_code.strip() != settings.email_verification_code.strip():
        raise HTTPException(status_code=400, detail="Invalid verification code.")

    old_email = current_user.email
    current_user.email = settings.pending_new_email
    settings.pending_new_email = None
    settings.email_verification_code = None

    db.add(current_user)
    db.add(settings)
    await db.commit()

    logger.info(
        "User %s changed email from '%s' to '%s'.", current_user.id, old_email, current_user.email
    )
    return {"message": "Email address updated successfully.", "email": current_user.email}


@router.get("/security/sessions", response_model=List[UserSessionResponse])
async def list_active_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[UserSessionResponse]:
    """List active security login sessions for current user."""
    repo = SettingsRepository(db)
    sessions = await repo.get_active_sessions(current_user.id)
    return [UserSessionResponse.model_validate(s) for s in sessions]


@router.delete("/security/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Revoke a specific active login session."""
    import uuid

    repo = SettingsRepository(db)
    try:
        sess_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format.")

    success = await repo.revoke_session(current_user.id, sess_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Active session not found.")

    return {"message": "Session revoked successfully."}


@router.post("/security/sessions/revoke-all")
async def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Revoke all active sessions for current user (invalidate all devices)."""
    repo = SettingsRepository(db)
    count = await repo.revoke_all_sessions(current_user.id)
    return {"message": "All active sessions revoked successfully.", "revoked_count": count}


@router.get("/privacy/export")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Download complete JSON dump of profile, resumes, matches, applications, and chat history."""
    repo = SettingsRepository(db)
    export_data = await repo.export_user_data(current_user)
    return export_data


@router.delete("/account/purge")
async def purge_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Permanently delete account and purge all associated records."""
    user_id = str(current_user.id)
    repo = SettingsRepository(db)
    await repo.purge_user_account(current_user)

    logger.info("Permanently purged account and all associated records for user ID %s.", user_id)
    return {"message": "Account permanently deleted and all data purged."}
