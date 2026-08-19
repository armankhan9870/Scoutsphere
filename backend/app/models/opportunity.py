"""Opportunity ORM model with pgvector embedding column."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, List, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.match import Match
    from app.models.skill_gap import SkillGap


class Opportunity(Base):
    """Job, Internship, or Hackathon listing with pgvector embedding."""

    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    opportunity_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # JOB, INTERNSHIP, HACKATHON
    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # pgvector 384-dimensional vector embedding for opportunity semantic search
    embedding: Mapped[Optional[Any]] = mapped_column(Vector(384), nullable=True)

    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    matches: Mapped[List["Match"]] = relationship(
        "Match", back_populates="opportunity", cascade="all, delete-orphan"
    )
    skill_gaps: Mapped[List["SkillGap"]] = relationship(
        "SkillGap", back_populates="opportunity", cascade="all, delete-orphan"
    )
    applications: Mapped[List["Application"]] = relationship(
        "Application", back_populates="opportunity", cascade="all, delete-orphan"
    )
