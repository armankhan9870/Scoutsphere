"""003 Users and Auth Module Migration

Revision ID: 003_users_auth_module
Revises: 002_add_pgvector_hnsw_indexes
Create Date: 2026-08-16 15:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_users_auth_module"
down_revision: Union[str, None] = "002_add_pgvector_hnsw_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    is_postgres = conn.dialect.name == "postgresql"

    # 1. Enable citext extension on PostgreSQL
    if is_postgres:
        op.execute("CREATE EXTENSION IF NOT EXISTS citext;")

    # 2. Add new columns to users table
    op.add_column("users", sa.Column("phone", sa.String(length=50), nullable=True))
    op.add_column(
        "users", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default="false")
    )
    op.add_column(
        "users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="1")
    )
    op.add_column("users", sa.Column("oauth_provider", sa.String(length=50), nullable=True))
    op.add_column("users", sa.Column("oauth_id", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))

    # Make password_hash nullable for OAuth users
    op.alter_column("users", "password_hash", existing_type=sa.String(length=255), nullable=True)

    # 3. Create user_profiles table
    op.create_table(
        "user_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True) if is_postgres else sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True) if is_postgres else sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column(
            "target_roles",
            postgresql.ARRAY(sa.String()) if is_postgres else sa.JSON(),
            nullable=False,
            server_default="{}" if is_postgres else "[]",
        ),
        sa.Column(
            "preferred_locations",
            postgresql.ARRAY(sa.String()) if is_postgres else sa.JSON(),
            nullable=False,
            server_default="{}" if is_postgres else "[]",
        ),
        sa.Column(
            "remote_preference", sa.String(length=50), nullable=False, server_default="hybrid"
        ),
        sa.Column("education", postgresql.JSONB() if is_postgres else sa.JSON(), nullable=True),
        sa.Column("current_status", sa.String(length=50), nullable=False, server_default="student"),
        sa.Column(
            "resume_id",
            postgresql.UUID(as_uuid=True) if is_postgres else sa.String(length=36),
            sa.ForeignKey("resumes.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("idx_user_profiles_user_id", "user_profiles", ["user_id"])
    op.create_index("idx_user_profiles_resume_id", "user_profiles", ["resume_id"])

    # 4. Create user_settings table
    op.create_table(
        "user_settings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True) if is_postgres else sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True) if is_postgres else sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "notification_prefs",
            postgresql.JSONB() if is_postgres else sa.JSON(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "privacy_prefs",
            postgresql.JSONB() if is_postgres else sa.JSON(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("theme", sa.String(length=50), nullable=False, server_default="dark"),
        sa.Column("auto_run_agents", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "preferred_llm_provider", sa.String(length=50), nullable=False, server_default="gemini"
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("idx_user_settings_user_id", "user_settings", ["user_id"])

    # 5. Create refresh_tokens table
    op.create_table(
        "refresh_tokens",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True) if is_postgres else sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True) if is_postgres else sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(length=255), nullable=False, unique=True),
        sa.Column("device_info", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=50), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("idx_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("idx_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"])
    op.create_index("idx_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"])

    # 6. Create auth_audit_log table
    op.create_table(
        "auth_audit_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True) if is_postgres else sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True) if is_postgres else sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("event", sa.String(length=100), nullable=False),
        sa.Column("ip_address", sa.String(length=50), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("idx_auth_audit_log_user_id", "auth_audit_log", ["user_id"])
    op.create_index("idx_auth_audit_log_created_at", "auth_audit_log", ["created_at"])


def downgrade() -> None:
    op.drop_table("auth_audit_log")
    op.drop_table("refresh_tokens")
    op.drop_table("user_settings")
    op.drop_table("user_profiles")

    op.drop_column("users", "last_login_at")
    op.drop_column("users", "oauth_id")
    op.drop_column("users", "oauth_provider")
    op.drop_column("users", "token_version")
    op.drop_column("users", "email_verified")
    op.drop_column("users", "phone")
