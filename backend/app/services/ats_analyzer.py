"""Standalone enterprise ATS Analysis Engine.

Performs rule-based structural, parsing, formatting, metric, verb, section, and keyword checks
combined with LLMClient qualitative improvement suggestions.
"""

import json
import re
from typing import Any, Dict, List, Tuple

from app.core.llm import LLMClient
from app.core.logging import logger
from app.schemas.ats_analysis import ATSAnalysisResponse, ATSCategoryScore, ATSSubScores

# Taxonomy of strong leadership and technical action verbs
STRONG_ACTION_VERBS = {
    "engineered",
    "architected",
    "developed",
    "built",
    "spearheaded",
    "designed",
    "implemented",
    "optimized",
    "orchestrated",
    "automated",
    "lead",
    "led",
    "managed",
    "deployed",
    "scaled",
    "created",
    "refactored",
    "increased",
    "reduced",
    "delivered",
    "launched",
    "executed",
    "transformed",
    "directed",
    "formulated",
    "established",
    "streamlined",
    "accelerated",
    "pioneered",
    "championed",
    "analyzed",
    "benchmarked",
    "integrated",
    "provisioned",
    "overhauled",
}

# Weak or passive phrases to avoid in bullet points
WEAK_PASSIVE_PHRASES = [
    "worked on",
    "responsible for",
    "helped with",
    "assisted in",
    "tasked with",
    "handled",
    "did",
    "involved in",
    "part of",
    "made",
    "assisted",
    "helped",
    "tried",
    "looked after",
    "duties included",
]

# Common industry and technical role keywords
COMMON_ROLE_KEYWORDS = {
    "python",
    "fastapi",
    "sql",
    "postgresql",
    "docker",
    "aws",
    "ci/cd",
    "rest",
    "api",
    "react",
    "typescript",
    "javascript",
    "git",
    "agile",
    "unit testing",
    "microservices",
    "system design",
    "machine learning",
    "devops",
    "cloud",
    "kubernetes",
    "leadership",
    "project management",
    "architecture",
    "data analysis",
    "data pipeline",
    "database",
    "linux",
    "backend",
    "frontend",
    "full stack",
}


def check_formatting(raw_text: str) -> Tuple[float, List[str], Dict[str, Any]]:
    """Analyzes ATS parseability: tables, graphics, non-standard symbols, ASCII borders."""
    details = []
    issues_found = 0

    # 1. ASCII table borders or pipe grid detection
    ascii_table_pattern = re.compile(r"(\+[-+]+\+|\|.*\|.*\|)")
    if ascii_table_pattern.search(raw_text):
        details.append(
            "Detected tabular formatting / grid borders (| or +-+) which confuse ATS parsers."
        )
        issues_found += 2

    # 2. Multi-column tab delimiter check
    multi_tab_pattern = re.compile(r"\t{2,}")
    if len(multi_tab_pattern.findall(raw_text)) > 3:
        details.append(
            "Detected multi-column tab stops that may cause text misordering during ATS ingestion."
        )
        issues_found += 1

    # 3. Non-standard unicode / corrupted characters
    corrupted_chars = re.findall(r"[\ufffd\u25a0\u25ba\u25cb\u25cf\u2605]", raw_text)
    if corrupted_chars:
        details.append(
            f"Contains {len(corrupted_chars)} non-standard or unparseable icon/bullet symbols."
        )
        issues_found += 1

    # 4. Text length vs unparseable graphics indicator
    if len(raw_text.strip()) < 100:
        details.append(
            "Extremely sparse raw text extracted. File may contain text embedded inside scanned images or text boxes."
        )
        issues_found += 3

    if issues_found == 0:
        score = 100.0
        details.append("Clean, ATS-parseable single-column layout with standard typography.")
    else:
        score = max(20.0, 100.0 - (issues_found * 25.0))

    findings = {
        "issues_count": issues_found,
        "has_tables": bool(ascii_table_pattern.search(raw_text)),
    }
    return score, details, findings


