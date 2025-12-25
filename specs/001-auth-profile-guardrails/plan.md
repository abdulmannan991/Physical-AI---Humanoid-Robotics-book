# Implementation Plan: Authentication, User Profile, Chat Linking & Guardrails Update

**Branch**: `001-auth-profile-guardrails` | **Date**: 2025-12-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-auth-profile-guardrails/spec.md`

## Summary

This feature adds user authentication, profile management, and improved chatbot guardrails to the Physical AI & Humanoid Robotics course platform. The implementation includes:
- Email/password authentication with JWT session management
- User profile pages with image upload (base64-encoded storage in PostgreSQL)
- Chat session linking to authenticated users (backward-compatible with guest sessions)
- Relaxed guardrails that allow greetings, request clarification for ambiguous questions, and only block clearly off-topic queries

**Technical Approach**: Extend the existing FastAPI backend with new authentication endpoints and user management, create Docusaurus pages for login/signup/profile, add authentication middleware, and update the chatbot RAG system's prompt engineering for improved guardrails.

## Technical Context

**Language/Version**:
- **Frontend**: TypeScript 5.6.2 with React 19.0.0 + Docusaurus 3.9.2
- **Backend**: Python 3.11 with FastAPI 0.109.0

**Primary Dependencies**:
- **Frontend**: Docusaurus 3.9.2, React 19, @chatscope/chat-ui-kit-react 2.1.1
- **Backend**: FastAPI 0.109.0, SQLAlchemy 2.0.25 (asyncio), asyncpg 0.29.0, psycopg 3.1.0, pydantic 2.5.0
- **Authentication**: PyJWT (to be added), bcrypt (to be added)
- **Database**: Neon PostgreSQL (already configured)

**Storage**:
- **Database**: Neon PostgreSQL (existing)
  - New table: `users` (id UUID PK, email TEXT UNIQUE, username TEXT UNIQUE, password_hash TEXT, profile_image_url TEXT, created_at TIMESTAMP)
  - Modified table: `chat_sessions` (add user_id UUID FK nullable)
- **Session Storage**: JWT tokens (httpOnly cookies)
- **Image Storage**: Base64-encoded BLOBs in PostgreSQL profile_image_url column

**Testing**:
- **Frontend**: TypeScript type checking (`tsc`)
- **Backend**: pytest 7.4.0, pytest-asyncio 0.23.0, pytest-cov 4.1.0 (80% coverage requirement)
- **API Tests**: Test all new endpoints with httpx
- **Integration Tests**: End-to-end authentication flow, session management, image upload

**Target Platform**:
- **Frontend**: Modern browsers (Chrome, Firefox, Safari - last 3 versions)
- **Backend**: Linux server (FastAPI on uvicorn)
- **Deployment**: Frontend on GitHub Pages, Backend on hosting platform (Railway/Render)

**Project Type**: Web application (backend + frontend)

**Performance Goals**:
- Account creation < 60 seconds (SC-001)
- Login < 10 seconds (SC-002)
- Profile image upload < 3 seconds for 5MB images (SC-003)
- Profile page load < 2 seconds (SC-004)
- Password hashing < 200ms overhead (SC-011)
- JWT validation < 50ms overhead (SC-012)

**Constraints**:
- Must not break existing chatbot functionality (FR-031)
- Must not modify existing chat_sessions/query_logs table structure except adding user_id column (Constitution Section 4.2)
- Must maintain backward compatibility with existing guest chat sessions
- Must follow Docusaurus 3.x architecture (no v2 patterns - Constitution Section 2)
- Must use TypeScript (.ts/.tsx) for all frontend code (Constitution Section 4)
- Backend code must remain in `/backend` directory (Constitution Section 3)
- No modifications to existing Docusaurus book content or styling (Constitution Section 2)

**Scale/Scope**:
- Expected users: Educational platform, moderate traffic (~1000-10000 concurrent users)
- Database: Single PostgreSQL instance (Neon)
- Sessions: Multiple concurrent sessions per user supported (FR-011)
- Image storage: 5MB limit per image, base64 storage acceptable for moderate user base

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Frontend Isolation (Constitution Section 2 - CRITICAL)

**Rule**: The existing Docusaurus book (v1.x) is immutable. New pages MUST follow Docusaurus conventions.

**Compliance**:
- ✅ Login/Signup/Profile pages will use Docusaurus page system (`src/pages/login.tsx`, etc.)
- ✅ NO modifications to existing docs structure or book content
- ✅ NO global CSS changes or theme overrides
- ✅ Landing page redirect remains untouched
- ✅ All new components scoped to authentication feature

**Verification**: Review all frontend changes to ensure zero modifications to `/docs`, `/static`, or existing page files.

---

### Gate 2: Backend Isolation (Constitution Section 3 - NON-NEGOTIABLE)

**Rule**: ALL backend code MUST reside exclusively in `/backend`. Structure MUST follow established patterns.

**Compliance**:
- ✅ Authentication code will be in `/backend/app/api/v1/auth.py` (new)
- ✅ User models in `/backend/app/models/database.py` (extend existing)
- ✅ Auth services in `/backend/app/services/auth.py` (new)
- ✅ Middleware in `/backend/app/core/middleware.py` (extend existing)
- ✅ NO backend files outside `/backend` directory

**Structure Additions**:
```
backend/app/
├── api/v1/
│   └── auth.py          # NEW: Authentication endpoints
├── services/
│   └── auth.py          # NEW: Authentication logic
├── models/
│   └── database.py      # MODIFY: Add User model
└── core/
    ├── middleware.py    # MODIFY: Add auth middleware
    └── security.py      # MODIFY: Add JWT utilities
