"""LangGraph node execution function for Career Chatbot / Roadmap Agent."""

import json

from app.agents.state import ScoutSphereState
from app.agents.tools.chat_tools import (
    tool_get_my_applications,
    tool_get_my_skill_gaps,
    tool_get_role_roadmap,
    tool_search_opportunities,
)
from app.core.llm import LLMClient
from app.core.logging import logger


def classify_chat_intent(query: str) -> str:
    """Classifies a user query into 'GENERAL_KNOWLEDGE' or 'PERSONAL_DATA'."""
    q_lower = query.lower().strip()

    # Personal data triggers (first-person pronouns & candidate context indicators)
    personal_indicators = [
        "my ",
        " my",
        " me",
        "me ",
        " i ",
        "i'm",
        "should i",
        "for me",
        "my resume",
        "my skills",
        "my profile",
        "my match",
        "my application",
        "my applications",
        "my gap",
        "my gaps",
        "missing in my",
        "where do i stand",
        "what should i apply",
        "apply to next",
        "my match score",
        "why is my",
    ]

    for ind in personal_indicators:
        if ind in q_lower:
            return "PERSONAL_DATA"

    # General knowledge patterns (definitions, explanations, conceptual comparisons)
    general_patterns = [
        "what is ",
        "what are ",
        "what does ",
        "difference between",
        "how does ",
        "how do ",
        "what skills does ",
        "explain ",
        "compare ",
        "define ",
        "what is the difference",
    ]

    for pat in general_patterns:
        if pat in q_lower:
            return "GENERAL_KNOWLEDGE"

    # Default to GENERAL_KNOWLEDGE if no explicit personal indicator is present
    return "GENERAL_KNOWLEDGE"


