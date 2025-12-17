# Tasks: RAG Chatbot for Physical AI Course

**Input**: Design documents from `/specs/002-rag-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)
**Constitution**: `backend/.specify/memory/constitution.md` (v2.0.0)

**Tests**: NOT included in this implementation (no TDD requirement in spec). Testing tasks can be added later if needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. The backend is completely isolated in `/backend`, and frontend components live only in `src/components/Chatbot/`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `src/components/Chatbot/`
- **Existing Docusaurus**: `docs/`, `static/`, `docusaurus.config.ts` (MUST NOT BE MODIFIED except minimal chatbot import)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, backend scaffolding, and environment setup

- [X] T001 Create `/backend` directory at project root
- [X] T002 Create backend folder structure: `backend/app/{__init__.py,main.py,api/,core/,models/,services/,utils/}`
- [X] T003 [P] Create backend subdirectories: `backend/app/api/v1/{__init__.py}`, `backend/app/core/{__init__.py}`, `backend/app/models/{__init__.py}`, `backend/app/services/{__init__.py}`, `backend/app/utils/{__init__.py}`
- [X] T004 [P] Create additional backend directories: `backend/tests/{__init__.py,unit/,integration/,contract/}`, `backend/scripts/{__init__.py}`, `backend/data/{qdrant/,raw/}`
- [X] T005 Create `backend/pyproject.toml` with Poetry dependencies (FastAPI, Qdrant Client, Cohere SDK, Psycopg3, Pydantic, Uvicorn, pytest, black, ruff, mypy)
- [X] T006 Create `backend/requirements.txt` generated from `pyproject.toml` (for pip compatibility)
- [X] T007 Create `backend/.gitignore` (exclude `.env`, `data/qdrant/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`)
- [X] T008 Update existing `backend/.env.example` to ensure all required variables are present (COHERE_API_KEY, DATABASE_URL, QDRANT_URL, OPENAI_API_KEY or ANTHROPIC_API_KEY, ADMIN_API_KEY, CORS_ORIGINS)
- [X] T009 [P] Create `backend/README.md` documenting setup and architecture
- [X] T010 [P] Create `src/components/Chatbot/` directory for frontend components

**Checkpoint**: Backend structure created, dependencies defined, ready for foundational infrastructure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Configuration & Core Setup

- [X] T011 Implement `backend/app/core/config.py` using Pydantic Settings to load environment variables (Cohere, Qdrant, Neon, LLM, CORS, admin keys)
- [X] T012 [P] Implement `backend/app/core/security.py` for input sanitization (XSS prevention, whitespace validation)
- [X] T013 [P] Implement `backend/app/core/middleware.py` for CORS whitelisting, rate limiting (10 req/min per session), request logging

### Database Layer (Neon PostgreSQL)

- [X] T014 Create Neon PostgreSQL schema in `backend/app/models/database.py` using SQLAlchemy (tables: `chat_sessions`, `query_logs` with NO PII fields)
- [X] T015 Implement `backend/app/services/database.py` service layer with methods: `create_session()`, `log_query()`, `get_session()`, handle Neon unavailability gracefully

### Vector Store (Qdrant)

- [X] T016 Implement `backend/app/services/qdrant.py` Qdrant client initialization from config, create collection `course_content` with HNSW indexing
- [X] T017 Add Qdrant operations in `backend/app/services/qdrant.py`: `upsert_chunks(List[Dict])`, `search_similar(query_vector, top_k=5, metadata_filter=None)`, handle Qdrant unavailability

### Embeddings (Cohere)

- [X] T018 Implement `backend/app/services/embeddings.py` Cohere client initialization, `generate_embedding(text: str) -> List[float]` with error handling, modular design for future provider replacement

### LLM Client

- [X] T019 Implement `backend/app/services/llm.py` LLM client (OpenAI or Anthropic) with `generate_response(prompt: str, context: str) -> str`, streaming support optional, rate limit handling

### Pydantic Models

- [X] T020 [P] Create `backend/app/models/request.py` with `ChatRequest(query, session_id, selected_text, top_k)`, `IngestRequest()` using Pydantic Field validation
- [X] T021 [P] Create `backend/app/models/response.py` with `Citation(chapter, section, url, relevance_score)`, `ChatResponse(answer, citations, confidence, session_id)`, `HealthResponse(status, version, qdrant_status, llm_status, database_status)`

### FastAPI Base

- [X] T022 Implement `backend/app/main.py` FastAPI application initialization, include middleware from T013, mount `/api/v1/` router
- [X] T023 Create `backend/app/api/v1/__init__.py` API router aggregator
- [X] T024 [P] Implement `backend/app/api/v1/health.py` with `GET /api/v1/health` endpoint returning system health (Qdrant, LLM, Neon status)
- [X] T025 Create `backend/app/api/dependencies.py` for shared dependencies (DB session, config, API key validation)

### Content Utilities

- [X] T026 Implement `backend/app/utils/chunking.py` with `chunk_markdown(file_path: str, max_tokens=512, overlap=50) -> List[Dict]` preserving metadata (chapter, section, URL from frontmatter)
- [X] T027 [P] Implement `backend/app/utils/validators.py` with `validate_url(url: str) -> bool`, `sanitize_text(text: str) -> str`, URL validation for citations

**Checkpoint**: Foundation ready - all services, models, and infrastructure in place. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Basic Q&A Interaction (Priority: P1) 🎯 MVP

**Goal**: Enable students to click a chatbot FAB, ask questions, and receive RAG-powered answers with citations. This is the minimum viable chatbot.

**Independent Test**: Open chatbot, type "What is the Perception-Action Loop?", verify response includes accurate information with chapter citations.

### Backend Implementation for US1

- [X] T028 [US1] Implement `backend/app/services/ingestion.py` with `parse_docs_folder(docs_path: str) -> List[Dict]` reading Markdown files from `/docs`, extracting frontmatter metadata
- [X] T029 [US1] Add `embed_and_store(chunks: List[Dict])` in `backend/app/services/ingestion.py` calling Cohere embeddings service (T018) and Qdrant upsert (T017), make idempotent
- [X] T030 [US1] Create `backend/scripts/run_ingestion.py` standalone script to run ingestion pipeline (`parse_docs_folder` → `chunk_markdown` → `embed_and_store`), handle errors gracefully
- [X] T031 [US1] Implement `backend/app/services/rag.py` with `retrieve(query: str, top_k=5) -> List[Dict]`: generate query embedding (T018), search Qdrant (T017), return chunks with metadata
- [X] T032 [US1] Add `generate_answer(query: str, chunks: List[Dict]) -> ChatResponse` in `backend/app/services/rag.py`: assemble prompt with chunks, call LLM (T019), extract citations from chunks, return ChatResponse with confidence score
- [X] T033 [US1] Implement `POST /api/v1/chat` in `backend/app/api/v1/chat.py`: accept `ChatRequest`, call RAG service (T031, T032), log to Neon (T015), return `ChatResponse`, handle errors (Qdrant/LLM down)
- [X] T034 [US1] Add session creation logic in `backend/app/api/v1/chat.py`: if `session_id` is None, create new session in Neon (T015), return in response

### Frontend Implementation for US1

- [X] T035 [P] [US1] Create `src/components/Chatbot/types.ts` with TypeScript interfaces (`Message`, `ChatSession`, `Citation`)
- [X] T036 [P] [US1] Implement `src/components/Chatbot/FloatingActionButton.tsx` FAB component (56x56px, bottom-right fixed, toggle onClick)
- [X] T037 [P] [US1] Implement `src/components/Chatbot/ChatWindow.tsx` chat window component (slide-up animation 300ms, fade-out 200ms, close button)
- [X] T038 [P] [US1] Implement `src/components/Chatbot/ChatMessage.tsx` message bubble component (distinct styles for user vs bot, citations as clickable links)
- [X] T039 [P] [US1] Implement `src/components/Chatbot/ChatInput.tsx` input field component (disable send on empty/whitespace, Enter to send, clear after send)
- [X] T040 [P] [US1] Implement `src/components/Chatbot/TypingIndicator.tsx` animated typing dots component
- [X] T041 [P] [US1] Create `src/components/Chatbot/ChatWidget.module.css` scoped CSS styles (NO global CSS), animations for open/close, message fade-in (150ms)
- [X] T042 [US1] Implement `src/components/Chatbot/useChatbot.ts` React hook: API client for `/api/v1/chat`, state management (messages, isOpen, isLoading), session storage for history, error handling
- [X] T043 [US1] Implement `src/components/Chatbot/ChatWidget.tsx` main component: compose FAB, ChatWindow, ChatMessage, ChatInput, TypingIndicator, wire up useChatbot hook
- [X] T044 [US1] Integrate ChatWidget into Docusaurus: add minimal import in `docusaurus.config.ts` or create theme override in `src/theme/Root.tsx` (MUST NOT modify existing pages or book content)

**Checkpoint**: User Story 1 fully functional - users can ask questions and get RAG-powered answers with citations. MVP complete!

---

## Phase 4: User Story 2 - Text Selection Explanation (Priority: P2)

**Goal**: Enable students to highlight text on a page and ask the chatbot to explain it without typing a full question.

**Independent Test**: Select text "inverse kinematics", click context menu "Ask Chatbot", verify chatbot opens with pre-filled query "Explain: inverse kinematics".

### Backend Implementation for US2

- [X] T045 [US2] Update `POST /api/v1/chat` in `backend/app/api/v1/chat.py` to handle `selected_text` field from `ChatRequest`: if present, prepend "Explain: {selected_text}" to query, truncate to 500 chars if > 1000 chars (FR-014)

### Frontend Implementation for US2

- [X] T046 [P] [US2] Implement `src/components/Chatbot/TextSelectionHandler.tsx` component: listen for `mouseup` event, detect selection with `window.getSelection()`, show context menu/tooltip with "Ask Chatbot about this" button
- [X] T047 [US2] Add context menu positioning logic in `TextSelectionHandler.tsx`: avoid going off-screen, handle mobile touch selection (iOS Safari, Android Chrome)
- [X] T048 [US2] Update `src/components/Chatbot/useChatbot.ts` hook: add `openWithSelectedText(text: string)` method that opens chatbot, pre-fills input with "Explain: {text}", focus input
- [X] T049 [US2] Integrate `TextSelectionHandler.tsx` into `ChatWidget.tsx`: render alongside FAB, wire to `openWithSelectedText` method
- [X] T050 [US2] Update `ChatInput.tsx` to support pre-filled query prop, allow users to edit before sending

**Checkpoint**: User Story 2 complete - text selection feature working independently, enhances US1 functionality.

---

## Phase 5: User Story 3 - Out-of-Scope Handling (Priority: P3)

**Goal**: Gracefully reject out-of-scope questions with standard fallback message.

**Independent Test**: Ask "What's the capital of France?", verify exact fallback: "I cannot provide information related to this topic. However, if you have any queries regarding the 'Physical AI & Humanoid Robotics' book, let me know — I am here to assist you."

### Backend Implementation for US3

- [X] T051 [US3] Add `check_confidence(chunks: List[Dict]) -> float` method in `backend/app/services/rag.py`: calculate average relevance score from top chunks
- [X] T052 [US3] Update `generate_answer()` in `backend/app/services/rag.py`: if confidence < 0.6 (FR-008), return `ChatResponse` with exact fallback message: "I cannot provide information related to this topic. However, if you have any queries regarding the 'Physical AI & Humanoid Robotics' book, let me know — I am here to assist you.", confidence=0.0, empty citations
- [X] T053 [US3] Add optional keyword-based out-of-scope detection in `backend/app/services/rag.py`: check for common unrelated topics (weather, jokes, general coding), return fallback message early

### Frontend Implementation for US3

- [X] T054 [US3] Update `src/components/Chatbot/ChatMessage.tsx` to handle low-confidence responses: display fallback message with special styling (info color, icon), no citations shown

**Checkpoint**: User Story 3 complete - guardrails in place, chatbot politely declines out-of-scope questions.

---

## Phase 6: User Story 4 - Mobile-Responsive Chat Experience (Priority: P4)

**Goal**: Ensure chatbot works seamlessly on mobile devices (< 768px) without blocking screen or causing usability issues.

**Independent Test**: Open chatbot on 375px mobile viewport, verify FAB is tappable, chat window fits 90% viewport, messages are readable, tap-outside-to-close works.

### Frontend Implementation for US4

- [X] T055 [P] [US4] Add mobile media queries in `src/components/Chatbot/ChatWidget.module.css`: adjust FAB size (ensure 56x56px minimum), chat window height (90% viewport on mobile), font sizes
- [X] T056 [P] [US4] Update `src/components/Chatbot/ChatWindow.tsx`: on mobile (< 768px), add tap-outside-to-close listener, ensure input field remains visible when on-screen keyboard opens
- [X] T057 [US4] Update `src/components/Chatbot/ChatMessage.tsx`: ensure long URLs in citations wrap gracefully (FR-024), prevent horizontal scrolling
- [X] T058 [US4] Update `src/components/Chatbot/TextSelectionHandler.tsx`: improve mobile text selection handling (iOS Safari quirks, Android Chrome touch events)

**Checkpoint**: User Story 4 complete - chatbot fully responsive on mobile devices.

---

## Phase 7: User Story 5 - Conversation History Persistence (Priority: P5)

**Goal**: Persist conversation history within browser session so users can close/reopen chatbot without losing context.

**Independent Test**: Ask 3 questions, close chatbot, reopen within same session, verify all 3 messages still visible.

### Frontend Implementation for US5

- [X] T059 [US5] Update `src/components/Chatbot/useChatbot.ts`: save messages to `sessionStorage` on every update, load from `sessionStorage` on mount, clear on page refresh
- [X] T060 [US5] Add scroll optimization in `src/components/Chatbot/ChatWindow.tsx`: virtual scrolling or windowing for 20+ messages (FR-031), auto-scroll to bottom on new message
- [X] T061 [US5] Ensure session history cleared when user refreshes page (FR-030): verify sessionStorage behavior, add comment documenting no cross-session persistence

**Checkpoint**: User Story 5 complete - conversation history persists within session.

---

## Phase 8: Docker & Deployment

**Purpose**: Containerize backend for local dev and production deployment

- [X] T062 Create `backend/Dockerfile` multi-stage build (builder: install deps, runtime: Python 3.11-slim, copy app, expose port 8000)
- [X] T063 Create `backend/docker-compose.yml` for local dev: services for FastAPI (build from Dockerfile), Qdrant (Docker image), expose ports, environment variables from `.env` file
- [X] T064 Add health check in `backend/Dockerfile`: `HEALTHCHECK CMD curl --fail http://localhost:8000/api/v1/health || exit 1`
- [X] T065 Update `backend/README.md`: add Docker setup instructions, docker-compose up commands, local vs production deployment notes