```

**Verification**: All new backend code verified to be under `/backend/app/`.

---

### Gate 3: Database Safety (Constitution Section 4.2 - PII Protection)

**Rule**: NO PII allowed in chat_sessions or query_logs tables per constitution.

**Compliance**:
- ✅ User table is separate from chat tables
- ✅ chat_sessions.user_id is nullable FK (optional link, not PII)
- ✅ NO IP addresses, emails, or device fingerprints in chat tables
- ✅ Existing PII protection rules remain enforced
- ⚠️ **NEW CONCERN**: Profile images (base64 BLOBs) are considered user content, not PII
- ✅ Email/password stored ONLY in users table with proper hashing

**Verification**: Review database migrations to ensure no PII fields added to chat tables.

---

### Gate 4: Testing Standards (Constitution Section 7)

**Rule**: Minimum 80% code coverage for backend. All endpoints must have tests.

**Compliance**:
- ✅ Unit tests for all auth service functions
- ✅ Integration tests for full auth flow
- ✅ API tests for all new endpoints (signup, login, logout, profile)
- ✅ Test coverage tracked with pytest-cov (--cov-fail-under=80)

**Test Plan**:
- Authentication flow tests (signup → login → access protected route → logout)
- Username collision tests (hamza → hamza2 → hamza3)
- Session expiry tests
- Concurrent session tests
- Image upload validation tests
- Guardrails tests (greetings, ambiguous questions, off-topic questions)

**Verification**: Run `pytest --cov=app --cov-report=term-missing` and verify ≥80% coverage.

---

### Gate 5: Spec-Kit Workflow (Constitution Section 3 & 8)

**Rule**: Follow 5-step cycle. No "vibe coding". Every feature needs spec → plan → tasks → implementation.

**Compliance**:
- ✅ Specification completed ([spec.md](./spec.md))
- ✅ Clarifications resolved (4 questions answered)
- ⏳ Planning in progress (this file)
- ⏳ Tasks breakdown pending (`/speckit.tasks`)
- ⏳ Implementation pending (only after tasks approved)

**Verification**: This plan must be approved before running `/speckit.tasks`.

---

### Summary of Gate Status

| Gate | Status | Notes |
|------|--------|-------|
| Frontend Isolation | ✅ PASS | New pages follow Docusaurus conventions |
| Backend Isolation | ✅ PASS | All code in `/backend/app/` |
| Database Safety | ✅ PASS | No PII in chat tables, user table separated |
| Testing Standards | ⏳ PENDING | Will be verified in Phase 1/2 |
| Spec-Kit Workflow | ✅ PASS | Following all steps in order |

**Overall Status**: ✅ **READY TO PROCEED** (pending items will be addressed in subsequent phases)

---

## Project Structure

### Documentation (this feature)

```text
specs/001-auth-profile-guardrails/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (database schema)
├── quickstart.md        # Phase 1 output (setup guide)
├── contracts/           # Phase 1 output (API contracts)
│   ├── auth-api.yaml    # OpenAPI spec for auth endpoints
│   └── profile-api.yaml # OpenAPI spec for profile endpoints
├── checklists/          # Quality validation (existing)
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT YET CREATED)
```

### Source Code (repository root)

```text
# Web application structure (existing + additions)

backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py          # NEW: /signup, /login, /logout, /me endpoints
│   │   │   ├── profile.py       # NEW: /profile/* endpoints
│   │   │   ├── chat.py          # MODIFY: Link sessions to users
│   │   │   ├── health.py        # EXISTING: Health check
│   │   │   └── ingest.py        # EXISTING: Content ingestion
│   │   └── dependencies.py      # MODIFY: Add auth dependencies
│   ├── core/
│   │   ├── config.py            # MODIFY: Add JWT config
│   │   ├── middleware.py        # MODIFY: Add auth middleware
│   │   └── security.py          # MODIFY: Add JWT/bcrypt utilities
│   ├── models/
│   │   ├── database.py          # MODIFY: Add User model
│   │   ├── request.py           # MODIFY: Add auth request models
│   │   └── response.py          # MODIFY: Add auth response models
│   ├── services/
│   │   ├── auth.py              # NEW: Authentication logic
│   │   ├── database.py          # MODIFY: Add user CRUD operations
│   │   └── llm.py               # MODIFY: Update guardrails prompt
│   └── main.py                  # MODIFY: Register auth routes
├── tests/
│   ├── api/
│   │   └── v1/
│   │       ├── test_auth.py     # NEW: Auth endpoint tests
│   │       └── test_profile.py  # NEW: Profile endpoint tests
│   ├── services/
│   │   └── test_auth.py         # NEW: Auth service tests
│   └── integration/
│       └── test_auth_flow.py    # NEW: End-to-end auth tests
├── alembic/                     # Database migrations
│   └── versions/
│       └── 001_add_auth.py      # NEW: Create users table, add user_id to chat_sessions
└── pyproject.toml               # MODIFY: Add PyJWT, bcrypt dependencies

