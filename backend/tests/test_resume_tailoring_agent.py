"""Unit test suite for Resume Tailoring Agent anti-fabrication fact-checker and ATS score estimator."""

from app.services.tailoring.ats_scorer import estimate_ats_score
from app.services.tailoring.fact_checker import FactCheckerService


def test_fact_checker_validates_legitimate_resume() -> None:
    """Verifies that FactChecker passes legitimate resume skills and companies."""
    base = {
        "skills": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "PostgreSQL"}],
        "experience": [{"company": "TechCorp", "role": "Intern"}],
    }
    tailored = {
        "skills": [{"name": "Python"}, {"name": "FastAPI"}],
        "experience": [{"company": "TechCorp", "role": "Backend Intern"}],
    }

    checker = FactCheckerService()
    is_valid, violations = checker.verify_tailored_resume(base, tailored)
    assert is_valid is True
    assert len(violations) == 0


def test_fact_checker_rejects_hallucinated_skills() -> None:
    """Verifies that FactChecker strictly rejects fabricated skills not present in base resume."""
    base = {
        "skills": [{"name": "Python"}, {"name": "FastAPI"}],
        "experience": [{"company": "TechCorp", "role": "Intern"}],
    }
    tailored_fake = {
        "skills": [{"name": "Python"}, {"name": "Quantum Computing"}, {"name": "Blockchain"}],
        "experience": [{"company": "TechCorp", "role": "Intern"}],
    }

    checker = FactCheckerService()
    is_valid, violations = checker.verify_tailored_resume(base, tailored_fake)
    assert is_valid is False
    assert len(violations) >= 2
    assert "Quantum Computing" in violations[0] or "Quantum Computing" in violations[1]


def test_ats_score_estimator() -> None:
    """Verifies ATS Score calculation for keyword overlap %, formatting safety, and document length."""
    tailored_resume = {
        "target_role": "Backend Engineer",
        "summary": "Experienced Python developer skilled in FastAPI, PostgreSQL, and Docker.",
        "skills": [
            {"name": "Python"},
            {"name": "FastAPI"},
            {"name": "PostgreSQL"},
            {"name": "Docker"},
        ],
        "experience": [
            {
                "company": "TechCorp",
                "role": "Software Developer Intern",
                "duration": "6 months",
                "highlights": [
                    "Developed async REST microservices with FastAPI and PostgreSQL",
                    "Optimized database queries and containerized apps with Docker",
                ],
            }
        ],
        "projects": [
            {
                "title": "ScoutSphere Platform",
                "description": "Built multi-agent platform using Python and FastAPI.",
            }
        ],
    }

    required_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    ats_report = estimate_ats_score(tailored_resume, required_skills)

    assert ats_report["overall_ats_score"] >= 85.0
    assert ats_report["keyword_overlap_score"] == 100.0
    assert ats_report["formatting_score"] == 100.0
    assert "formatting_checklist" in ats_report
