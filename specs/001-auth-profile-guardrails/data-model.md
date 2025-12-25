# Data Model: Authentication, User Profile, Chat Linking & Guardrails Update

**Feature**: `001-auth-profile-guardrails`
**Date**: 2025-12-21
**Status**: Design Phase
**Related Documents**: [spec.md](./spec.md), [plan.md](./plan.md), [research.md](./research.md)

## Overview

This document defines the database schema and data model for the authentication and user profile feature. The design extends the existing Neon PostgreSQL database with a new `users` table and modifies the existing `chat_sessions` table to support user account linking.

### Design Principles

1. **Backward Compatibility**: Existing guest chat sessions must continue to work (user_id nullable)
2. **Data Integrity**: Foreign key constraints with appropriate cascade behavior
3. **Performance**: Indexes on frequently queried columns
4. **Security**: Password hashing (Argon2id), no PII in chat tables
5. **Simplicity**: Minimal schema changes to existing tables

---

## Entity Definitions

### 1. User (NEW)

**Purpose**: Represents a registered user account with authentication credentials and profile information.

**Table**: `users`

**Primary Key**: `id` (UUID)

#### Fields

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL, DEFAULT uuid_generate_v4() | Unique user identifier |
| `email` | TEXT | UNIQUE, NOT NULL | User's email address (used for login) |
| `username` | TEXT | UNIQUE, NOT NULL | Display name (auto-derived from email) |
| `password_hash` | TEXT | NOT NULL | Argon2id hashed password |
| `profile_image_url` | TEXT | NULLABLE | Base64-encoded profile image (JPG/PNG/WebP, max 5MB) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Account creation timestamp |

#### Relationships

- **One-to-Many** with `ChatSession`: A user can have multiple chat sessions
  - Foreign key: `chat_sessions.user_id` → `users.id`
  - Cascade behavior: ON DELETE SET NULL (preserve sessions if user deleted)

#### Validations

**Application-Level Validations** (enforced in FastAPI):
- `email`:
  - Format: Valid email per RFC 5322 (Pydantic EmailStr)
  - Uniqueness: Check before insert (handled by UNIQUE constraint + application check for better error messages)
- `username`:
  - Format: Alphanumeric + underscores, 3-30 characters
  - Derivation: Extract part before "@" from email (e.g., "hamza@gmail.com" → "hamza")
  - Collision Resolution: Append sequential numbers if username exists ("hamza" → "hamza2" → "hamza3")
  - Uniqueness: Check before insert
- `password` (before hashing):
  - Minimum 8 characters
  - At least one number
  - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
  - Hashed with Argon2id (memory=65536KB, time_cost=3, parallelism=4)
- `profile_image_url`:
  - If not NULL: Base64-encoded string
  - Decoded size: ≤5MB
  - Formats: JPG, PNG, WebP (validated via Pillow)
  - Magic bytes verification to prevent malicious uploads

**Database-Level Validations**:
- UNIQUE constraints on `email` and `username`
- NOT NULL constraints on required fields
- CHECK constraint: `LENGTH(password_hash) > 0` (ensure hashing occurred)

#### Indexes

```sql
-- Primary key (automatic)
CREATE INDEX idx_users_pkey ON users (id);

-- Unique constraints (automatic indexes)
CREATE UNIQUE INDEX idx_users_email ON users (email);
CREATE UNIQUE INDEX idx_users_username ON users (username);

-- Performance optimization for lookups
CREATE INDEX idx_users_created_at ON users (created_at DESC);
```

#### State Transitions

Users have a simple lifecycle:
1. **Created**: New user signs up (initial state)
2. **Active**: User exists and can log in (persistent state)
3. *Future*: Soft delete or suspension (not in current scope)

No explicit state field is needed; existence in table = active.

#### Sample Data

```sql
INSERT INTO users (id, email, username, password_hash, profile_image_url, created_at) VALUES
  (
    '123e4567-e89b-12d3-a456-426614174000',
    'hamza@gmail.com',
    'hamza',
    '$argon2id$v=19$m=65536,t=3,p=4$...',  -- Hashed 'SecurePass123!'
    NULL,  -- No profile image yet
    '2025-12-21 10:00:00+00'
  ),
  (
    '223e4567-e89b-12d3-a456-426614174001',
    'hamza@yahoo.com',
    'hamza2',  -- Username collision resolved
    '$argon2id$v=19$m=65536,t=3,p=4$...',
    'data:image/jpeg;base64,/9j/4AAQSkZJRg...',  -- Base64-encoded JPEG
    '2025-12-21 11:00:00+00'
  );
```

