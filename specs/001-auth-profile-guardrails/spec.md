# Feature Specification: Authentication, User Profile, Chat Linking & Guardrails Update

**Feature Branch**: `001-auth-profile-guardrails`
**Created**: 2025-12-21
**Status**: Draft
**Input**: User description: "Authentication, User Profile, Chat Linking & Guardrails Update - Add user authentication system with login/signup pages, user profile management, improved chatbot guardrails, and link chat sessions to authenticated users"

## Clarifications

### Session 2025-12-21

- Q: When multiple users sign up with emails that would generate the same username (e.g., both hamza@gmail.com and hamza@yahoo.com → "hamza"), how should the system handle this collision? → A: Append sequential number (e.g., "hamza" → "hamza2", "hamza3")
- Q: Where should uploaded profile images be stored? → A: Database BLOB storage with base64 encoding in profile_image_url field
- Q: When a user's session expires while they're actively viewing their profile page, what should happen? → A: Redirect to login page with "Session expired, please log in again" message
- Q: How should the system handle concurrent login attempts from different devices for the same user account? → A: Allow concurrent sessions from multiple devices (each device gets its own session)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Account Creation and Authentication (Priority: P1)

A visitor to the Physical AI & Humanoid Robotics course platform wants to create an account to access personalized features and save their chat history. They navigate to the signup page, enter their email and password, and the system automatically creates a username from their email. After successful registration, they can log in using their credentials.

**Why this priority**: Authentication is the foundation for all other user-specific features. Without it, profile management and chat linking cannot function. This provides immediate value by enabling user identity and session persistence.

**Independent Test**: Can be fully tested by navigating to `/signup`, creating an account with valid credentials, then logging in at `/login`. Success delivers user authentication and session management independent of other features.

**Acceptance Scenarios**:

1. **Given** a visitor on the signup page, **When** they enter email "hamza@gmail.com" and a valid password, **Then** the system creates an account with username "hamza" (or "hamza2" if "hamza" is taken) and redirects them to login or the home page
2. **Given** a registered user on the login page, **When** they enter correct email and password, **Then** the system authenticates them and grants access to protected content
3. **Given** a user on the login page, **When** they enter incorrect credentials, **Then** the system displays an error message without revealing whether email or password is incorrect
4. **Given** a visitor on the signup page, **When** they enter an email already registered, **Then** the system displays an error message indicating the email is already in use
5. **Given** a visitor on the signup page, **When** they enter a weak password (less than 8 characters), **Then** the system rejects it with a clear password requirements message
6. **Given** a user "hamza" already exists, **When** a new visitor signs up with email "hamza@yahoo.com", **Then** the system creates an account with username "hamza2"
7. **Given** a user is logged in on their laptop, **When** they log in from their phone, **Then** both sessions remain active and the laptop session is not terminated

---

### User Story 2 - User Profile Management (Priority: P2)

An authenticated user wants to view and manage their profile information, including their username, email, and profile image. They navigate to the profile page where they can see their details and upload or change their profile picture. The interface works seamlessly across desktop, tablet, and mobile devices.

**Why this priority**: Profile management provides value to authenticated users and enhances the user experience. It depends on authentication (P1) but is independent of chat features. Users can manage their identity even without using the chatbot.

**Independent Test**: Can be tested by logging in and navigating to `/profile`. User can view their information and upload a profile image. Success delivers profile viewing and image management independent of chat functionality.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they navigate to `/profile`, **Then** they see their username, email, and current profile image
2. **Given** an authenticated user on the profile page, **When** they upload a new profile image (JPG, PNG, or WebP), **Then** the system updates their profile image and displays it immediately
3. **Given** an authenticated user on the profile page, **When** they view it on a mobile device, **Then** the interface adapts responsively and all features remain accessible
4. **Given** an unauthenticated visitor, **When** they try to access `/profile`, **Then** the system redirects them to the login page
5. **Given** an authenticated user on the profile page, **When** they upload an invalid image file (exceeding size limit or wrong format), **Then** the system displays a clear error message with acceptable formats and size limits
6. **Given** an authenticated user viewing their profile, **When** their session expires, **Then** the system redirects them to the login page with message "Session expired, please log in again"

