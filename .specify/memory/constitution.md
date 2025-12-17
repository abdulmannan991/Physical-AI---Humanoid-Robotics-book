<!--
Sync Impact Report:
Version change: 0.0.0 → 1.0.0 (MAJOR: Initial creation/significant update of the Constitution file based on provided project context)
Modified principles: All (from template placeholders to specific project rules)
Added sections: N/A (sections are filled from template, but content is new)
Removed sections: Generic [SECTION_2_NAME]/[SECTION_2_CONTENT] and [SECTION_3_NAME]/[SECTION_3_CONTENT] (not specified by user)
Templates requiring updates:
- .specify/templates/plan-template.md: ⚠ pending (review for alignment with new principles)
- .specify/templates/spec-template.md: ⚠ pending (review for alignment with new principles)
- .specify/templates/tasks-template.md: ⚠ pending (review for alignment with new principles)
- .claude/commands/speckit.constitution.md: ✅ updated (this file's guidance is aligned)
Follow-up TODOs: N/A
-->
# Project Constitution: Physical AI & Humanoid Robotics Course

## 1. Project Vision

- **Goal:** Create a comprehensive, interactive digital book on Physical AI & Humanoid Robotics.
- **Platform:** Docusaurus 3 (TypeScript) deployed to GitHub Pages.
- **Structure:** "Docs-Only Mode" (Book structure). The landing page (`/`) must redirect immediately to Chapter 1. No blog.

## 2. The "Context7" Golden Rule (CRITICAL)

- **Rule:** The AI must NEVER rely on its internal training data for Docusaurus syntax, as it may be outdated (v2 vs v3).
- **Mandate:** For ANY task involving frontend code, `docusaurus.config.ts`, swizzling, or CSS customization, you MUST first use the `context7` MCP server to fetch the latest official documentation.
- **Verification:** Before implementing a UI feature, cite the Docusaurus docs URL you retrieved via Context7.

## 3. Spec-Kit Workflow Enforcement

- We strictly follow the 5-step cycle:
  1. **Constitution** (This file - The Laws)
  2. **Specification** (Detailed requirements gathering)
  3. **Planning** (Architecture and logic mapping)
  4. **Tasks** (Atomic, step-by-step checklists)
  5. **Implementation** (Coding - only after steps 1-4 are approved)
- **Anti-Pattern:** "Vibe Coding" (jumping to code without a plan) is strictly forbidden.

## 4. Code Quality & Standards

- **Strict TypeScript:** Use `.ts` and `.tsx` for all config and page files. No `.js` allowed.
- **Content:** All educational content must be written in Markdown/MDX with interactive components (Mermaid diagrams, Tabs).
- **Structure:** Maintain a clean folder structure suitable for a textbook (e.g., `/docs/01-module/`, `/docs/02-module/`).

## 5. Governance

- This constitution supersedes all other practices.
- Amendments require formal documentation in the `history/` folder.
- All code generation tasks must explicitly verify compliance with these principles before execution.

**Version**: 1.0.0 | **Ratifie/d**: 2025-12-04 | **Last Amended**: 2025-12-04

---

# 6. Phase 2 — RAG Chatbot & Backend Subsystem (v2.0.0)

[PASTE THE RAG CONSTITUTION CONTENT HERE,
slightly adjusted to say “Phase 2” instead of “separate project”]

<!--
Sync Impact Report:
Version change: 0.0.0 → 2.0.0 (MAJOR: Initial creation of RAG Chatbot subsystem constitution, separate from v1.x book-only project)
Modified principles: All (new constitution for isolated subsystem)
Added sections: RAG-specific principles, API design rules, vector database governance, embedding pipeline standards
Removed sections: N/A (new document)
Templates requiring updates:
- backend/.specify/templates/plan-template.md: ⚠ pending (to be created for backend subsystem)
- backend/.specify/templates/spec-template.md: ⚠ pending (to be created for backend subsystem)
- backend/.specify/templates/tasks-template.md: ⚠ pending (to be created for backend subsystem)
Follow-up TODOs:
- Create backend-specific .specify/templates directory structure
- Define backend-specific Spec-Kit workflow templates
- Establish backend testing and deployment templates aligned with these principles
-->
# Project Constitution: RAG Chatbot & Backend API Subsystem

## 1. Subsystem Vision & Scope

- **Goal:** Build a production-ready RAG (Retrieval-Augmented Generation) chatbot that enables intelligent Q&A over the Physical AI & Humanoid Robotics course content.
- **Architecture:** FastAPI backend + Qdrant vector database + embedding pipeline + React UI component.
- **Version:** v2.0.0 (Major subsystem addition to existing v1.x book project).
- **Isolation Mandate:** ALL backend code MUST reside exclusively in `/backend`. ZERO modifications to existing Docusaurus book content, structure, or styling.

## 2. Frontend Isolation & Safety (CRITICAL)

- **Rule:** The existing Docusaurus book (v1.x) is immutable. The chatbot UI is ONLY a new React component.
- **Mandate:**
  - Chatbot UI components MUST live under `src/components/Chatbot/`.
  - NO global CSS, theme overrides, or layout modifications allowed.
  - NO changes to existing pages, docs structure, or `docusaurus.config.ts` beyond adding the chatbot component reference if needed.
  - The landing page redirect to Chapter 1 remains untouched.
- **Verification:** Before committing frontend code, confirm ZERO changes to `/docs`, `/static`, or existing page files.

## 3. Backend Isolation & Structure (NON-NEGOTIABLE)

- **Root Folder:** `/backend` at project root.
- **Mandatory Structure:**
  ```
  backend/
  ├── app/                    # FastAPI application
  │   ├── api/                # API route handlers
  │   ├── core/               # Config, dependencies, middleware
  │   ├── models/             # Pydantic models
  │   ├── services/           # Business logic (RAG, embeddings, Qdrant)
  │   └── main.py             # FastAPI entry point
  ├── data/                   # Ingestion scripts, raw content
  ├── tests/                  # Backend unit + integration tests
  ├── .env.example            # Environment variables template
  ├── pyproject.toml          # Python dependencies (Poetry/pip)
  └── README.md               # Backend-specific documentation
  ```
- **Forbidden Locations:** No backend files in Docusaurus root, `src/`, `docs/`, `.specify/memory` (v1.x), or any existing folders.

## 4. RAG Pipeline Principles

### 4.1 Embedding Strategy
- **Model:** Use a SOTA open-source embedding model (e.g., `sentence-transformers/all-MiniLM-L6-v2` or `text-embedding-ada-002` if using OpenAI).
- **Chunking:** Content MUST be chunked intelligently (e.g., by heading, paragraph, or semantic boundaries) with metadata (chapter, section, URL).
- **Metadata:** Every chunk MUST include: `source_file`, `chapter`, `section`, `url`, `chunk_id`.

### 4.2 Vector Database (Qdrant)
- **Deployment:** Qdrant MUST run via Docker (local dev) or Qdrant Cloud (production).
- **Collection Design:** Single collection `course_content` with versioning support.
- **Indexing:** Use HNSW index for fast retrieval.
- **Persistence:** Vector DB data MUST be excluded from git (`data/qdrant/` in `.gitignore`).

### 4.3 Retrieval Quality
- **Top-k:** Default retrieval of top 5 chunks, configurable per query.
- **Reranking:** Implement optional reranking (e.g., Cross-Encoder) for improved relevance.
- **Fallback:** If confidence score < 0.6, return "I don't have enough information" instead of hallucinating.

### 4.4 Generation (LLM Integration)
- **Model:** Use a chat-optimized LLM (e.g., GPT-4, Claude 3.5 Sonnet, or Llama 3).
- **Context Window:** Include system prompt + retrieved chunks + user query. Limit context to 4k tokens max.
- **Citation:** Responses MUST include source citations (chapter/section links).
- **Streaming:** Support streaming responses for UX.

## 5. API Design & Standards

### 5.1 Endpoint Structure
- **Base Path:** `/api/v1/`
- **Required Endpoints:**
  - `POST /api/v1/chat` - Send query, receive RAG response
  - `GET /api/v1/health` - Health check
  - `POST /api/v1/ingest` - Admin endpoint to trigger content re-ingestion (protected)
  - `GET /api/v1/collections/stats` - Vector DB statistics (optional, for monitoring)

### 5.2 Request/Response Models
- **Strict Pydantic Validation:** All inputs/outputs MUST use Pydantic models.
- **Error Handling:** Return structured errors with HTTP status codes (400, 404, 500) and clear messages.
- **Rate Limiting:** Implement rate limiting (e.g., 10 requests/min per IP) to prevent abuse.

### 5.3 Security
- **CORS:** Whitelist only the Docusaurus frontend domain.
- **Authentication:** Admin endpoints MUST require API key authentication.
- **Input Sanitization:** Validate and sanitize all user inputs to prevent injection attacks.
- **Secrets Management:** NEVER hardcode API keys. Use environment variables (`.env` file, excluded from git).

## 6. Content Ingestion Pipeline

- **Source:** Markdown files from `/docs/`.
- **Process:**
  1. Parse markdown files (preserve headings, code blocks, diagrams).
  2. Chunk content with metadata.
  3. Generate embeddings.
  4. Upsert to Qdrant with versioning.
- **Automation:** Trigger re-ingestion via `/api/v1/ingest` endpoint or CI/CD hook on content updates.
- **Idempotency:** Ingestion MUST be idempotent (can run multiple times without duplicates).

## 7. Testing & Quality Assurance

- **Unit Tests:** MUST cover all service functions (embedding, retrieval, generation).
- **Integration Tests:** Test full RAG pipeline end-to-end.
- **API Tests:** Use `pytest` + `httpx` to test FastAPI endpoints.
- **Coverage:** Minimum 80% code coverage for backend.
- **CI/CD:** Run tests automatically on PR creation (GitHub Actions recommended).

## 8. Spec-Kit Workflow Enforcement (Backend Context)

- We follow the same 5-step cycle as the main project:
  1. **Constitution** (This file - Backend Laws)
  2. **Specification** (RAG system requirements)
  3. **Planning** (Architecture, API design, data flow)
  4. **Tasks** (Atomic implementation steps)
  5. **Implementation** (Coding - only after steps 1-4 are approved)
- **Anti-Pattern:** "Vibe Coding" is forbidden. Every feature MUST have a spec, plan, and task breakdown before implementation.
- **Templates:** Backend subsystem SHOULD have its own `.specify/templates/` under `/backend/` if workflow diverges from main project.

## 9. Code Quality & Standards

### 9.1 Python (Backend)
- **Version:** Python 3.11+ (match with production deployment environment).
- **Formatting:** Use `black` (line length 88) and `isort` for imports.
- **Linting:** Use `ruff` or `pylint` with strict rules.
- **Type Hints:** MANDATORY for all functions. Use `mypy` for type checking.
- **Docstrings:** Google-style docstrings for all public functions/classes.

### 9.2 TypeScript (Chatbot UI)
- **Strict Mode:** Enable `strict: true` in `tsconfig.json`.
- **Component Structure:** Functional components + React Hooks only.
- **Styling:** Scoped CSS modules or styled-components (NO global styles).
- **State Management:** Use React Context API or lightweight state management (Zustand/Jotai) if needed.

### 9.3 Dependencies
- **Backend:** Pin major versions in `pyproject.toml`. Use virtual environment (Poetry/venv).
- **Frontend:** Chatbot component dependencies MUST NOT conflict with Docusaurus dependencies.

## 10. Deployment & Infrastructure

- **Development:** Docker Compose for local setup (FastAPI + Qdrant + optional LLM mock).
- **Production:** Separate deployment from Docusaurus (e.g., FastAPI on Railway/Render, Qdrant Cloud).
- **Environment Variables:**
  - `QDRANT_URL`, `QDRANT_API_KEY`
  - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (LLM provider)
  - `EMBEDDING_MODEL_NAME`
  - `CORS_ORIGINS`
  - `ADMIN_API_KEY`
- **Monitoring:** Log all queries, retrieval scores, and LLM responses for quality monitoring.

## 11. Documentation Requirements

- **Backend README:** MUST include setup instructions, API endpoint documentation, and architecture diagram.
- **API Docs:** Auto-generated via FastAPI's `/docs` (Swagger UI).
- **Chatbot UI Docs:** Include usage instructions and component props documentation.
- **ADRs (Architecture Decision Records):** Document major decisions (e.g., "Why Qdrant over Pinecone?") in `backend/docs/adr/`.

## 12. Governance

- **This constitution supersedes all other practices for the backend subsystem.**
- **Version Control:** This constitution uses independent semantic versioning (v2.0.0) from the main project (v1.x).
- **Amendments:** Changes require:
  1. RFC (Request for Comment) document in `backend/docs/rfcs/`.
  2. Approval from project maintainer.
  3. Version bump following semver rules.
  4. Update to this file with Sync Impact Report.
- **Compliance Verification:** All PRs touching `/backend` MUST reference this constitution and confirm alignment.

## 13. Migration & Coexistence Rules

- **Independence:** Backend subsystem can be developed, tested, and deployed independently of the Docusaurus book.
- **Versioning:** Backend API follows semver independently (v2.x.x). Frontend book remains v1.x.x.
- **Rollback Safety:** If RAG chatbot fails, Docusaurus book MUST remain functional.
- **Future Integration:** When ready, chatbot UI is integrated as a standalone component (e.g., floating chat button on book pages).

---

**Version**: 2.0.0
**Ratified**: 2025-12-13
**Last Amended**: 2025-12-13
**Scope**: RAG Chatbot & Backend API Subsystem
**Parent Project**: Physical AI & Humanoid Robotics Course (v1.x)
**Original Constitution**: `.specify/memory/constitution.md` (IMMUTABLE - v1.x only)