---

### 2. ChatSession (MODIFIED)

**Purpose**: Represents a conversation session between a user and the RAG chatbot.

**Table**: `chat_sessions` (existing table, adding one column)

**Primary Key**: `session_id` (UUID)

#### New Field

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | UUID | NULLABLE, FOREIGN KEY | Link to authenticated user (NULL for guest sessions) |

#### Foreign Key Constraint

```sql
ALTER TABLE chat_sessions
ADD CONSTRAINT fk_chat_sessions_user_id
FOREIGN KEY (user_id)
REFERENCES users (id)
ON DELETE SET NULL;  -- Preserve sessions if user deleted
```

**Rationale**: `ON DELETE SET NULL` ensures that if a user account is deleted, their chat history is retained as anonymous guest sessions. This supports data retention policies and analytics while respecting user deletion.

#### New Index

```sql
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions (user_id);
```

**Rationale**: Enables fast queries for "get all sessions for user X" when displaying chat history in profile page.

#### Existing Fields (unchanged)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `session_id` | UUID | PRIMARY KEY | Unique session identifier |
| `started_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Session creation time |
| `last_activity_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Last message timestamp |
| `message_count` | INTEGER | NOT NULL, DEFAULT 0 | Number of messages in session |

#### Relationships (UPDATED)

- **Many-to-One** with `User` (OPTIONAL): A session may belong to a user
  - Foreign key: `chat_sessions.user_id` → `users.id`
  - Nullability: TRUE (guest sessions have NULL user_id)
  - Cascade: ON DELETE SET NULL
- **One-to-Many** with `QueryLog` (existing): A session has multiple query logs

#### Migration Strategy

```sql
-- Step 1: Add nullable column (no data modification)
ALTER TABLE chat_sessions
ADD COLUMN user_id UUID NULLABLE;

-- Step 2: Add foreign key constraint
ALTER TABLE chat_sessions
ADD CONSTRAINT fk_chat_sessions_user_id
FOREIGN KEY (user_id)
REFERENCES users (id)
ON DELETE SET NULL;

-- Step 3: Add index for performance
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions (user_id);

-- Step 4: Existing guest sessions remain with user_id=NULL (no backfill needed)
```

**Backward Compatibility**: All existing chat_sessions have `user_id=NULL`, representing guest sessions. Application logic continues to work:
- Guest users: Create sessions with `user_id=NULL`
- Authenticated users: Create sessions with `user_id=<user_uuid>`

#### Sample Data

```sql
-- Existing guest session (unchanged)
INSERT INTO chat_sessions (session_id, user_id, started_at, last_activity_at, message_count) VALUES
  ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', NULL, '2025-12-20 14:30:00+00', '2025-12-20 14:35:00+00', 5);

-- New authenticated user session
INSERT INTO chat_sessions (session_id, user_id, started_at, last_activity_at, message_count) VALUES
  ('b2c3d4e5-f6a7-8901-bcde-f12345678901', '123e4567-e89b-12d3-a456-426614174000', '2025-12-21 10:05:00+00', '2025-12-21 10:10:00+00', 3);
```

---

### 3. QueryLog (NO CHANGES)

**Purpose**: Represents individual queries within a chat session.

**Table**: `query_logs` (existing, no modifications)

**Note**: This table remains unchanged per Constitution Section 4.2 (no PII in chat tables). User identity is linked via `chat_sessions.user_id`, not directly in query logs.

#### Existing Fields

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `log_id` | UUID | PRIMARY KEY | Unique log entry identifier |
| `session_id` | UUID | FOREIGN KEY → chat_sessions.session_id | Parent session |
| `query_text` | TEXT | NOT NULL | User query (max 2000 chars) |
| `response_text_truncated` | TEXT | NULLABLE | First 500 chars of response |
| `confidence_score` | NUMERIC(3,2) | NULLABLE | RAG confidence (0.0-1.0) |
| `retrieval_latency_ms` | INTEGER | NULLABLE | Qdrant retrieval time |
| `llm_latency_ms` | INTEGER | NULLABLE | LLM generation time |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Query timestamp |

**Relationship**: Many-to-One with `ChatSession` (existing, unchanged)

---

## Entity Relationship Diagram

