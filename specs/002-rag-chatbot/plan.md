# Implementation Plan: RAG Chatbot for Physical AI Course

**Branch**: `002-rag-chatbot` | **Date**: 2025-12-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-rag-chatbot/spec.md`
**Constitution**: `backend/.specify/memory/constitution.md` (v2.0.0)

## Summary

Build a production-ready RAG (Retrieval-Augmented Generation) chatbot that enables intelligent Q&A over Physical AI & Humanoid Robotics course content. The system consists of an isolated FastAPI backend with Cohere embeddings, Qdrant vector database, Neon PostgreSQL for session persistence, and a React-based chatbot UI integrated into the existing Docusaurus book frontend. ALL backend code resides in `/backend`, with ZERO modifications to existing book content (v1.x).

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/React 19 (frontend - already in Docusaurus)
**Primary Dependencies**:
- **Backend**: FastAPI, Qdrant Client, Cohere SDK, OpenAI/Anthropic SDK, Psycopg3/SQLAlchemy, Pydantic, Uvicorn
- **Frontend**: React 19 (Docusaurus), CSS Modules/styled-components, Fetch API/Axios

**Storage**:
- **Vector Store**: Qdrant (Docker local dev, Cloud for production)
- **Relational DB**: Neon PostgreSQL (session metadata, query logs - NO PII)
- **Frontend**: sessionStorage (conversation history)

**Testing**:
- **Backend**: pytest (unit + integration), httpx (API tests), pytest-cov (80% minimum coverage)
- **Frontend**: React Testing Library, Jest (Docusaurus default)

**Target Platform**:
- **Backend**: Linux server (Docker containerized), Python 3.11+ runtime
- **Frontend**: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

**Project Type**: Web application (isolated backend + embedded frontend component)

**Performance Goals**:
- < 5 seconds end-to-end query response time (95th percentile)
- < 10 seconds maximum latency (99th percentile)
- Support 10 concurrent users without degradation
- < 1 second Cohere embedding generation
- < 500ms Qdrant vector search

**Constraints**:
- Backend code ONLY in `/backend` (NO files in Docusaurus root, `src/`, `docs/`)
- Frontend components ONLY in `src/components/Chatbot/` (NO global CSS/theme changes)
- NO modifications to `/docs`, `/static`, existing pages, or `docusaurus.config.ts` (except chatbot import)
- Cohere API for embeddings (modular design for future replacement)
- Neon PostgreSQL for metadata (NO PII logging: no IPs, emails, device fingerprints)
- Docker containerization required for backend
- CORS whitelisting (Docusaurus domain only)
- Rate limiting: 10 requests/minute per session
- 80% minimum test coverage for backend

**Scale/Scope**:
- ~50-100 Markdown content files in `/docs`
- ~500-2000 content chunks in Qdrant
- 10-50 concurrent users (initial launch)
- Session-based history (no cross-session persistence)
- Single Qdrant collection: `course_content`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Backend Isolation (Constitution Section 3)
- ALL backend code in `/backend`: ✅ Confirmed in project structure
- No backend logic in Docusaurus root or `src/`: ✅ Enforced
- Mandatory backend folder structure defined: ✅ See Project Structure

### ✅ Frontend Isolation (Constitution Section 2)
- Chatbot UI ONLY in `src/components/Chatbot/`: ✅ Enforced
- NO global CSS, theme overrides, layout changes: ✅ Scoped CSS modules required
- NO changes to `/docs`, `/static`, existing pages: ✅ Gated in Phase 8 validation

### ✅ RAG Pipeline Principles (Constitution Section 4)
- Cohere embeddings (modular architecture): ✅ FR-032
- Qdrant vector DB (HNSW indexing): ✅ FR-006
- Top-k retrieval (top 5 chunks): ✅ FR-006
- Confidence threshold (0.6): ✅ FR-008
- Citation requirements: ✅ FR-009

### ✅ API Design & Standards (Constitution Section 5)
- Base path `/api/v1/`: ✅ Defined in endpoints
- Pydantic validation: ✅ FR-015, all models
- Rate limiting (10 req/min): ✅ FR-017
- CORS whitelisting: ✅ FR-019
- No hardcoded secrets: ✅ FR-018, `.env` only

### ✅ Content Ingestion Pipeline (Constitution Section 6)
- Source: `/docs` Markdown files: ✅ Confirmed
- Intelligent chunking with metadata: ✅ Phase 3
- Idempotent ingestion: ✅ Rerun without duplicates

### ✅ Testing & Quality (Constitution Section 7)
- 80% code coverage minimum: ✅ Backend testing enforced
- Unit + integration tests: ✅ pytest framework

### ✅ Spec-Kit Workflow (Constitution Section 8)
- 5-step cycle (Constitution → Spec → Plan → Tasks → Implementation): ✅ Currently in Phase 1 (Planning)
- No "vibe coding": ✅ Gated - must complete plan before tasks

### ✅ Code Quality (Constitution Section 9)
- Python type hints + mypy strict: ✅ Enforced in linting
- TypeScript strict mode: ✅ Enforced in `tsconfig.json`
- Black + Ruff formatting: ✅ Pre-commit hooks

### ✅ Database Abstraction (Constitution Section 4.2)
- Service layer for all DB access: ✅ FR-036
- No direct SQL in route handlers: ✅ Enforced

### ✅ PII Protection (Constitution Section 5.3)
- NO IP addresses, emails, device fingerprints: ✅ FR-037
- Session IDs only: ✅ Enforced

### ✅ Containerization (Constitution Section 10)
- Dockerfile in `/backend`: ✅ FR-039
- Docker Compose for local dev: ✅ FR-041
- Environment variable exposure: ✅ FR-042

**GATE RESULT**: ✅ **PASS** - All constitutional requirements satisfied

## Project Structure

### Documentation (this feature)

```text
specs/002-rag-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (current)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   ├── openapi.yaml     # REST API contract
│   └── examples/        # Request/response examples
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by plan)
```

### Source Code (repository root)

```text
# Backend (ALL backend code in /backend - Constitution Section 3)
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py            # POST /api/v1/chat
│   │   │   ├── health.py          # GET /api/v1/health
│   │   │   ├── ingest.py          # POST /api/v1/ingest (admin)
│   │   │   └── stats.py           # GET /api/v1/collections/stats
│   │   └── dependencies.py        # Shared dependencies (DB session, API keys)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Environment variables (Pydantic Settings)
│   │   ├── middleware.py          # CORS, rate limiting, logging
│   │   └── security.py            # Input sanitization, API key validation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py             # ChatRequest, IngestRequest (Pydantic)
│   │   ├── response.py            # ChatResponse, Citation (Pydantic)
│   │   └── database.py            # SQLAlchemy ORM models (sessions, logs)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embeddings.py          # Cohere embedding generation
│   │   ├── llm.py                 # OpenAI/Anthropic LLM client
│   │   ├── qdrant.py              # Qdrant client & operations
│   │   ├── rag.py                 # RAG orchestration (retrieve + generate)
│   │   ├── database.py            # Neon PostgreSQL service layer
│   │   └── ingestion.py           # Content parsing & ingestion
│   └── utils/
│       ├── __init__.py
│       ├── chunking.py            # Text chunking logic
│       └── validators.py          # URL validation, text sanitization
├── data/
│   ├── qdrant/                    # Qdrant persistence (gitignored)
│   └── raw/                       # Optional: cached parsed content
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── unit/
│   │   ├── test_embeddings.py
│   │   ├── test_rag.py
│   │   └── test_chunking.py
│   ├── integration/
│   │   ├── test_api_endpoints.py
│   │   └── test_ingestion_pipeline.py
│   └── contract/
│       └── test_openapi_contract.py
├── scripts/
│   ├── __init__.py
│   └── run_ingestion.py           # Standalone ingestion runner
├── .env.example                   # Environment variables template
├── .gitignore
├── Dockerfile
├── docker-compose.yml             # Local dev (FastAPI + Qdrant)
├── pyproject.toml                 # Poetry dependencies
├── requirements.txt               # Pip-compatible (generated)
├── README.md                      # Backend-specific docs
└── .specify/
    └── memory/
        └── constitution.md        # v2.0.0 backend constitution

