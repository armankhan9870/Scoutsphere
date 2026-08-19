"""Add HNSW pgvector index and composite query indexes for 5,000+ scaling.

Revision ID: 002_add_pgvector_hnsw_indexes
Revises: 001_initial_schema
Create Date: 2026-08-14
"""

from alembic import op

# revision identifiers
revision = "002_add_pgvector_hnsw_indexes"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add HNSW cosine distance index on opportunities.embedding for fast 5,000+ vector queries
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_opportunities_embedding_hnsw "
        "ON opportunities USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64);"
    )

    # 2. Add HNSW cosine distance index on resumes.embedding
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_resumes_embedding_hnsw "
        "ON resumes USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64);"
    )

    # 3. Add composite index on opportunity_type, is_remote, and deadline for catalog filters
    op.create_index(
        "idx_opportunities_type_remote_deadline",
        "opportunities",
        ["opportunity_type", "is_remote", "deadline"],
    )


def downgrade() -> None:
    op.drop_index("idx_opportunities_type_remote_deadline", table_name="opportunities")
    op.execute("DROP INDEX IF EXISTS idx_opportunities_embedding_hnsw;")
    op.execute("DROP INDEX IF EXISTS idx_resumes_embedding_hnsw;")
