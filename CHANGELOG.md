# ScoutSphere Changelog

All notable changes to the ScoutSphere multi-agent career assistant platform will be documented in this file.

---

## [Phase 15] - 2026-08-14

### Added
- **Prompt Injection Defense Guardrails (`/backend/app/core/security_guardrails.py`)**:
  - Input sanitization function stripping prompt injection vectors (`"ignore previous instructions"`, `"jailbreak mode"`) before prompt assembly.
- **File Upload Security & Virus Scan Hook**:
  - Enforced `.pdf` and `.docx` extension validation, 10MB file size limit, and `stub_virus_scan_hook` for EICAR test virus checking.
- **Rate-Limiting & Token Usage Cost Middleware (`/backend/app/core/middleware.py`)**:
  - Sliding window rate-limiter (120 req/min per IP) and daily per-user LLM token cost estimation tracker.
- **HNSW pgvector Indexes & Composite Scaling (`/backend/alembic/versions/002_add_pgvector_hnsw_indexes.py`)**:
  - Added HNSW cosine distance index `idx_opportunities_embedding_hnsw` (`m=16`, `ef_construction=64`) for fast 5,000+ vector matching queries and composite filter index on `(opportunity_type, is_remote, deadline)`.
- **Hardening Test Suite (`/backend/tests/test_hardening_security.py`)**:
  - Verified prompt injection defense, upload extension/size limits, and virus scan rejection.

---

## [Phase 14] - 2026-08-14

### Added
- Complete React 19 Frontend Experience with 9 UI pages/flows.

---

## [Phase 13] - 2026-08-14

### Added
- Master LangGraph Orchestrator, AgentRun observability table, onboarding pipeline endpoints, and end-to-end integration test.

---

## [Phase 12] - 2026-08-14

### Added
- Career Chatbot & Roadmap Agent with RAG retriever, pgvector knowledge, 4 tools, streaming API, and React Chatbot UI.

---

## [Phase 11] - 2026-08-14

### Added
- Application Lifecycle State Machine, Kanban grouping, dashboard stats, and stale nudges.

---

## [Phase 10] - 2026-08-14

### Added
- Application Assistant Agent with cover letter & portal form field drafting.

---

## [Phase 9] - 2026-08-14

### Added
- Resume Tailoring Agent, FactChecker anti-fabrication diff pass, ATS score estimator.

---

## [Phase 8] - 2026-08-14

### Added
- Skill Gap Agent with delta calculator, URL validation & domain flagging.

---

## [Phase 7] - 2026-08-14

### Added
- Hybrid Matching & Scoring Engine, LLM Top-20 Re-ranking Pass, GET /users/{id}/matches.

---

## [Phase 6] - 2026-08-14

### Added
- Discovery Agent with 3 mock sources, deduplication, and Celery beat periodic schedule.

---

## [Phase 5] - 2026-08-14

### Added
- Provider-Agnostic `LLMClient`, Resume Analysis Agent, Canonical Skill Taxonomy Normalizer (~200 skills), and 4 resume fixtures.

---

## [Phase 4] - 2026-08-14

### Added
- JWT Authentication System & Profile Management.

---

## [Phase 3] - 2026-08-14

### Added
- SQLAlchemy 2.0 ORM Models & Async Repository Pattern.

---

## [Phase 2] - 2026-08-14

### Added
- Monorepo Skeleton & Docker Infrastructure.

---

## [Phase 1] - 2026-08-14

### Added
- Multi-Agent Architecture Blueprint, ERD, REST API Surface Spec, ADRs 001-003.