# Frontend (chatbot UI ONLY - Constitution Section 2)
src/
└── components/
    └── Chatbot/
        ├── ChatWidget.tsx         # Main chatbot component
        ├── FloatingActionButton.tsx   # FAB component
        ├── ChatWindow.tsx         # Chat window with messages
        ├── ChatMessage.tsx        # Individual message bubble
        ├── ChatInput.tsx          # Input field + send button
        ├── TypingIndicator.tsx    # Animated typing dots
        ├── TextSelectionHandler.tsx   # Text selection context menu
        ├── ChatWidget.module.css  # Scoped styles (NO global CSS)
        ├── types.ts               # TypeScript interfaces
        ├── useChatbot.ts          # React hook for API calls
        └── __tests__/
            ├── ChatWidget.test.tsx
            └── useChatbot.test.ts

# Existing Docusaurus structure (UNTOUCHED - Constitution Section 2)
docs/                              # Course content (source for ingestion)
static/                            # Static assets (untouched)
docusaurus.config.ts               # May add ChatWidget import only
sidebars.ts                        # Untouched
```

**Structure Decision**: Web application with isolated backend. Backend follows FastAPI best practices with clear separation of concerns (api/, core/, models/, services/). Frontend is a minimal React component integrated into existing Docusaurus without modifying book content. Docker containerization for backend only (frontend built via Docusaurus).

## Complexity Tracking

**NO VIOLATIONS DETECTED** - All constitution requirements satisfied without complexity trade-offs.

---

## Phase 0: Research & Technology Selection

**Goal**: Resolve all technical unknowns and establish implementation patterns for RAG pipeline, Cohere integration, Neon PostgreSQL schema, and Docker setup.

### Research Tasks

#### R1: Cohere Embedding API Integration
**Question**: What are the best practices for using Cohere embeddings API with Python? What are the rate limits, batch processing capabilities, and error handling patterns?

**Research Scope**:
- Cohere Python SDK usage (`cohere.Client`)
- Embedding model selection (`embed-english-v3.0` vs `embed-multilingual-v3.0`)
- Batch embedding limits (how many texts per API call)
- Rate limiting and retry strategies
- Cost optimization (caching embeddings for duplicate queries)
- Error codes and handling (API down, rate limit, invalid input)

**Deliverable**: Document Cohere integration pattern with code examples in `research.md`

---

#### R2: Qdrant Vector Database Operations
**Question**: How to design Qdrant collections for course content with metadata filtering and optimal retrieval performance?

**Research Scope**:
- Collection creation with payload schema (`chapter`, `section`, `url`, `chunk_id`)
- HNSW index configuration (M, ef_construct parameters for < 500ms search)
- Vector search with metadata filtering (e.g., retrieve only from specific chapters)
- Batch upsert strategies for ingestion
- Backup and recovery patterns
- Local Docker vs Qdrant Cloud setup differences

**Deliverable**: Document Qdrant schema design and best practices in `research.md`

---

#### R3: Neon PostgreSQL Schema Design
**Question**: What is the optimal schema for storing chat session metadata and query logs in Neon PostgreSQL with minimal latency and NO PII?

**Research Scope**:
- Table design for `chat_sessions` and `query_logs`
- Indexes for fast lookups by `session_id` and timestamp range queries
- Connection pooling (psycopg3 vs SQLAlchemy async)
- Graceful degradation when Neon is unavailable (FR-038)
- Data retention policies (automatic cleanup of old logs)
- Neon-specific optimizations (serverless PostgreSQL features)

**Deliverable**: Document Neon schema and connection patterns in `research.md`

---

#### R4: FastAPI + LLM Streaming Integration
**Question**: How to implement streaming LLM responses through FastAPI with proper error handling and connection management?

**Research Scope**:
- FastAPI `StreamingResponse` with async generators
- OpenAI streaming API (`stream=True`)
- Anthropic streaming API (if using Claude)
- Frontend consumption of SSE (Server-Sent Events)
- Error handling mid-stream (LLM timeout, connection drop)
- Token counting and rate limit tracking

**Deliverable**: Document streaming pattern with code examples in `research.md`

---

#### R5: Text Chunking Strategies for RAG
**Question**: What chunking strategy maximizes retrieval quality for educational content (textbook chapters with headings, code blocks, diagrams)?

**Research Scope**:
- Heading-based chunking (split by `##` Markdown headings)
- Semantic chunking (sentence-transformers or LangChain)
- Chunk size optimization (512 tokens vs 1024 tokens)
- Overlap strategies (50 token overlap between chunks)
- Metadata preservation (chapter, section, URL from frontmatter)
- Handling edge cases (code blocks, Mermaid diagrams, math equations)