def check_section_completeness(raw_text: str) -> Tuple[float, List[str], Dict[str, Any]]:
    """Validates presence of core essential resume sections."""
    details = []
    text_lower = raw_text.lower()
    missing_sections = []
    found_sections = []

    # Contact Check
    has_email = bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_text))
    has_phone = bool(re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", raw_text)) or bool(
        re.search(r"\+\d{1,3}\s?\d{6,12}", raw_text)
    )
    if has_email and has_phone:
        found_sections.append("Contact Information")
    else:
        missing_sections.append("Complete Contact Info (email/phone)")

    # Summary Check
    if re.search(r"\b(summary|objective|profile|about me)\b", text_lower):
        found_sections.append("Professional Summary")
    else:
        missing_sections.append("Professional Summary / Objective")

    # Experience Check
    if re.search(r"\b(experience|employment|work history|career|work experience)\b", text_lower):
        found_sections.append("Work Experience")
    else:
        missing_sections.append("Work Experience")

    # Education Check
    if re.search(
        r"\b(education|academic|degree|university|college|b\.s|m\.s|bachelor|master)\b", text_lower
    ):
        found_sections.append("Education")
    else:
        missing_sections.append("Education")

    # Skills Check
    if re.search(r"\b(skills|competencies|tech stack|technical skills|technologies)\b", text_lower):
        found_sections.append("Skills & Technical Competencies")
    else:
        missing_sections.append("Skills Section")

    # Score calculation (20 points per missing core section)
    score = max(0.0, 100.0 - (len(missing_sections) * 20.0))

    if missing_sections:
        details.append(f"Missing essential ATS sections: {', '.join(missing_sections)}.")
    else:
        details.append(
            "All 5 core ATS resume sections (Contact, Summary, Experience, Education, Skills) detected."
        )

    findings = {
        "found_sections": found_sections,
        "missing_sections": missing_sections,
    }
    return score, details, findings


def check_quantified_achievements(raw_text: str) -> Tuple[float, List[str], Dict[str, Any]]:
    """Evaluates presence of quantitative metrics, percentages, currency, and numerical impact."""
    details = []

    # Extract bullet points, filtering out skill summary lines like '- Languages: Python, SQL'
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    bullet_lines = [
        b_line
        for b_line in lines
        if (b_line.startswith(("-", "*", "•", "–")) or re.match(r"^\d+\.\s", b_line))
        and not re.match(
            r"^[-*•–]\s*(languages|frameworks|databases|methodologies|tools|certifications|honors)\s*:",
            b_line,
            re.IGNORECASE,
        )
    ]

    if not bullet_lines:
        # Fallback: treat non-header short lines as bullets
        bullet_lines = [
            b_line for b_line in lines if 15 <= len(b_line) <= 250 and not b_line.isupper()
        ]

    if not bullet_lines:
        return (
            30.0,
            ["No clear experience bullet points found to measure quantified achievements."],
            {"total_bullets": 0, "quantified_bullets": 0},
        )

    # Regex for quantitative indicators
    metric_regex = re.compile(
        r"(\d+(\.\d+)?%|\$\d+|\b\d+\s*(k|m|b|million|billion|users|clients|customers|ms|seconds|hrs|hours|percent)\b|\b(increased|reduced|grew|saved|scaled|improved|boosted|cut)\b.*\b\d+\b|\b\d+x\b)"
    )

    quantified_bullets = []
    unquantified_bullets = []

    for idx, bullet in enumerate(bullet_lines, start=1):
        if metric_regex.search(bullet.lower()):
            quantified_bullets.append((idx, bullet))
        else:
            unquantified_bullets.append((idx, bullet))

    quantified_ratio = len(quantified_bullets) / len(bullet_lines) if bullet_lines else 0.0
    score = round(min(100.0, (quantified_ratio / 0.60) * 100.0), 1)

    if quantified_ratio >= 0.60:
        details.append(
            f"Strong quantitative impact: {len(quantified_bullets)} of {len(bullet_lines)} bullet points contain metrics ({int(quantified_ratio * 100)}%)."
        )
    else:
        details.append(
            f"Only {len(quantified_bullets)} of {len(bullet_lines)} bullets include quantifiable metrics ({int(quantified_ratio * 100)}%). Target is at least 60%."
        )
        if unquantified_bullets:
            sample_bullet = unquantified_bullets[0][1]
            if len(sample_bullet) > 60:
                sample_bullet = sample_bullet[:60] + "..."
            details.append(f"Example bullet lacking metrics: '{sample_bullet}'")

    findings = {
        "total_bullets": len(bullet_lines),
        "quantified_bullets_count": len(quantified_bullets),
        "quantified_ratio": quantified_ratio,
        "unquantified_bullet_samples": [b[1] for b in unquantified_bullets[:3]],
    }
    return score, details, findings


