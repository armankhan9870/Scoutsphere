"""LangGraph node execution function for Matching & Ranking Agent."""

import uuid

from app.agents.state import ScoutSphereState
from app.core.logging import logger
from app.services.matching.hybrid_scorer import calculate_hybrid_score
from app.services.matching.reranker import LLMRerankerService


async def run_matching_agent_node(state: ScoutSphereState) -> ScoutSphereState:
    """LangGraph node executing vector scoring + heuristic weighting + top-20 LLM re-ranking."""
    logger.info("Executing Matching Agent node for user_id=%s", state.get("user_id"))

    user_profile = state.get("parsed_profile") or {}
    raw_opps = state.get("discovered_opportunities") or []
    user_settings = state.get("user_settings") or {}

    # Extract user matching threshold preferences
    min_score_percent = user_settings.get("min_match_score", 70)
    min_score_threshold = float(min_score_percent) / 100.0 if min_score_percent else 0.70
    auto_hide = user_settings.get("auto_hide_low_score", False)

    # 1. Baseline heuristic scoring
    candidate_scores = []
    for opp in raw_opps:

        class DummyOpp:
            def __init__(self, d):
                self.id = d.get("id") or str(uuid.uuid4())
                self.title = d.get("title", "")
                self.company_name = d.get("company_name", "")
                self.opportunity_type = d.get("opportunity_type", "JOB")
                self.required_skills_json = d.get("required_skills_json", [])
                self.location = d.get("location", "")
                self.is_remote = d.get("is_remote", True)

        opp_obj = DummyOpp(opp)
        score_dict = calculate_hybrid_score(user_profile, opp_obj, cosine_distance=0.4)
        candidate_scores.append(score_dict)

    # Sort initial candidates by heuristic score
    candidate_scores.sort(key=lambda x: x["fit_score"], reverse=True)

    # 2. LLM top-20 re-ranking pass
    preferred_provider = user_settings.get("preferred_llm_provider", "gemini")
    reranker = LLMRerankerService(preferred_provider=preferred_provider)
    final_matches = await reranker.rerank_top_candidates(user_profile, candidate_scores[:20])

    # Filter out low-score matches if user auto-hide preference is enabled
    if auto_hide:
        final_matches = [m for m in final_matches if m.get("fit_score", 0.0) >= min_score_threshold]

    new_state = dict(state)
    new_state["matches"] = final_matches
    new_state["next_node"] = "skill_gap_agent"

    logger.info("Matching Agent node successfully generated %d ranked matches.", len(final_matches))
    return new_state  # type: ignore
