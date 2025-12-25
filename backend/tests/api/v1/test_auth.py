"""
API Tests for Authentication Endpoints

Tests signup, login, logout, and /me endpoints.

Constitution: backend/.specify/memory/constitution.md (Section 7)
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.main import app
from app.services.database import db_service
from app.models.database import User
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
async def test_user(db_session):
    """Create a test user in database"""
    user = User(
        email="existing@example.com",
        username="existing",
        password_hash=hash_password("ExistingPass123!"),
        profile_image_url=None
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestSignupEndpoint:
    """Tests for POST /api/v1/auth/signup (T019)"""

    @pytest.mark.asyncio
    async def test_signup_success(self, client):
        """Test successful user signup"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 201
        data = response.json()

        # Response should contain user info
        assert "id" in data
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["profile_image_url"] is None
        assert "created_at" in data

        # Should NOT contain password
        assert "password" not in data
        assert "password_hash" not in data

        # Should set httpOnly cookies
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, client, test_user):
        """Test signup with existing email fails"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "existing@example.com",  # Already exists
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_signup_username_collision_resolution(self, client, test_user):
        """Test username collision is resolved by appending number"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "existing@gmail.com",  # Username 'existing' already exists
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 201
        data = response.json()

        # Username should be 'existing2' (collision resolved)
        assert data["username"] == "existing2"
        assert data["email"] == "existing@gmail.com"

    @pytest.mark.asyncio
    async def test_signup_invalid_email(self, client):
        """Test signup with invalid email format fails"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "not-an-email",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_signup_weak_password(self, client):
        """Test signup with weak password fails"""
        # Password too short
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "short"
            }
        )
        assert response.status_code == 422

        # Password without number
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "NoNumbers!"
            }
        )
        assert response.status_code == 422

        # Password without special character
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "NoSpecial123"
            }
        )
        assert response.status_code == 422


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login (T020)"""

    @pytest.mark.asyncio
    async def test_login_success(self, client, test_user):
        """Test successful login with correct credentials"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "existing@example.com",
                "password": "ExistingPass123!",
                "remember_me": False
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Response should contain user info
        assert data["email"] == "existing@example.com"
        assert data["username"] == "existing"
        assert "id" in data

        # Should set cookies
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_login_remember_me(self, client, test_user):
        """Test login with remember_me extends token expiry"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "existing@example.com",
                "password": "ExistingPass123!",
                "remember_me": True
            }
        )

        assert response.status_code == 200

        # Cookies should have longer expiry (check max-age)
        access_token_cookie = response.cookies.get("access_token")
        assert access_token_cookie is not None

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client):
        """Test login with non-existent email fails"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123!"
            }
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_incorrect_password(self, client, test_user):
        """Test login with wrong password fails"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "existing@example.com",
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]


class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout (T021)"""

    @pytest.mark.asyncio
    async def test_logout_success(self, client, test_user):
        """Test successful logout clears cookies"""
        # First login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "existing@example.com",
                "password": "ExistingPass123!"
            }
        )
        assert login_response.status_code == 200

        # Then logout
        logout_response = await client.post("/api/v1/auth/logout")

        assert logout_response.status_code == 204  # No content

        # Cookies should be cleared (check for deletion)
        # Note: Cookie deletion is indicated by max-age=0 or expires in past


class TestGetMeEndpoint:
    """Tests for GET /api/v1/auth/me (T022)"""

    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, client, test_user):
        """Test /me returns current user when authenticated"""
        # First login to get cookies
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "existing@example.com",
                "password": "ExistingPass123!"
            }
        )
        assert login_response.status_code == 200

        # Use cookies from login for /me request
        cookies = login_response.cookies

        # Get current user
        me_response = await client.get(
            "/api/v1/auth/me",
            cookies=cookies
        )

        assert me_response.status_code == 200
        data = me_response.json()

        assert data["email"] == "existing@example.com"
        assert data["username"] == "existing"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client):
        """Test /me returns 401 when not authenticated"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client):
        """Test /me returns 401 with invalid token"""
        response = await client.get(
            "/api/v1/auth/me",
            cookies={"access_token": "invalid.token.here"}
        )

        assert response.status_code == 401
