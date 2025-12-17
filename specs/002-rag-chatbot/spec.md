# Feature Specification: RAG Chatbot for Physical AI Course

**Feature Branch**: `002-rag-chatbot`
**Created**: 2025-12-13
**Status**: Draft
**Version**: 2.0.0
**Constitution**: `backend/.specify/memory/constitution.md` (v2.0.0)
**Input**: User description: "Physical AI & Humanoid Robotics RAG Chatbot - Intelligent Q&A system with RAG pipeline, vector database, and LLM integration"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Q&A Interaction (Priority: P1)

Students reading the course content need quick answers to specific questions without leaving the page or searching through multiple chapters. They can click a chatbot button, ask a question in natural language, and receive an accurate answer with citations to relevant course sections.

**Why this priority**: This is the core value proposition. Without basic Q&A, the feature has no purpose. This represents the minimum viable chatbot that delivers immediate value to users.

**Independent Test**: Can be fully tested by opening the chatbot, typing "What is the Perception-Action Loop?", and verifying that the response includes accurate information with chapter citations. Delivers standalone value as a course content search assistant.

**Acceptance Scenarios**:

1. **Given** a user is reading Chapter 3, **When** they click the floating chatbot button at the bottom-right, **Then** the chat window opens with a smooth slide-up animation
2. **Given** the chat window is open, **When** the user types "What is ROS 2?" and presses Enter, **Then** the system shows a typing indicator while processing
3. **Given** the system is processing a query, **When** the RAG pipeline retrieves relevant content and generates a response, **Then** the answer appears in the chat with citations (e.g., "According to Chapter 2: ROS 2 Fundamentals...")
4. **Given** a response is displayed, **When** the user clicks a citation link, **Then** the browser navigates to the corresponding chapter/section in the book
5. **Given** the chat window is open, **When** the user clicks the close button or FAB again, **Then** the chat window closes with a smooth fade-out animation

---

### User Story 2 - Text Selection Explanation (Priority: P2)

While reading, students encounter complex concepts or technical jargon they don't fully understand. They can highlight the confusing text, right-click or use a context menu, and ask the chatbot to explain just that specific snippet without formulating a full question.

**Why this priority**: This enhances the basic Q&A by reducing user effort. Instead of manually copying text and asking "explain this," users get instant contextual help. Adds significant UX value but requires P1 to be functional first.

**Independent Test**: Can be tested by selecting the text "inverse kinematics" on any page, clicking the "Ask Chatbot" context menu option, and verifying the chatbot opens with a pre-filled query explaining the selected text. Delivers value as a contextual learning assistant.

**Acceptance Scenarios**:

1. **Given** a user is reading a page, **When** they select/highlight text (e.g., "HNSW indexing"), **Then** a context menu or tooltip appears with "Ask Chatbot about this" option
2. **Given** the context menu is visible, **When** the user clicks "Ask Chatbot about this", **Then** the chatbot opens with a pre-filled query like "Explain: HNSW indexing"
3. **Given** the chatbot receives a text-selection query, **When** it generates a response, **Then** the answer focuses specifically on explaining the selected text with relevant context from the course
4. **Given** the explanation is displayed, **When** the user wants to ask follow-up questions, **Then** they can continue the conversation naturally in the same chat session

---

### User Story 3 - Out-of-Scope Handling (Priority: P3)

Students might ask questions unrelated to the course content (e.g., "What's the weather?", "Write me Python code for sorting"). The chatbot should gracefully decline and guide users back to course-related queries.

**Why this priority**: This is a quality-of-life feature that prevents misuse and sets clear expectations. It's important for long-term user trust but not critical for initial value delivery. Can be implemented after core Q&A works.

**Independent Test**: Can be tested by asking "What's the capital of France?" and verifying the chatbot responds with the exact fallback message: "I cannot provide information related to this topic. However, if you have any queries regarding the 'Physical AI & Humanoid Robotics' book, let me know — I am here to assist you." Delivers value as a guardrail feature.

