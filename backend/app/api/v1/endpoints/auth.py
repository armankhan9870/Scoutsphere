"""Production-grade Authentication endpoints.

Endpoints:
- POST /signup
- POST /login
- POST /refresh
- POST /logout
- POST /logout-all
- POST /verify-email
- POST /resend-verification
- POST /forgot-password
- POST /reset-password
- POST /google
- GET  /me
- GET  /sessions
- DELETE /sessions/{session_id}
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_current_user_and_session
from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_secure_token,
    hash_password,
    hash_token,
    send_password_reset_email_stub,
    send_verification_email_stub,
    verify_google_id_token,
    verify_password,
)
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.user_settings import UserSettings
from app.repositories.user_repository import UserRepository
from app.repositories.user_session_repository import UserSessionRepository
from app.schemas.auth import (
    ForgotPasswordRequest,
    GoogleAuthRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    SignUpRequest,
    TokenResponse,
    UserSessionResponse,
    VerifyEmailRequest,
)
from app.schemas.user import UserResponse

router = APIRouter()

REFRESH_COOKIE_NAME = "scoutsphere_refresh_token"


def _ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensures datetime object is timezone-aware UTC for safe comparisons across SQLite and Postgres."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _set_refresh_cookie(response: Response, refresh_token_str: str) -> None:
    """Helper to attach secure httpOnly refresh cookie to HTTP response."""
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token_str,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT.lower() == "production",
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Helper to clear refresh cookie on logout or token invalidation."""
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/api/v1/auth",
    )


