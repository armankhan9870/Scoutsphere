"""Pytest configuration and shared fixtures for ScoutSphere backend unit tests."""

import uuid
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

import app.models
from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import hash_password
from app.main import app
from app.models.user import User

DEMO_USER_ID = uuid.UUID("3e8ec9ae-9d67-48f7-9622-c52de2c7def9")


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    """Ensure all SQLAlchemy tables exist with latest schema and seed demo user for test assertions."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.exec_driver_sql("PRAGMA foreign_keys = OFF;")
        for table in reversed(Base.metadata.sorted_tables):
            await conn.exec_driver_sql(f"DELETE FROM {table.name};")
        await conn.exec_driver_sql("PRAGMA foreign_keys = ON;")

    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.id == DEMO_USER_ID))
        if not user:
            demo_user = User(
                id=DEMO_USER_ID,
                email="alex.rivera@scoutsphere.ai",
                password_hash=hash_password("scoutsphere123"),
                full_name="Alex Rivera",
                target_roles=["Software Engineer", "AI Systems Engineer"],
                is_active=True,
                is_verified=True,
            )
            db.add(demo_user)
            await db.commit()
    yield


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provides an async HTTP client connected to the FastAPI ASGI application."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator:
    """Provides an async database session for test execution."""
    async with AsyncSessionLocal() as session:
        yield session