**Acceptance Scenarios**:

1. **Given** the chat is open, **When** a user asks a completely unrelated question (e.g., "Tell me a joke"), **Then** the chatbot responds with "I cannot provide information related to this topic. However, if you have any queries regarding the 'Physical AI & Humanoid Robotics' book, let me know — I am here to assist you."
2. **Given** the user asks a borderline question (e.g., "How do I install Python?"), **When** the RAG pipeline returns low-confidence results (< 0.6), **Then** the chatbot responds with the same fallback message
3. **Given** the fallback message is displayed, **When** the user asks a valid course-related question next, **Then** the chatbot resumes normal Q&A functionality

---

### User Story 4 - Mobile-Responsive Chat Experience (Priority: P4)

Students accessing the course on mobile devices or tablets need the same chatbot functionality without it blocking the entire screen or being difficult to interact with on smaller displays.

**Why this priority**: Enhances accessibility across devices but is secondary to core functionality. Desktop users can fully validate the feature first, then mobile optimization ensures broader reach.

**Independent Test**: Can be tested by opening the chatbot on a 375px-width mobile viewport and verifying the FAB is easily tappable, the chat window doesn't overflow the screen, and messages are readable. Delivers value as a cross-device accessibility feature.

**Acceptance Scenarios**:

1. **Given** a user is on a mobile device (< 768px width), **When** they tap the FAB, **Then** the chat window opens and occupies 90% of the viewport height without covering navigation elements
2. **Given** the chat is open on mobile, **When** the user types a message using the on-screen keyboard, **Then** the input field remains visible and the chat scrolls appropriately
3. **Given** a response is displayed on mobile, **When** citations include long URLs, **Then** they wrap gracefully without horizontal scrolling
4. **Given** the chat is open on mobile, **When** the user taps outside the chat window, **Then** the chat closes automatically

---

### User Story 5 - Conversation History Persistence (Priority: P5)

Students want to review previous questions they asked during a reading session without losing context when they close and reopen the chatbot.

**Why this priority**: Nice-to-have feature that improves UX for power users but isn't essential for initial launch. Session-based persistence (not cross-session) is sufficient for v2.0.0.

**Independent Test**: Can be tested by asking 3 questions, closing the chatbot, reopening it within the same session, and verifying all previous messages are still visible. Delivers value as a conversation continuity feature.

**Acceptance Scenarios**:

1. **Given** a user has asked 5 questions in a chat session, **When** they close the chatbot and reopen it within the same browser session, **Then** all previous messages are still visible
2. **Given** conversation history exists, **When** the user refreshes the page, **Then** the chat history is cleared (no cross-session persistence in v2.0.0)
3. **Given** the chat has 20+ messages, **When** the user scrolls up, **Then** older messages load smoothly without performance degradation

---

### Edge Cases

- **What happens when the vector database (Qdrant) is unavailable?**
  The chatbot displays an error message: "Sorry, I'm temporarily unavailable. Please try again in a moment." (FR-025)

- **What happens when the user sends an empty message?**
  The send button remains disabled until at least 1 non-whitespace character is entered. (FR-016)

- **What happens when the RAG pipeline returns multiple contradictory chunks?**
  The LLM synthesizes the information and notes discrepancies if present, citing both sources. (FR-010)

- **What happens when the user rapidly sends multiple messages before the first response arrives?**
  Messages are queued and processed sequentially to avoid race conditions. (FR-027)

- **What happens when a citation link points to a non-existent page?**
  The system validates URLs during ingestion; if a link is broken, the citation shows the chapter name without a clickable link. (FR-028)

- **What happens when the LLM API rate limit is exceeded?**
  The chatbot displays: "I'm experiencing high traffic. Please wait 30 seconds and try again." The backend implements exponential backoff. (FR-026)

- **What happens when selected text is extremely long (> 1000 characters)?**
  The system truncates to the first 500 characters and shows "Explain: [truncated text]..." (FR-014)