**Checkpoint**: Backend fully containerized, can run via `docker-compose up`.

---

## Phase 9: Admin & Ingestion Endpoint

**Purpose**: Admin-only endpoint to trigger re-ingestion

- [X] T066 Implement `POST /api/v1/ingest` in `backend/app/api/v1/ingest.py`: require X-API-Key header (validate against ADMIN_API_KEY from config), call ingestion script (T028-T030), return ingestion stats (chunks_ingested, duration_seconds)
- [X] T067 Add admin endpoint to API router in `backend/app/api/v1/__init__.py`

**Checkpoint**: Admin can manually trigger content re-ingestion via protected endpoint.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, code quality, documentation

- [X] T068 [P] Add code formatting pre-commit hooks: Black (line length 88), Ruff linting, isort for imports in `backend/.pre-commit-config.yaml`
- [X] T069 [P] Add type checking: run mypy strict mode on `backend/app/`, ensure 100% type hints, fix any type errors
- [X] T070 [P] Update `backend/README.md` with quickstart guide, API endpoint documentation, troubleshooting section
- [X] T071 [P] Create `backend/docs/adr/001-why-qdrant.md` Architecture Decision Record documenting why Qdrant over Pinecone
- [X] T072 Validate constitution compliance: verify ALL backend code in `/backend`, NO changes to `/docs` or `/static`, chatbot components ONLY in `src/components/Chatbot/`
- [X] T073 Manual testing: run through all 5 user story independent tests, verify acceptance scenarios, test edge cases (Qdrant down, LLM rate limit, empty query)
- [X] T074 [P] Add logging throughout backend: structured logging (JSON), log levels (INFO for queries, ERROR for failures), ensure no PII logged
- [X] T075 Security audit: verify API keys in `.env` only, CORS whitelist configured, rate limiting works, input sanitization active, no XSS vulnerabilities

