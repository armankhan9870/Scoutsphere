"""Database seed script populating demo student user, demo resume, and ~15 diverse opportunities."""

import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from sqlalchemy import select

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.match import Match
from app.models.opportunity import Opportunity
from app.models.resume import Resume
from app.models.skill import Skill
from app.models.user import User, UserSkill

ph = PasswordHasher()


def generate_mock_vector(dim: int = 384, seed_val: float = 0.1) -> list[float]:
    """Generates a normalized L2 384-dimensional float vector for semantic search testing."""
    vec = [random.uniform(-1.0, 1.0) + seed_val for _ in range(dim)]
    norm = sum(x * x for x in vec) ** 0.5
    return [x / norm for x in vec]


async def seed_database() -> None:
    """Populates PostgreSQL/SQLite database with initial schema entities and demo dataset."""
    print("Starting database seeding process...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Create Demo Skills
        skills_data = [
            ("Python", "Languages"),
            ("FastAPI", "Frameworks"),
            ("PostgreSQL", "Databases"),
            ("Docker", "DevOps"),
            ("LangChain", "AI/ML"),
            ("LangGraph", "AI/ML"),
            ("React", "Frontend"),
            ("TypeScript", "Languages"),
            ("PyTorch", "AI/ML"),
            ("Kubernetes", "DevOps"),
            ("Redis", "Databases"),
            ("Node.js", "Backend"),
        ]

        skill_map = {}
        for name, category in skills_data:
            skill = Skill(
                name=name,
                category=category,
                normalized_name=name.lower().strip(),
            )
            session.add(skill)
            skill_map[name] = skill

        await session.flush()
        print(f"Created {len(skill_map)} core skill catalog items.")

        # 2. Create Demo Student User
        existing_user_res = await session.execute(
            select(User).where(User.email == "student@scoutsphere.ai")
        )
        demo_user = existing_user_res.scalar_one_or_none()
        if not demo_user:
            demo_user = User(
                id=uuid.UUID("3e8ec9ae-9d67-48f7-9622-c52de2c7def9"),
                email="student@scoutsphere.ai",
                hashed_password=ph.hash("DemoStudent123!"),
                full_name="Alex Rivera",
            )
            session.add(demo_user)
            await session.flush()

        # Link User Skills
        user_skills = [
            UserSkill(
                user_id=demo_user.id,
                skill_id=skill_map["Python"].id,
                proficiency_level="Advanced",
                verified=True,
            ),
            UserSkill(
                user_id=demo_user.id,
                skill_id=skill_map["FastAPI"].id,
                proficiency_level="Intermediate",
                verified=True,
            ),
            UserSkill(
                user_id=demo_user.id,
                skill_id=skill_map["PostgreSQL"].id,
                proficiency_level="Intermediate",
                verified=True,
            ),
            UserSkill(
                user_id=demo_user.id,
                skill_id=skill_map["Docker"].id,
                proficiency_level="Beginner",
                verified=False,
            ),
        ]
        session.add_all(user_skills)

        # 3. Create Demo Resume
        demo_resume_vector = generate_mock_vector(384, seed_val=0.5)
        demo_resume = Resume(
            id=uuid.UUID("f8a92b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c"),
            user_id=demo_user.id,
            raw_text="""
Alex Rivera - Computer Science Senior
Email: alex.rivera@example.com | GitHub: github.com/alexrivera

SUMMARY:
Passionate senior CS student specializing in Python backend services, asynchronous APIs with FastAPI, PostgreSQL, and agentic AI tools. Built multi-agent workflows using LangChain and Docker containers.

EXPERIENCE:
Software Engineering Intern | TechCorp (Jun 2025 - Aug 2025)
- Developed async REST microservices with FastAPI and PostgreSQL.
- Optimized query performance using SQL indexes and Redis caching.

PROJECTS:
- ScoutSphere: Multi-agent career assistant platform using FastAPI, LangGraph, and pgvector.
- Smart Search: Semantic vector search engine built with SentenceTransformers.

SKILLS:
Python, FastAPI, PostgreSQL, Docker, LangChain, React, TypeScript, Git
            """,
            parsed_data_json={
                "skills": [
                    "Python",
                    "FastAPI",
                    "PostgreSQL",
                    "Docker",
                    "LangChain",
                    "React",
                    "TypeScript",
                ],
                "education": [
                    {
                        "degree": "B.S. Computer Science",
                        "institution": "State University",
                        "graduation": "2026",
                    }
                ],
                "experience": [
                    {
                        "role": "Software Engineering Intern",
                        "company": "TechCorp",
                        "duration": "3 months",
                    }
                ],
            },
            embedding=demo_resume_vector,
            is_active=True,
        )
        session.add(demo_resume)
        await session.flush()

        # 4. Create 15 Sample Opportunities with ACTIVE LIVE external portals
        sample_opportunities = [
            # INTERNSHIPS
            {
                "title": "Backend Engineering Intern",
                "company_name": "Stripe",
                "opportunity_type": "INTERNSHIP",
                "description": "Join the core billing team to build high-scale API payment pipelines using Python and async architecture.",
                "required_skills_json": ["Python", "FastAPI", "PostgreSQL", "Redis"],
                "location": "San Francisco, CA (Hybrid)",
                "is_remote": False,
                "source_url": "https://stripe.com/jobs/search",
                "seed": 0.45,
            },
            {
                "title": "AI/ML Research Intern",
                "company_name": "Google DeepMind",
                "opportunity_type": "INTERNSHIP",
                "description": "Collaborate on next-generation multi-agent reasoning graphs and PyTorch LLM fine-tuning techniques.",
                "required_skills_json": ["Python", "PyTorch", "LangChain", "LangGraph"],
                "location": "Remote",
                "is_remote": True,
                "source_url": "https://deepmind.google/careers/",
                "seed": 0.52,
            },
            {
                "title": "Cloud Infrastructure Intern",
                "company_name": "AWS",
                "opportunity_type": "INTERNSHIP",
                "description": "Build containerized microservices and automated CI/CD deployment pipelines using Docker and Kubernetes.",
                "required_skills_json": ["Docker", "Kubernetes", "Python", "PostgreSQL"],
                "location": "Seattle, WA",
                "is_remote": False,
                "source_url": "https://amazon.jobs/",
                "seed": 0.20,
            },
            {
                "title": "Full-Stack Developer Intern",
                "company_name": "Spotify",
                "opportunity_type": "INTERNSHIP",
                "description": "Develop web features for creator tools using React, TypeScript, Node.js, and RESTful web APIs.",
                "required_skills_json": ["React", "TypeScript", "Node.js", "Python"],
                "location": "New York, NY (Hybrid)",
                "is_remote": False,
                "source_url": "https://lifeatspotify.com/jobs",
                "seed": 0.30,
            },
            {
                "title": "AI Product Engineering Intern",
                "company_name": "Vercel",
                "opportunity_type": "INTERNSHIP",
                "description": "Build agentic user interfaces and streaming AI workflows with Next.js, React, and serverless backends.",
                "required_skills_json": ["React", "TypeScript", "Python", "FastAPI"],
                "location": "Remote",
                "is_remote": True,
                "source_url": "https://vercel.com/careers",
                "seed": 0.40,
            },
            # JOBS
            {
                "title": "Associate AI Systems Engineer",
                "company_name": "ScoutSphere Inc",
                "opportunity_type": "JOB",
                "description": "Build production multi-agent systems, vector retrieval systems with pgvector, and FastAPI backend servers.",
                "required_skills_json": ["Python", "FastAPI", "LangGraph", "PostgreSQL", "Docker"],
                "location": "Remote",
                "is_remote": True,
                "source_url": "https://www.linkedin.com/jobs/search/?keywords=AI%20Engineer",
                "seed": 0.55,
            },
            {
                "title": "Junior Backend Engineer",
                "company_name": "CloudScale Systems",
                "opportunity_type": "JOB",
                "description": "Design asynchronous database access patterns, Redis caching layers, and scalable microservices.",
                "required_skills_json": ["Python", "FastAPI", "PostgreSQL", "Redis"],
                "location": "Austin, TX (Hybrid)",
                "is_remote": False,
                "source_url": "https://www.linkedin.com/jobs/search/?keywords=Backend%20Engineer",
                "seed": 0.48,
            },
            {
                "title": "Entry-Level Machine Learning Engineer",
                "company_name": "DataFlow AI",
                "opportunity_type": "JOB",
                "description": "Train embedding models, construct vector RAG pipelines, and integrate PyTorch models into production.",
                "required_skills_json": ["Python", "PyTorch", "LangChain", "PostgreSQL"],
                "location": "San Jose, CA",
                "is_remote": False,
                "source_url": "https://www.linkedin.com/jobs/search/?keywords=Machine%20Learning",
                "seed": 0.38,
            },
            {
                "title": "Junior DevOps & Platform Engineer",
                "company_name": "InfraGen Cloud",
                "opportunity_type": "JOB",
                "description": "Maintain Docker Compose and Kubernetes clusters, automate PostgreSQL backups, and monitor service health.",
                "required_skills_json": ["Docker", "Kubernetes", "PostgreSQL", "Python"],
                "location": "Remote",
                "is_remote": True,
                "source_url": "https://www.linkedin.com/jobs/search/?keywords=DevOps",
                "seed": 0.15,
            },
            {
                "title": "Full-Stack AI Developer",
                "company_name": "Cognitive Tech",
                "opportunity_type": "JOB",
                "description": "Build end-to-end web applications combining React TypeScript frontends with FastAPI AI backend engines.",
                "required_skills_json": ["React", "TypeScript", "Python", "FastAPI", "PostgreSQL"],
                "location": "Remote",
                "is_remote": True,
                "source_url": "https://www.linkedin.com/jobs/search/?keywords=Full%20Stack%20AI",
                "seed": 0.42,
            },
            # HACKATHONS
            {
                "title": "Global Agentic AI Hackathon 2026",
                "company_name": "LangChain & OpenRouter",
                "opportunity_type": "HACKATHON",
                "description": "48-hour global virtual hackathon building multi-agent graphs, autonomous tool-using bots, and RAG apps.",
                "required_skills_json": ["Python", "LangGraph", "LangChain", "FastAPI"],
                "location": "Online / Global",
                "is_remote": True,
                "source_url": "https://devpost.com/hackathons",
                "seed": 0.58,
            },
            {
                "title": "Open Source AI Challenge 2026",
                "company_name": "Groq & Ollama",
                "opportunity_type": "HACKATHON",
                "description": "Build high-throughput AI applications using open-weight models and zero-cost local inference engines.",
                "required_skills_json": ["Python", "FastAPI", "Docker"],
                "location": "Online",
                "is_remote": True,
                "source_url": "https://unstop.com/competitions",
                "seed": 0.40,
            },
            {
                "title": "CalHacks 12.0",
                "company_name": "UC Berkeley",
                "opportunity_type": "HACKATHON",
                "description": "The world's largest collegiate hackathon. Build groundbreaking AI products in 36 continuous hours.",
                "required_skills_json": ["Python", "React", "TypeScript", "FastAPI"],
                "location": "San Francisco, CA",
                "is_remote": False,
                "source_url": "https://calhacks.io/",
                "seed": 0.35,
            },
            {
                "title": "HackMIT 2026",
                "company_name": "MIT",
                "opportunity_type": "HACKATHON",
                "description": "Premier undergraduate hackathon uniting 1,000+ top hackers to build innovative tech solutions.",
                "required_skills_json": ["Python", "FastAPI", "PostgreSQL", "React"],
                "location": "Cambridge, MA",
                "is_remote": False,
                "source_url": "https://hackmit.org/",
                "seed": 0.44,
            },
            {
                "title": "Web3 & AI Fusion Buildathon",
                "company_name": "ETHGlobal",
                "opportunity_type": "HACKATHON",
                "description": "Combine autonomous AI agents with decentralized databases and vector indexing infrastructure.",
                "required_skills_json": ["Python", "TypeScript", "Docker"],
                "location": "Online",
                "is_remote": True,
                "source_url": "https://ethglobal.com/events",
                "seed": 0.25,
            },
        ]

        opp_objects = []
        for opp_data in sample_opportunities:
            vector = generate_mock_vector(384, seed_val=opp_data["seed"])
            deadline_dt = datetime.now(timezone.utc) + timedelta(days=random.randint(14, 90))

            opp = Opportunity(
                title=opp_data["title"],
                company_name=opp_data["company_name"],
                opportunity_type=opp_data["opportunity_type"],
                description=opp_data["description"],
                required_skills_json=opp_data["required_skills_json"],
                embedding=vector,
                location=opp_data["location"],
                is_remote=opp_data["is_remote"],
                source_url=opp_data["source_url"],
                deadline=deadline_dt,
            )
            opp_objects.append(opp)
            session.add(opp)

        await session.flush()
        print(
            f"Created {len(opp_objects)} sample opportunities across Jobs, Internships, and Hackathons."
        )

        # 5. Create Initial Fit Match for Demo User
        best_opp = opp_objects[5]  # Associate AI Systems Engineer
        demo_match = Match(
            user_id=demo_user.id,
            opportunity_id=best_opp.id,
            fit_score=0.92,
            skill_overlap_score=0.88,
            match_reasons_json={
                "highlights": [
                    "92% vector similarity score between student profile and role description",
                    "Strong skill overlap in Python, FastAPI, PostgreSQL, and LangGraph",
                ]
            },
        )
        session.add(demo_match)
        await session.commit()
        print("Created demo match record.")

    print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
