"""Unit & integration tests for Phase 17 Settings API endpoints and user settings aliases."""

import pytest
from httpx import AsyncClient

DEMO_USER_ID = "3e8ec9ae-9d67-48f7-9622-c52de2c7def9"


@pytest.mark.asyncio
async def test_get_and_update_settings(async_client: AsyncClient) -> None:
    """Test retrieving user settings and updating career/AI preferences."""
    # 1. GET /settings
    res = await async_client.get("/api/v1/settings")
    assert res.status_code == 200
    data = res.json()
    assert "min_match_score" in data
    assert "preferred_llm_provider" in data

    # 2. PUT /settings
    update_payload = {
        "min_match_score": 85,
        "preferred_llm_provider": "groq",
        "agent_tone": "exploratory",
        "auto_background_agents": True,
        "work_style": "remote",
    }
    put_res = await async_client.put("/api/v1/settings", json=update_payload)
    assert put_res.status_code == 200
    updated_data = put_res.json()
    assert updated_data["min_match_score"] == 85
    assert updated_data["preferred_llm_provider"] == "groq"
    assert updated_data["auto_background_agents"] is True


@pytest.mark.asyncio
async def test_user_id_settings_and_patch(async_client: AsyncClient) -> None:
    """Test GET /users/{id}/settings and PATCH /users/{id}/settings."""
    # 1. GET /users/{id}/settings
    get_res = await async_client.get(f"/api/v1/users/{DEMO_USER_ID}/settings")
    assert get_res.status_code == 200
    assert "preferred_llm_provider" in get_res.json()

    # 2. PATCH /users/{id}/settings
    patch_res = await async_client.patch(
        f"/api/v1/users/{DEMO_USER_ID}/settings",
        json={"cover_letter_tone": "formal", "theme": "dark"},
    )
    assert patch_res.status_code == 200
    patched_data = patch_res.json()
    assert patched_data["cover_letter_tone"] == "formal"
    assert patched_data["theme"] == "dark"


@pytest.mark.asyncio
async def test_user_export_and_soft_delete(async_client: AsyncClient) -> None:
    """Test background task export and soft-delete endpoints."""
    # 1. POST /users/{id}/settings/export
    exp_res = await async_client.post(f"/api/v1/users/{DEMO_USER_ID}/settings/export")
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert "download_url" in exp_data
    assert exp_data["status"] == "PROCESSING"

    # 2. POST /users/{id}/account/delete (soft-delete)
    del_res = await async_client.post(f"/api/v1/users/{DEMO_USER_ID}/account/delete")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["is_active"] is False
    assert "scheduled_purge_at" in del_data


@pytest.mark.asyncio
async def test_list_and_revoke_sessions(async_client: AsyncClient) -> None:
    """Test active security sessions listing and revocation."""
    # 1. GET /users/{id}/sessions
    res = await async_client.get(f"/api/v1/users/{DEMO_USER_ID}/sessions")
    assert res.status_code == 200
    sessions = res.json()
    assert isinstance(sessions, list)
    assert len(sessions) > 0

    session_id = sessions[0]["id"]

    # 2. DELETE /users/{id}/sessions/{session_id}
    del_res = await async_client.delete(f"/api/v1/users/{DEMO_USER_ID}/sessions/{session_id}")
    assert del_res.status_code == 200
    assert del_res.json()["message"] == "Session revoked successfully."


@pytest.mark.asyncio
async def test_privacy_data_export(async_client: AsyncClient) -> None:
    """Test downloading full user JSON data export."""
    res = await async_client.get("/api/v1/settings/privacy/export")
    assert res.status_code == 200
    export_data = res.json()
    assert "user_profile" in export_data
    assert "settings" in export_data
    assert "resumes" in export_data
    assert "matches" in export_data
    assert "applications" in export_data
