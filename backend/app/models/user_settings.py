"""ORM model for user settings and notification/privacy configurations."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserSettings(Base):
    """User settings table storing notification, privacy, and LLM preferences."""

    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    notification_prefs: Mapped[dict] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=lambda: {
            "email_alerts": True,
            "match_notifications": True,
            "weekly_digest": False,
        },
        nullable=False,
    )
    privacy_prefs: Mapped[dict] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=lambda: {
            "profile_visibility": "private",
            "allow_data_training": False,
        },
        nullable=False,
    )
    theme: Mapped[str] = mapped_column(String(50), default="dark", nullable=False)
    auto_run_agents: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preferred_llm_provider: Mapped[str] = mapped_column(
        String(50), default="gemini", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Synonyms for backward compatibility
    auto_background_agents = synonym("auto_run_agents")

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="settings")

    def __init__(self, **kwargs: Any):
        valid_cols = {
            "id",
            "user_id",
            "notification_prefs",
            "privacy_prefs",
            "theme",
            "auto_run_agents",
            "auto_background_agents",
            "preferred_llm_provider",
            "created_at",
            "updated_at",
        }
        extra_kwargs = {}
        for k in list(kwargs.keys()):
            if k not in valid_cols:
                extra_kwargs[k] = kwargs.pop(k)

        super().__init__(**kwargs)
        for k, v in extra_kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, name: str) -> Any:
        defaults = {
            "agent_tone": "exploratory",
            "min_match_score": 70,
            "auto_hide_low_score": False,
            "exclude_resume_from_training": False,
            "default_resume_template": "modern_clean",
            "cover_letter_tone": "conversational",
            "auto_tailor_high_matches": False,
            "discovery_frequency": "daily",
            "source_filters": {},
            "target_roles": [],
            "target_locations": [],
            "target_industries": [],
            "work_style": "remote",
            "min_salary": None,
            "opportunity_types": ["internship", "job", "hackathon"],
            "notify_high_matches": True,
            "notify_deadlines": True,
            "notify_status_changes": True,
            "notify_weekly_digest": False,
            "email_notifications_enabled": False,
            "layout_density": "comfortable",
            "pending_new_email": None,
            "email_verification_code": None,
        }
        if name in defaults:
            return defaults[name]
        raise AttributeError(f"'UserSettings' object has no attribute '{name}'")