**Deliverable**: Document chunking strategy with algorithm in `research.md`

---

#### R6: Docker Containerization for FastAPI
**Question**: What is the optimal Dockerfile and docker-compose.yml structure for FastAPI + Qdrant local development?

**Research Scope**:
- Multi-stage Docker build (builder + runtime)
- Python base image selection (python:3.11-slim vs alpine)
- Dependency caching (Poetry layer caching)
- Environment variable injection (.env file vs docker-compose environment)
- Health checks for FastAPI service
- docker-compose orchestration (FastAPI, Qdrant, optional Neon proxy)

**Deliverable**: Document Docker setup patterns in `research.md`

---

#### R7: React Text Selection Detection
**Question**: How to implement robust text selection detection and context menu rendering in React without breaking Docusaurus?

**Research Scope**:
- `window.getSelection()` API usage
- Context menu positioning (avoid going off-screen)
- Mobile text selection handling (iOS Safari, Android Chrome)
- Integration with Docusaurus without global event listeners
- Accessibility considerations (keyboard navigation)

**Deliverable**: Document text selection pattern with React hooks in `research.md`

---

#### R8: Rate Limiting Implementation
**Question**: What rate limiting strategy works best for FastAPI with per-session tracking (not per-IP)?

**Research Scope**:
- slowapi library vs custom middleware
- Session-based rate limiting (session ID from cookies/headers)
- Redis vs in-memory rate limit storage
- Graceful rate limit responses (429 with Retry-After header)
- Bypassing rate limits for admin endpoints

