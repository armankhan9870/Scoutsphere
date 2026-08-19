"""LangGraph node execution function for Resume Tailoring Agent with FactChecker pass."""

import json

from app.agents.schemas.resume_tailoring_schema import TailoredResumeOutput
from app.agents.state import ScoutSphereState
from app.core.llm import LLMClient
from app.core.logging import logger
from app.services.tailoring.ats_scorer import estimate_ats_score
from app.services.tailoring.fact_checker import FactCheckerService


def _normalize_skills_list(skills_raw) -> list:
    """Helper formatting string skill names into TailoredSkill dict instances."""
    formatted = []
    for s in skills_raw:
        if isinstance(s, dict) and "name" in s:
            formatted.append(s)
        elif isinstance(s, str):
            formatted.append({"name": s, "category": "Core Skills"})
    return formatted


async def run_resume_tailoring_node(state: ScoutSphereState) -> ScoutSphereState:
    """LangGraph node reordering skills, rewriting bullets, and executing fact-checker pass."""
    user_profile = state.get("parsed_profile") or {}
    raw_opps = state.get("discovered_opportunities") or []
    target_opp_id = state.get("target_opportunity_id")

    target_opp = raw_opps[0] if raw_opps else {}
    if target_opp_id and raw_opps:
        for o in raw_opps:
            if str(o.get("id")) == str(target_opp_id):
                target_opp = o
                break

    target_role = target_opp.get("title", "Software Engineer")
    req_skills = target_opp.get("required_skills_json") or []

    logger.info("Executing Resume Tailoring Agent for role '%s'", target_role)

    prompt = (
        f"BASE CANDIDATE PROFILE:\n{json.dumps(user_profile)}\n\n"
        f"TARGET ROLE: {target_role}\n"
        f"REQUIRED ATS KEYWORDS: {req_skills}"
    )
    user_settings = state.get("user_settings") or {}
    preferred_provider = user_settings.get("preferred_llm_provider", "gemini")
    cover_letter_tone = user_settings.get("cover_letter_tone", "conversational")

    system_prompt = (
        f"You are an ATS Resume Optimization Agent. Rewrite bullet points using active verbs and required keywords. "
        f"Tone guideline for generated text: {cover_letter_tone}. "
        f"HARD CONSTRAINT: Do NOT fabricate experience or skills not present in base profile. Output raw JSON."
    )

    llm = LLMClient(preferred_provider=preferred_provider)

    try:
        raw_res = await llm.generate(
            prompt=prompt, system_prompt=system_prompt, response_format="json"
        )
        cleaned_str = raw_res.strip()
        if cleaned_str.startswith("```json"):
            cleaned_str = cleaned_str.split("```json")[1].split("```")[0].strip()
        elif cleaned_str.startswith("```"):
            cleaned_str = cleaned_str.split("```")[1].split("```")[0].strip()

        tailored_data = json.loads(cleaned_str)
    except Exception as e:
        logger.warning(
            "LLM tailoring generation error: %s. Using default baseline tailoring.", str(e)
        )
        tailored_data = {
            "target_role": target_role,
            "summary": f"Targeted Software Engineer specializing in {', '.join(req_skills[:3]) if req_skills else 'software architecture'}.",
            "skills": _normalize_skills_list(
                user_profile.get("skills", ["Python", "FastAPI", "PostgreSQL"])
            ),
            "experience": user_profile.get("experience", []),
            "projects": user_profile.get("projects", []),
        }

    # Ensure required fields exist in tailored_data
    if "target_role" not in tailored_data:
        tailored_data["target_role"] = target_role
    if "summary" not in tailored_data:
        tailored_data["summary"] = f"Targeted professional aligned with {target_role} requirements."

    # Format skills to match TailoredSkill schema
    raw_skills = tailored_data.get("skills", [])
    tailored_data["skills"] = _normalize_skills_list(
        raw_skills if raw_skills else user_profile.get("skills", [])
    )

    # Execute Fact-Checker Diff Verification
    fact_checker = FactCheckerService()
    is_valid, violations = fact_checker.verify_tailored_resume(user_profile, tailored_data)

    if not is_valid:
        logger.warning(
            "Fact-checker rejected hallucinated claims: %s. Reverting skills to base profile.",
            violations,
        )
        tailored_data["skills"] = _normalize_skills_list(
            user_profile.get("skills", ["Python", "FastAPI", "PostgreSQL"])
        )

    validated_output = TailoredResumeOutput(**tailored_data)

    # Estimate ATS score breakdown
    ats_score = estimate_ats_score(validated_output.model_dump(), req_skills)

    new_state = dict(state)
    new_state["tailored_resume"] = {
        "content": validated_output.model_dump(),
        "ats_score_breakdown": ats_score,
        "is_fact_check_passed": is_valid,
    }
    new_state["next_node"] = "application_assistant_agent"

    logger.info("Resume Tailoring Agent complete. ATS Score: %s", ats_score["overall_ats_score"])
    return new_state  # type: ignore