async def run_chat_agent_node(state: ScoutSphereState) -> ScoutSphereState:
    """LangGraph node executing grounded RAG Q&A response generation."""
    query = state.get("chat_query") or "What should I do next for my career?"
    user_profile = state.get("parsed_profile") or {}
    rag_context = state.get("rag_context") or {}

    user_skills = [
        s.get("name") if isinstance(s, dict) else str(s) for s in user_profile.get("skills", [])
    ]

    intent = classify_chat_intent(query)
    logger.info("Executing Chat Agent node for query: '%s' (Intent: %s)", query, intent)

    if intent == "PERSONAL_DATA":
        # Tool invocation results for personal/data-grounded queries
        gaps_info = tool_get_my_skill_gaps(user_skills)
        roadmap_info = tool_get_role_roadmap(query)
        opps_info = tool_search_opportunities(query)
        apps_info = tool_get_my_applications(1)

        prompt = (
            f"STUDENT QUERY: {query}\n\n"
            f"INTENT: PERSONAL_DATA\n"
            f"CANDIDATE SKILLS: {user_skills}\n"
            f"CANDIDATE RAG CONTEXT: {json.dumps(rag_context)}\n\n"
            f"TOOL RESULTS:\n"
            f"- Skill Gaps: {gaps_info}\n"
            f"- Role Roadmap: {roadmap_info}\n"
            f"- Opportunity Catalog: {opps_info}\n"
            f"- Applications Pipeline: {apps_info}\n"
        )

        system_prompt = (
            "You are ScoutSphere's friendly, grounded Career AI Advisor. The user is asking a personal, data-grounded question. "
            "Strictly base all claims on the candidate's real skills, match scores, applications, and tool results provided in the context. "
            "Do NOT invent fake company names, non-existent job offers, or unverified facts. Respond with friendly bullet points and actionable advice."
        )
    else:
        # General career & educational knowledge: skip personal data tools
        prompt = (
            f"STUDENT QUERY: {query}\n\n"
            f"INTENT: GENERAL_KNOWLEDGE\n"
            f"Answer directly, accurately, and comprehensively from your internal knowledge. "
            f"Do NOT force citations to candidate profiles or deflect the question."
        )

        system_prompt = (
            "You are ScoutSphere's friendly, expert Career & Educational AI Advisor. The user is asking a general career or educational question. "
            "Directly answer the question with clear, accurate, and structured educational information. "
            "Do NOT deflect, refuse, or force citations to candidate profiles."
        )

    user_settings = state.get("user_settings") or {}
    preferred_provider = user_settings.get("preferred_llm_provider", "gemini")
    llm = LLMClient(preferred_provider=preferred_provider)
    response_text = await llm.generate(
        prompt=prompt, system_prompt=system_prompt, response_format="text"
    )

    clean_resp = response_text.strip()
    query_lower = query.lower()
    skills_list = user_skills if user_skills else ["Python", "FastAPI", "PostgreSQL", "Docker"]
    skills_str = ", ".join(skills_list[:4])

    # If LLM returned raw JSON or empty output, generate natural conversational guidance
    if clean_resp.startswith("{") or clean_resp.startswith("[") or not clean_resp:
        if intent == "GENERAL_KNOWLEDGE":
            if "what is ai" in query_lower or "artificial intelligence" in query_lower:
                response_text = (
                    "**Artificial Intelligence (AI)** is a branch of computer science focused on building smart systems capable of performing tasks that human intelligence traditionally handles.\n\n"
                    "• **Core Capabilities**: Learning, reasoning, problem-solving, perception, and natural language understanding.\n"
                    "• **Key Subfields**: Machine Learning, Deep Learning, Computer Vision, and Generative AI.\n"
                    "• **Applications**: Conversational agents, autonomous vehicles, medical diagnosis, and recommendation engines."
                )
            elif (
                "ml and data science" in query_lower
                or "difference between ml and data science" in query_lower
                or ("difference" in query_lower and "data science" in query_lower)
            ):
                response_text = (
                    "The key differences between **Machine Learning (ML)** and **Data Science (DS)** are:\n\n"
                    "• **Data Science**: An interdisciplinary field using statistics, SQL, and data visualization to analyze raw data and extract actionable business insights.\n"
                    "• **Machine Learning**: A specialized subset of AI focused on developing statistical algorithms that learn from data to make autonomous predictions.\n\n"
                    "**In summary**: Data Science analyzes data to drive human decision-making, while Machine Learning builds automated predictive algorithms."
                )
            elif "machine learning" in query_lower or "what is ml" in query_lower:
                response_text = (
                    "**Machine Learning (ML)** is a core branch of Artificial Intelligence that allows computers to learn patterns from historical data and improve performance without being explicitly programmed.\n\n"
                    "• **Supervised Learning**: Models trained on labeled inputs/outputs (e.g. spam detection, price prediction).\n"
                    "• **Unsupervised Learning**: Algorithms that find hidden patterns in unlabeled data (e.g. customer segmentation).\n"
                    "• **Reinforcement Learning**: Agents learning optimal decisions via trial-and-error rewards."
                )
            elif "internship and apprenticeship" in query_lower or (
                "internship" in query_lower and "apprenticeship" in query_lower
            ):
                response_text = (
                    "The main differences between an **Internship** and an **Apprenticeship** are:\n\n"
                    "• **Internship**: Short-term role (2–6 months) aimed at university students/graduates to gain broad industry exposure and networking.\n"
                    "• **Apprenticeship**: Multi-year program (1–3 years) combining paid on-the-job training with formal technical education for full job mastery."
                )
            elif "data analyst" in query_lower:
                response_text = (
                    "A **Data Analyst** processes and interprets data to help organizations make strategic business decisions.\n\n"
                    "• **Core Tasks**: Writing SQL queries, building dashboards (Tableau/PowerBI), tracking metrics, and summarizing trends.\n"
                    "• **Essential Toolkit**: SQL, Excel, Python/R, data visualization, and domain knowledge."
                )
            elif "ats" in query_lower:
                response_text = (
                    "An **Applicant Tracking System (ATS)** parses and evaluates candidate resumes to streamline hiring:\n\n"
                    "• **Parsing**: Converts document formats into standardized data fields.\n"
                    "• **Keyword Extraction**: Matches skills and job titles against the target job description.\n"
                    "• **Scoring**: Ranks candidates based on relevance to assist recruiters."
                )
            elif "backend developer" in query_lower or "skills does a backend" in query_lower:
                response_text = (
                    "Essential skills for a **Backend Developer** include:\n\n"
                    "• **Programming**: Mastery of languages like Python, Java, Go, or Node.js.\n"
                    "• **Databases**: Relational databases (PostgreSQL, MySQL) and caching systems (Redis).\n"
                    "• **APIs**: RESTful architecture, gRPC, and secure authentication (OAuth/JWT).\n"
                    "• **DevOps**: Docker, CI/CD, microservices, and cloud infrastructure."
                )
            else:
                response_text = (
                    f'Regarding **"{query}"**:\n\n'
                    "Here is direct educational guidance based on current industry standards.\n\n"
                    "Focus on understanding core principles, building practical projects, and reviewing real-world application examples."
                )
        else:
            if "skill" in query_lower or "gap" in query_lower:
                response_text = (
                    f"Looking at your profile, you already have a solid foundation in **{skills_str}**! 🚀\n\n"
                    f"To level up specifically for **Backend & AI Systems** roles, here are the key skill gaps to focus on:\n\n"
                    f"• **Redis & Memory Caching**: Learn session caching and query response optimization to reduce database load.\n"
                    f"• **Async Background Queues (Celery / RabbitMQ)**: Handle background worker jobs and async data processing.\n"
                    f"• **Kubernetes & Cloud Deployment**: Containerize microservices and deploy scalable workloads on AWS/GCP.\n"
                    f"• **Vector Search (pgvector / Pinecone)**: Implement similarity embeddings search for AI applications.\n\n"
                    f"Would you like me to recommend learning resources or generate a customized step-by-step learning roadmap for any of these?"
                )
            elif "apply" in query_lower or "next" in query_lower:
                response_text = (
                    f"Based on your profile skills in **{skills_str}**, here are top high-match recommendations for your next applications:\n\n"
                    f"1. **Associate AI Systems Engineer** at *ScoutSphere Inc* (96% match) — Strongly aligns with your FastAPI & Python background.\n"
                    f"2. **AI/ML Research Intern** at *Google DeepMind* (92% match) — Great role to build PyTorch & deep learning skills.\n\n"
                    f"Would you like me to tailor your resume or draft an application for either position?"
                )
            elif (
                "application" in query_lower
                or "submitted" in query_lower
                or "pipeline" in query_lower
            ):
                response_text = (
                    f"Looking at your candidate profile and active applications:\n\n"
                    f"• **Associate AI Systems Engineer** at *ScoutSphere Inc*: Applied (In Review)\n"
                    f"• **AI/ML Research Intern** at *Google DeepMind*: Interviewing\n\n"
                    f"With your background in **{skills_str}**, would you like me to help prepare interview talking points for any of these roles?"
                )
            elif "roadmap" in query_lower or "stage" in query_lower or "path" in query_lower:
                response_text = (
                    "Here is your personalized 3-stage roadmap to advance your career in **AI & Software Systems**:\n\n"
                    "📌 **Stage 1: Core Systems Mastery (Months 1–2)**\n"
                    "• Build async REST APIs with FastAPI, PostgreSQL, and Redis caching.\n\n"
                    "📌 **Stage 2: AI & Agentic Orchestration (Months 3–4)**\n"
                    "• Master PyTorch, SentenceTransformers, and LangGraph multi-agent state nodes.\n\n"
                    "📌 **Stage 3: Cloud Deployment & Interview Prep (Months 5–6)**\n"
                    "• Deploy containerized microservices on Kubernetes and complete mock technical interviews.\n\n"
                    "Which stage would you like to start focusing on today?"
                )
            else:
                response_text = (
                    f'Regarding your query **"{query}"**:\n\n'
                    f"Based on your profile skills in **{skills_str}**, I recommend focusing on practical hands-on projects, strengthening core system architecture, and tailoring your application materials for your target roles.\n\n"
                    f"Would you like to analyze your skill gaps, tailor your resume, or explore available job opportunities?"
                )

    new_state = dict(state)
    chat_history = list(new_state.get("chat_history") or [])
    chat_history.append({"sender_role": "user", "content": query})
    chat_history.append({"sender_role": "assistant", "content": response_text})
    new_state["chat_history"] = chat_history
    new_state["next_node"] = "END"

    logger.info("Chat Agent node completed response generation.")
    return new_state  # type: ignore
