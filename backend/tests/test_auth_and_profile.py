"""Integration tests for user registration, authentication, profile updates, and resume upload."""

import io
import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_auth_profile_and_resume_flow(async_client: AsyncClient) -> None:
    """Tests complete flow: Signup -> Login -> Update Profile -> Upload Resume PDF -> Fetch Active Resume."""

    test_email = f"integration.{uuid.uuid4().hex[:8]}@scoutsphere.ai"
    # 1. Signup
    signup_payload = {
        "email": test_email,
        "password": "SecurePassword123!",
        "full_name": "Integration Tester",
        "target_roles": ["Backend Engineer"],
    }
    signup_res = await async_client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_res.status_code == 201
    token_data = signup_res.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Fetch /auth/me
    me_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    user_info = me_res.json()
    assert user_info["email"] == test_email

    # 3. Update Profile
    profile_update = {
        "target_roles": ["Backend Engineer", "AI Developer"],
        "location_preference": "Remote Only",
    }
    update_res = await async_client.put(
        "/api/v1/users/profile", json=profile_update, headers=headers
    )
    assert update_res.status_code == 200
    updated_info = update_res.json()
    assert updated_info["location_preference"] == "Remote Only"
    assert "AI Developer" in updated_info["target_roles"]

    # 4. Upload Resume File
    sample_pdf_bytes = b"%PDF-1.4 Mock PDF Resume Content for Testing ScoutSphere"
    files = {"file": ("test_resume.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")}
    upload_res = await async_client.post("/api/v1/resumes/upload", files=files, headers=headers)
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    assert upload_data["is_active"] is True

    # 5. Fetch Active Resume
    active_res = await async_client.get("/api/v1/resumes/active", headers=headers)
    assert active_res.status_code == 200
    active_resume = active_res.json()
    assert active_resume["is_active"] is True
    assert active_resume["id"] == upload_data["id"]