def _extract_device_and_ip(request: Request) -> tuple[str, str]:
    """Helper to extract user-agent device info and IP address from incoming HTTP request."""
    user_agent = request.headers.get("user-agent", "Web Browser")
    device_info = user_agent[:250] if user_agent else "Web Browser"
    client_ip = request.headers.get("x-forwarded-for")
    if client_ip:
        ip_address = client_ip.split(",")[0].strip()
    elif request.client and request.client.host:
        ip_address = request.client.host
    else:
        ip_address = "127.0.0.1"
    return device_info, ip_address


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def signup(
    payload: SignUpRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Registers a new user with Argon2 password hashing and triggers email verification stub."""
    user_repo = UserRepository(db)
    session_repo = UserSessionRepository(db)

    existing = await user_repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Generate verification token
    verification_token = generate_secure_token(32)
    verification_token_hash = hash_token(verification_token)
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)

    user = User(
        email=payload.email.lower().strip(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        target_roles=payload.target_roles or [],
        is_verified=False,
        email_verification_token_hash=verification_token_hash,
        email_verification_expires_at=verification_expires,
    )
    user = await user_repo.create(user)

    # Ensure UserProfile and UserSettings objects are instantiated & persisted
    profile = UserProfile(
        user_id=user.id,
        target_roles=payload.target_roles or [],
    )
    settings_obj = UserSettings(
        user_id=user.id,
    )
    db.add(profile)
    db.add(settings_obj)
    await db.flush()

    # Trigger stub email send
    send_verification_email_stub(user.email, verification_token)

    # Create active device session
    device_info, ip_address = _extract_device_and_ip(request)
    session = await session_repo.create_session(
        user_id=user.id,
        device_info=device_info,
        ip_address=ip_address,
        token_hash="",
    )

    # Issue JWT tokens
    refresh_token, jti = create_refresh_token(user.id, session_id=session.id)
    await session_repo.update_token_hash(session.id, hash_token(refresh_token))

    access_token = create_access_token(user.id, session_id=session.id)
    _set_refresh_cookie(response, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_verified=user.is_verified,
        message=f"Registration successful. Please verify your email using token: {verification_token}",
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticates user credentials with rate-limiting and lockout protection."""
    user_repo = UserRepository(db)
    session_repo = UserSessionRepository(db)

    user = await user_repo.get_by_email(payload.email)
    now = datetime.now(timezone.utc)

    lockout_until = _ensure_utc(user.lockout_until) if user else None

    # Rate limiting & lockout check
    if user and lockout_until:
        if lockout_until > now:
            remaining_mins = max(1, int((lockout_until - now).total_seconds() // 60))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account locked due to multiple failed login attempts. Please try again in {remaining_mins} minutes.",
            )
        else:
            user.lockout_until = None
            user.failed_login_attempts = 0

    if (
        not user
        or not user.password_hash
        or not verify_password(payload.password, user.password_hash)
    ):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                user.lockout_until = now + timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
                await db.commit()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Account locked due to {settings.MAX_FAILED_LOGIN_ATTEMPTS} consecutive failed login attempts. Try again in {settings.LOGIN_LOCKOUT_MINUTES} minutes.",
                )
            await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Reset lockout counters on success
    user.failed_login_attempts = 0
    user.lockout_until = None
    await db.commit()

    device_info, ip_address = _extract_device_and_ip(request)
    session = await session_repo.create_session(
        user_id=user.id,
        device_info=device_info,
        ip_address=ip_address,
        token_hash="",
    )

    refresh_token, jti = create_refresh_token(user.id, session_id=session.id)
    await session_repo.update_token_hash(session.id, hash_token(refresh_token))

    access_token = create_access_token(user.id, session_id=session.id)
    _set_refresh_cookie(response, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_verified=user.is_verified,
    )


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    payload: Optional[RefreshTokenRequest] = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Issues a new access token and rotates the refresh token with REPLAY / REUSE DETECTION."""
    session_repo = UserSessionRepository(db)

    cookie_token = request.cookies.get(REFRESH_COOKIE_NAME)
    body_token = payload.refresh_token if payload else None
    raw_refresh_token = body_token or cookie_token

    if not raw_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing.",
        )

    decoded = decode_token(raw_refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        _clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    user_id_str = decoded.get("sub")
    sid_str = decoded.get("sid")

    if not user_id_str or not sid_str:
        _clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token claims.",
        )

    user_id = uuid.UUID(user_id_str)
    session_id = uuid.UUID(sid_str)

    session = await session_repo.get_by_id(session_id)
    presented_hash = hash_token(raw_refresh_token)

    # REUSE DETECTION & REPLAY ATTACK DEFENSE
    if not session or not session.is_active or session.token_hash != presented_hash:
        # Security trigger: revoke ALL sessions for this user!
        await session_repo.revoke_all_user_sessions(user_id)
        _clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security alert: Refresh token reuse detected. All active sessions have been revoked for your protection.",
        )

    # Valid token -> ROTATE REFRESH TOKEN
    new_refresh_token, new_jti = create_refresh_token(user_id, session_id=session.id)
    await session_repo.update_token_hash(session.id, hash_token(new_refresh_token))

    new_access_token = create_access_token(user_id, session_id=session.id)
    _set_refresh_cookie(response, new_refresh_token)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    current_data: tuple[User, Optional[uuid.UUID]] = Depends(get_current_user_and_session),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Revokes the current device login session and clears the refresh cookie."""
    user, session_id = current_data
    if session_id:
        session_repo = UserSessionRepository(db)
        await session_repo.revoke_session(session_id, user.id)

    _clear_refresh_cookie(response)
    return MessageResponse(message="Successfully logged out.")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Revokes ALL active login sessions across all devices for the current user."""
    session_repo = UserSessionRepository(db)
    revoked_count = await session_repo.revoke_all_user_sessions(current_user.id)
    _clear_refresh_cookie(response)
    return MessageResponse(message=f"Successfully logged out from {revoked_count} active sessions.")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Verifies a user's email address using a valid verification token."""
    user_repo = UserRepository(db)
    token_hash = hash_token(payload.token)

    user = await user_repo.get_by_email_verification_token(token_hash)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unrecognized verification token.",
        )

    now = datetime.now(timezone.utc)
    expires_at = _ensure_utc(user.email_verification_expires_at)
    if expires_at and expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please request a new verification link.",
        )

    user.is_verified = True
    user.email_verification_token_hash = None
    user.email_verification_expires_at = None
    await db.commit()

    return MessageResponse(message="Email address verified successfully.")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    payload: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Triggers resending an email verification link (stubbed)."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(payload.email)

    if user and not user.is_verified:
        token = generate_secure_token(32)
        user.email_verification_token_hash = hash_token(token)
        user.email_verification_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        await db.commit()
        send_verification_email_stub(user.email, token)

    return MessageResponse(
        message="If an unverified account exists for this email, a new verification link has been sent."
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Generates a secure password reset token and stubs email transmission."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(payload.email)

    if user:
        reset_token = generate_secure_token(32)
        user.password_reset_token_hash = hash_token(reset_token)
        user.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        await db.commit()
        send_password_reset_email_stub(user.email, reset_token)

    return MessageResponse(
        message="If an account exists with this email address, password reset instructions have been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Resets user password with Argon2 hashing and invalidates all existing login sessions."""
    user_repo = UserRepository(db)
    session_repo = UserSessionRepository(db)
    token_hash = hash_token(payload.token)

    user = await user_repo.get_by_password_reset_token(token_hash)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    now = datetime.now(timezone.utc)
    expires_at = _ensure_utc(user.password_reset_expires_at)
    if expires_at and expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired. Please request a new one.",
        )

    user.password_hash = hash_password(payload.new_password)
    user.password_reset_token_hash = None
    user.password_reset_expires_at = None
    await db.commit()

    # Revoke all active sessions on password change
    await session_repo.revoke_all_user_sessions(user.id)

    return MessageResponse(
        message="Password reset successfully. Please log in with your new password."
    )


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    payload: GoogleAuthRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticates via Google OAuth, safely linking to existing email accounts."""
    google_data = await verify_google_id_token(payload.credential)
    if not google_data or not google_data.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google OAuth credential token.",
        )

    google_sub = google_data.get("sub", "")
    email = google_data.get("email", "").lower().strip()
    name = google_data.get("name", email.split("@")[0])
    picture = google_data.get("picture")

    user_repo = UserRepository(db)
    session_repo = UserSessionRepository(db)

    # 1. Lookup by Google ID
    user = await user_repo.get_by_google_id(google_sub)

    # 2. Lookup by email & link account
    if not user:
        user = await user_repo.get_by_email(email)
        if user:
            user.google_id = google_sub
            user.is_verified = True
            if picture and not user.avatar_url:
                user.avatar_url = picture
            await db.commit()
        else:
            # Create new user via Google Sign-In
            user = User(
                email=email,
                password_hash=None,
                full_name=name,
                avatar_url=picture,
                google_id=google_sub,
                is_verified=True,
                target_roles=[],
            )
            user = await user_repo.create(user)

            profile = UserProfile(
                user_id=user.id,
                target_roles=[],
                avatar_url=picture,
            )
            settings_obj = UserSettings(
                user_id=user.id,
            )
            db.add(profile)
            db.add(settings_obj)
            await db.flush()

    device_info, ip_address = _extract_device_and_ip(request)
    session = await session_repo.create_session(
        user_id=user.id,
        device_info=f"Google Sign-In ({device_info})",
        ip_address=ip_address,
        token_hash="",
    )

    refresh_token, jti = create_refresh_token(user.id, session_id=session.id)
    await session_repo.update_token_hash(session.id, hash_token(refresh_token))

    access_token = create_access_token(user.id, session_id=session.id)
    _set_refresh_cookie(response, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_verified=user.is_verified,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Retrieves profile details for the currently authenticated user."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        target_roles=current_user.target_roles or [],
        location_preference=current_user.location_preference or "Remote / Hybrid",
        bio=current_user.bio,
        avatar_url=current_user.avatar_url,
        is_verified=current_user.is_verified,
        google_id=current_user.google_id,
        has_password=current_user.password_hash is not None,
        created_at=current_user.created_at,
    )


@router.get("/sessions", response_model=List[UserSessionResponse])
async def list_sessions(
    current_data: tuple[User, Optional[uuid.UUID]] = Depends(get_current_user_and_session),
    db: AsyncSession = Depends(get_db),
) -> List[UserSessionResponse]:
    """Retrieves active and recent device login sessions for the current user."""
    user, current_sid = current_data
    session_repo = UserSessionRepository(db)
    sessions = await session_repo.get_user_sessions(user.id)

    response_list = []
    for s in sessions:
        response_list.append(
            UserSessionResponse(
                id=s.id,
                device_info=s.device_info,
                ip_address=s.ip_address,
                last_active=s.last_active,
                created_at=s.created_at,
                is_active=s.is_active,
                is_current=(s.id == current_sid),
            )
        )
    return response_list


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: uuid.UUID,
    response: Response,
    current_data: tuple[User, Optional[uuid.UUID]] = Depends(get_current_user_and_session),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Revokes a specific device login session."""
    user, current_sid = current_data
    session_repo = UserSessionRepository(db)

    success = await session_repo.revoke_session(session_id, user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or already revoked.",
        )

    if session_id == current_sid:
        _clear_refresh_cookie(response)

    return MessageResponse(message="Session revoked successfully.")
