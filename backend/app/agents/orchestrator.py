"""Master LangGraph Orchestrator connecting all specialized agent nodes into a unified stateful workflow."""

import time

from langgraph.graph import END, StateGraph

from app.agents.nodes.application_assistant_node import run_application_assistant_node
from app.agents.nodes.chat_node import run_chat_agent_node
from app.agents.nodes.discovery_node import run_discovery_agent_node
from app.agents.nodes.matching_node import run_matching_agent_node
from app.agents.nodes.resume_analysis_node import run_resume_analysis_node
from app.agents.nodes.resume_tailoring_node import run_resume_tailoring_node
from app.agents.nodes.skill_gap_node import run_skill_gap_agent_node
from app.agents.nodes.tracking_node import run_tracking_agent_node
from app.agents.state import ScoutSphereState
from app.core.logging import logger


def route_intent_branches(state: ScoutSphereState) -> str:
    """Conditional router directing execution along on-demand pipeline branches."""
    intent = state.get("current_intent") or "onboarding"
    logger.info("Orchestrator routing intent '%s'", intent)

    if intent == "tailor_resume":
        return "resume_tailoring_agent"
    elif intent == "draft_application":
        return "application_assistant_agent"
    elif intent == "chat":
        return "chat_agent"
    else:
        return "END"


def build_scoutsphere_orchestrator():
    """Constructs stateful LangGraph execution graph connecting all 9 agents."""
    builder = StateGraph(ScoutSphereState)

    # 1. Add Agent Nodes
    builder.add_node("discovery_agent", run_discovery_agent_node)
    builder.add_node("resume_analysis_agent", run_resume_analysis_node)
    builder.add_node("matching_agent", run_matching_agent_node)
    builder.add_node("skill_gap_agent", run_skill_gap_agent_node)
    builder.add_node("resume_tailoring_agent", run_resume_tailoring_node)
    builder.add_node("application_assistant_agent", run_application_assistant_node)
    builder.add_node("tracking_agent", run_tracking_agent_node)
    builder.add_node("chat_agent", run_chat_agent_node)

    # 2. Wire Onboarding Pipeline Edges
    builder.set_entry_point("discovery_agent")
    builder.add_edge("discovery_agent", "resume_analysis_agent")
    builder.add_edge("resume_analysis_agent", "matching_agent")
    builder.add_edge("matching_agent", "skill_gap_agent")

    # 3. Conditional Router Branching
    builder.add_conditional_edges(
        "skill_gap_agent",
        route_intent_branches,
        {
            "resume_tailoring_agent": "resume_tailoring_agent",
            "application_assistant_agent": "application_assistant_agent",
            "chat_agent": "chat_agent",
            "END": END,
        },
    )

    builder.add_edge("resume_tailoring_agent", END)
    builder.add_edge("application_assistant_agent", "tracking_agent")
    builder.add_edge("tracking_agent", END)
    builder.add_edge("chat_agent", END)

    return builder.compile()


# Compiled Singleton Graph Engine
orchestrator_graph = build_scoutsphere_orchestrator()


async def run_full_onboarding_pipeline(state: ScoutSphereState) -> ScoutSphereState:
    """Executes the complete onboarding pipeline (Discovery -> Analysis -> Matching -> Skill Gap)."""
    start_time = time.time()
    logger.info(
        "Starting Master Orchestrator Onboarding Pipeline run for user_id=%s", state.get("user_id")
    )

    # Execute compiled graph
    final_state = await orchestrator_graph.ainvoke(state)

    elapsed_ms = int((time.time() - start_time) * 1000)
    logger.info("Master Orchestrator pipeline execution complete in %d ms.", elapsed_ms)
    return final_state
