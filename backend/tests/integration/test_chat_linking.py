"""
Integration Tests for Chat Session Linking

Tests authenticated chat flow (session linked to user) and guest chat flow (user_id=NULL).

Constitution: backend/.specify/memory/constitution.md (Section 7)
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.main import app
from app.services.database import db_service
from app.models.database import User, ChatSession
from app.core.security import hash_password


@pytest.fixture
async def client():
    """Create async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session():
    """Create database session for tests"""
    async with db_service.get_session() as session:
        yield session


@pytest.fixture
async def authenticated_user(client):
    """Create and login a test user, return cookies and user data"""
    # Create user via signup
    signup_response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": f"chatlink{uuid4().hex[:8]}@example.com",
            "password": "ChatLink123!"
        }
    )

    assert signup_response.status_code == 201

    return {
        "cookies": signup_response.cookies,
        "user_data": signup_response.json()
    }


class TestAuthenticatedChatFlow:
    """Tests for authenticated chat sessions (T070)"""

    @pytest.mark.asyncio
    async def test_authenticated_chat_creates_linked_session(self, client, authenticated_user, db_session):
        """
        Test chat request from authenticated user creates session linked to user.

        Constitution Reference: FR-024 (Link sessions to users)
        """
        cookies = authenticated_user["cookies"]
        user_id = authenticated_user["user_data"]["id"]

        # Send chat request
        chat_response = await client.post(
            "/api/v1/chat",
            json={
                "query": "What is Physical AI?",
                "top_k": 3
            },
            cookies=cookies
        )

        assert chat_response.status_code == 200
        chat_data = chat_response.json()

        # Should return a session ID
        assert "session_id" in chat_data

        session_id = chat_data["session_id"]

        # Verify session is linked to user in database
        from sqlalchemy import select
        result = await db_session.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        assert session is not None, "Chat session should exist in database"
        assert str(session.user_id) == user_id, "Session should be linked to authenticated user"

    @pytest.mark.asyncio
    async def test_authenticated_chat_history_accessible(self, client, authenticated_user):
        """
        Test authenticated user can view their chat history.

        Constitution Reference: FR-028 (Chat history endpoint)
        """
        cookies = authenticated_user["cookies"]

        # Create multiple chat sessions
        for i in range(3):
            await client.post(
                "/api/v1/chat",
                json={"query": f"Test query {i}", "top_k": 3},
                cookies=cookies
            )

        # Get chat history
        history_response = await client.get(
            "/api/v1/profile/chat-history",
            cookies=cookies
        )

        assert history_response.status_code == 200
        history_data = history_response.json()

        # Should return list of sessions
        assert isinstance(history_data, list) or "sessions" in history_data
        sessions = history_data if isinstance(history_data, list) else history_data["sessions"]

        # Should have at least the 3 sessions we created
        assert len(sessions) >= 3

        # Each session should have required fields
        for session in sessions[:3]:
            assert "session_id" in session
            assert "started_at" in session
            assert "last_activity_at" in session

    @pytest.mark.asyncio
    async def test_chat_sessions_persist_across_logins(self, client, db_session):
        """
        Test chat sessions persist when user logs out and logs back in.

        Constitution Reference: FR-026 (Session persistence)
        """
        # Create user
        email = f"persist{uuid4().hex[:8]}@example.com"
        password = "Persist123!"

        signup_response = await client.post(
            "/api/v1/auth/signup",
            json={"email": email, "password": password}
        )
        assert signup_response.status_code == 201

        # Create chat session while logged in
        chat_response1 = await client.post(
            "/api/v1/chat",
            json={"query": "First query", "top_k": 3},
            cookies=signup_response.cookies
        )
        assert chat_response1.status_code == 200
        session_id_1 = chat_response1.json()["session_id"]

        # Logout
        await client.post("/api/v1/auth/logout", cookies=signup_response.cookies)

        # Login again
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        assert login_response.status_code == 200

        # Get chat history
        history_response = await client.get(
            "/api/v1/profile/chat-history",
            cookies=login_response.cookies
        )
        assert history_response.status_code == 200

        # Previous session should be in history
        sessions = history_response.json()
        if isinstance(sessions, dict):
            sessions = sessions.get("sessions", [])

        session_ids = [s["session_id"] for s in sessions]
        assert session_id_1 in session_ids, "Session should persist across logins"


