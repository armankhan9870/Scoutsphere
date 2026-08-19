# ScoutSphere - REST API Specification

## Base URL
`/api/v1`

---

## Resource Endpoint Overview

| Resource | Base Path | Description |
| :--- | :--- | :--- |
| **Auth** | `/auth` | Authentication, token creation, refresh, and user context |
| **Users** | `/users` | Profile information, target roles, and skill management |
| **Resumes** | `/resumes` | Resume upload, async parsing, vectorization, and retrieval |
| **Opportunities** | `/opportunities` | Searching, filtering, scraping, and detailed view of opportunities |
| **Matches** | `/matches` | User-opportunity vector scoring, fit calculations, and re-ranking |
| **Skill Gaps** | `/skill-gaps` | Detailed gap analysis and learning path recommendations |
| **Applications** | `/applications` | Application tracking pipeline, cover letter drafting, status logs |
| **Chat** | `/chat` | Conversational RAG session and message streaming APIs |
| **Roadmap** | `/roadmap` | Multi-step career roadmap generation and milestone tracking |

---

## 1. Auth Endpoint (`/auth`)

### `POST /auth/register`
Creates a new user account.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "Jane Doe",
    "target_roles": ["Backend Engineer", "AI Engineer"]
  }
  ```
- **Response `201 Created`**:
  ```json
  {
    "id": "uuid-v4",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "access_token": "jwt_token_string",
    "refresh_token": "jwt_refresh_string",
    "token_type": "bearer"
  }
  ```

### `POST /auth/login`
Authenticates existing credentials and returns JWT pair.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "access_token": "jwt_access_string",
    "refresh_token": "jwt_refresh_string",
    "token_type": "bearer"
  }
  ```

### `POST /auth/refresh`
Refreshes expired access tokens using a valid refresh token.
- **Request Body**: `{"refresh_token": "jwt_refresh_string"}`
- **Response `200 OK`**: `{"access_token": "new_jwt_access_string"}`

---

## 2. Users Endpoint (`/users`)

