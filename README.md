# ScoutSphere 🚀
> **Multi-Agent AI Career Assistant Platform**

ScoutSphere is a $0 free-tier, open-source multi-agent career assistant platform that autonomously discovers relevant internships, hackathons, and jobs based on a student's skills, resume, and interests.

---

## 🛠️ Tech Stack & $0 Cost Floor Architecture

- **Backend**: Python 3.13, FastAPI, Pydantic v2, Async SQLAlchemy 2.0, Alembic
- **Agent Orchestration**: LangGraph stateful multi-agent graphs + LangChain core
- **LLM Provider Chain**: Unified `LLMClient` with rate-limit backoff & fallback chain:
  1. Google Gemini API free tier (`Gemini Flash`)
  2. Groq free tier (`Llama 3.x / Qwen`)
  3. OpenRouter free tier
  4. Local Ollama (`Llama 3.x`)
- **Database & Vectors**: PostgreSQL 17 + `pgvector` HNSW cosine similarity index
- **Task Queue**: Celery + Redis
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, TanStack Query
- **Deployment & Dev Container**: Docker Compose

---

## 📂 Project Monorepo Structure

```
ScoutSphere/
├── backend/          # FastAPI application, SQLAlchemy models, LangGraph agents, Celery worker
├── frontend/         # React 19 + TypeScript + Vite frontend UI dashboard
├── infra/            # Docker Compose orchestration & service Dockerfiles
├── docs/             # System Architecture, ERD, API Specs & ADRs
├── .env.example      # Master environment configuration template
└── CHANGELOG.md      # Phase release logs
```

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Setup Environment
```bash
cp .env.example .env
```

### 2. Launch Local Stack with Docker Compose
```bash
docker compose -f infra/docker-compose.yml up -d --build
```

### 3. Verify Local Services
- **React Frontend**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Local Testing & Verification Commands

### Run Backend Pytest Suite
```bash
cd backend
pytest -v
```

### Run Code Quality & Linting
```bash
# Backend checks
ruff check backend/
black --check backend/
mypy backend/

# Frontend checks
cd frontend
npm run lint
```

---

## 📖 Architecture Documentation
- [Multi-Agent Architecture Blueprint](file:///d:/Krish%20Sir/ScoutSphere/docs/architecture.md)
- [Database ERD & Schema Spec](file:///d:/Krish%20Sir/ScoutSphere/docs/erd.md)
- [REST API Specification](file:///d:/Krish%20Sir/ScoutSphere/docs/api-spec.md)
- [ADR 001: LangGraph Choice](file:///d:/Krish%20Sir/ScoutSphere/docs/adr/001-langgraph-over-function-calling.md)
- [ADR 002: pgvector Choice](file:///d:/Krish%20Sir/ScoutSphere/docs/adr/002-pgvector-over-separate-vectordb.md)
- [ADR 003: Hybrid Resume Parsing](file:///d:/Krish%20Sir/ScoutSphere/docs/adr/003-resume-parsing-approach.md)