- **What happens when the embedding service (Cohere) is unavailable?**
  The system cannot process new queries and displays: "Sorry, I'm temporarily unavailable. Please try again in a moment." Existing sessions remain accessible for viewing history. (FR-032)

- **What happens when the Neon PostgreSQL database is unavailable?**
  Chat functionality continues but session metadata and query logs are not persisted. The chatbot warns: "Session history may not be saved." (FR-033)

## Requirements *(mandatory)*

### Functional Requirements

#### Core Chat Functionality

- **FR-001**: System MUST provide a Floating Action Button (FAB) fixed at the bottom-right corner of all course pages (excluding admin pages)
- **FR-002**: System MUST toggle the chat window open/closed when the FAB is clicked
- **FR-003**: System MUST display a typing indicator (animated dots or spinner) while the RAG pipeline is processing a query
- **FR-004**: System MUST render user messages and bot responses in distinct, visually differentiated chat bubbles (e.g., different colors/alignment)
- **FR-005**: System MUST include smooth animations for chat window opening (slide-up, 300ms), closing (fade-out, 200ms), and message appearance (fade-in, 150ms)

#### RAG Pipeline & Content Retrieval

- **FR-006**: System MUST retrieve top 5 relevant content chunks from Qdrant vector database for each user query
- **FR-007**: System MUST use Cohere embeddings API to generate semantic vectors for matching user queries with course content
- **FR-008**: System MUST return the exact fallback message ("I cannot provide information related to this topic. However, if you have any queries regarding the 'Physical AI & Humanoid Robotics' book, let me know — I am here to assist you.") when retrieval confidence score is below 0.6 OR when the query is determined to be out-of-scope
- **FR-009**: System MUST include citations in responses with chapter name, section name, and clickable URL to the source content
- **FR-010**: System MUST synthesize information from multiple retrieved chunks when necessary to provide a coherent answer
- **FR-032**: System MUST implement modular embedding architecture that allows replacement of Cohere with alternative providers (e.g., OpenAI, sentence-transformers) through configuration change only
- **FR-033**: System MAY optionally use Cohere's reranking API to improve relevance of retrieved chunks before passing to LLM

#### Text Selection Feature

- **FR-011**: System MUST detect when a user selects/highlights text on a course page
- **FR-012**: System MUST display a context menu or tooltip with "Ask Chatbot about this" option when text is selected
- **FR-013**: System MUST pre-fill the chat input with "Explain: [selected text]" when the user triggers the context menu action
- **FR-014**: System MUST truncate selected text to 500 characters maximum if the selection exceeds 1000 characters

#### Security & Guardrails

- **FR-015**: System MUST validate that all user inputs are sanitized to prevent XSS attacks
- **FR-016**: System MUST reject messages that contain only whitespace characters
- **FR-017**: System MUST enforce rate limiting (10 requests per minute per user session) on the backend API
- **FR-018**: System MUST store API keys and secrets in environment variables, not hardcoded in source code
- **FR-019**: System MUST use CORS whitelisting to only accept requests from the Docusaurus frontend domain
- **FR-020**: System MUST log all queries and responses (non-sensitive data only) for quality monitoring

#### Mobile & Responsive Design

- **FR-021**: System MUST render the chat window at 90% viewport height on mobile devices (< 768px width)
- **FR-022**: System MUST ensure the FAB is at least 56x56px and easily tappable on touch devices
- **FR-023**: System MUST allow the chat window to close when the user taps outside it on mobile devices
- **FR-024**: System MUST wrap long URLs in citations to prevent horizontal scrolling

#### Error Handling & Resilience

- **FR-025**: System MUST display a user-friendly error message when the Qdrant database is unavailable ("I'm temporarily unavailable. Please try again.")
- **FR-026**: System MUST display a retry message when the LLM API rate limit is exceeded ("High traffic detected. Please wait 30 seconds and try again.")
- **FR-027**: System MUST queue multiple rapid-fire messages and process them sequentially to avoid race conditions
- **FR-028**: System MUST validate citation URLs during content ingestion and mark broken links as non-clickable

