"""Smoke test for FastAPI /health check endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient) -> None:
    """Verifies that GET /api/v1/health returns HTTP 200 OK with valid status schema."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ScoutSphere"
    assert "version" in data
    assert "database" in data