---

### User Story 3 - Chat History and Session Linking (Priority: P3)

An authenticated user wants to see their previous chat conversations with the RAG-based assistant. When they use the chatbot, their queries are automatically linked to their user account. They can view their chat history in their profile page, organized by date and session.

**Why this priority**: Chat linking provides value but depends on both authentication (P1) and profile infrastructure (P2). It enhances the user experience but the chatbot works without it. Guest users can still use chat without accounts.

**Independent Test**: Can be tested by logging in, using the chatbot, and viewing chat history in the profile page. Success delivers personalized chat history without affecting guest chatbot usage.

**Acceptance Scenarios**:

1. **Given** an authenticated user using the chatbot, **When** they send a query, **Then** the system links the chat session to their user account
2. **Given** an authenticated user on their profile page, **When** they view their chat history, **Then** they see all their previous chat sessions organized chronologically
3. **Given** a guest user (not logged in) using the chatbot, **When** they send a query, **Then** the system creates a chat session with no user link (user_id = NULL)
4. **Given** an authenticated user viewing their chat history, **When** they click on a previous session, **Then** they can see the full conversation for that session
5. **Given** an authenticated user with multiple chat sessions, **When** they view their profile on mobile, **Then** the chat history displays in a scrollable, responsive format

---

### User Story 4 - Improved Chatbot Guardrails (Priority: P1)

A user (authenticated or guest) interacts with the RAG-based chatbot assistant. When they ask questions clearly within the scope of the Physical AI & Humanoid Robotics course, the bot responds helpfully. When questions are ambiguous, the bot asks for clarification with multiple-choice options. Only when questions clearly fall outside the course scope does the bot politely decline to answer.

**Why this priority**: Guardrails directly impact user experience for every chatbot interaction. Overly strict guardrails frustrate users and block legitimate questions. This is critical for core functionality and affects all users immediately.

**Independent Test**: Can be tested by sending various types of queries to the chatbot - greetings, course-related questions, ambiguous questions, and clearly off-topic questions. Success delivers appropriate responses for each category without breaking existing chatbot functionality.

**Acceptance Scenarios**:

1. **Given** a user interacting with the chatbot, **When** they send a greeting like "Hello" or "Hi", **Then** the bot responds with a friendly greeting and offers help with the course
2. **Given** a user asking a course-related question, **When** they ask "Which chapters are included in this book?", **Then** the bot retrieves and answers from the RAG knowledge base
3. **Given** a user asking an ambiguous question, **When** they ask "What is Physical AI?", **Then** the bot asks clarification: "Are you asking about: 1) Physical AI & Humanoid Robotics (this course), 2) Another AI book, 3) A general AI topic?"
4. **Given** a user responding to a clarification question, **When** they select option 1, **Then** the bot answers using the course content
5. **Given** a user asking a clearly off-topic question, **When** they ask "How do I bake a cake?", **Then** the bot responds: "I can only help with the Physical AI & Humanoid Robotics course content"
6. **Given** a user asking about another specific book, **When** they ask "Tell me about the React documentation", **Then** the bot politely declines and reminds them of the course scope

---

### Edge Cases

- What happens when a user tries to sign up with a malformed email address (e.g., "notanemail")? → System rejects with validation error (FR-002)
- What happens when a user's session expires while they're viewing their profile? → System redirects to login with "Session expired, please log in again" message (FR-014)
- How does the system handle concurrent login attempts from different devices for the same account? → System allows concurrent sessions; each device gets its own session token (FR-011)
- What happens when a user uploads a profile image larger than the maximum allowed size?
- How does the system behave if the database connection fails during signup or login?
- What happens when a user tries to access protected routes without authentication?
- How does the chatbot handle rapid-fire messages that might be ambiguous?
- What happens if a user's profile image data becomes corrupted in the database?
- How does the system handle password reset requests (not in scope but affects edge cases)?
- What happens when chat session storage reaches capacity limits?

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication System

