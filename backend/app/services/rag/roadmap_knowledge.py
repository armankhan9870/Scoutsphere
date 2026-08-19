"""Curated career role roadmaps for RAG knowledge retrieval."""

from typing import Any, Dict

CURATED_ROADMAPS: Dict[str, Dict[str, Any]] = {
    "ml_engineer": {
        "target_role": "Machine Learning Engineer",
        "milestones": [
            {
                "phase": "Phase 1: Math & Python Foundations",
                "duration": "4 weeks",
                "skills": ["Python", "NumPy", "Pandas", "Linear Algebra", "SQL"],
                "suggested_projects": [
                    "Data Cleaning Pipeline",
                    "Exploratory Data Analysis Notebook",
                ],
            },
            {
                "phase": "Phase 2: Core ML & Deep Learning",
                "duration": "6 weeks",
                "skills": ["Scikit-Learn", "PyTorch", "TensorFlow", "Feature Engineering"],
                "suggested_projects": [
                    "Image Classifier with PyTorch",
                    "Predictive Analytics Model",
                ],
            },
            {
                "phase": "Phase 3: LLMs, RAG & Multi-Agent Systems",
                "duration": "6 weeks",
                "skills": ["LangChain", "LangGraph", "pgvector", "FastAPI", "Docker"],
                "suggested_projects": [
                    "RAG Vector Q&A System",
                    "Autonomous Multi-Agent Career Bot",
                ],
            },
        ],
    },
    "backend_engineer": {
        "target_role": "Backend Engineer",
        "milestones": [
            {
                "phase": "Phase 1: Async APIs & Databases",
                "duration": "4 weeks",
                "skills": ["Python", "FastAPI", "PostgreSQL", "SQLAlchemy 2.0"],
                "suggested_projects": ["Async REST API Microservice"],
            },
            {
                "phase": "Phase 2: Task Queues & Caching",
                "duration": "4 weeks",
                "skills": ["Redis", "Celery", "Docker", "Git"],
                "suggested_projects": ["Background Job Queue Manager"],
            },
            {
                "phase": "Phase 3: System Design & Microservices",
                "duration": "6 weeks",
                "skills": ["Kubernetes", "Nginx", "CI/CD", "System Design"],
                "suggested_projects": ["Distributed Containerized App"],
            },
        ],
    },
    "data_scientist": {
        "target_role": "Data Scientist",
        "milestones": [
            {
                "phase": "Phase 1: Statistics & SQL",
                "duration": "4 weeks",
                "skills": ["Python", "Pandas", "SQL", "Statistics"],
                "suggested_projects": ["Customer Churn Analysis"],
            },
            {
                "phase": "Phase 2: Predictive Modeling",
                "duration": "6 weeks",
                "skills": ["Scikit-Learn", "XGBoost", "Matplotlib", "Seaborn"],
                "suggested_projects": ["Housing Price Prediction"],
            },
        ],
    },
}


def get_curated_roadmap(role: str) -> Dict[str, Any]:
    """Retrieves curated roadmap document matching target role keywords."""
    cleaned = role.lower().strip()
    if "ml" in cleaned or "machine learning" in cleaned or "ai" in cleaned:
        return CURATED_ROADMAPS["ml_engineer"]
    elif "backend" in cleaned or "fastapi" in cleaned or "python" in cleaned:
        return CURATED_ROADMAPS["backend_engineer"]
    elif "data" in cleaned or "statistics" in cleaned:
        return CURATED_ROADMAPS["data_scientist"]

    return CURATED_ROADMAPS["ml_engineer"]