class TestGuestChatFlow:
    """Tests for guest chat sessions (T071)"""

    @pytest.mark.asyncio
    async def test_guest_chat_creates_unlinked_session(self, client, db_session):
        """
        Test chat request from guest (no auth) creates session with user_id=NULL.

        Constitution Reference: FR-025 (Guest chat support)
        """
        # Send chat request without authentication
        chat_response = await client.post(
            "/api/v1/chat",
            json={
                "query": "What is robotics?",
                "top_k": 3
            }
        )

        assert chat_response.status_code == 200
        chat_data = chat_response.json()

        assert "session_id" in chat_data
        session_id = chat_data["session_id"]

        # Verify session exists with user_id=NULL
        from sqlalchemy import select
        result = await db_session.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        assert session is not None, "Guest chat session should exist in database"
        assert session.user_id is None, "Guest session should have user_id=NULL"

    @pytest.mark.asyncio
    async def test_guest_chat_continues_session(self, client):
        """
        Test guest can continue chat in same session.

        Constitution Reference: FR-031 (Backward compatibility)
        """
        # First message (creates session)
        chat_response1 = await client.post(
            "/api/v1/chat",
            json={"query": "First question", "top_k": 3}
        )
        assert chat_response1.status_code == 200
        session_id = chat_response1.json()["session_id"]

        # Second message (continues session)
        chat_response2 = await client.post(
            "/api/v1/chat",
            json={
                "query": "Follow-up question",
                "session_id": session_id,
                "top_k": 3
            }
        )
        assert chat_response2.status_code == 200

        # Should use same session
        assert chat_response2.json()["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_existing_guest_sessions_still_work(self, client, db_session):
        """
        Test that existing guest sessions (from before auth feature) still work.

        This ensures backward compatibility per FR-031.

        Constitution Reference: FR-031 (Backward compatibility)
        """
        # Manually create a guest session (simulating pre-existing data)
        from sqlalchemy import insert
        from datetime import datetime

        guest_session_id = uuid4()

        await db_session.execute(
            insert(ChatSession).values(
                session_id=guest_session_id,
                user_id=None,  # Guest session
                started_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow(),
                message_count=0
            )
        )
        await db_session.commit()

        # Try to continue this guest session
        chat_response = await client.post(
            "/api/v1/chat",
            json={
                "query": "Continuing old guest session",
                "session_id": str(guest_session_id),
                "top_k": 3
            }
        )

        assert chat_response.status_code == 200
        assert chat_response.json()["session_id"] == str(guest_session_id)


class TestChatHistoryEndpoint:
    """Tests for GET /api/v1/profile/chat-history (T069)"""

    @pytest.mark.asyncio
    async def test_chat_history_requires_authentication(self, client):
        """Test chat history endpoint requires authentication"""
        response = await client.get("/api/v1/profile/chat-history")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_chat_history_pagination(self, client, authenticated_user, db_session):
        """
        Test chat history supports pagination with limit/offset.

        Constitution Reference: FR-029 (Pagination)
        """
        cookies = authenticated_user["cookies"]

        # Create 10 chat sessions
        for i in range(10):
            await client.post(
                "/api/v1/chat",
                json={"query": f"Query {i}", "top_k": 3},
                cookies=cookies
            )

        # Get first 5 sessions
        response1 = await client.get(
            "/api/v1/profile/chat-history?limit=5&offset=0",
            cookies=cookies
        )
        assert response1.status_code == 200
        data1 = response1.json()
        sessions1 = data1 if isinstance(data1, list) else data1.get("sessions", [])
        assert len(sessions1) <= 5

        # Get next 5 sessions
        response2 = await client.get(
            "/api/v1/profile/chat-history?limit=5&offset=5",
            cookies=cookies
        )
        assert response2.status_code == 200
        data2 = response2.json()
        sessions2 = data2 if isinstance(data2, list) else data2.get("sessions", [])

        # Should be different sessions
        session_ids_1 = [s["session_id"] for s in sessions1]
        session_ids_2 = [s["session_id"] for s in sessions2]

        # No overlap between pages
        assert len(set(session_ids_1) & set(session_ids_2)) == 0

    @pytest.mark.asyncio
    async def test_chat_history_ordered_by_recent_activity(self, client, authenticated_user):
        """
        Test chat history is ordered by last_activity_at DESC.

        Constitution Reference: FR-028 (Ordering)
        """
        cookies = authenticated_user["cookies"]

        # Create sessions with delays
        import asyncio

        session_ids = []
        for i in range(3):
            response = await client.post(
                "/api/v1/chat",
                json={"query": f"Query {i}", "top_k": 3},
                cookies=cookies
            )
            session_ids.append(response.json()["session_id"])
            await asyncio.sleep(0.1)  # Small delay between sessions

        # Get history
        history_response = await client.get(
            "/api/v1/profile/chat-history",
            cookies=cookies
        )
        assert history_response.status_code == 200

        sessions = history_response.json()
        if isinstance(sessions, dict):
            sessions = sessions.get("sessions", [])

        # Most recent session should be first
        # (last created session is session_ids[-1])
        assert sessions[0]["session_id"] == session_ids[-1]

    @pytest.mark.asyncio
    async def test_chat_history_only_shows_user_sessions(self, client, db_session):
        """
        Test chat history only returns sessions belonging to the current user.

        Constitution Reference: FR-027 (User isolation)
        """
        # Create two users
        user1_response = await client.post(
            "/api/v1/auth/signup",
            json={"email": f"user1{uuid4().hex[:8]}@example.com", "password": "User1Pass123!"}
        )
        user1_cookies = user1_response.cookies

        user2_response = await client.post(
            "/api/v1/auth/signup",
            json={"email": f"user2{uuid4().hex[:8]}@example.com", "password": "User2Pass123!"}
        )
        user2_cookies = user2_response.cookies

        # User 1 creates 2 chat sessions
        for i in range(2):
            await client.post(
                "/api/v1/chat",
                json={"query": f"User 1 query {i}", "top_k": 3},
                cookies=user1_cookies
            )

        # User 2 creates 3 chat sessions
        user2_session_ids = []
        for i in range(3):
            response = await client.post(
                "/api/v1/chat",
                json={"query": f"User 2 query {i}", "top_k": 3},
                cookies=user2_cookies
            )
            user2_session_ids.append(response.json()["session_id"])

        # User 2 gets chat history
        history_response = await client.get(
            "/api/v1/profile/chat-history",
            cookies=user2_cookies
        )
        assert history_response.status_code == 200

        sessions = history_response.json()
        if isinstance(sessions, dict):
            sessions = sessions.get("sessions", [])

        # Should only see User 2's sessions
        assert len(sessions) == 3
        returned_session_ids = [s["session_id"] for s in sessions]
        assert set(returned_session_ids) == set(user2_session_ids)
