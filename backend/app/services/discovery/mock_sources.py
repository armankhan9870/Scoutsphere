"""Mock discovery sources for testing pipeline without external API rate limits."""

from typing import Any, Dict, List, Optional

from app.services.discovery.base_source import OpportunitySource, RawOpportunity


class MockJobBoardSource(OpportunitySource):
    """Mock job board API producing realistic entry-level and junior developer listings."""

    async def fetch(
        self, query: str = "", filters: Optional[Dict[str, Any]] = None
    ) -> List[RawOpportunity]:
        return [
            RawOpportunity(
                title="Junior Python Backend Engineer",
                organization="CloudScale AI Solutions",
                opportunity_type="JOB",
                raw_description="Build asynchronous APIs, PostgreSQL queries, and Redis caching layers using Python 3.13 and FastAPI.",
                skills_found=["Python", "FastAPI", "PostgreSQL", "Redis"],
                location="Remote",
                is_remote=True,
                deadline_str="2026-10-15",
                apply_url="https://cloudscale.ai/jobs/jr-python-backend",
                source_name="MockJobBoard",
            ),
            RawOpportunity(
                title="Associate AI Developer",
                organization="NeuralCraft Systems",
                opportunity_type="JOB",
                raw_description="Develop agentic AI workflows with LangChain, LangGraph, and pgvector vector search integrations.",
                skills_found=["Python", "LangChain", "LangGraph", "pgvector", "Docker"],
                location="San Francisco, CA (Hybrid)",
                is_remote=False,
                deadline_str="2026-11-01",
                apply_url="https://neuralcraft.io/careers/assoc-ai-dev",
                source_name="MockJobBoard",
            ),
        ]


class MockHackathonSource(OpportunitySource):
    """Mock hackathon source producing collegiate and global hackathon listings."""

    async def fetch(
        self, query: str = "", filters: Optional[Dict[str, Any]] = None
    ) -> List[RawOpportunity]:
        return [
            RawOpportunity(
                title="Autonomous AI Agent Challenge 2026",
                organization="LangGraph & Groq Community",
                opportunity_type="HACKATHON",
                raw_description="48-hour global virtual hackathon building multi-agent systems and tool-using LLM graphs.",
                skills_found=["Python", "LangGraph", "FastAPI", "Docker"],
                location="Online / Virtual",
                is_remote=True,
                deadline_str="2026-09-20",
                apply_url="https://agent-challenge-2026.devpost.com",
                source_name="MockHackathonBoard",
            ),
            RawOpportunity(
                title="CalHacks 12.0 AI Buildathon",
                organization="UC Berkeley CalHacks",
                opportunity_type="HACKATHON",
                raw_description="World's largest collegiate hackathon focused on next-gen AI applications and full-stack web products.",
                skills_found=["React", "TypeScript", "Python", "FastAPI"],
                location="San Francisco, CA",
                is_remote=False,
                deadline_str="2026-10-10",
                apply_url="https://calhacks.io/hack12-apply",
                source_name="MockHackathonBoard",
            ),
        ]


class MockInternshipSource(OpportunitySource):
    """Mock internship source producing software and data science internship listings."""

    async def fetch(
        self, query: str = "", filters: Optional[Dict[str, Any]] = None
    ) -> List[RawOpportunity]:
        return [
            RawOpportunity(
                title="Software Engineering Intern - Fall 2026",
                organization="Stripe Inc",
                opportunity_type="INTERNSHIP",
                raw_description="Join core payments engineering team to design resilient REST APIs with Python, FastAPI, and Docker.",
                skills_found=["Python", "FastAPI", "Docker", "PostgreSQL"],
                location="Remote",
                is_remote=True,
                deadline_str="2026-09-30",
                apply_url="https://stripe.com/careers/intern-fall-2026",
                source_name="MockInternshipBoard",
            ),
            RawOpportunity(
                title="AI Research & ML Intern",
                organization="Google DeepMind Labs",
                opportunity_type="INTERNSHIP",
                raw_description="Investigate multi-agent reasoning, vector retrieval pipelines, and PyTorch model fine-tuning.",
                skills_found=["Python", "PyTorch", "LangChain", "Pandas"],
                location="Mountain View, CA (Hybrid)",
                is_remote=False,
                deadline_str="2026-10-01",
                apply_url="https://deepmind.google/careers/ml-intern-2026",
                source_name="MockInternshipBoard",
            ),
        ]
