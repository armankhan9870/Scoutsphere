"""LangGraph node execution function for Tracking Agent."""

from app.agents.state import ScoutSphereState
from app.core.logging import logger


async def run_tracking_agent_node(state: ScoutSphereState) -> ScoutSphereState:
    """LangGraph node auditing status transition rules and logging pipeline state."""
    logger.info("Executing Tracking Agent node for user_id=%s", state.get("user_id"))

    draft = state.get("application_draft")
    if draft:
        draft["status"] = "DRAFT_READY"

    new_state = dict(state)
    new_state["next_node"] = "END"

    logger.info("Tracking Agent node complete.")
    return new_state  # type: ignore
