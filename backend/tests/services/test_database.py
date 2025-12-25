"""
Unit Tests for Database Service

Tests session linking, user queries, and chat history operations.

Constitution: backend/.specify/memory/constitution.md (Section 7)
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from app.services.database import db_service
from app.models.database import User, ChatSession
from app.core.security import hash_password


@pytest.fixture
async def db_session():
    """Create database session for tests"""
    async with db_service.get_session() as session:
        yield session


@pytest.fixture
async def test_user(db_session):
    """Create a test user"""
    user = User(
        email=f"testuser{uuid4().hex[:8]}@example.com",
        username=f"testuser{uuid4().hex[:6]}",
        password_hash=hash_password("TestPass123!"),
        profile_image_url=None
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestSessionLinking:
    """Tests for linking chat sessions to users (T067)"""

    @pytest.mark.asyncio
    async def test_create_authenticated_session(self, db_session, test_user):
        """Test creating chat session linked to authenticated user"""
        # Create session linked to user
        session = ChatSession(
            session_id=uuid4(),
            user_id=test_user.id,
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow(),
            message_count=0
        )

        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Verify session is linked
        assert session.user_id == test_user.id
        assert session.user.email == test_user.email

    @pytest.mark.asyncio
    async def test_multiple_sessions_per_user(self, db_session, test_user):
        """Test user can have multiple chat sessions"""
        # Create 3 sessions for the same user
        session_ids = []
        for i in range(3):
            session = ChatSession(
                session_id=uuid4(),
                user_id=test_user.id,
                started_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow(),
                message_count=i + 1
            )
            db_session.add(session)
            session_ids.append(session.session_id)

        await db_session.commit()

        # Query user's sessions
        from sqlalchemy import select
        result = await db_session.execute(
            select(ChatSession).where(ChatSession.user_id == test_user.id)
        )
        sessions = result.scalars().all()

        assert len(sessions) == 3
        assert all(s.user_id == test_user.id for s in sessions)


class TestGuestSessions:
    """Tests for guest chat sessions (T068)"""

    @pytest.mark.asyncio
    async def test_create_guest_session(self, db_session):
        """Test creating chat session with user_id=NULL for guests"""
        # Create session without user
        session = ChatSession(
            session_id=uuid4(),
            user_id=None,  # Guest session
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow(),
            message_count=0
        )

        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Verify session is not linked to any user
        assert session.user_id is None

    @pytest.mark.asyncio
    async def test_query_guest_sessions(self, db_session):
        """Test querying guest sessions (user_id IS NULL)"""
        # Create 2 guest sessions
        guest_sessions = []
        for i in range(2):
            session = ChatSession(
                session_id=uuid4(),
                user_id=None,
                started_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow(),
                message_count=0
            )
            db_session.add(session)
            guest_sessions.append(session)

        await db_session.commit()

        # Query guest sessions
        from sqlalchemy import select
        result = await db_session.execute(
            select(ChatSession).where(ChatSession.user_id.is_(None))
        )
        sessions = result.scalars().all()

        # Should find at least our 2 guest sessions
        assert len(sessions) >= 2


class TestChatHistoryQueries:
    """Tests for chat history database queries (T069)"""

    @pytest.mark.asyncio
    async def test_get_user_sessions_ordered(self, db_session, test_user):
        """Test getting user sessions ordered by last_activity_at DESC"""
        # Create sessions with different activity times
        now = datetime.utcnow()

        sessions_data = [
            {"started_at": now - timedelta(hours=3), "last_activity": now - timedelta(hours=2)},
            {"started_at": now - timedelta(hours=2), "last_activity": now - timedelta(hours=1)},
            {"started_at": now - timedelta(hours=1), "last_activity": now},
        ]

        session_ids = []
        for data in sessions_data:
            session = ChatSession(
                session_id=uuid4(),
                user_id=test_user.id,
                started_at=data["started_at"],
                last_activity_at=data["last_activity"],
                message_count=1
            )
            db_session.add(session)
            session_ids.append(session.session_id)

        await db_session.commit()

        # Query sessions ordered by last_activity_at DESC
        from sqlalchemy import select
        result = await db_session.execute(
            select(ChatSession)
            .where(ChatSession.user_id == test_user.id)
            .order_by(ChatSession.last_activity_at.desc())
        )
        sessions = result.scalars().all()

        # Most recent activity should be first
        assert sessions[0].session_id == session_ids[2]
        assert sessions[1].session_id == session_ids[1]
        assert sessions[2].session_id == session_ids[0]

    @pytest.mark.asyncio
    async def test_pagination_with_limit_offset(self, db_session, test_user):
        """Test paginated chat history queries"""
        # Create 10 sessions
        for i in range(10):
            session = ChatSession(
                session_id=uuid4(),
                user_id=test_user.id,
                started_at=datetime.utcnow() - timedelta(minutes=10 - i),
                last_activity_at=datetime.utcnow() - timedelta(minutes=10 - i),
                message_count=i + 1
            )
            db_session.add(session)

        await db_session.commit()

        # Query first 5 sessions
        from sqlalchemy import select
        result1 = await db_session.execute(
            select(ChatSession)
            .where(ChatSession.user_id == test_user.id)
            .order_by(ChatSession.last_activity_at.desc())
            .limit(5)
            .offset(0)
        )
        page1_sessions = result1.scalars().all()

        # Query next 5 sessions
        result2 = await db_session.execute(
            select(ChatSession)
            .where(ChatSession.user_id == test_user.id)
            .order_by(ChatSession.last_activity_at.desc())
            .limit(5)
            .offset(5)
        )
        page2_sessions = result2.scalars().all()

        assert len(page1_sessions) == 5
        assert len(page2_sessions) == 5

        # Pages should be different
        page1_ids = {s.session_id for s in page1_sessions}
        page2_ids = {s.session_id for s in page2_sessions}
        assert len(page1_ids & page2_ids) == 0

    @pytest.mark.asyncio
    async def test_count_user_sessions(self, db_session, test_user):
        """Test counting total sessions for a user"""
        # Create 7 sessions
        for i in range(7):
            session = ChatSession(
                session_id=uuid4(),
                user_id=test_user.id,
                started_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow(),
                message_count=i + 1
            )
            db_session.add(session)

        await db_session.commit()

        # Count sessions
        from sqlalchemy import select, func
        result = await db_session.execute(
            select(func.count()).select_from(ChatSession).where(ChatSession.user_id == test_user.id)
        )
        count = result.scalar()

        assert count == 7


class TestUserDeletion:
    """Tests for user deletion with ON DELETE SET NULL behavior"""

    @pytest.mark.asyncio
    async def test_delete_user_preserves_sessions(self, db_session, test_user):
        """Test deleting user sets session user_id to NULL (preserves sessions)"""
        # Create session for user
        session = ChatSession(
            session_id=uuid4(),
            user_id=test_user.id,
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow(),
            message_count=1
        )
        db_session.add(session)
        await db_session.commit()

        session_id = session.session_id

        # Delete user
        await db_session.delete(test_user)
        await db_session.commit()

        # Session should still exist but with user_id=NULL
        from sqlalchemy import select
        result = await db_session.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        session_after_delete = result.scalar_one_or_none()

        assert session_after_delete is not None, "Session should still exist"
        assert session_after_delete.user_id is None, "Session user_id should be NULL"


class TestChatSessionRelationship:
    """Tests for User <-> ChatSession relationship"""

    @pytest.mark.asyncio
    async def test_user_chat_sessions_relationship(self, db_session, test_user):
        """Test accessing user's chat sessions via relationship"""
        # Create sessions for user
        for i in range(3):
            session = ChatSession(
                session_id=uuid4(),
                user_id=test_user.id,
                started_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow(),
                message_count=i + 1
            )
            db_session.add(session)

        await db_session.commit()
        await db_session.refresh(test_user)

        # Access sessions via relationship
        # Note: Need to load the relationship explicitly
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select

        result = await db_session.execute(
            select(User)
            .where(User.id == test_user.id)
            .options(selectinload(User.chat_sessions))
        )
        user_with_sessions = result.scalar_one()

        # Should have 3 sessions
        assert len(user_with_sessions.chat_sessions) == 3

    @pytest.mark.asyncio
    async def test_session_user_relationship(self, db_session, test_user):
        """Test accessing user from chat session via relationship"""
        # Create session
        session = ChatSession(
            session_id=uuid4(),
            user_id=test_user.id,
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow(),
            message_count=1
        )
        db_session.add(session)
        await db_session.commit()

        # Access user via relationship
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select

        result = await db_session.execute(
            select(ChatSession)
            .where(ChatSession.session_id == session.session_id)
            .options(selectinload(ChatSession.user))
        )
        session_with_user = result.scalar_one()

        # Should access user
        assert session_with_user.user is not None
        assert session_with_user.user.id == test_user.id
        assert session_with_user.user.email == test_user.email