**Checkpoint**: All user stories polished, code quality high, ready for deployment.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Enhances US1 but independently testable
  - User Story 3 (P3): Can start after Foundational - Adds guardrails to US1 but independently testable
  - User Story 4 (P4): Can start after Foundational - Mobile optimization for US1 but independently testable
  - User Story 5 (P5): Can start after Foundational - History persistence for US1 but independently testable
- **Docker (Phase 8)**: Can start after Foundational - No dependencies on user stories
- **Admin Endpoint (Phase 9)**: Depends on Foundational + Ingestion (T028-T030 from US1)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Independence

**All user stories are independently implementable and testable after Foundational phase:**

- **US1** provides core Q&A functionality (MVP)
- **US2** adds text selection feature (works with or without US1 complete)
- **US3** adds guardrails (enhances US1 but US1 works without it)
- **US4** adds mobile support (enhances US1 but US1 works on desktop without it)
- **US5** adds history persistence (enhances US1 but US1 works without it)

This design allows incremental delivery: US1 → Deploy → US2 → Deploy → US3 → Deploy, etc.

### Within Each User Story

- Backend tasks can run in parallel with Frontend tasks (different directories)
- Models and services can run in parallel if marked [P] (different files)
- Frontend components marked [P] can run in parallel (different files)
- Integration tasks depend on their component tasks completing