```
┌─────────────────┐
│     User        │
│─────────────────│
│ id (PK)         │◄──────────┐
│ email (UNIQUE)  │           │
│ username (UNIQUE)│          │
│ password_hash   │           │ user_id (FK, nullable)
│ profile_image_url│          │
│ created_at      │           │
└─────────────────┘           │
                              │
                    ┌─────────┴────────┐
                    │  ChatSession     │
                    │──────────────────│
                    │ session_id (PK)  │◄──────────┐
                    │ user_id (FK)     │           │
                    │ started_at       │           │ session_id (FK)
                    │ last_activity_at │           │
                    │ message_count    │           │
                    └──────────────────┘           │
                                                   │
                                         ┌─────────┴────────┐
                                         │    QueryLog      │
                                         │──────────────────│
                                         │ log_id (PK)      │
                                         │ session_id (FK)  │
                                         │ query_text       │
                                         │ response_text... │
                                         │ confidence_score │
                                         │ ...              │
                                         └──────────────────┘

Relationships:
- User → ChatSession: One-to-Many (optional, user_id nullable)
- ChatSession → QueryLog: One-to-Many (existing)
- User can have 0+ ChatSessions (guest users have none)
- ChatSession can have 0 or 1 User (NULL = guest session)
```

---

## Database Migration Script

**File**: `backend/alembic/versions/001_add_authentication.py`

```python
"""Add authentication tables and user linking

Revision ID: 001_add_authentication
Revises: <previous_revision>
Create Date: 2025-12-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# Revision identifiers
revision = '001_add_authentication'
down_revision = '<previous_revision>'  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration: Create users table and link to chat_sessions."""

    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('username', sa.Text(), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('profile_image_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),

        # Constraints
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.UniqueConstraint('username', name='uq_users_username'),
        sa.CheckConstraint('LENGTH(password_hash) > 0', name='ck_users_password_hash_not_empty'),

        # Table comment
        comment='User accounts with authentication credentials'
    )

    # 2. Create indexes on users table
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)
    op.create_index('idx_users_created_at', 'users', ['created_at'], postgresql_using='btree')

    # 3. Add user_id column to chat_sessions (nullable for backward compatibility)
    op.add_column(
        'chat_sessions',
        sa.Column('user_id', UUID(as_uuid=True), nullable=True)
    )

    # 4. Create foreign key constraint
    op.create_foreign_key(
        'fk_chat_sessions_user_id',
        'chat_sessions',
        'users',
        ['user_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # 5. Create index on user_id for fast lookups
    op.create_index('idx_chat_sessions_user_id', 'chat_sessions', ['user_id'])


def downgrade() -> None:
    """Rollback migration: Remove users table and user_id from chat_sessions."""

    # 1. Drop index on chat_sessions.user_id
    op.drop_index('idx_chat_sessions_user_id', table_name='chat_sessions')

    # 2. Drop foreign key constraint
    op.drop_constraint('fk_chat_sessions_user_id', 'chat_sessions', type_='foreignkey')

    # 3. Drop user_id column from chat_sessions
    op.drop_column('chat_sessions', 'user_id')

    # 4. Drop indexes on users table
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_email', table_name='users')

    # 5. Drop users table
    op.drop_table('users')
```

---

## Query Patterns

### Common Queries

#### 1. User Authentication (Login)

```sql
-- Find user by email and verify password (application-level comparison)
SELECT id, email, username, password_hash, profile_image_url, created_at
FROM users
WHERE email = $1;
```

**Expected Performance**: <10ms (indexed on email)

#### 2. Create New User (Signup)

```sql
-- Check if email exists
SELECT id FROM users WHERE email = $1;

-- Check if username exists (for collision detection)
SELECT id FROM users WHERE username = $1;

-- Insert new user
INSERT INTO users (email, username, password_hash, profile_image_url)
VALUES ($1, $2, $3, $4)
RETURNING id, email, username, profile_image_url, created_at;
```

**Expected Performance**: <50ms total (includes uniqueness checks + insert)

#### 3. Get User Profile with Chat History

```sql
-- Get user info
SELECT id, email, username, profile_image_url, created_at
FROM users
WHERE id = $1;

-- Get user's chat sessions (paginated)
SELECT session_id, started_at, last_activity_at, message_count
FROM chat_sessions
WHERE user_id = $1
ORDER BY last_activity_at DESC
LIMIT $2 OFFSET $3;

-- Count total sessions for pagination
SELECT COUNT(*) FROM chat_sessions WHERE user_id = $1;
```

**Expected Performance**: <100ms for profile + 20 sessions (indexed on user_id)

#### 4. Create Authenticated Chat Session

