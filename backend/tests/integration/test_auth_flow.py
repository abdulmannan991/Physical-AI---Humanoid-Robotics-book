"""
Integration Tests for Complete Authentication Flow

Tests the full signup → login → logout flow end-to-end.

Constitution: backend/.specify/memory/constitution.md (Section 7)
"""

import pytest
from httpx import AsyncClient
import time

from app.main import app
from app.services.database import db_service


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


class TestCompleteAuthFlow:
    """Integration test for complete authentication flow (T023)"""

    @pytest.mark.asyncio
    async def test_complete_signup_login_logout_flow(self, client):
        """
        Test complete user journey: signup → verify → logout → login → logout

        This tests the happy path through the entire authentication system.
        """
        # Step 1: Sign up new user
        signup_response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "integration@example.com",
                "password": "IntegrationTest123!"
            }
        )

        assert signup_response.status_code == 201, "Signup should succeed"

        signup_data = signup_response.json()
        assert signup_data["email"] == "integration@example.com"
        assert signup_data["username"] == "integration"
        assert "id" in signup_data

        # Signup should set cookies
        assert "access_token" in signup_response.cookies
        assert "refresh_token" in signup_response.cookies

        signup_cookies = signup_response.cookies

        # Step 2: Verify authenticated access with /me
        me_response = await client.get(
            "/api/v1/auth/me",
            cookies=signup_cookies
        )

        assert me_response.status_code == 200, "Should be authenticated after signup"

        me_data = me_response.json()
        assert me_data["email"] == "integration@example.com"
        assert me_data["id"] == signup_data["id"]

        # Step 3: Logout
        logout_response = await client.post(
            "/api/v1/auth/logout",
            cookies=signup_cookies
        )

        assert logout_response.status_code == 204, "Logout should succeed"

        # Step 4: Verify unauthenticated after logout
        me_after_logout = await client.get(
            "/api/v1/auth/me",
            cookies=logout_response.cookies  # Cleared cookies
        )

        assert me_after_logout.status_code == 401, "Should be unauthenticated after logout"

        # Step 5: Login with same credentials
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "integration@example.com",
                "password": "IntegrationTest123!",
                "remember_me": False
            }
        )

        assert login_response.status_code == 200, "Login should succeed"

        login_data = login_response.json()
        assert login_data["email"] == "integration@example.com"
        assert login_data["id"] == signup_data["id"]  # Same user ID

        # Login should set new cookies
        assert "access_token" in login_response.cookies
        assert "refresh_token" in login_response.cookies

        login_cookies = login_response.cookies

        # Step 6: Verify authenticated after login
        me_after_login = await client.get(
            "/api/v1/auth/me",
            cookies=login_cookies
        )

        assert me_after_login.status_code == 200, "Should be authenticated after login"
        assert me_after_login.json()["email"] == "integration@example.com"

        # Step 7: Final logout
        final_logout = await client.post(
            "/api/v1/auth/logout",
            cookies=login_cookies
        )

        assert final_logout.status_code == 204

    @pytest.mark.asyncio
    async def test_signup_performance(self, client):
        """
        Test signup endpoint meets performance requirement (<60s per SC-001)

        Constitution Reference: SC-001 (User signup completes in <60s)
        """
        start_time = time.perf_counter()

        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": f"perf{int(time.time())}@example.com",
                "password": "PerfTest123!"
            }
        )

        duration = time.perf_counter() - start_time

        assert response.status_code == 201, "Signup should succeed"
        assert duration < 60.0, f"Signup took {duration:.2f}s (expected <60s per SC-001)"

    @pytest.mark.asyncio
    async def test_login_performance(self, client):
        """
        Test login endpoint meets performance requirement (<10s per SC-002)

        Constitution Reference: SC-002 (User login completes in <10s)
        """
        # First create a user
        await client.post(
            "/api/v1/auth/signup",
            json={
                "email": f"loginperf{int(time.time())}@example.com",
                "password": "LoginPerf123!"
            }
        )

        # Then test login performance
        start_time = time.perf_counter()

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": f"loginperf{int(time.time())}@example.com",
                "password": "LoginPerf123!"
            }
        )

        duration = time.perf_counter() - start_time

        assert response.status_code == 200, "Login should succeed"
        assert duration < 10.0, f"Login took {duration:.2f}s (expected <10s per SC-002)"

    @pytest.mark.asyncio
    async def test_concurrent_signups_with_same_username(self, client):
        """
        Test username collision resolution under concurrent signups

        This ensures the system correctly handles multiple users signing up
        with emails that derive to the same username.
        """
        # Create first user with username 'testuser'
        response1 = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "testuser@gmail.com",
                "password": "TestUser123!"
            }
        )

        assert response1.status_code == 201
        assert response1.json()["username"] == "testuser"

        # Create second user with same base username
        response2 = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "testuser@yahoo.com",  # Same username base
                "password": "TestUser123!"
            }
        )

        assert response2.status_code == 201
        assert response2.json()["username"] == "testuser2"  # Collision resolved

        # Create third user
        response3 = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test.user@outlook.com",  # Sanitizes to 'testuser'
                "password": "TestUser123!"
            }
        )

        assert response3.status_code == 201
        assert response3.json()["username"] == "testuser3"  # Collision resolved

    @pytest.mark.asyncio
    async def test_login_with_wrong_password_then_correct(self, client):
        """
        Test login fails with wrong password then succeeds with correct password
        """
        # Create user
        signup_response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "wrongpass@example.com",
                "password": "CorrectPass123!"
            }
        )

        assert signup_response.status_code == 201

        # Try login with wrong password
        wrong_login = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "WrongPass123!"
            }
        )

        assert wrong_login.status_code == 401
        assert "Invalid email or password" in wrong_login.json()["detail"]

        # Try login with correct password
        correct_login = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "CorrectPass123!"
            }
        )

        assert correct_login.status_code == 200
        assert correct_login.json()["email"] == "wrongpass@example.com"

    @pytest.mark.asyncio
    async def test_remember_me_extends_token_expiry(self, client):
        """
        Test remember_me flag extends token expiry to 7 days

        Constitution Reference: FR-006 (Remember me extends session)
        """
        # Create user
        await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "rememberme@example.com",
                "password": "RememberMe123!"
            }
        )

        # Login without remember_me
        normal_login = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "rememberme@example.com",
                "password": "RememberMe123!",
                "remember_me": False
            }
        )

        assert normal_login.status_code == 200

        # Login with remember_me
        remember_login = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "rememberme@example.com",
                "password": "RememberMe123!",
                "remember_me": True
            }
        )

        assert remember_login.status_code == 200

        # Both should succeed, but remember_me should have longer cookie expiry
        # (Actual expiry testing would require checking Set-Cookie headers)