### Parallel Opportunities

#### Phase 1 (Setup)
All tasks T001-T010 can run in parallel except T005 depends on T002.

#### Phase 2 (Foundational)
- Configuration tasks T011-T013 can run in parallel
- Database setup T014-T015 sequential
- Vector store T016-T017 sequential
- Embeddings T018, LLM T019, Models T020-T021 all parallel
- FastAPI base T022-T025 mostly parallel after T022
- Utilities T026-T027 parallel

#### Phase 3 (US1 - Backend)
T028-T030 sequential (ingestion pipeline), T031-T034 sequential (RAG + endpoint).

#### Phase 3 (US1 - Frontend)
All T035-T041 parallel (different files), T042-T044 sequential (integration).

**Backend and Frontend work can proceed in parallel.**

#### Phase 4 (US2)
T045 (backend), T046-T050 (frontend) - backend and frontend in parallel.

#### Phase 5 (US3)
T051-T053 sequential (backend), T054 (frontend) - can run in parallel.

#### Phase 6 (US4)
All T055-T058 parallel (different CSS/components).

#### Phase 7 (US5)
T059-T061 sequential (hook update logic).

#### Phase 8 (Docker)
T062-T065 mostly sequential.

#### Phase 9 (Admin)
T066-T067 sequential.

#### Phase 10 (Polish)
All T068-T075 parallel except T072-T073 should be last.