def check_action_verbs(raw_text: str) -> Tuple[float, List[str], Dict[str, Any]]:
    """Evaluates usage of strong technical action verbs vs weak/passive phrasing."""
    details = []
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    bullet_lines = [
        b_line
        for b_line in lines
        if (b_line.startswith(("-", "*", "•", "–")) or re.match(r"^\d+\.\s", b_line))
        and not re.match(
            r"^[-*•–]\s*(languages|frameworks|databases|methodologies|tools|certifications|honors)\s*:",
            b_line,
            re.IGNORECASE,
        )
    ]

    if not bullet_lines:
        bullet_lines = [
            b_line for b_line in lines if 15 <= len(b_line) <= 250 and not b_line.isupper()
        ]

    if not bullet_lines:
        return (
            40.0,
            ["No bullet points found for action-verb evaluation."],
            {"strong_verbs": 0, "weak_phrases": 0},
        )

    strong_count = 0
    weak_found = []

    for idx, bullet in enumerate(bullet_lines, start=1):
        clean_bullet = re.sub(r"^[-*•–\d\.]+\s*", "", bullet).strip().lower()
        first_word = clean_bullet.split()[0] if clean_bullet else ""
        first_word = re.sub(r"[^\w]", "", first_word)

        if first_word in STRONG_ACTION_VERBS:
            strong_count += 1

        # Check for weak passive phrases
        for weak in WEAK_PASSIVE_PHRASES:
            if weak in clean_bullet:
                weak_found.append((idx, weak, bullet))
                break

    strong_ratio = strong_count / len(bullet_lines) if bullet_lines else 0.0
    penalty = len(weak_found) * 15.0
    base_score = (strong_ratio / 0.70) * 100.0
    score = round(max(10.0, min(100.0, base_score - penalty)), 1)

    if weak_found:
        weak_samples = [f"'{w[1]}' in bullet {w[0]}" for w in weak_found[:3]]
        details.append(
            f"Detected {len(weak_found)} weak or passive phrase(s): {', '.join(weak_samples)}. Replace with strong action verbs."
        )

    if strong_ratio >= 0.70:
        details.append(
            f"High action-verb frequency: {strong_count} of {len(bullet_lines)} bullets start with impactful verbs ({int(strong_ratio * 100)}%)."
        )
    else:
        details.append(
            f"Only {strong_count} of {len(bullet_lines)} bullets begin with strong action verbs ({int(strong_ratio * 100)}%). Target is at least 70%."
        )

    findings = {
        "total_bullets": len(bullet_lines),
        "strong_verb_count": strong_count,
        "weak_phrase_count": len(weak_found),
        "weak_samples": [w[2] for w in weak_found[:3]],
    }
    return score, details, findings


def check_keyword_density(raw_text: str) -> Tuple[float, List[str], Dict[str, Any]]:
    """Evaluates presence and density of core role/tech keywords."""
    details = []
    text_lower = raw_text.lower()
    words = re.findall(r"\b[a-z0-9\+\#\./-]+\b", text_lower)
    total_words = len(words)

    if total_words == 0:
        return 0.0, ["Empty or unreadable text."], {"unique_keywords": 0, "density": 0.0}

    found_keywords = [kw for kw in COMMON_ROLE_KEYWORDS if kw in text_lower]

    # Calculate frequency of matched keywords
    matched_word_count = sum(text_lower.count(kw) for kw in found_keywords)
    density_pct = (matched_word_count / total_words) * 100.0

    if len(found_keywords) >= 8:
        base_score = 90.0
    elif len(found_keywords) >= 5:
        base_score = 75.0
    elif len(found_keywords) >= 2:
        base_score = 50.0
    else:
        base_score = 25.0

    # Keyword stuffing penalty (> 15% density)
    if density_pct > 15.0:
        score = max(30.0, base_score - 30.0)
        details.append(
            f"Keyword stuffing risk: detected high keyword concentration ({density_pct:.1f}%). ATS algorithms flag artificial repetition."
        )
    elif len(found_keywords) < 3:
        score = base_score
        details.append(
            f"Low role keyword density: found only {len(found_keywords)} common industry terms ({', '.join(found_keywords) if found_keywords else 'none'})."
        )
    else:
        score = base_score
        details.append(
            f"Found {len(found_keywords)} key technical and domain keywords with balanced density ({density_pct:.1f}%)."
        )

    findings = {
        "found_keywords": found_keywords,
        "unique_keyword_count": len(found_keywords),
        "density_pct": round(density_pct, 2),
    }
    return score, details, findings