**Deliverable**: Document rate limiting implementation in `research.md`

---

### Research Consolidation

**Output File**: `specs/002-rag-chatbot/research.md`

**Structure**:
```markdown
# Research: RAG Chatbot Implementation

## R1: Cohere Embedding API Integration
**Decision**: [Selected approach]
**Rationale**: [Why chosen]
**Alternatives Considered**: [Other options]
**Implementation Pattern**: [Code example]

## R2: Qdrant Vector Database Operations
[Same structure]

...

## Summary of Technology Choices
- Embedding: Cohere `embed-english-v3.0`
- Vector DB: Qdrant Cloud (production), Docker (local)
- Relational DB: Neon PostgreSQL with psycopg3
- LLM: [OpenAI GPT-4 / Anthropic Claude 3.5 Sonnet - specify choice]
- Chunking: [Heading-based / Semantic - specify choice]
- Rate Limiting: [slowapi / Custom - specify choice]
```

---

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete with all technology decisions finalized

### Task 1.1: Data Model Design

**Output File**: `specs/002-rag-chatbot/data-model.md`

**Content**:

#### Entity 1: Chat Session (Neon PostgreSQL)
```sql
CREATE TABLE chat_sessions (
  session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  message_count INTEGER DEFAULT 0
);

CREATE INDEX idx_sessions_last_activity ON chat_sessions(last_activity_at);
```

**Validation Rules**:
- `session_id`: Must be valid UUID v4
- `message_count`: Must be >= 0
- `last_activity_at`: Must be >= `started_at`

**State Transitions**: Active → Idle (30min timeout) → Archived (24hr cleanup)

---

#### Entity 2: Query Log (Neon PostgreSQL)
```sql
CREATE TABLE query_logs (
  log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES chat_sessions(session_id),
  query_text TEXT NOT NULL,
  response_text_truncated TEXT, -- First 500 chars
  confidence_score DECIMAL(3,2),
  retrieval_latency_ms INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_logs_session ON query_logs(session_id);
CREATE INDEX idx_logs_created_at ON query_logs(created_at);
```

