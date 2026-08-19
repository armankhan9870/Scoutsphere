"""Normalizes RawOpportunity items into canonical Opportunity ORM objects with skill normalization and embeddings."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.embeddings import generate_embedding
from app.models.opportunity import Opportunity
from app.services.discovery.base_source import RawOpportunity
from app.services.skill_normalizer import normalize_skill_name


def normalize_raw_opportunity(raw: RawOpportunity) -> Opportunity:
    """Transforms a RawOpportunity payload into a standardized Opportunity model."""
    # 1. Normalize skill names
    normalized_skills = []
    seen = set()
    for s in raw.skills_found:
        canonical, _ = normalize_skill_name(s)
        if canonical.lower() not in seen:
            seen.add(canonical.lower())
            normalized_skills.append(canonical)

    # 2. Parse deadline string
    deadline_dt: Optional[datetime] = None
    if raw.deadline_str:
        try:
            deadline_dt = datetime.strptime(raw.deadline_str, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            deadline_dt = datetime.now(timezone.utc) + timedelta(days=30)
    else:
        deadline_dt = datetime.now(timezone.utc) + timedelta(days=45)

    # 3. Generate 384-dimensional vector embedding for semantic matching
    embedding_text = (
        f"{raw.title} at {raw.organization}. {raw.raw_description} Skills: "
        + ", ".join(normalized_skills)
    )
    vector = generate_embedding(embedding_text, dimension=384)

    return Opportunity(
        title=raw.title.strip(),
        company_name=raw.organization.strip(),
        opportunity_type=raw.opportunity_type.upper(),
        description=raw.raw_description.strip(),
        required_skills_json=normalized_skills,
        embedding=vector,
        location=raw.location.strip(),
        is_remote=raw.is_remote,
        source_url=raw.apply_url.strip(),
        deadline=deadline_dt,
    )
