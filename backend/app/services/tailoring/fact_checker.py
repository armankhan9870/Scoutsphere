"""Anti-fabrication fact-checking service diffing tailored claims against original base resume data."""

from typing import Any, Dict, List, Tuple

from app.core.logging import logger


class FactCheckerService:
    """Verifies that tailored resume bullet points and skills do not hallucinate non-existent experience."""

    def verify_tailored_resume(
        self, base_resume_data: Dict[str, Any], tailored_resume_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Compares tailored resume against original base resume data.

        Returns (is_valid, list_of_violations).
        """
        violations = []

        # 1. Base skill set (case-insensitive)
        base_skills = {
            (s.get("name") if isinstance(s, dict) else str(s)).lower().strip()
            for s in base_resume_data.get("skills", [])
        }

        # Check tailored skills
        tailored_skills = tailored_resume_data.get("skills", [])
        for s in tailored_skills:
            name = (s.get("name") if isinstance(s, dict) else str(s)).lower().strip()
            if name and name not in base_skills:
                violations.append(f"Fabricated skill detected: '{s}' not present in base resume.")

        # 2. Base companies & degrees
        base_companies = {
            e.get("company", "").lower().strip()
            for e in base_resume_data.get("experience", [])
            if isinstance(e, dict)
        }
        tailored_experience = tailored_resume_data.get("experience", [])
        for e in tailored_experience:
            if isinstance(e, dict):
                comp = e.get("company", "").lower().strip()
                if comp and comp not in base_companies:
                    violations.append(
                        f"Fabricated employer detected: '{e.get('company')}' not in base resume."
                    )

        is_valid = len(violations) == 0
        if not is_valid:
            logger.warning("FactChecker detected %d anti-fabrication violations.", len(violations))

        return is_valid, violations