**Validation Rules**:
- `query_text`: Max 2000 chars, no PII
- `confidence_score`: Between 0.0 and 1.0
- NO `user_ip`, NO `user_agent`, NO `email` (PII protection)

---

#### Entity 3: Content Chunk (Qdrant Payload)
```json
{
  "chunk_id": "string (UUID)",
  "source_file": "string (docs/01-intro/perception-action-loop.md)",
  "chapter": "string (Module 1: Physical AI Foundations)",
  "section": "string (Understanding the Perception-Action Loop)",
  "url": "string (/docs/01-intro/perception-action-loop)",
  "raw_text": "string (chunk content)",
  "token_count": "integer"
}
```

**Validation Rules**:
- `chunk_id`: Must be unique across collection
- `url`: Must start with `/docs/` and be valid
- `token_count`: Must be <= 512 (chunking constraint)

---

#### Entity 4: ChatRequest (Pydantic)
```python
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[UUID] = None
    selected_text: Optional[str] = Field(None, max_length=500)
    top_k: int = Field(5, ge=1, le=10)
```

---

#### Entity 5: ChatResponse (Pydantic)
```python
class Citation(BaseModel):
    chapter: str
    section: str
    url: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: float = Field(..., ge=0.0, le=1.0)
    session_id: UUID
```

---

### Task 1.2: API Contracts (OpenAPI)

**Output File**: `specs/002-rag-chatbot/contracts/openapi.yaml`

**Endpoints**:

#### POST /api/v1/chat
```yaml
summary: Send a query and receive RAG-powered answer
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ChatRequest'
responses:
  200:
    description: Successful response with answer and citations
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ChatResponse'
  400:
    description: Invalid request (empty query, query too long)
  429:
    description: Rate limit exceeded
  500:
    description: Internal server error (LLM/Qdrant unavailable)
```

#### GET /api/v1/health
```yaml
summary: Health check endpoint
responses:
  200:
    description: System is healthy
    content:
      application/json:
        schema:
          type: object
          properties:
            status: {type: string, enum: [healthy, degraded, unhealthy]}
            version: {type: string}
            qdrant_status: {type: string}
            llm_status: {type: string}
            database_status: {type: string}
```

#### POST /api/v1/ingest (Admin)
```yaml
summary: Trigger content re-ingestion (requires admin API key)
security:
  - ApiKeyAuth: []
responses:
  200:
    description: Ingestion completed
    content:
      application/json:
        schema:
          type: object
          properties:
            status: {type: string}
            chunks_ingested: {type: integer}
            duration_seconds: {type: number}
  401:
    description: Invalid or missing API key
  500:
    description: Ingestion failed
```

**Security Scheme**:
```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
```

---

### Task 1.3: Quickstart Guide

**Output File**: `specs/002-rag-chatbot/quickstart.md`

**Content**:
```markdown
# RAG Chatbot Quickstart

## Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Node.js 20+ (for Docusaurus)
- API Keys: Cohere, OpenAI/Anthropic, Neon PostgreSQL

## Backend Setup (5 minutes)

1. Navigate to backend:
   cd backend

2. Install dependencies:
   poetry install
   # OR
   pip install -r requirements.txt

3. Configure environment:
   cp .env.example .env
   # Edit .env with your API keys

4. Start Qdrant (local):
   docker-compose up -d qdrant

5. Run ingestion:
   python scripts/run_ingestion.py

6. Start FastAPI:
   uvicorn app.main:app --reload --port 8000

7. Test health endpoint:
   curl http://localhost:8000/api/v1/health

## Frontend Setup (2 minutes)

1. Navigate to project root:
   cd ..

2. Start Docusaurus:
   yarn start

3. Open http://localhost:3000
4. Click the chatbot FAB (bottom-right)
5. Ask: "What is the Perception-Action Loop?"

## Docker Setup (1-step alternative)

   cd backend && docker-compose up

   This starts FastAPI + Qdrant together.
   Visit http://localhost:8000/docs for Swagger UI.
```

