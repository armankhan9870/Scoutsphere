"""User and UserSkill ORM models for core authentication and account metadata."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.auth_audit_log import AuthAuditLog
    from app.models.chat import ChatSession
    from app.models.match import Match
    from app.models.refresh_token import RefreshToken
    from app.models.resume import Resume
    from app.models.roadmap import Roadmap
    from app.models.skill import Skill
    from app.models.skill_gap import SkillGap
    from app.models.user_profile import UserProfile
    from app.models.user_session import UserSession
    from app.models.user_settings import UserSettings

_USER_TRANSIENT_STORE: Dict[uuid.UUID, Dict[str, Any]] = {}


class UserSkill(Base):
    """Junction table linking users with skills and proficiency ratings."""

    __tablename__ = "user_skills"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    proficiency_level: Mapped[str] = mapped_column(String(50), default="Intermediate")
    verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="user_skills")


class User(Base):
    """User account entity for authentication and profile linkage."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(
        CITEXT().with_variant(String(255), "sqlite"),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    token_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Synonyms for backward compatibility
    password_hash = synonym("hashed_password")
    is_verified = synonym("email_verified")

    # 1:1 & 1:N Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    settings: Mapped[Optional["UserSettings"]] = relationship(
        "UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    auth_audit_logs: Mapped[List["AuthAuditLog"]] = relationship(
        "AuthAuditLog", back_populates="user", cascade="all, delete-orphan"
    )
    user_skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )

    # Application domain relationships
    resumes: Mapped[List["Resume"]] = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )
    matches: Mapped[List["Match"]] = relationship(
        "Match", back_populates="user", cascade="all, delete-orphan"
    )
    applications: Mapped[List["Application"]] = relationship(
        "Application", back_populates="user", cascade="all, delete-orphan"
    )
    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        "ChatSession", back_populates="user", cascade="all, delete-orphan"
    )
    roadmaps: Mapped[List["Roadmap"]] = relationship(
        "Roadmap", back_populates="user", cascade="all, delete-orphan"
    )
    skill_gaps: Mapped[List["SkillGap"]] = relationship(
        "SkillGap", back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[List["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs: Any):
        target_roles = kwargs.pop("target_roles", [])
        location_pref = kwargs.pop("location_preference", None)
        bio = kwargs.pop("bio", None)

        valid_cols = {
            "id",
            "email",
            "hashed_password",
            "full_name",
            "phone",
            "email_verified",
            "is_active",
            "token_version",
            "oauth_provider",
            "oauth_id",
            "created_at",
            "updated_at",
            "last_login_at",
            "password_hash",
            "is_verified",
        }
        extra_kwargs = {}
        for k in list(kwargs.keys()):
            if k not in valid_cols:
                extra_kwargs[k] = kwargs.pop(k)

        super().__init__(**kwargs)
        if not self.id:
            self.id = uuid.uuid4()

        self._target_roles = target_roles or []
        self._location_preference = location_pref
        self._bio = bio
        self._avatar_url = extra_kwargs.pop("avatar_url", None)
        for k, v in extra_kwargs.items():
            setattr(self, k, v)

    @property
    def target_roles(self) -> List[str]:
        if getattr(self, "profile", None) and self.profile.target_roles:
            return self.profile.target_roles
        return getattr(self, "_target_roles", [])

    @target_roles.setter
    def target_roles(self, value: List[str]):
        self._target_roles = value
        if getattr(self, "profile", None):
            self.profile.target_roles = value

    @property
    def location_preference(self) -> Optional[str]:
        if getattr(self, "profile", None) and self.profile.preferred_locations:
            return ", ".join(self.profile.preferred_locations)
        return getattr(self, "_location_preference", None)

    @location_preference.setter
    def location_preference(self, value: Optional[str]):
        self._location_preference = value
        if getattr(self, "profile", None) and value:
            self.profile.preferred_locations = [value]

    @property
    def bio(self) -> Optional[str]:
        if getattr(self, "profile", None) and self.profile.bio:
            return self.profile.bio
        return getattr(self, "_bio", None)

    @bio.setter
    def bio(self, value: Optional[str]):
        self._bio = value
        if getattr(self, "profile", None):
            self.profile.bio = value

    @property
    def avatar_url(self) -> Optional[str]:
        if getattr(self, "profile", None) and self.profile.avatar_url:
            return self.profile.avatar_url
        return getattr(self, "_avatar_url", None)

    @avatar_url.setter
    def avatar_url(self, value: Optional[str]):
        self._avatar_url = value
        if getattr(self, "profile", None):
            self.profile.avatar_url = value

    @property
    def google_id(self) -> Optional[str]:
        return self.oauth_id

    @google_id.setter
    def google_id(self, value: Optional[str]):
        self.oauth_id = value
        self.oauth_provider = "google"

    @property
    def email_verification_token_hash(self) -> Optional[str]:
        return _USER_TRANSIENT_STORE.get(self.id, {}).get("email_verification_token_hash")

    @email_verification_token_hash.setter
    def email_verification_token_hash(self, value: Optional[str]):
        _USER_TRANSIENT_STORE.setdefault(self.id, {})["email_verification_token_hash"] = value

    @property
    def email_verification_expires_at(self) -> Optional[datetime]:
        return _USER_TRANSIENT_STORE.get(self.id, {}).get("email_verification_expires_at")

    @email_verification_expires_at.setter
    def email_verification_expires_at(self, value: Optional[datetime]):
        _USER_TRANSIENT_STORE.setdefault(self.id, {})["email_verification_expires_at"] = value

    @property
    def password_reset_token_hash(self) -> Optional[str]:
        return _USER_TRANSIENT_STORE.get(self.id, {}).get("password_reset_token_hash")

    @password_reset_token_hash.setter
    def password_reset_token_hash(self, value: Optional[str]):
        _USER_TRANSIENT_STORE.setdefault(self.id, {})["password_reset_token_hash"] = value

    @property
    def password_reset_expires_at(self) -> Optional[datetime]:
        return _USER_TRANSIENT_STORE.get(self.id, {}).get("password_reset_expires_at")

    @password_reset_expires_at.setter
    def password_reset_expires_at(self, value: Optional[datetime]):
        _USER_TRANSIENT_STORE.setdefault(self.id, {})["password_reset_expires_at"] = value

    @property
    def failed_login_attempts(self) -> int:
        return _USER_TRANSIENT_STORE.get(self.id, {}).get("failed_login_attempts", 0)

    @failed_login_attempts.setter
    def failed_login_attempts(self, value: int):
        _USER_TRANSIENT_STORE.setdefault(self.id, {})["failed_login_attempts"] = value

    @property
    def lockout_until(self) -> Optional[datetime]:
        return _USER_TRANSIENT_STORE.get(self.id, {}).get("lockout_until")

    @lockout_until.setter
    def lockout_until(self, value: Optional[datetime]):
        _USER_TRANSIENT_STORE.setdefault(self.id, {})["lockout_until"] = value

    def __getattr__(self, name: str) -> Any:
        defaults = {
            "bio": None,
            "email_verification_token_hash": None,
            "email_verification_expires_at": None,
            "password_reset_token_hash": None,
            "password_reset_expires_at": None,
            "failed_login_attempts": 0,
            "lockout_until": None,
            "deleted_at": None,
        }
        if name in defaults:
            return defaults[name]
        raise AttributeError(f"'User' object has no attribute '{name}'")