- **FR-001**: System MUST provide a signup page at `/signup` accessible to visitors
- **FR-002**: System MUST validate email format during signup and reject invalid email addresses
- **FR-003**: System MUST require passwords to be at least 8 characters long with at least one number and one special character
- **FR-004**: System MUST hash passwords using industry-standard secure hashing before storing in the database
- **FR-005**: System MUST automatically derive username from email by extracting the part before "@" (e.g., hamza@gmail.com → hamza). If the derived username already exists, append sequential numbers (hamza2, hamza3, etc.) until a unique username is found
- **FR-006**: System MUST ensure usernames are unique by checking against existing users and applying sequential numbering for collision resolution
- **FR-007**: System MUST provide a login page at `/login` accessible to users
- **FR-008**: System MUST authenticate users by verifying email and password against stored hashed credentials
- **FR-009**: System MUST implement secure session management with appropriate token security measures
- **FR-010**: System MUST support session durations of 7 days for persistent sessions or 1 day for standard sessions
- **FR-011**: System MUST allow users to maintain concurrent sessions from multiple devices simultaneously (each device receives its own session token)
- **FR-012**: System MUST provide route protection to prevent unauthenticated access to `/profile` and other protected pages
- **FR-013**: System MUST redirect unauthenticated users attempting to access protected routes to `/login`
- **FR-014**: System MUST redirect users to the login page with a "Session expired, please log in again" message when their session expires while viewing protected pages
- **FR-015**: System MUST provide logout functionality that invalidates the current device's session token without affecting sessions on other devices

#### User Profile

- **FR-016**: System MUST provide a profile page at `/profile` accessible only to authenticated users
- **FR-017**: System MUST display username, email, and profile image on the profile page
- **FR-018**: System MUST allow authenticated users to upload a new profile image
- **FR-019**: System MUST accept profile images in JPG, PNG, and WebP formats
- **FR-020**: System MUST limit profile image uploads to 5MB maximum file size
- **FR-021**: System MUST store profile images as base64-encoded BLOB data in the database within the profile_image_url field
- **FR-022**: System MUST provide a default profile image for users who haven't uploaded one
- **FR-023**: System MUST render the profile page responsively for desktop (>1024px), tablet (768px-1024px), and mobile (<768px) viewports

#### Chat Linking

- **FR-024**: System MUST link chat sessions to user accounts through a user identifier reference
- **FR-025**: System MUST allow chat sessions to exist without user links to support guest chat sessions
- **FR-026**: System MUST automatically link new chat sessions to the authenticated user's ID when they're logged in
- **FR-027**: System MUST create chat sessions without user links for unauthenticated (guest) users
- **FR-028**: System MUST display chat history on the profile page for authenticated users
- **FR-029**: System MUST organize chat history chronologically with most recent sessions first
- **FR-030**: System MUST allow users to view individual chat session details (full conversation)
- **FR-031**: System MUST NOT break existing chatbot functionality for guest users

#### Improved Guardrails

- **FR-032**: System MUST allow the chatbot to respond to greetings (Hello, Hi, Hey, etc.) with a friendly welcome message
- **FR-033**: System MUST allow the chatbot to answer questions clearly about the Physical AI & Humanoid Robotics course content
- **FR-034**: System MUST implement an ambiguity detection mechanism to identify questions that could refer to multiple topics
- **FR-035**: System MUST present clarification options (2-3 choices) when ambiguous questions are detected
- **FR-036**: System MUST only trigger strict guardrails when users clearly ask about other books, courses, or unrelated topics
- **FR-037**: System MUST provide a polite decline message: "I can only help with the Physical AI & Humanoid Robotics course content" for off-topic requests
- **FR-038**: System MUST NOT block basic course-related questions like "Which chapters are included?" or "What is Physical AI?"