def check_length(raw_text: str) -> Tuple[float, List[str], Dict[str, Any]]:
    """Evaluates word count against optimal ATS bounds (450 - 1000 words)."""
    details = []
    words = raw_text.split()
    word_count = len(words)

    if 450 <= word_count <= 1000:
        score = 100.0
        status = "Optimal (1-2 pages)"
        details.append(f"Optimal word count for ATS ingestion ({word_count} words).")
    elif 350 <= word_count < 450:
        score = 80.0
        status = "Slightly Concise (< 450 words)"
        details.append(
            f"Word count ({word_count} words) is slightly concise. Consider expanding on key achievements."
        )
    elif 1000 < word_count <= 1250:
        score = 85.0
        status = "Slightly Long (> 1000 words)"
        details.append(
            f"Word count ({word_count} words) is slightly long. Concise bullet points improve readability."
        )
    elif word_count < 350:
        score = 40.0
        status = "Critically Short (< 350 words)"
        details.append(
            f"Resume is critically short ({word_count} words). Missing detailed role responsibilities."
        )
    else:
        score = 50.0
        status = "Excessive Length (> 1250 words)"
        details.append(
            f"Excessive document length ({word_count} words). ATS algorithms rank concise resumes higher."
        )

    findings = {"word_count": word_count, "length_status": status}
    return score, details, findings