#### Session & History

- **FR-029**: System MUST persist conversation history within the same browser session using sessionStorage for frontend display
- **FR-030**: System MUST clear frontend conversation history when the page is refreshed or the session ends
- **FR-031**: System MUST support scrolling through long conversation histories (20+ messages) without performance degradation

#### Database & Persistence (Neon PostgreSQL)

- **FR-034**: System MUST store chat session metadata in Neon PostgreSQL including session ID, start time, last activity time, and message count
- **FR-035**: System MUST log all user queries and bot responses (non-PII only) to Neon PostgreSQL for quality monitoring and analytics
- **FR-036**: System MUST abstract all database access behind a service layer to allow future database replacement without affecting application logic
- **FR-037**: System MUST NOT store personally identifiable information (PII) in query logs (e.g., no IP addresses, user emails, or device fingerprints beyond session ID)
- **FR-038**: System MUST handle Neon PostgreSQL unavailability gracefully by continuing chat functionality without session persistence and displaying a warning message

#### Containerization & Deployment

- **FR-039**: System MUST provide a Dockerfile in the `/backend` directory for containerizing the FastAPI application
- **FR-040**: System MUST support running the containerized backend in both local development and cloud production environments
- **FR-041**: System MUST include a docker-compose.yml file for local development that orchestrates backend services (FastAPI, Qdrant if local)
- **FR-042**: System MUST expose environment variables for all configuration (API keys, database URLs, CORS origins) to the container runtime

### Key Entities *(include if feature involves data)*

- **User Query**: Represents a question or text-selection request from the student. Attributes include query text, timestamp, session ID, selected text flag (boolean), logged in Neon PostgreSQL.

- **RAG Response**: Represents the chatbot's answer. Attributes include response text, confidence score (0.0-1.0), source citations (array of chapter/section/URL), timestamp, tokens used (for monitoring), logged in Neon PostgreSQL.

- **Citation**: Represents a reference to course content. Attributes include chapter name, section name, page URL, relevance score (0.0-1.0).

- **Content Chunk**: Represents a segment of ingested course content stored in Qdrant. Attributes include chunk ID, source file path, chapter, section, embedding vector (generated via Cohere), raw text, URL.

- **Chat Session** (stored in Neon PostgreSQL): Represents metadata about a user's conversation. Attributes include session ID (UUID), start timestamp, last activity timestamp, total message count. Frontend also maintains session data in sessionStorage for display.

- **Query Log** (stored in Neon PostgreSQL): Represents a logged interaction for analytics. Attributes include log ID, session ID, query text, response text (truncated), confidence score, timestamp, retrieval latency (ms). NO PII stored.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can open the chatbot and receive a relevant answer to a course-related question in under 5 seconds (from query submission to response display)
- **SC-002**: The chatbot provides citations with working links for at least 90% of successful responses
- **SC-003**: The chatbot correctly identifies and rejects out-of-scope questions with the fallback message at least 85% of the time
- **SC-004**: Users can successfully use the text-selection feature and receive an explanation in under 3 clicks (select → context menu → response)
- **SC-005**: The chat interface is fully functional on mobile devices (< 768px) with no layout breaking or horizontal scrolling
- **SC-006**: The system maintains an average retrieval confidence score of 0.75 or higher for in-scope queries during testing
- **SC-007**: Users can maintain a conversation of at least 10 back-and-forth exchanges without errors or session loss
- **SC-008**: The chat window opens and closes with smooth animations (no janky or delayed rendering) on devices with at least 30 FPS
- **SC-009**: The backend API successfully handles 10 concurrent user requests without errors or timeout (within rate limit)
- **SC-010**: Zero API keys or secrets are exposed in frontend code or network responses during security audit

## Scope & Boundaries *(mandatory)*

### In Scope

