# ADR-002: Choice of pgvector Over a Separate Vector Database

## Context & Problem Statement
ScoutSphere requires vector similarity search to perform semantic matching between student profiles (resumes, skills, interests) and opportunities (jobs, internships, hackathons). 

Using dedicated vector databases (e.g. Pinecone, Qdrant Cloud, Weaviate) introduces extra infrastructure, hosting costs, separate cluster synchronization issues, and dual-database transactional inconsistency.

## Decision Drivers
- **Zero Cost Floor**: Must run 100% free locally (Docker Compose) and on free hosting tiers (Neon / Supabase PostgreSQL).
- **ACID Transactions**: Vector operations (e.g., updating a resume embedding) must be atomic with relational metadata (e.g., user profiles, match records).
- **Simplified Operations**: Avoid running and managing a second database service.
- **SQL Expressiveness**: Perform vector similarity filtering directly inside standard SQL `JOIN` queries with users, opportunities, and applications.

## Considered Options
1. **Dedicated SaaS Vector Database (Pinecone / Qdrant Cloud)**
2. **Local Self-Hosted Vector DB (Milvus / Qdrant Docker)**
3. **PostgreSQL 17 + `pgvector` Extension**

## Decision Outcome
Chosen Option: **Option 3 - PostgreSQL 17 + pgvector**.

### Justification:
- **Zero Cost**: `pgvector` is an open-source C extension for PostgreSQL available natively in official Postgres Docker images and free database hosts (Neon, Supabase).
- **Single Source of Truth**: User records, resumes, opportunity metadata, and vector embeddings reside in the same PostgreSQL instance.
- **Performant Indexing**: HNSW (Hierarchical Navigable Small World) indexing in `pgvector` provides sub-50ms nearest-neighbor searches across tens of thousands of listings.
- **Unified SQL**: Allows single-query vector distance calculation and relational filtering:
  ```sql
  SELECT o.id, o.title, (o.embedding <=> :user_vector) AS distance
  FROM opportunities o
  WHERE o.is_remote = true AND o.deadline > NOW()
  ORDER BY o.embedding <=> :user_vector LIMIT 10;
  ```

## Status
Accepted.

## Consequences
- **Positive**: Zero extra operational complexity, zero hosting cost, single DB backup/restore, relational vector queries.
- **Negative**: Scale ceiling is tied to PostgreSQL instance hardware, but more than sufficient for portfolio and production scale under 1M vectors.
