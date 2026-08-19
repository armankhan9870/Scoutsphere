"""Unified state schema for LangGraph multi-agent orchestration."""

import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict


class ScoutSphereState(TypedDict):
    """LangGraph shared execution state across all agents."""

    user_id: str
    session_id: str
    current_intent: Optional[str]

    # Resume & Profile Agent Context
    raw_resume_text: Optional[str]
    user_profile: Optional[Dict[str, Any]]
    parsed_profile: Optional[Dict[str, Any]]
    profile_embedding: Optional[List[float]]
    user_settings: Optional[Dict[str, Any]]

    # Discovery Agent Context
    search_filters: Optional[Dict[str, Any]]
    discovered_opportunities: Optional[List[Dict[str, Any]]]

    # Matching & Gap Analysis Agent Context
    target_opportunity_id: Optional[str]
    matches: Optional[List[Dict[str, Any]]]
    skill_gap_analysis: Optional[Dict[str, Any]]

    # Application & Artifact Generation Context
    tailored_resume: Optional[Dict[str, Any]]
    application_draft: Optional[Dict[str, Any]]

    # Chat & Roadmap Context
    chat_query: Optional[str]
    chat_history: Annotated[List[Dict[str, str]], operator.add]
    rag_context: Optional[Dict[str, Any]]
    roadmap_result: Optional[Dict[str, Any]]

    # System Logs & Error Tracking
    messages: Annotated[List[Dict[str, Any]], operator.add]
    errors: Annotated[List[Dict[str, Any]], operator.add]
    next_node: Optional[str]
