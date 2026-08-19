"""ORM model for user extended profiles."""

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.resume import Resume
    from app.models.user import User


class RemotePreferenceEnum(str, enum.Enum):
    """Remote work preference options."""

    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    NO_PREFERENCE = "no_preference"


class CurrentStatusEnum(str, enum.Enum):
    """User career status enum."""

    STUDENT = "student"
    GRAD = "grad"
    PROFESSIONAL = "professional"


class UserProfile(Base):
    """User profile model for career parameters, preferences, and personal details."""

    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_roles: Mapped[List[str]] = mapped_column(
        ARRAY(String).with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
    )
    preferred_locations: Mapped[List[str]] = mapped_column(
        ARRAY(String).with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
    )
    remote_preference: Mapped[RemotePreferenceEnum] = mapped_column(
        SQLEnum(RemotePreferenceEnum, name="remote_preference_enum", native_enum=False),
        default=RemotePreferenceEnum.HYBRID,
        nullable=False,
    )
    education: Mapped[Optional[dict]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    current_status: Mapped[CurrentStatusEnum] = mapped_column(
        SQLEnum(CurrentStatusEnum, name="current_status_enum", native_enum=False),
        default=CurrentStatusEnum.STUDENT,
        nullable=False,
    )
    resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    resume: Mapped[Optional["Resume"]] = relationship("Resume", foreign_keys=[resume_id])