### `GET /users/me`
Retrieves authenticated user profile.
- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**:
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "target_roles": ["Backend Engineer"],
    "location_preference": "Remote",
    "skills": [
      {"name": "Python", "category": "Languages", "proficiency_level": "Advanced"},
      {"name": "FastAPI", "category": "Frameworks", "proficiency_level": "Intermediate"}
    ]
  }
  ```

### `PUT /users/me`
Updates user preferences and skills.
- **Request Body**:
  ```json
  {
    "full_name": "Jane Doe",
    "target_roles": ["Full-Stack Engineer", "AI Developer"],
    "location_preference": "Hybrid"
  }
  ```
- **Response `200 OK`**: Updated profile object.

---

## 3. Resumes Endpoint (`/resumes`)

### `POST /resumes/upload`
Uploads a PDF resume file and triggers asynchronous parsing and vector embedding.
- **Content-Type**: `multipart/form-data`
- **Form Field**: `file` (PDF document)
- **Response `202 Accepted`**:
  ```json
  {
    "resume_id": "uuid",
    "task_id": "celery-task-id",
    "status": "PROCESSING",
    "message": "Resume uploaded successfully. Analysis enqueued."
  }
  ```

### `GET /resumes/{id}`
Fetches parsed resume details and processing status.
- **Response `200 OK`**:
  ```json
  {
    "id": "uuid",
    "status": "READY",
    "parsed_data": {
      "skills": ["Python", "Docker", "PostgreSQL", "LangChain"],
      "experience": [
        {
          "company": "Tech Corp",
          "role": "Software Developer Intern",
          "duration": "6 months",
          "summary": "Built FastAPI backend endpoints and Celery pipelines."
        }
      ],
      "education": [{"institution": "State University", "degree": "B.S. CS"}]
    },
    "created_at": "2026-08-14T02:50:00Z"
  }
  ```

---

## 4. Opportunities Endpoint (`/opportunities`)

### `GET /opportunities/search`
Searches and filters job, internship, and hackathon listings.
- **Query Parameters**:
  - `query` (optional): search string
  - `type` (optional): `JOB`, `INTERNSHIP`, `HACKATHON`
  - `is_remote` (optional): boolean
  - `limit`: integer (default 20)
  - `offset`: integer (default 0)
- **Response `200 OK`**:
  ```json
  {
    "total": 42,
    "items": [
      {
        "id": "uuid",
        "title": "AI/ML Intern",
        "company_name": "Innovate Lab",
        "opportunity_type": "INTERNSHIP",
        "location": "Remote",
        "is_remote": true,
        "required_skills": ["Python", "PyTorch", "FastAPI"],
        "source_url": "https://example.com/jobs/123",
        "deadline": "2026-09-30T00:00:00Z"
      }
    ]
  }
  ```

### `POST /opportunities/crawl`
Triggers the Discovery Agent to scrape/fetch fresh listings.
- **Request Body**: `{"keywords": ["LangGraph", "FastAPI"], "types": ["INTERNSHIP"]}`
- **Response `202 Accepted`**: `{"task_id": "celery-task-id", "status": "QUEUED"}`

---

## 5. Matches Endpoint (`/matches`)

### `GET /matches/recommended`
Retrieves top-ranked opportunity matches for the authenticated user using hybrid vector cosine similarity + skill overlap re-ranking.
- **Query Parameters**: `limit` (default 10)
- **Response `200 OK`**:
  ```json
  [
    {
      "match_id": "uuid",
      "opportunity": {
        "id": "uuid",
        "title": "Backend AI Developer",
        "company_name": "ScoutSphere Inc"
      },
      "fit_score": 0.89,
      "skill_overlap_score": 0.85,
      "match_reasons": [
        "Strong experience with Python and FastAPI",
        "High semantic overlap in backend resume projects"
      ]
    }
  ]
  ```

---

## 6. Skill Gaps Endpoint (`/skill-gaps`)

### `GET /skill-gaps/{opportunity_id}`
Triggers or retrieves a skill gap report comparing user skills against opportunity requirements.
- **Response `200 OK`**:
  ```json
  {
    "opportunity_id": "uuid",
    "missing_skills": ["Docker", "Kubernetes"],
    "match_impact_score": 0.15,
    "recommended_resources": [
      {
        "skill": "Docker",
        "title": "Docker Beginner to Advanced Guide",
        "url": "https://docs.docker.com/get-started/"
      }
    ]
  }
  ```

---

## 7. Applications Endpoint (`/applications`)

### `POST /applications`
Creates a new tracked application entry.
- **Request Body**:
  ```json
  {
    "opportunity_id": "uuid",
    "status": "APPLIED",
    "notes": "Applied on company portal"
  }
  ```
- **Response `201 Created`**: Application model with default pipeline state.

### `POST /applications/{id}/cover-letter`
Drafts a personalized cover letter using the Application Assistant Agent.
- **Response `200 OK`**:
  ```json
  {
    "application_id": "uuid",
    "cover_letter": "Dear Hiring Manager, I am excited to apply..."
  }
  ```

### `PATCH /applications/{id}/status`
Updates application pipeline status and logs transition history.
- **Request Body**: `{"status": "INTERVIEWING", "notes": "First round scheduled"}`
- **Response `200 OK`**: Updated application object.

---

## 8. Chat & Roadmap Endpoints (`/chat`, `/roadmap`)

### `POST /chat/sessions`
Creates a new chat session.
- **Response `201 Created`**: `{"session_id": "uuid", "title": "New Career Conversation"}`

### `POST /chat/sessions/{id}/messages`
Sends a message to the RAG Career Chatbot and receives a response.
- **Request Body**: `{"content": "How can I prepare for a FastAPI backend interview?"}`
- **Response `200 OK`**:
  ```json
  {
    "id": "uuid",
    "sender_role": "assistant",
    "content": "To prepare for FastAPI interviews, focus on pydantic models, async engine, dependency injection...",
    "context_metadata": {"retrieved_chunks": 3}
  }
  ```

### `POST /roadmap/generate`
Generates a multi-milestone career roadmap based on target role.
- **Request Body**: `{"target_role": "Senior AI Systems Engineer"}`
- **Response `200 OK`**:
  ```json
  {
    "roadmap_id": "uuid",
    "target_role": "Senior AI Systems Engineer",
    "milestones": [
      {"phase": "Phase 1", "title": "Master Python Async & FastAPI", "duration": "4 weeks"},
      {"phase": "Phase 2", "title": "Build Multi-Agent Graphs with LangGraph", "duration": "6 weeks"}
    ]
  }
  ```
