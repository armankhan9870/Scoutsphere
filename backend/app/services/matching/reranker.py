"""LLM re-ranking service bounded to top 20 candidate opportunities per batch."""

import json
from typing import Any, Dict, List, Optional

from app.core.llm import LLMClient
from app.core.logging import logger


class LLMRerankerService:
    """Re-ranks top candidate matches and synthesizes natural-language fit rationale."""

    def __init__(
        self, llm_client: Optional[LLMClient] = None, preferred_provider: Optional[str] = None
    ):
        self.llm = llm_client or LLMClient(preferred_provider=preferred_provider)

    async def rerank_top_candidates(
        self,
        user_profile: Dict[str, Any],
        top_candidates: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Executes single batch LLM call on top ~20 candidate opportunities.

        Refines score (0-100) and generates 2-sentence rationale per candidate.
        """
        if not top_candidates:
            return []

        # Bound to top 20 candidates max
        bounded_candidates = top_candidates[:20]

        prompt = f"""
CANDIDATE USER PROFILE:
{json.dumps(user_profile)}

TOP CANDIDATE OPPORTUNITIES TO EVALUATE (Total {len(bounded_candidates)}):
{json.dumps(bounded_candidates)}

INSTRUCTIONS:
Evaluate each candidate opportunity against the student profile.
Return a JSON array of objects with fields:
- "opportunity_id": string ID
- "final_score": float between 0.0 and 100.0
- "rationale": short 2-sentence natural language rationale explaining why this opportunity is a good fit.
"""

        system_prompt = (
            "You are an expert Career Matching AI. Output ONLY a valid JSON array of match evaluations. "
            "Do not include markdown code block formatting."
        )

        try:
            llm_output_str = await self.llm.generate(
                prompt=prompt, system_prompt=system_prompt, response_format="json"
            )

            cleaned_str = llm_output_str.strip()
            if cleaned_str.startswith("```json"):
                cleaned_str = cleaned_str.split("```json")[1].split("```")[0].strip()
            elif cleaned_str.startswith("```"):
                cleaned_str = cleaned_str.split("```")[1].split("```")[0].strip()

            eval_list = json.loads(cleaned_str)
            eval_map = {
                item["opportunity_id"]: item for item in eval_list if "opportunity_id" in item
            }
        except Exception as e:
            logger.warning(
                "LLM Re-ranking batch parse error: %s. Using baseline heuristics.", str(e)
            )
            eval_map = {}

        results = []
        for cand in bounded_candidates:
            opp_id = cand["opportunity_id"]
            eval_item = eval_map.get(opp_id, {})

            final_score = eval_item.get("final_score", cand["fit_score"])
            # Ensure score remains in valid range
            final_score = round(min(100.0, max(0.0, float(final_score))), 1)

            matching_skills_str = (
                ", ".join(cand.get("matching_skills", [])) or "core technical competencies"
            )
            default_rationale = (
                f"Strong match for {cand['title']} at {cand['company_name']}. "
                f"Direct skill overlap in {matching_skills_str} and target role alignment."
            )
            rationale = eval_item.get("rationale") or default_rationale

            cand["final_score"] = final_score
            cand["rationale"] = rationale
            results.append(cand)

        # Sort descending by final score
        results.sort(key=lambda x: x["final_score"], reverse=True)
        return results
