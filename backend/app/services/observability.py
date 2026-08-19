"""Observability tracer service logging agent execution runs into PostgreSQL."""

import uuid
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.agent_run import AgentRun


async def log_agent_run(
    db: AsyncSession,
    user_id: uuid.UUID,
    session_id: str,
    agent_name: str,
    input_json: Dict[str, Any],
    output_json: Dict[str, Any],
    latency_ms: int,
    status: str = "SUCCESS",
) -> AgentRun:
    """Logs an agent execution event for debugging and performance observability."""
    run_entry = AgentRun(
        user_id=user_id,
        session_id=session_id,
        agent_name=agent_name,
        input_json=input_json,
        output_json=output_json,
        latency_ms=latency_ms,
        status=status,
    )
    db.add(run_entry)
    await db.commit()
    logger.info(
        "Logged AgentRun trace for '%s' (latency: %d ms, status: %s)",
        agent_name,
        latency_ms,
        status,
    )
    return run_entry