frontend/ (Docusaurus)
├── src/
│   ├── pages/
│   │   ├── login.tsx            # NEW: Login page
│   │   ├── signup.tsx           # NEW: Signup page
│   │   ├── profile.tsx          # NEW: Profile page
│   │   └── index.tsx            # EXISTING: Landing page (unchanged)
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── LoginForm.tsx    # NEW: Login form component
│   │   │   ├── SignupForm.tsx   # NEW: Signup form component
│   │   │   └── AuthProvider.tsx # NEW: Auth context provider
│   │   ├── Profile/
│   │   │   ├── ProfileView.tsx  # NEW: Profile display component
│   │   │   ├── ProfileImageUpload.tsx # NEW: Image upload component
│   │   │   └── ChatHistory.tsx  # NEW: Chat history display
│   │   └── Chatbot/             # EXISTING: Chatbot components
│   │       └── ChatWidget.tsx   # MODIFY: Add auth context awareness
│   ├── theme/
│   │   └── Root.tsx             # MODIFY: Wrap with AuthProvider
│   └── hooks/
│       └── useAuth.ts           # NEW: Authentication hook
├── package.json                 # MODIFY: Add any new dependencies (if needed)
└── tsconfig.json                # EXISTING: TypeScript config (unchanged)
```

**Structure Decision**: Web application architecture (backend + frontend). The project already follows this pattern with FastAPI backend in `/backend` and Docusaurus frontend in `/src`. This feature extends both sides:

- **Backend**: New authentication module following existing FastAPI structure (api/services/models pattern)
- **Frontend**: New Docusaurus pages following existing page-based routing, new React components for auth UI
- **Database**: New users table + migration to add user_id FK to existing chat_sessions table
- **Integration**: Auth context flows from Root.tsx → components, backend validates JWT on protected routes

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** All gates pass constitution requirements. No additional complexity introduced beyond feature requirements.

---

## Phase 0: Research & Technical Decisions

### Research Questions

Based on Technical Context and Constitution requirements, the following technical decisions need research:

1. **JWT Implementation Strategy**
   - Decision needed: JWT library selection (PyJWT vs python-jose)
   - Research: Token storage strategy (httpOnly cookies vs localStorage)
   - Rationale required: Refresh token implementation (yes/no)

2. **Password Hashing Algorithm**
   - Decision needed: bcrypt vs argon2 vs scrypt
   - Research: Salt rounds/work factor tuning for <200ms target
   - Rationale required: Password strength validation rules

3. **Frontend State Management**
   - Decision needed: React Context API vs external state library
   - Research: Auth token refresh strategy on frontend
   - Rationale required: Session expiry detection mechanism

4. **Database Migration Strategy**
   - Decision needed: Alembic migration approach for adding user_id to chat_sessions
   - Research: Handling existing guest sessions during migration
   - Rationale required: Index strategy for user_id lookups

5. **Image Upload & Validation**
   - Decision needed: Base64 encoding in browser vs backend
   - Research: Image validation libraries (Pillow integration)
   - Rationale required: MIME type validation approach

6. **Guardrails Prompt Engineering**
   - Decision needed: Prompt structure for ambiguity detection
   - Research: Few-shot examples vs rule-based classification
   - Rationale required: Confidence threshold tuning

### Research Outputs → research.md

All research findings will be documented in `research.md` with:
- **Decision**: What was chosen
- **Rationale**: Why chosen (performance, security, maintainability)
- **Alternatives Considered**: What else was evaluated
- **Implementation Notes**: Key details for Phase 1

---

## Phase 1: Design & Contracts

### Prerequisites
- ✅ `research.md` completed with all technical decisions finalized
- ✅ Constitution gates passed
- ✅ Spec clarifications resolved

### Deliverables

#### 1. data-model.md

**Entities to define:**

**User Entity** (NEW):
```
Entity: User
Table: users
Primary Key: id (UUID)
Unique Constraints: email, username

Fields:
- id: UUID (PK, auto-generated)
- email: TEXT (UNIQUE, NOT NULL)
- username: TEXT (UNIQUE, NOT NULL)
- password_hash: TEXT (NOT NULL)
- profile_image_url: TEXT (nullable, stores base64-encoded image)
- created_at: TIMESTAMP (NOT NULL, default NOW())

Relationships:
- One-to-Many with ChatSession (user → chat_sessions)

Validations:
- email: Valid email format (RFC 5322)
- username: Auto-derived from email, sequential numbering for collisions
- password_hash: bcrypt with work factor from research.md
- profile_image_url: Max 5MB base64, formats: JPG/PNG/WebP

State Transitions: N/A (users are created and remain active)

Indexes:
- PRIMARY KEY (id)
- UNIQUE INDEX (email)
- UNIQUE INDEX (username)
```

**ChatSession Entity** (MODIFIED):
```
Entity: ChatSession
Table: chat_sessions
Primary Key: session_id (UUID)

NEW Field:
- user_id: UUID (FK to users.id, nullable)

Relationships (NEW):
- Many-to-One with User (chat_session → user, optional)

Constraints:
- user_id nullable to support guest sessions
- Foreign key with ON DELETE SET NULL (preserve sessions if user deleted)

