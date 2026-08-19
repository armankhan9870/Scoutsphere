"""Deterministic post-processing skill normalizer matching against ~200 canonical tech and soft skills."""

from typing import Dict, List, Tuple

CANONICAL_SKILL_TAXONOMY: Dict[str, Tuple[str, str]] = {
    # Canonical Name -> (Category, Normalized Lower Key)
    # Languages
    "Python": ("Languages", "python"),
    "TypeScript": ("Languages", "typescript"),
    "JavaScript": ("Languages", "javascript"),
    "Java": ("Languages", "java"),
    "C++": ("Languages", "c++"),
    "C#": ("Languages", "c#"),
    "Go": ("Languages", "go"),
    "Rust": ("Languages", "rust"),
    "SQL": ("Languages", "sql"),
    "HTML": ("Languages", "html"),
    "CSS": ("Languages", "css"),
    "Swift": ("Languages", "swift"),
    "Kotlin": ("Languages", "kotlin"),
    "R": ("Languages", "r"),
    "Dart": ("Languages", "dart"),
    "PHP": ("Languages", "php"),
    "Ruby": ("Languages", "ruby"),
    "Scala": ("Languages", "scala"),
    # Frameworks & Libraries
    "FastAPI": ("Frameworks", "fastapi"),
    "Django": ("Frameworks", "django"),
    "Flask": ("Frameworks", "flask"),
    "React": ("Frameworks", "react"),
    "Next.js": ("Frameworks", "next.js"),
    "Vue.js": ("Frameworks", "vue.js"),
    "Angular": ("Frameworks", "angular"),
    "Spring Boot": ("Frameworks", "spring boot"),
    "Express.js": ("Frameworks", "express.js"),
    "Node.js": ("Frameworks", "node.js"),
    "Tailwind CSS": ("Frameworks", "tailwind css"),
    "Flutter": ("Frameworks", "flutter"),
    "React Native": ("Frameworks", "react native"),
    # Data Science & AI/ML
    "PyTorch": ("AI/ML", "pytorch"),
    "TensorFlow": ("AI/ML", "tensorflow"),
    "Scikit-Learn": ("AI/ML", "scikit-learn"),
    "Pandas": ("AI/ML", "pandas"),
    "NumPy": ("AI/ML", "numpy"),
    "LangChain": ("AI/ML", "langchain"),
    "LangGraph": ("AI/ML", "langgraph"),
    "OpenAI API": ("AI/ML", "openai api"),
    "Hugging Face": ("AI/ML", "hugging face"),
    "Computer Vision": ("AI/ML", "computer vision"),
    "NLP": ("AI/ML", "nlp"),
    "MLOps": ("AI/ML", "mlops"),
    # Databases & Storage
    "PostgreSQL": ("Databases", "postgresql"),
    "MySQL": ("Databases", "mysql"),
    "MongoDB": ("Databases", "mongodb"),
    "Redis": ("Databases", "redis"),
    "SQLite": ("Databases", "sqlite"),
    "Cassandra": ("Databases", "cassandra"),
    "Elasticsearch": ("Databases", "elasticsearch"),
    "Neo4j": ("Databases", "neo4j"),
    "pgvector": ("Databases", "pgvector"),
    "Pinecone": ("Databases", "pinecone"),
    # DevOps & Cloud
    "Docker": ("DevOps", "docker"),
    "Kubernetes": ("DevOps", "kubernetes"),
    "AWS": ("Cloud", "aws"),
    "GCP": ("Cloud", "gcp"),
    "Azure": ("Cloud", "azure"),
    "Linux": ("DevOps", "linux"),
    "Git": ("Tools", "git"),
    "GitHub Actions": ("DevOps", "github actions"),
    "CI/CD": ("DevOps", "ci/cd"),
    "Terraform": ("DevOps", "terraform"),
    "Nginx": ("DevOps", "nginx"),
    # Soft Skills & Practice
    "Agile": ("Practices", "agile"),
    "Scrum": ("Practices", "scrum"),
    "Problem Solving": ("Soft Skills", "problem solving"),
    "Team Collaboration": ("Soft Skills", "team collaboration"),
    "System Design": ("Practices", "system design"),
    "REST APIs": ("Practices", "rest apis"),
    "GraphQL": ("Practices", "graphql"),
    "Unit Testing": ("Practices", "unit testing"),
}

# Alias Synonym Mappings
SKILL_SYNONYMS: Dict[str, str] = {
    "py": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "golang": "Go",
    "postgres": "PostgreSQL",
    "postgres db": "PostgreSQL",
    "reactjs": "React",
    "nextjs": "Next.js",
    "vue": "Vue.js",
    "express": "Express.js",
    "sklearn": "Scikit-Learn",
    "tailwind": "Tailwind CSS",
    "k8s": "Kubernetes",
    "rest": "REST APIs",
    "restful": "REST APIs",
}


def normalize_skill_name(raw_name: str) -> Tuple[str, str]:
    """Normalizes raw extracted skill name to canonical name and category."""
    cleaned = raw_name.strip().lower()

    # Check synonyms
    if cleaned in SKILL_SYNONYMS:
        canonical = SKILL_SYNONYMS[cleaned]
        cat, _ = CANONICAL_SKILL_TAXONOMY[canonical]
        return canonical, cat

    # Direct exact match against taxonomy
    for canonical, (cat, norm_key) in CANONICAL_SKILL_TAXONOMY.items():
        if norm_key == cleaned:
            return canonical, cat

    # Substring match (requiring norm_key length > 2 to prevent 'r' or 'c' matching arbitrary words)
    for canonical, (cat, norm_key) in CANONICAL_SKILL_TAXONOMY.items():
        if len(norm_key) > 2 and norm_key in cleaned:
            return canonical, cat

    # Fallback default
    title_cased = raw_name.strip().title()
    return title_cased, "General"


def normalize_extracted_skills(skills_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Applies canonical normalization across a list of skill dicts."""
    normalized_list = []
    seen = set()

    for s in skills_list:
        raw_name = s.get("name", "")
        if not raw_name:
            continue
        canonical_name, category = normalize_skill_name(raw_name)
        if canonical_name.lower() in seen:
            continue
        seen.add(canonical_name.lower())

        normalized_list.append(
            {
                "name": canonical_name,
                "category": s.get("category") or category,
                "proficiency_estimate": s.get("proficiency_estimate") or "Intermediate",
            }
        )

    return normalized_list