class ATSAnalyzer:
    """Enterprise ATS Analyzer combining deterministic rule-based analysis and LLM suggestions."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

    async def analyze(self, resume_id: str, raw_text: str) -> ATSAnalysisResponse:
        """Executes full ATS evaluation on raw resume text."""
        # 1. Execute Rule-Based Checks
        fmt_score, fmt_details, fmt_findings = check_formatting(raw_text)
        sec_score, sec_details, sec_findings = check_section_completeness(raw_text)
        qua_score, qua_details, qua_findings = check_quantified_achievements(raw_text)
        act_score, act_details, act_findings = check_action_verbs(raw_text)
        key_score, key_details, key_findings = check_keyword_density(raw_text)
        len_score, len_details, len_findings = check_length(raw_text)

        # 2. Calculate Weighted Composite ATS Score
        weights = {
            "formatting": 0.20,
            "section_completeness": 0.20,
            "quantified_achievements": 0.25,
            "action_verbs": 0.15,
            "keyword_density": 0.10,
            "length": 0.10,
        }

        sub_scores_dict = {
            "formatting": fmt_score,
            "section_completeness": sec_score,
            "quantified_achievements": qua_score,
            "action_verbs": act_score,
            "keyword_density": key_score,
            "length": len_score,
        }

        overall_score = round(sum(sub_scores_dict[cat] * weights[cat] for cat in weights), 1)

        # Helper status generator
        def get_status(s: float) -> str:
            if s >= 80.0:
                return "Good"
            elif s >= 60.0:
                return "Needs Improvement"
            else:
                return "Critical"

        category_breakdown = {
            "Formatting & Layout": ATSCategoryScore(
                score=fmt_score, status=get_status(fmt_score), details=fmt_details
            ),
            "Section Completeness": ATSCategoryScore(
                score=sec_score, status=get_status(sec_score), details=sec_details
            ),
            "Quantified Achievements": ATSCategoryScore(
                score=qua_score, status=get_status(qua_score), details=qua_details
            ),
            "Action Verbs": ATSCategoryScore(
                score=act_score, status=get_status(act_score), details=act_details
            ),
            "Keyword Density": ATSCategoryScore(
                score=key_score, status=get_status(key_score), details=key_details
            ),
            "Document Length": ATSCategoryScore(
                score=len_score, status=get_status(len_score), details=len_details
            ),
        }

        rule_based_findings = {
            "formatting": fmt_findings,
            "sections": sec_findings,
            "quantified_achievements": qua_findings,
            "action_verbs": act_findings,
            "keywords": key_findings,
            "length": len_findings,
        }

        # 3. Generate Qualitative Improvement Suggestions via LLM + Rule-based fallback
        suggestions = await self._generate_suggestions(
            raw_text, sub_scores_dict, category_breakdown, rule_based_findings
        )

        import uuid

        return ATSAnalysisResponse(
            resume_id=uuid.UUID(str(resume_id)) if isinstance(resume_id, str) else resume_id,
            overall_ats_score=overall_score,
            sub_scores=ATSSubScores(**sub_scores_dict),
            category_breakdown=category_breakdown,
            rule_based_findings=rule_based_findings,
            improvement_suggestions=suggestions,
        )

    async def _generate_suggestions(
        self,
        raw_text: str,
        sub_scores: Dict[str, float],
        breakdown: Dict[str, ATSCategoryScore],
        findings: Dict[str, Any],
    ) -> List[str]:
        """Queries LLMClient for qualitative advice with fallback to rule-based findings."""
        fallback_suggestions = []

        # Construct deterministic fallback suggestions directly from rule findings
        if findings["sections"]["missing_sections"]:
            missing_str = ", ".join(findings["sections"]["missing_sections"])
            fallback_suggestions.append(f"Add missing essential section(s): {missing_str}.")

        if findings["quantified_achievements"].get("unquantified_bullet_samples"):
            sample = findings["quantified_achievements"]["unquantified_bullet_samples"][0]
            fallback_suggestions.append(
                f"Add concrete numerical metrics (%, $, scale) to bullet points such as: '{sample[:70]}...'"
            )

        if findings["action_verbs"].get("weak_samples"):
            sample = findings["action_verbs"]["weak_samples"][0]
            fallback_suggestions.append(
                f"Replace passive phrasing in bullet ('{sample[:70]}...') with strong action verbs like 'Engineered', 'Spearheaded', or 'Architected'."
            )

        if findings["formatting"].get("has_tables"):
            fallback_suggestions.append(
                "Remove ASCII table borders or multi-column table elements to ensure uncorrupted ATS text extraction."
            )

        if findings["keywords"].get("unique_keyword_count", 0) < 4:
            fallback_suggestions.append(
                "Include core technical skills and methodologies (e.g. Python, SQL, REST APIs, CI/CD, Agile) in a dedicated Skills section."
            )

        if findings["length"].get("word_count", 0) < 350:
            fallback_suggestions.append(
                f"Expand resume text beyond current {findings['length']['word_count']} words with detailed bullet points describing your technical accomplishments."
            )

        if not fallback_suggestions:
            fallback_suggestions.append(
                "Resume formatting and content are strong. Keep bullet points concise and updated with recent metrics."
            )

        # Query LLMClient for rich qualitative suggestions
        prompt = f"""You are a senior enterprise HR Tech ATS Resume Auditor. Analyze the following resume raw text and rule-based diagnostic findings.
Generate 3 to 5 highly specific, actionable bullet-point improvement suggestions. Each suggestion MUST directly cite a specific bullet point or section from the text and explain how to rewrite it (e.g., 'In bullet 2 of Experience: replace "worked on database" with "Architected PostgreSQL database system, boosting query speed by 40%"').

RULE-BASED DIAGNOSTIC SUMMARY:
- Sub-Scores: {json.dumps(sub_scores)}
- Missing Sections: {findings["sections"]["missing_sections"]}
- Weak Bullets: {findings["action_verbs"].get("weak_samples", [])}
- Metricless Bullets: {findings["quantified_achievements"].get("unquantified_bullet_samples", [])}

RAW RESUME TEXT:
{raw_text[:2000]}

OUTPUT FORMAT: Return ONLY a JSON object with key "suggestions" containing a list of strings.
Example: {{"suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]}}
"""
        try:
            llm_response = await self.llm_client.generate(prompt, response_format="json")
            data = json.loads(llm_response)
            if (
                isinstance(data, dict)
                and "suggestions" in data
                and isinstance(data["suggestions"], list)
            ):
                if data["suggestions"]:
                    return data["suggestions"]
        except Exception as e:
            logger.warning("LLM generation for ATS suggestions fallback trigger: %s", str(e))

        return fallback_suggestions