Indexes (NEW):
- INDEX (user_id) for user's chat history queries
```

#### 2. contracts/

**Generate OpenAPI schemas for new endpoints:**

**contracts/auth-api.yaml**:
```yaml
openapi: 3.0.0
paths:
  /api/v1/auth/signup:
    post:
      summary: Create new user account
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, password]
              properties:
                email: { type: string, format: email }
                password: { type: string, minLength: 8 }
      responses:
        201:
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
        400:
          description: Validation error (email taken, weak password, etc.)

  /api/v1/auth/login:
    post:
      summary: Authenticate user and create session
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, password]
              properties:
                email: { type: string }
                password: { type: string }
                remember_me: { type: boolean, default: false }
      responses:
        200:
          description: Login successful, JWT token in httpOnly cookie
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
        401:
          description: Invalid credentials

  /api/v1/auth/logout:
    post:
      summary: Invalidate current session
      security:
        - cookieAuth: []
      responses:
        200:
          description: Logout successful
        401:
          description: Not authenticated

  /api/v1/auth/me:
    get:
      summary: Get current user info
      security:
        - cookieAuth: []
      responses:
        200:
          description: Current user
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
        401:
          description: Not authenticated

components:
  schemas:
    UserResponse:
      type: object
      properties:
        id: { type: string, format: uuid }
        email: { type: string, format: email }
        username: { type: string }
        profile_image_url: { type: string, nullable: true }
        created_at: { type: string, format: date-time }

  securitySchemes:
    cookieAuth:
      type: apiKey
      in: cookie
      name: session_token
```

**contracts/profile-api.yaml**:
```yaml
openapi: 3.0.0
paths:
  /api/v1/profile:
    get:
      summary: Get user profile
      security:
        - cookieAuth: []
      responses:
        200:
          description: User profile with chat history
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProfileResponse'

  /api/v1/profile/image:
    post:
      summary: Upload profile image
      security:
        - cookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [image_data]
              properties:
                image_data: { type: string, description: "Base64-encoded image (JPG/PNG/WebP, max 5MB)" }
      responses:
        200:
          description: Image uploaded
          content:
            application/json:
              schema:
                type: object
                properties:
                  profile_image_url: { type: string }
        400:
          description: Invalid image (wrong format, too large, etc.)

  /api/v1/profile/chat-history:
    get:
      summary: Get user's chat sessions
      security:
        - cookieAuth: []
      parameters:
        - name: limit
          in: query
          schema: { type: integer, default: 20 }
        - name: offset
          in: query
          schema: { type: integer, default: 0 }
      responses:
        200:
          description: List of chat sessions
          content:
            application/json:
              schema:
                type: object
                properties:
                  sessions:
                    type: array
                    items:
                      $ref: '#/components/schemas/ChatSessionSummary'
                  total: { type: integer }

components:
  schemas:
    ProfileResponse:
      type: object
      properties:
        user:
          $ref: './auth-api.yaml#/components/schemas/UserResponse'
        chat_sessions:
          type: array
          items:
            $ref: '#/components/schemas/ChatSessionSummary'

    ChatSessionSummary:
      type: object
      properties:
        session_id: { type: string, format: uuid }
        started_at: { type: string, format: date-time }
        last_activity_at: { type: string, format: date-time }
        message_count: { type: integer }
```

#### 3. quickstart.md

**Setup guide for developers:**

```markdown
# Authentication Feature Quickstart

## Prerequisites
- Python 3.11+
- Node.js 20+
- Neon PostgreSQL database
- Existing backend + frontend setup completed

## Backend Setup

1. Install new dependencies:
   ```bash
   cd backend
   poetry add PyJWT bcrypt pillow
   poetry install
   ```

2. Update environment variables (.env):
   ```env
   # Add these new variables:
   JWT_SECRET_KEY=<generate-strong-secret>
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 1 day
   JWT_REFRESH_TOKEN_EXPIRE_MINUTES=10080  # 7 days
   ```

3. Run database migration:
   ```bash
   alembic upgrade head
   ```

4. Start backend:
   ```bash
   uvicorn app.main:app --reload
   ```

## Frontend Setup

1. No new dependencies required (using existing React/Docusaurus)

