"""LangGraph node execution function for Application Assistant Agent."""

import json

from app.agents.schemas.application_assistant_schema import (
    ApplicationDraftPackage,
    ApplicationFormFields,
)
from app.agents.state import ScoutSphereState
from app.core.llm import LLMClient
from app.core.logging import logger


async def run_application_assistant_node(state: ScoutSphereState) -> ScoutSphereState:
    """LangGraph node drafting customized cover letter and pre-filling job portal fields."""
    user_profile = state.get("parsed_profile") or {}
    raw_opps = state.get("discovered_opportunities") or []
    target_opp_id = state.get("target_opportunity_id")

    target_opp = raw_opps[0] if raw_opps else {}
    if target_opp_id and raw_opps:
        for o in raw_opps:
            if str(o.get("id")) == str(target_opp_id):
                target_opp = o
                break

    role_title = target_opp.get("title", "Software Engineer")
    company_name = target_opp.get("company_name", "Tech Corp")
    opp_desc = target_opp.get("description", "")

    user_name = user_profile.get("full_name") or "Alex Rivera"
    user_email = user_profile.get("email") or "student@scoutsphere.ai"

    logger.info(
        "Executing Application Assistant Agent for role '%s' at '%s'", role_title, company_name
    )

    prompt = (
        f"CANDIDATE NAME: {user_name}\n"
        f"CANDIDATE EMAIL: {user_email}\n"
        f"CANDIDATE PROFILE: {json.dumps(user_profile)}\n\n"
        f"TARGET ROLE: {role_title}\n"
        f"COMPANY NAME: {company_name}\n"
        f"JOB DESCRIPTION: {opp_desc}\n"
    )
    system_prompt = "You are an Application Assistant. Draft a compelling 3-paragraph cover letter and pre-fill form fields. Output raw JSON."

    user_settings = state.get("user_settings") or {}
    preferred_provider = user_settings.get("preferred_llm_provider", "gemini")
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

        draft_data = json.loads(cleaned_str)
        package = ApplicationDraftPackage(**draft_data)
    except Exception as e:
        logger.warning(
            "LLM application draft generation error: %s. Using default baseline draft.", str(e)
        )
        default_cover = (
            f"Dear Hiring Team at {company_name},\n\n"
            f"I am writing to express my strong enthusiasm for the {role_title} position. "
            f"With my background in Python backend development, FastAPI microservices, and database systems, "
            f"I am confident in my ability to contribute effectively to your engineering goals.\n\n"
            f"My hands-on experience includes developing RESTful services and containerized environments. "
            f"I look forward to discussing how my technical background aligns with {company_name}.\n\n"
            f"Sincerely,\n{user_name}"
        )
        default_fields = ApplicationFormFields(
            full_name=user_name,
            email=user_email,
            why_this_role=f"Deep interest in building scalable systems as a {role_title}.",
            why_this_company=f"Strong alignment with {company_name}'s mission and engineering stack.",
        )
        package = ApplicationDraftPackage(cover_letter=default_cover, form_fields=default_fields)

    new_state = dict(state)
    new_state["application_draft"] = package.model_dump()
    new_state["next_node"] = "tracking_agent"

    logger.info(
        "Application Assistant Agent complete. Cover letter and portal form fields drafted."
    )
    return new_state  # type: ignore