- RAG-powered Q&A chatbot for Physical AI & Humanoid Robotics course content
- Text selection to chatbot query feature
- Floating Action Button (FAB) UI component
- Chat window with typing indicators and animations
- Backend FastAPI service with Qdrant vector database integration
- LLM integration (OpenAI GPT-4 or Anthropic Claude 3.5 Sonnet)
- Content ingestion pipeline for Markdown files in `/docs`
- Citation generation with clickable links to course sections
- Mobile-responsive design
- Session-based conversation history
- Rate limiting and security guardrails

### Out of Scope (Future Versions)

- Cross-session conversation history (persistent storage across browser refreshes) - deferred to v2.1.0
- Multi-language support (translations) - deferred to v2.2.0
- Voice input/output for chatbot - deferred to v3.0.0
- User authentication or personalized responses - not planned for v2.x
- Admin dashboard for monitoring chatbot performance - deferred to v2.3.0
- Integration with external knowledge bases (beyond course content) - not planned
- Chatbot API for third-party integrations - not planned for v2.x
- A/B testing different LLM models within the UI - deferred to v2.4.0

## Assumptions *(mandatory)*

1. **LLM Provider Availability**: We assume OpenAI or Anthropic APIs are available and stable. If both are down, the chatbot will be unavailable (acceptable for v2.0.0).

2. **Content Format**: All course content is in Markdown/MDX format under `/docs`. No other formats (PDF, DOCX) will be ingested in this version.

3. **Embedding Provider**: We assume Cohere's embedding API produces sufficiently high-quality embeddings for the course domain. No custom fine-tuning is required. The modular architecture allows switching to alternative providers if needed.

4. **User Intent**: Users asking questions genuinely want answers from the course content, not general web search results or unrelated information.

5. **Browser Support**: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+) with JavaScript enabled. No support for IE11 or browsers with strict content security policies blocking inline scripts.

6. **Session Duration**: A typical user session lasts 30-60 minutes. Conversation history beyond this timeframe is not critical for UX.

7. **Content Update Frequency**: Course content is updated infrequently (weekly or monthly). Manual re-ingestion via admin endpoint is acceptable; real-time auto-ingestion is not required.

8. **Network Latency**: Average network latency between frontend and backend is under 200ms. Users on extremely slow connections (< 1 Mbps) may experience degraded performance but this is an acceptable trade-off.

9. **Rate Limiting**: 10 requests per minute per user is sufficient to prevent abuse while not hindering legitimate use. Power users asking 10+ questions per minute are edge cases.

10. **Citation Accuracy**: We assume the metadata (chapter, section, URL) extracted during content ingestion is accurate. Manual verification of citations is performed during QA, but automated URL validation is the only runtime check.

11. **Neon PostgreSQL Availability**: We assume Neon's serverless PostgreSQL is available with reasonable latency (< 50ms connection time). If Neon is unavailable, chatbot continues without session persistence (graceful degradation acceptable for v2.0.0).

12. **Cohere API Stability**: We assume Cohere's embedding API is available and stable. Embedding requests complete in < 1 second for queries up to 512 tokens. If Cohere is down, chatbot becomes unavailable (acceptable for v2.0.0).

13. **Docker Environment**: We assume the deployment environment supports Docker containers (Docker Engine 20.10+ for Linux, Docker Desktop for local development on macOS/Windows).

## Dependencies *(if applicable)*

### External Systems

- **Qdrant Vector Database**: Required for storing and retrieving content embeddings. Must be accessible via HTTP/HTTPS. Local Docker instance for development, Qdrant Cloud for production.

- **LLM API (OpenAI or Anthropic)**: Required for generating natural language responses. API keys must be valid and have sufficient quota/credits.

- **Cohere API**: Required for generating text embeddings and optionally for reranking retrieved chunks. API key must be valid with sufficient credits. Modular design allows replacement with alternative providers.

