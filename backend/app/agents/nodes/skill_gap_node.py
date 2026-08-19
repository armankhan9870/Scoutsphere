"""LangGraph node execution function for Skill Gap Agent."""

import json

from app.agents.schemas.skill_gap_schema import RecommendedResource, SkillGapOutput
from app.agents.state import ScoutSphereState
from app.core.llm import LLMClient
from app.core.logging import logger
from app.services.skill_gap.delta_calculator import compute_skill_delta
from app.services.skill_gap.url_validator import validate_and_flag_resources

FALLBACK_RESOURCES = {
    "kubernetes": {
        "title": "Kubernetes Official Basics & Concepts Guide",
        "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        "type": "Documentation",
        "time": "6 hours",
    },
    "pytorch": {
        "title": "Deep Learning with PyTorch: 60 Minute Blitz",
        "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html",
        "type": "Tutorial",
        "time": "3 hours",
    },
    "docker": {
        "title": "Docker Official Get Started Guide",
        "url": "https://docs.docker.com/get-started/",
        "type": "Documentation",
        "time": "4 hours",
    },
    "react": {
        "title": "React Official Interactive Documentation",
        "url": "https://react.dev/learn",
        "type": "Interactive",
        "time": "5 hours",
    },
}


async def run_skill_gap_agent_node(state: ScoutSphereState) -> ScoutSphereState:
    """LangGraph node calculating skill deltas, querying LLM for resources, and validating URLs."""
    user_profile = state.get("parsed_profile") or {}
    raw_opps = state.get("discovered_opportunities") or []
    target_opp_id = state.get("target_opportunity_id")

    user_skills = user_profile.get("skills") or []

    # Find target opportunity skills
    required_skills = []
    if raw_opps:
        target = raw_opps[0]
        if target_opp_id:
            for o in raw_opps:
                if str(o.get("id")) == str(target_opp_id):
                    target = o
                    break
        required_skills = target.get("required_skills_json") or []

    missing, weak, priority = compute_skill_delta(user_skills, required_skills)

    # If candidate meets 100% of skills, handle gracefully
    if not priority:
        logger.info("Candidate meets 100% of required skills. Zero skill gap detected.")
        output = SkillGapOutput(
            missing_skills=[],
            weak_skills=[],
            priority_order=[],
            recommended_resources=[],
            match_impact_score=0.0,
        )
        new_state = dict(state)
        new_state["skill_gap_analysis"] = output.model_dump()
        new_state["next_node"] = "resume_tailoring_agent"
        return new_state  # type: ignore

    # Query LLM for learning resource recommendations
    user_settings = state.get("user_settings") or {}
    preferred_provider = user_settings.get("preferred_llm_provider", "gemini")
    llm = LLMClient(preferred_provider=preferred_provider)
    prompt = f"MISSING SKILLS TO LEARN: {missing}\nWEAK SKILLS TO REINFORCE: {weak}"
    system_prompt = (
        "You are a Career Advisor. Recommend 1-2 real official learning resources for each skill. "
        "Prefer official documentation URLs. Output raw JSON."
    )

    try:
        raw_res = await llm.generate(
            prompt=prompt, system_prompt=system_prompt, response_format="json"
        )
        cleaned_str = raw_res.strip()
        if cleaned_str.startswith("```json"):
            cleaned_str = cleaned_str.split("```json")[1].split("```")[0].strip()
        elif cleaned_str.startswith("```"):
            cleaned_str = cleaned_str.split("```")[1].split("```")[0].strip()

        data = json.loads(cleaned_str)
        raw_resources = data.get("recommended_resources", [])
    except Exception as e:
        logger.warning(
            "LLM skill gap resource generation error: %s. Using default verified resources.", str(e)
        )
        raw_resources = []
        for sk in priority:
            sk_lower = sk.lower()
            if sk_lower in FALLBACK_RESOURCES:
                info = FALLBACK_RESOURCES[sk_lower]
                raw_resources.append(
                    {
                        "skill": sk,
                        "resource_title": info["title"],
                        "resource_url": info["url"],
                        "resource_type": info["type"],
                        "estimated_time": info["time"],
                    }
                )
            else:
                raw_resources.append(
                    {
                        "skill": sk,
                        "resource_title": f"Official {sk} Documentation & Tutorial",
                        "resource_url": "https://docs.python.org/3/",
                        "resource_type": "Documentation",
                        "estimated_time": "5 hours",
                    }
                )

    # Apply URL validation and flagging
    validated_resources = validate_and_flag_resources(raw_resources)

    # Estimate potential match score boost
    impact_boost = round(len(priority) * 8.5, 1)

    output = SkillGapOutput(
        missing_skills=missing,
        weak_skills=weak,
        priority_order=priority,
        recommended_resources=[RecommendedResource(**r) for r in validated_resources],
        match_impact_score=impact_boost,
    )

    new_state = dict(state)
    new_state["skill_gap_analysis"] = output.model_dump()
    new_state["next_node"] = "resume_tailoring_agent"

    logger.info("Skill Gap Agent node complete. Detected %d gap skills.", len(priority))
    return new_state  # type: ignore