---

## Parallel Example: User Story 1

```bash
# Backend tasks (run in parallel):
Task T028: "Implement ingestion service"
Task T035: "Create TypeScript types" (Frontend - different directory)

# Frontend components (run in parallel after T035):
Task T036: "FloatingActionButton component"
Task T037: "ChatWindow component"
Task T038: "ChatMessage component"
Task T039: "ChatInput component"
Task T040: "TypingIndicator component"
Task T041: "ChatWidget CSS module"

# Integration (sequential):
Task T042: "useChatbot hook" (depends on T036-T041)
Task T043: "ChatWidget main component" (depends on T042)
Task T044: "Integrate into Docusaurus" (depends on T043)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T027) **CRITICAL - blocks all stories**
3. Complete Phase 3: User Story 1 (T028-T044)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Open chatbot, ask "What is the Perception-Action Loop?"
   - Verify RAG pipeline works: retrieval → embedding → LLM → citations
   - Verify frontend: FAB opens/closes, animations smooth, messages display correctly
5. Deploy/demo MVP if ready

**At this point, you have a functional RAG chatbot (MVP).**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (text selection feature)
4. Add User Story 3 → Test independently → Deploy/Demo (guardrails)
5. Add User Story 4 → Test independently → Deploy/Demo (mobile support)
6. Add User Story 5 → Test independently → Deploy/Demo (history persistence)
7. Add Docker (Phase 8) → Containerized deployment
8. Add Admin Endpoint (Phase 9) → Content re-ingestion capability
9. Polish (Phase 10) → Production-ready

**Each story adds value without breaking previous stories.**

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (CRITICAL - must be done before stories)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (backend + frontend)
   - Developer B: User Story 2 (backend + frontend)
   - Developer C: Docker setup (Phase 8)
3. **Stories complete and integrate independently**
4. **Test each story independently before merging**

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability
- **Each user story should be independently completable and testable**
- **Backend isolation enforced**: ALL backend code in `/backend`, ZERO in `src/`, `docs/`, Docusaurus root
- **Frontend isolation enforced**: Chatbot components ONLY in `src/components/Chatbot/`, scoped CSS, NO global styles
- **Constitution compliance critical**: Re-verify in T072 before deployment
- **Commit after each task or logical group**
- **Stop at any checkpoint to validate story independently**
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence, modifying existing Docusaurus book content

---

**Total Tasks**: 75
**Parallelizable Tasks**: 38 (marked with [P])
**User Stories**: 5 (P1-P5)
**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = T001-T044 = 44 tasks

**Ready for Implementation**: All tasks are atomic, ordered, and have clear file paths. Begin with Phase 1 Setup.