- **Neon PostgreSQL**: Required for storing chat session metadata and query logs (non-PII). Must be accessible via connection string (DATABASE_URL). Serverless PostgreSQL with auto-scaling.

### Internal Systems

- **Docusaurus Frontend (v1.x)**: The chatbot UI component integrates into the existing book pages. Assumes Docusaurus v3.x is running and React 19 is available.

- **Content in `/docs`**: RAG pipeline depends on Markdown files being present and properly formatted. Missing or malformed files will result in incomplete knowledge base.

### Third-Party Libraries (Frontend)

- React 19 (already provided by Docusaurus)
- CSS Modules or styled-components for scoped styling
- Fetch API or Axios for backend communication

### Third-Party Libraries (Backend)

- FastAPI (Python web framework)
- Qdrant Client (Python SDK for vector database)
- Cohere Python SDK (for embeddings and optional reranking)
- OpenAI Python SDK OR Anthropic Python SDK (for LLM)
- Pydantic (for request/response validation)
- Uvicorn (ASGI server)
- Psycopg3 or SQLAlchemy (for Neon PostgreSQL connection)
- Python-dotenv (for environment variable management)

### Infrastructure

- Docker (for local Qdrant instance and backend containerization)
- Docker Compose (for orchestrating local development services)
- Python 3.11+ runtime environment
- Node.js 20+ (already required by Docusaurus)
- Container registry (Docker Hub, GitHub Container Registry, or cloud provider registry) for production deployment

## Constraints *(if applicable)*

1. **Backend Isolation**: ALL backend code MUST reside in `/backend` directory. No backend logic or API routes can be placed in the Docusaurus root or `src/` folder. (Constitution v2.0.0, Section 3)

2. **Frontend Isolation**: Chatbot UI components MUST be placed ONLY in `src/components/Chatbot/`. No modifications to existing Docusaurus pages, global CSS, or theme files are allowed. (Constitution v2.0.0, Section 2)

3. **No Modification to v1.x Constitution**: The original constitution at `.specify/memory/constitution.md` MUST remain untouched. This feature operates under the new v2.0.0 constitution at `backend/.specify/memory/constitution.md`.

4. **Type Safety**: ALL TypeScript code MUST use strict mode. All Python code MUST include type hints and pass `mypy` strict checks. (Constitution v2.0.0, Section 9)

5. **Testing Coverage**: Minimum 80% code coverage for backend services. (Constitution v2.0.0, Section 7)

6. **API Key Security**: API keys MUST be stored in `.env` files (gitignored) and accessed via environment variables. Hardcoded keys are strictly forbidden. (Constitution v2.0.0, Section 5.3)

7. **CORS Whitelisting**: Backend API MUST only accept requests from the Docusaurus frontend domain(s). Open CORS is forbidden. (Constitution v2.0.0, Section 5.3)

8. **Rate Limiting**: Backend MUST enforce 10 requests/minute per IP to prevent abuse. This is a hard limit. (Constitution v2.0.0, Section 5.2)

9. **Content Source**: RAG pipeline MUST only ingest content from `/docs`. External sources (web scraping, PDFs) are out of scope.

10. **Embedding Provider**: MUST use Cohere API for embeddings in v2.0.0. Architecture MUST be modular to allow future provider replacement. (Constitution v2.0.0, Section 4.1)

11. **Database Abstraction**: ALL database access MUST go through a service layer. Direct SQL queries in route handlers are forbidden. (Constitution v2.0.0, Section 4.2)

12. **PII Protection**: MUST NOT log personally identifiable information (IP addresses, emails, device fingerprints) in Neon PostgreSQL. Session IDs are the only user identifiers allowed. (Constitution v2.0.0, Section 5.3)

13. **Containerization**: Backend MUST be deployable as a Docker container. Dockerfile MUST live in `/backend`. (Constitution v2.0.0, Section 10)

14. **Response Latency**: 95th percentile response time MUST be under 10 seconds (from query submission to full response display). Longer latencies degrade UX unacceptably.

