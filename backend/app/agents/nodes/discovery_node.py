"""LangGraph node execution function for Discovery Agent."""

from app.agents.state import ScoutSphereState
from app.core.logging import logger
from app.services.discovery.mock_sources import (
    MockHackathonSource,
    MockInternshipSource,
    MockJobBoardSource,
)
from app.services.discovery.normalizer import normalize_raw_opportunity


async def run_discovery_agent_node(state: ScoutSphereState) -> ScoutSphereState:
    """LangGraph node executing multi-source opportunity discovery and normalization."""
    logger.info("Executing Discovery Agent node for user_id=%s", state.get("user_id"))

    sources = [
        MockJobBoardSource(),
        MockHackathonSource(),
        MockInternshipSource(),
    ]

    all_raw = []
    for source in sources:
        raw_items = await source.fetch()
        all_raw.extend(raw_items)

    normalized_dicts = []
    for raw in all_raw:
        opp_model = normalize_raw_opportunity(raw)
        normalized_dicts.append(
            {
                "title": opp_model.title,
                "company_name": opp_model.company_name,
                "opportunity_type": opp_model.opportunity_type,
                "description": opp_model.description,
                "required_skills_json": opp_model.required_skills_json,
                "location": opp_model.location,
                "is_remote": opp_model.is_remote,
                "source_url": opp_model.source_url,
            }
        )

    new_state = dict(state)
    new_state["discovered_opportunities"] = normalized_dicts
    new_state["next_node"] = "matching_agent"

    logger.info(
        "Discovery Agent node successfully gathered %d opportunities.", len(normalized_dicts)
    )
    return new_state  # type: ignore
