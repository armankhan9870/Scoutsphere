"""LangGraph node execution function for Resume & Profile Analysis Agent."""

import json
import os

from app.agents.schemas.resume_analysis_schema import ResumeAnalysisOutput
from app.agents.state import ScoutSphereState
from app.core.embeddings import generate_embedding
from app.core.llm import LLMClient
from app.core.logging import logger
from app.services.skill_normalizer import normalize_extracted_skills

PROMPT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../prompts/resume_analysis.md")
)


def load_system_prompt() -> str:
    """Reads externalized prompt file from /backend/app/agents/prompts/resume_analysis.md."""
    if os.path.exists(PROMPT_PATH):
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "Extract structured resume JSON with skills, experience, education, and projects."


async def run_resume_analysis_node(state: ScoutSphereState) -> ScoutSphereState:
    """LangGraph node executing LLM profile extraction, skill normalization, and vector embedding."""
    raw_text = state.get("raw_resume_text", "")
    profile = state.get("user_profile") or {}
    logger.info("Executing Resume Analysis Agent node for user_id=%s", state.get("user_id"))

    system_prompt = load_system_prompt()
    user_prompt = f"RAW RESUME TEXT:\n{raw_text}\n\nUSER CAREER PROFILE:\n{json.dumps(profile)}"

    user_settings = state.get("user_settings") or {}
    preferred_provider = user_settings.get("preferred_llm_provider", "gemini")
    llm = LLMClient(preferred_provider=preferred_provider)
    llm_output_str = await llm.generate(
        prompt=user_prompt, system_prompt=system_prompt, response_format="json"
    )

    # Parse JSON output into Pydantic schema
    try:
        cleaned_json = llm_output_str.strip()
        if cleaned_json.startswith("```json"):
            cleaned_json = cleaned_json.split("```json")[1].split("```")[0].strip()
        elif cleaned_json.startswith("```"):
            cleaned_json = cleaned_json.split("```")[1].split("```")[0].strip()

        parsed_data = json.loads(cleaned_json)
    except Exception as e:
        logger.warning("JSON parsing error on LLM output: %s. Using default structure.", str(e))
        parsed_data = json.loads(llm._generate_stub_response(raw_text))

    # Apply deterministic canonical skill normalization (~200 skills taxonomy)
    if "skills" in parsed_data:
        parsed_data["skills"] = normalize_extracted_skills(parsed_data["skills"])

    # Validate output schema
    validated_output = ResumeAnalysisOutput(**parsed_data)

    # Generate pgvector 384-dimensional embedding from strengths summary & skills
    embedding_text = f"{validated_output.strengths_summary} Skills: " + ", ".join(
        [s.name for s in validated_output.skills]
    )
    vector_embedding = generate_embedding(embedding_text, dimension=384)

    # Update state
    new_state = dict(state)
    new_state["parsed_profile"] = validated_output.model_dump()
    new_state["profile_embedding"] = vector_embedding
    new_state["next_node"] = "matching_agent"

    logger.info(
        "Resume Analysis Agent node successfully extracted %d skills and generated embedding.",
        len(validated_output.skills),
    )
    return new_state  # type: ignore