15. **Browser Compatibility**: Must work on evergreen browsers (auto-updating). No support for IE11 or browsers without ES6 support.

## Risks & Mitigations *(if applicable)*

### Risk 1: LLM API Cost Overrun

**Severity**: High
**Probability**: Medium
**Impact**: If usage is higher than expected, LLM API costs (OpenAI/Anthropic) could exceed budget, forcing feature shutdown.

**Mitigation**:
- Implement strict rate limiting (10 req/min per user)
- Set API quota alerts (e.g., alert at 80% of monthly budget)
- Cache common queries to reduce redundant LLM calls
- Use a cheaper model (GPT-3.5-turbo) for development/testing, reserve GPT-4 for production
- Monitor token usage per query and optimize prompt length

---

### Risk 2: Qdrant Database Performance Degradation

**Severity**: Medium
**Probability**: Low
**Impact**: As content grows (more chapters ingested), vector search latency may increase, degrading UX.

**Mitigation**:
- Use HNSW indexing (already fast for up to 10M vectors)
- Monitor query latency and set alerts for > 500ms search times
- Optimize chunk size (512 tokens max) to keep vector count manageable
- Plan for Qdrant Cloud upgrade if local instance can't handle load
- Implement result caching for frequent queries (e.g., "What is ROS 2?")

---

### Risk 3: Hallucination or Incorrect Answers

**Severity**: High
**Probability**: Medium
**Impact**: Chatbot provides incorrect or misleading information, damaging user trust in the course.

**Mitigation**:
- Use confidence threshold (0.6) to reject low-quality retrievals
- Include citations in all responses so users can verify information
- Prompt engineering: Instruct LLM to ONLY use provided context, never fabricate
- Manual QA testing with 50+ diverse queries before launch
- Log all queries and responses for post-launch quality monitoring
- Implement user feedback mechanism ("Was this helpful? Yes/No")

---

### Risk 4: Frontend Integration Breaks Docusaurus Build

**Severity**: Medium
**Probability**: Low
**Impact**: Adding React components could conflict with Docusaurus v3 build process or cause runtime errors.

**Mitigation**:
- Follow Docusaurus component conventions (use `@docusaurus/` imports where applicable)
- Test build process (`yarn build`) after every frontend change
- Use scoped CSS modules to avoid style conflicts
- Implement feature flag to disable chatbot if critical errors occur
- Run Docusaurus in development mode (`yarn start`) continuously during development

---

### Risk 5: Content Ingestion Pipeline Failures

**Severity**: Medium
**Probability**: Medium
**Impact**: If ingestion fails (malformed Markdown, missing metadata), the RAG pipeline will have incomplete knowledge.

**Mitigation**:
- Validate Markdown files during ingestion (check for required frontmatter: title, chapter, section)
- Log all ingestion errors with specific file paths and line numbers
- Implement dry-run mode for testing ingestion without committing to Qdrant
- Manually review ingestion logs before deploying to production
- Create a fallback: if a file fails, skip it but continue processing other files

---

### Risk 6: Mobile UX Issues (Small Screens)

**Severity**: Low
**Probability**: Medium
**Impact**: Chat window may be unusable on very small screens (< 375px) or have touch target issues.

**Mitigation**:
- Test on real devices: iPhone SE (375px), Pixel 5 (393px), iPad Mini (768px)
- Use CSS media queries to adjust layout for < 375px screens
- Ensure FAB and close button are at least 44x44px (iOS touch target guideline)
- Implement "tap outside to close" for mobile to avoid accidental clicks
- Consider collapsible chat window that takes full screen on very small devices

---

## Open Questions *(if any)*

*All critical questions have been resolved during specification. No open questions remain that would block planning or implementation.*

---

**End of Specification**

**Next Steps**:
1. Validate this specification using `/speckit.analyze` or manual review
2. Proceed to `/speckit.plan` to design the technical architecture
3. Use `/speckit.tasks` to generate actionable implementation tasks