---

### Task 1.4: Agent Context Update

Run the agent context update script to add new technologies:

```bash
.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

**Technologies to Add**:
- Cohere Python SDK (`cohere`)
- Qdrant Client (`qdrant-client`)
- Neon PostgreSQL (`psycopg3`)
- FastAPI (`fastapi`)
- Pydantic v2 (`pydantic`)

**Preserve**: All existing manual additions between `<!-- MANUAL ADDITIONS START -->` and `<!-- MANUAL ADDITIONS END -->` markers

---

## Phase 2: Implementation Tasks (Deferred to /speckit.tasks)

**Note**: Detailed implementation tasks are generated by the `/speckit.tasks` command after this plan is approved. The tasks will be broken down into atomic, testable units following the structure defined in this plan.

**Task Categories** (preview):
1. Backend Foundation (create `/backend`, FastAPI setup, `.env`)
2. Database Setup (Neon schema, Qdrant collection, service layers)
3. Content Ingestion (chunking, embedding, Qdrant upsert)
4. RAG Pipeline (retrieval, LLM integration, guardrails)
5. API Endpoints (chat, health, ingest, error handling)
6. Frontend Components (FAB, ChatWindow, API client)
7. Docker & Deployment (Dockerfile, docker-compose.yml)
8. Testing (unit, integration, contract tests)
9. Validation & Safety (isolation checks, out-of-scope testing)

---

## Post-Phase 1 Constitution Re-Check

### ✅ Backend Isolation (Section 3)
- Project structure confirms all backend code in `/backend`: ✅
- No backend files in Docusaurus folders: ✅

### ✅ Frontend Isolation (Section 2)
- Chatbot components scoped to `src/components/Chatbot/`: ✅
- CSS modules prevent global style pollution: ✅

### ✅ RAG Pipeline (Section 4)
- Cohere embedding with modular design: ✅
- Qdrant HNSW index configuration: ✅
- Confidence threshold (0.6) enforced in RAG service: ✅

### ✅ API Design (Section 5)
- OpenAPI contract defines `/api/v1/*` endpoints: ✅
- Pydantic models for all requests/responses: ✅
- Rate limiting via middleware: ✅
- CORS whitelisting configured: ✅

### ✅ Database Abstraction (Section 4.2)
- Service layer (`services/database.py`) abstracts Neon access: ✅
- No direct SQL in route handlers: ✅

### ✅ PII Protection (Section 5.3)
- Neon schema excludes IP, email, user_agent: ✅
- Only `session_id` (UUID) stored: ✅

### ✅ Testing Coverage (Section 7)
- Test structure includes unit, integration, contract folders: ✅
- pytest + pytest-cov configured for 80% minimum: ✅

**GATE RESULT**: ✅ **PASS** - Design satisfies all constitutional requirements

---

## Next Steps

1. **Review this plan** for accuracy and completeness
2. **Run Phase 0 research** to generate `research.md` (can be done manually or via research agents)
3. **Run Phase 1 design** to generate `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`
4. **Approve the plan** before proceeding to `/speckit.tasks`
5. **Generate tasks** via `/speckit.tasks` command (creates `tasks.md` with atomic implementation steps)

**Current Status**: Planning phase complete. Awaiting approval to proceed to Phase 0 (Research) and Phase 1 (Design).

**Files Generated by This Plan**:
- ✅ `specs/002-rag-chatbot/plan.md` (this file)
- ⏳ `specs/002-rag-chatbot/research.md` (Phase 0 - to be generated)
- ⏳ `specs/002-rag-chatbot/data-model.md` (Phase 1 - to be generated)
- ⏳ `specs/002-rag-chatbot/quickstart.md` (Phase 1 - to be generated)
- ⏳ `specs/002-rag-chatbot/contracts/openapi.yaml` (Phase 1 - to be generated)
- ⏳ `specs/002-rag-chatbot/tasks.md` (Phase 2 - generated by `/speckit.tasks`)

**Branch**: `002-rag-chatbot`
**Ready for**: Phase 0 (Research) → Phase 1 (Design) → `/speckit.tasks`