2. Start development server:
   ```bash
   npm start
   ```

## Testing the Feature

1. **Signup**: Navigate to http://localhost:3000/signup
   - Enter email: test@example.com
   - Enter password: SecurePass123!
   - System creates username "test"

2. **Login**: Navigate to http://localhost:3000/login
   - Enter credentials
   - Redirected to home or profile

3. **Profile**: Navigate to http://localhost:3000/profile
   - View profile info
   - Upload profile image
   - View chat history

4. **Logout**: Click logout button (to be added to navbar)

## API Testing

```bash
# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!","remember_me":true}' \
  -c cookies.txt

# Get profile (with session cookie)
curl -X GET http://localhost:8000/api/v1/profile \
  -b cookies.txt
```

## Running Tests

```bash
# Backend tests
cd backend
pytest tests/api/v1/test_auth.py -v
pytest tests/services/test_auth.py -v
pytest tests/integration/test_auth_flow.py -v

# Coverage report
pytest --cov=app --cov-report=term-missing

# Frontend type check
cd ../
npm run typecheck
```
```

#### 4. Agent Context Update

Run the agent context update script:
```bash
.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

This will add the following technologies to the agent context:
- PyJWT (JWT token generation/validation)
- bcrypt (password hashing)
- Pillow (image validation)
- React Context API (auth state management)
- Alembic migrations (database schema updates)

---

## Phase 2: Task Breakdown (NOT CREATED BY THIS COMMAND)

Phase 2 is triggered by running `/speckit.tasks` command separately after this plan is approved.

The tasks command will generate a detailed, sequential task breakdown in `tasks.md` based on:
- This implementation plan
- The data model specification
- The API contracts
- The research decisions

**Expected task structure:**
1. **Setup Phase**: Database migrations, dependency installation
2. **Backend Core**: User model, auth service, JWT utilities
3. **Backend API**: Auth endpoints, profile endpoints, middleware
4. **Frontend Core**: Auth context, hooks, utility functions
5. **Frontend Pages**: Login, signup, profile pages
6. **Frontend Components**: Forms, image upload, chat history display
7. **Integration**: Link chatbot to auth, update guardrails
8. **Testing**: Unit tests, integration tests, API tests
9. **Documentation**: API docs, setup guide updates

---

## Implementation Notes

### Key Implementation Considerations

1. **Backward Compatibility**:
   - Existing guest chat sessions must continue working
   - Database migration must handle NULL user_id in chat_sessions
   - Chatbot must work for both authenticated and guest users

2. **Security Hardening**:
   - httpOnly cookies prevent XSS attacks
   - CORS configuration must whitelist only frontend domain
   - Rate limiting on auth endpoints (already in backend via slowapi)
   - Input validation on all endpoints (Pydantic models)

3. **Performance Optimization**:
   - Index on user_id in chat_sessions for fast history queries
   - JWT validation middleware should be lightweight (<50ms per request)
   - Image validation should reject oversized images before base64 encoding

4. **User Experience**:
   - Clear error messages for validation failures
   - Session expiry notification before redirect
   - Responsive design for all new pages (mobile, tablet, desktop)
   - Loading states during image upload

5. **Testing Strategy**:
   - Mock database for unit tests
   - In-memory database for integration tests
   - Automated tests in CI/CD pipeline
   - Manual testing on multiple devices/browsers

---

## Sign-off Checklist

Before proceeding to `/speckit.tasks`:

- [ ] Research.md completed with all technical decisions
- [ ] data-model.md reviewed and approved
- [ ] API contracts (auth-api.yaml, profile-api.yaml) validated
- [ ] quickstart.md tested by second developer
- [ ] Constitution gates re-verified (all ✅ PASS)
- [ ] Implementation notes reviewed for security/performance concerns
- [ ] Agent context updated successfully

**Status**: ⏳ **READY FOR PHASE 1 EXECUTION**

---

**Plan Version**: 1.0.0
**Last Updated**: 2025-12-21
**Next Command**: Begin Phase 0 research or proceed directly to task generation if research is minimal
