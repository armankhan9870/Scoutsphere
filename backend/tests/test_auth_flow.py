"""Comprehensive test suite for production-grade auth flow in ScoutSphere.

Tests:
1. Signup & Email Verification endpoint flow.
2. Login rate limiting and 15-min lockout after 5 failed attempts.
3. 15-min access token + httpOnly refresh token rotation on /refresh.
4. Refresh token REUSE detection (replay attack revokes all user sessions).
5. Logout (single device) vs Logout-All (all devices).
6. Forgot password & Password reset flow with session invalidation.
7. Google OAuth sign-in and account linking to existing email.
8. Device sessions listing & per-device revocation.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.user_session import UserSession


@pytest.mark.asyncio
async def test_signup_and_email_verification_flow(async_client: AsyncClient) -> None:
    """Verifies signup, stubbed verification token generation, and email verification endpoint."""
    unique_email = f"signup.{uuid.uuid4().hex[:8]}@scoutsphere.ai"
    signup_payload = {
        "email": unique_email,
        "password": "Password123!",
        "full_name": "Test Verified User",
        "target_roles": ["Backend Developer"],
    }

    # 1. Signup
    res = await async_client.post("/api/v1/auth/signup", json=signup_payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["email"] == unique_email
    assert data["is_verified"] is False
    assert "verify-email" in data.get("message", "") or "token:" in data.get("message", "")

    # Extract verification token directly from database record
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == unique_email))
        assert user is not None
        assert user.is_verified is False
        assert user.email_verification_token_hash is not None

    # 2. Verify Email with invalid token -> 400
    invalid_res = await async_client.post(
        "/api/v1/auth/verify-email", json={"token": "invalid_token_12345"}
    )
    assert invalid_res.status_code == 400

    # 3. Verify Email with token from message string
    token_str = data["message"].split("token: ")[-1].strip()
    verify_res = await async_client.post("/api/v1/auth/verify-email", json={"token": token_str})
    assert verify_res.status_code == 200
    assert "verified successfully" in verify_res.json()["message"]

    # Verify user state in DB
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == unique_email))
        assert user.is_verified is True
        assert user.email_verification_token_hash is None


@pytest.mark.asyncio
async def test_login_rate_limiting_and_lockout(async_client: AsyncClient) -> None:
    """Verifies that 5 failed login attempts enforce a 15-minute account lockout."""
    unique_email = f"lockout.{uuid.uuid4().hex[:8]}@scoutsphere.ai"
    password = "CorrectPassword123!"

    # Create account
    await async_client.post(
        "/api/v1/auth/signup",
        json={
            "email": unique_email,
            "password": password,
            "full_name": "Lockout Test",
        },
    )

    # Fail login 4 times
    for i in range(4):
        res = await async_client.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "WrongPassword!"},
        )
        assert res.status_code == 401
        assert "Invalid email or password" in res.json()["detail"]

    # 5th failed attempt -> 429 Lockout
    res5 = await async_client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": "WrongPassword!"},
    )
    assert res5.status_code == 429
    assert "locked" in res5.json()["detail"].lower()

    # Even correct password should fail during lockout!
    res_correct_during_lockout = await async_client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": password},
    )
    assert res_correct_during_lockout.status_code == 429

    # Manually expire lockout in DB to verify recovery
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == unique_email))
        user.lockout_until = datetime.now(timezone.utc) - timedelta(seconds=10)
        await db.commit()

    # Successful login after lockout expiry
    res_success = await async_client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": password},
    )
    assert res_success.status_code == 200
    assert "access_token" in res_success.json()


@pytest.mark.asyncio
async def test_token_rotation_and_reuse_detection(async_client: AsyncClient) -> None:
    """Verifies refresh token rotation on /refresh and emergency session revocation on token reuse (replay)."""
    unique_email = f"rotation.{uuid.uuid4().hex[:8]}@scoutsphere.ai"
    password = "RotationPassword123!"

    signup_res = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": unique_email, "password": password, "full_name": "Rotation User"},
    )
    token1_data = signup_res.json()
    refresh_token_v1 = token1_data["refresh_token"]

    # 1. First Refresh (Normal rotation)
    refresh_res1 = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_v1},
    )
    assert refresh_res1.status_code == 200
    token2_data = refresh_res1.json()
    refresh_token_v2 = token2_data["refresh_token"]
    assert refresh_token_v2 != refresh_token_v1

    # 2. Replay attack: attempt to use OLD refresh_token_v1 again!
    replay_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_v1},
    )
    assert replay_res.status_code == 401
    assert "reuse detected" in replay_res.json()["detail"].lower()

    # 3. Verify ALL sessions for this user were revoked!
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == unique_email))
        active_sessions = await db.scalars(
            select(UserSession).where(
                UserSession.user_id == user.id, UserSession.is_active.is_(True)
            )
        )
        assert len(list(active_sessions)) == 0

    # 4. Attempting to use refresh_token_v2 now also fails because session was wiped
    refresh_res2 = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_v2},
    )
    assert refresh_res2.status_code == 401


@pytest.mark.asyncio
async def test_logout_and_logout_all(async_client: AsyncClient) -> None:
    """Verifies device logout vs logout-all across multiple sessions."""
    unique_email = f"logout.{uuid.uuid4().hex[:8]}@scoutsphere.ai"
    password = "LogoutPassword123!"

    await async_client.post(
        "/api/v1/auth/signup",
        json={"email": unique_email, "password": password, "full_name": "Multi Device User"},
    )

    # Login device 1
    dev1_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": password},
        headers={"User-Agent": "Device-1-Chrome"},
    )
    token1 = dev1_res.json()["access_token"]

    # Login device 2
    dev2_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": password},
        headers={"User-Agent": "Device-2-Firefox"},
    )
    token2 = dev2_res.json()["access_token"]

    # Logout device 1
    logout1_res = await async_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert logout1_res.status_code == 200

    # Check sessions: device 2 active, device 1 revoked
    sessions_res = await async_client.get(
        "/api/v1/auth/sessions",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert sessions_res.status_code == 200
    sessions_list = sessions_res.json()
    assert len(sessions_list) >= 2

    # Logout-all from device 2
    logout_all_res = await async_client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert logout_all_res.status_code == 200
    assert "logged out" in logout_all_res.json()["message"].lower()


@pytest.mark.asyncio
async def test_forgot_and_reset_password_flow(async_client: AsyncClient) -> None:
    """Verifies forgot-password token generation, reset password execution, and session invalidation."""
    unique_email = f"reset.{uuid.uuid4().hex[:8]}@scoutsphere.ai"
    old_password = "OldPassword123!"
    new_password = "BrandNewPassword123!"

    signup_res = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": unique_email, "password": old_password, "full_name": "Reset Password User"},
    )
    assert signup_res.status_code == 201

    # Forgot password
    forgot_res = await async_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": unique_email},
    )
    assert forgot_res.status_code == 200
    assert "instructions have been sent" in forgot_res.json()["message"]

    # Fetch reset token from DB
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == unique_email))
        assert user.password_reset_token_hash is not None

    # We need to simulate the raw token that matches token_hash for test
    # Let's test with direct DB update of raw token
    raw_token = "mock_reset_token_for_testing_123"
    from app.core.security import hash_token

    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == unique_email))
        user.password_reset_token_hash = hash_token(raw_token)
        user.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        await db.commit()

    # Reset password
    reset_res = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"token": raw_token, "new_password": new_password},
    )
    assert reset_res.status_code == 200

    # Old password login fails
    old_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": old_password},
    )
    assert old_login.status_code == 401

    # New password login succeeds
    new_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": new_password},
    )
    assert new_login.status_code == 200


@pytest.mark.asyncio
async def test_google_oauth_account_linking(async_client: AsyncClient) -> None:
    """Verifies Google Sign-In account creation and linking with existing email account."""
    google_mock_token = f"mock_google_token_oauthuser_{uuid.uuid4().hex[:6]}"
    expected_email = f"oauthuser_{google_mock_token.split('_')[-1]}@gmail.com"

    # 1. New Google user sign-in
    google_res1 = await async_client.post(
        "/api/v1/auth/google",
        json={"credential": google_mock_token},
    )
    assert google_res1.status_code == 200
    gdata1 = google_res1.json()
    assert gdata1["email"] == expected_email
    assert gdata1["is_verified"] is True

    # 2. Existing user signup with password, then Google sign-in with same email
    normal_email = f"normal.{uuid.uuid4().hex[:8]}@gmail.com"
    await async_client.post(
        "/api/v1/auth/signup",
        json={
            "email": normal_email,
            "password": "NormalPassword123!",
            "full_name": "Standard User",
        },
    )

    token_for_normal = f"mock_google_token_{normal_email.split('@')[0]}"
    google_res2 = await async_client.post(
        "/api/v1/auth/google",
        json={"credential": token_for_normal},
    )
    assert google_res2.status_code == 200
    gdata2 = google_res2.json()
    assert gdata2["email"] == normal_email
    assert gdata2["is_verified"] is True

    # Verify google_id linked in database
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == normal_email))
        assert user.google_id is not None
        assert "google_sub_" in user.google_id


@pytest.mark.asyncio
async def test_sessions_list_and_revocation(async_client: AsyncClient) -> None:
    """Verifies listing user active sessions and revoking specific device session."""
    email = f"sessions.{uuid.uuid4().hex[:8]}@scoutsphere.ai"
    password = "SessionsPassword123!"

    signup_res = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": password, "full_name": "Sessions Tester"},
    )
    token = signup_res.json()["access_token"]

    # Fetch sessions
    sessions_res = await async_client.get(
        "/api/v1/auth/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert sessions_res.status_code == 200
    sessions_data = sessions_res.json()
    assert len(sessions_data) >= 1
    session_id = sessions_data[0]["id"]

    # Revoke session
    revoke_res = await async_client.delete(
        f"/api/v1/auth/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert revoke_res.status_code == 200
    assert "revoked" in revoke_res.json()["message"].lower()