### Key Entities

- **User**: Represents a registered user account with authentication credentials and profile information
  - Attributes: unique identifier, email (unique), username (unique, derived from email with sequential numbering for collisions), hashed password, profile image data (optional, base64-encoded BLOB), creation timestamp
  - Relationships: One-to-many with ChatSession

- **ChatSession**: Represents a conversation session between a user and the chatbot (already exists)
  - New attribute: user identifier reference (optional - may be empty for guest sessions)
  - Existing attributes: session identifier, start timestamp, last activity timestamp, message count
  - Relationships: Many-to-one with User (optional), One-to-many with QueryLog

- **QueryLog**: Represents individual queries within a chat session (already exists, no changes needed)
  - Attributes: log identifier, session reference, query text, response preview, confidence score, retrieval timing, generation timing, query timestamp

### Assumptions and Dependencies

**Technical Assumptions**:
- The system uses a relational database that supports foreign key relationships, nullable fields, and BLOB storage
- The frontend framework supports client-side page routing and protected routes
- The backend API can handle authentication token validation
- Image uploads can be processed, validated, base64-encoded, and stored in the database
- The database can efficiently handle base64-encoded image data (up to 5MB per image)
- The existing chatbot RAG system can be extended without breaking current functionality

**Business Assumptions**:
- Users prefer simple email/password authentication over social login initially
- Username derivation from email is acceptable to users (e.g., hamza@gmail.com → hamza)
- 5MB profile image limit is sufficient for user needs
- Session durations of 1-7 days meet user expectations for convenience and security
- Guest users should be able to use the chatbot without creating accounts

**Dependencies**:
- Existing database infrastructure (Neon PostgreSQL) must remain operational
- Existing chatbot RAG system and API endpoints must continue working
- Existing frontend pages and routing system must not be disrupted
- Chat session and query log tables already exist and contain production data
- The system must maintain backward compatibility with existing guest chat sessions

**Security Assumptions**:
- Industry-standard password hashing provides adequate security
- Session tokens stored securely prevent unauthorized access
- Password requirements (8+ chars, number, special char) provide acceptable security baseline
- Email validation prevents most malformed inputs
- Profile image upload validation prevents malicious file uploads
- Concurrent sessions from multiple devices are acceptable for this educational platform's security posture
- Individual session tokens can be invalidated without affecting other active sessions

**Constraints**:
- Must not break existing chatbot functionality for current users
- Must not modify or delete existing chat_sessions or query_logs tables structure (only add new optional column)
- Must support both authenticated and guest users simultaneously
- Must follow existing project architecture and patterns

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete account creation in under 60 seconds from landing on the signup page
- **SC-002**: Users can log in successfully within 10 seconds with valid credentials
- **SC-003**: Profile image uploads complete within 3 seconds for images under 5MB on standard broadband connections
- **SC-004**: The profile page loads within 2 seconds for authenticated users with chat history
- **SC-005**: Chatbot responds to greetings and basic questions within 2 seconds without triggering guardrails
- **SC-006**: Ambiguous questions trigger clarification prompts in 100% of test cases where multiple interpretations exist
- **SC-007**: Off-topic questions are correctly identified and declined in 95% of test cases
- **SC-008**: Chat sessions are successfully linked to authenticated users in 100% of cases when logged in
- **SC-009**: Guest users can still use the chatbot without authentication, maintaining existing functionality
- **SC-010**: Profile page renders correctly on mobile devices (320px-768px), tablets (768px-1024px), and desktop (>1024px) with no horizontal scrolling or layout breaks
- **SC-011**: Password security processing adds less than 200ms overhead to signup and login operations
- **SC-012**: Session authentication validation completes with less than 50ms overhead per authenticated request