```sql
-- Create session linked to user
INSERT INTO chat_sessions (user_id, started_at, last_activity_at, message_count)
VALUES ($1, NOW(), NOW(), 0)
RETURNING session_id, started_at;
```

#### 5. Create Guest Chat Session

```sql
-- Create session without user link
INSERT INTO chat_sessions (user_id, started_at, last_activity_at, message_count)
VALUES (NULL, NOW(), NOW(), 0)
RETURNING session_id, started_at;
```

---

## Performance Considerations

### Indexes Strategy

1. **users.email**: UNIQUE index (automatic) - supports fast login lookups
2. **users.username**: UNIQUE index (automatic) - supports collision detection
3. **users.created_at**: B-tree index - supports "newest users" queries (admin feature)
4. **chat_sessions.user_id**: B-tree index - supports chat history retrieval

### Estimated Storage Impact

**Per User**:
- Base user record: ~200 bytes (UUID, email, username, password hash, timestamp)
- Profile image (avg 2MB base64): ~2.7MB (1.33x base64 overhead)
- **Total**: ~2.7MB per user with image, ~200 bytes without

**Per Chat Session**:
- New user_id column: 16 bytes (UUID) + 1 byte (nullable flag) = 17 bytes
- **Impact on existing 1M sessions**: 17MB additional storage

**Index Overhead**:
- chat_sessions.user_id index: ~20MB for 1M sessions

**Total Impact for 10K users with images**: ~27GB (dominated by profile images)

### Performance Benchmarks (Expected)

| Operation | Expected Time | Target | Status |
|-----------|---------------|--------|--------|
| User Login (email lookup) | <10ms | <10s (SC-002) | ✅ EXCEEDS |
| User Signup (insert) | <50ms | <60s (SC-001) | ✅ EXCEEDS |
| Password Hash (Argon2id) | 150ms | <200ms (SC-011) | ✅ MEETS |
| Profile Page Load | <100ms | <2s (SC-004) | ✅ EXCEEDS |
| Chat History (20 sessions) | <50ms | <2s (SC-004) | ✅ EXCEEDS |

---

## Security Considerations

### Password Storage

- **Algorithm**: Argon2id (winner of Password Hashing Competition)
- **Parameters**: `memory=65536KB, time_cost=3, parallelism=4`
- **Salt**: Automatically generated per-password (16 bytes random)
- **Hash Length**: 32 bytes output
- **Rationale**: Resistant to GPU/ASIC attacks, configurable memory-hardness

### Profile Image Storage

- **Validation**: Multi-layer (size, format, magic bytes, Pillow re-encoding)
- **Sanitization**: Strip EXIF metadata via re-encoding
- **Storage**: Base64 TEXT in database (not binary BLOB for easier debugging)
- **Access Control**: Profile images returned only to authenticated users via API

### Foreign Key Cascade Behavior

- **ON DELETE SET NULL**: Preserves chat history analytics when user deletes account
- **Alternative Considered**: ON DELETE CASCADE (rejected - loses valuable data)
- **Privacy Note**: Anonymized sessions (user_id=NULL) retain no PII per Constitution 4.2

---

## Validation Rules Summary

### User Table

| Field | Validation | Enforced By |
|-------|------------|-------------|
| email | RFC 5322 format, unique | Application + DB UNIQUE |
| username | 3-30 alphanumeric+underscore, unique, collision handling | Application + DB UNIQUE |
| password | 8+ chars, 1 number, 1 special char, Argon2id hashed | Application |
| profile_image_url | ≤5MB decoded, JPG/PNG/WebP, magic bytes verified | Application (Pillow) |

### ChatSession Table

| Field | Validation | Enforced By |
|-------|------------|-------------|
| user_id | NULL or valid UUID in users table | DB FOREIGN KEY |

---

## Future Enhancements (Out of Scope)

1. **Soft Delete**: Add `deleted_at` timestamp for user account soft deletion
2. **Email Verification**: Add `email_verified` boolean + verification token
3. **Password Reset**: Add `reset_token` and `reset_token_expires_at` fields
4. **User Roles**: Add `role` enum (user, admin) for authorization
5. **Profile Metadata**: Add `display_name`, `bio`, `location` fields
6. **Session Metadata**: Add `device_type`, `browser` to chat_sessions (ensure no PII)

**Note**: These enhancements would require additional migrations and are not part of the current scope.

---

**Data Model Version**: 1.0.0
**Last Updated**: 2025-12-21
**Status**: ✅ Ready for Implementation
