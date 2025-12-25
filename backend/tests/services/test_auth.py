"""
Unit Tests for Authentication Service

Tests username generation, password hashing, and JWT token creation.

Constitution: backend/.specify/memory/constitution.md (Section 7 - 80% coverage)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.auth import AuthService
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from app.models.database import User


class TestUsernameGeneration:
    """Tests for username derivation from email (T016)"""

    def test_basic_username_derivation(self):
        """Test basic email to username conversion"""
        assert AuthService.derive_username("hamza@gmail.com") == "hamza"
        assert AuthService.derive_username("john.doe@example.com") == "johndoe"
        assert AuthService.derive_username("test_user@test.com") == "test_user"

    def test_username_with_special_characters(self):
        """Test username derivation removes special characters"""
        assert AuthService.derive_username("user+tag@gmail.com") == "usertag"
        assert AuthService.derive_username("my-email@test.com") == "myemail"
        assert AuthService.derive_username("test.user.123@example.com") == "testuser123"

    def test_username_lowercase_conversion(self):
        """Test usernames are converted to lowercase"""
        assert AuthService.derive_username("HAMZA@gmail.com") == "hamza"
        assert AuthService.derive_username("JohnDoe@example.com") == "johndoe"

    def test_username_empty_after_sanitization(self):
        """Test fallback to 'user' when sanitization removes everything"""
        assert AuthService.derive_username("@@@gmail.com") == "user"
        assert AuthService.derive_username("...@test.com") == "user"

    @pytest.mark.asyncio
    async def test_username_collision_resolution(self):
        """Test username collision resolution appends numbers"""
        # Mock database session
        db_mock = AsyncMock()

        # Mock existing users: hamza exists, hamza2 doesn't
        async def mock_execute(query):
            result_mock = MagicMock()
            # First call: hamza exists
            # Second call: hamza2 doesn't exist
            result_mock.scalar_one_or_none.side_effect = [
                User(username="hamza"),  # hamza exists
                None  # hamza2 available
            ]
            return result_mock

        db_mock.execute = mock_execute

        # Should return hamza2
        result = await AuthService.resolve_username_collision(db_mock, "hamza")
        assert result == "hamza2"

    @pytest.mark.asyncio
    async def test_username_no_collision(self):
        """Test username returned as-is when no collision"""
        db_mock = AsyncMock()

        async def mock_execute(query):
            result_mock = MagicMock()
            result_mock.scalar_one_or_none.return_value = None
            return result_mock

        db_mock.execute = mock_execute

        result = await AuthService.resolve_username_collision(db_mock, "uniqueuser")
        assert result == "uniqueuser"


class TestPasswordHashing:
    """Tests for password hashing and verification (T017)"""

    def test_password_hashing_creates_hash(self):
        """Test password is hashed (not stored as plain text)"""
        password = "SecurePass123!"
        password_hash = hash_password(password)

        # Hash should not equal original password
        assert password_hash != password

        # Hash should start with Argon2id identifier
        assert password_hash.startswith("$argon2id$")

        # Hash should be non-empty
        assert len(password_hash) > 50

    def test_password_hashing_is_deterministic_with_different_salts(self):
        """Test same password produces different hashes (random salt)"""
        password = "SecurePass123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Different salts = different hashes
        assert hash1 != hash2

    def test_password_verification_correct_password(self):
        """Test correct password verification succeeds"""
        password = "SecurePass123!"
        password_hash = hash_password(password)

        # Correct password should verify
        assert verify_password(password_hash, password) is True

    def test_password_verification_incorrect_password(self):
        """Test incorrect password verification fails"""
        password = "SecurePass123!"
        password_hash = hash_password(password)

        # Wrong password should fail
        assert verify_password(password_hash, "WrongPassword!") is False
        assert verify_password(password_hash, "securepass123!") is False  # case sensitive

    def test_password_hashing_performance(self):
        """Test password hashing completes within performance target (<200ms)"""
        import time

        password = "SecurePass123!"

        start = time.perf_counter()
        hash_password(password)
        duration = (time.perf_counter() - start) * 1000  # ms

        # Should complete in under 200ms (SC-011 requirement)
        assert duration < 200, f"Password hashing took {duration:.2f}ms (expected <200ms)"

    def test_password_verification_performance(self):
        """Test password verification completes within performance target (<200ms)"""
        import time

        password = "SecurePass123!"
        password_hash = hash_password(password)

        start = time.perf_counter()
        verify_password(password_hash, password)
        duration = (time.perf_counter() - start) * 1000  # ms

        # Should complete in under 200ms (SC-011 requirement)
        assert duration < 200, f"Password verification took {duration:.2f}ms (expected <200ms)"


class TestJWTTokens:
    """Tests for JWT token creation and validation (T018)"""

    def test_access_token_creation(self):
        """Test JWT access token is created successfully"""
        user_id = uuid4()
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)

        # Token should be non-empty string
        assert isinstance(token, str)
        assert len(token) > 50

        # Token should have JWT structure (header.payload.signature)
        assert token.count('.') == 2

    def test_refresh_token_creation(self):
        """Test JWT refresh token is created successfully"""
        user_id = uuid4()

        token = create_refresh_token(user_id=user_id)

        # Token should be non-empty string
        assert isinstance(token, str)
        assert len(token) > 50
        assert token.count('.') == 2

    def test_access_token_verification(self):
        """Test access token can be verified and decoded"""
        user_id = uuid4()
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = verify_token(token, token_type="access")

        # Payload should contain user info
        assert payload["sub"] == str(user_id)
        assert payload["email"] == email
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_refresh_token_verification(self):
        """Test refresh token can be verified and decoded"""
        user_id = uuid4()

        token = create_refresh_token(user_id=user_id)
        payload = verify_token(token, token_type="refresh")

        # Payload should contain user ID
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload

    def test_token_type_mismatch_raises_error(self):
        """Test verifying access token as refresh token fails"""
        from fastapi import HTTPException

        user_id = uuid4()
        access_token = create_access_token(user_id=user_id, email="test@example.com")

        # Should raise HTTPException for wrong token type
        with pytest.raises(HTTPException) as exc_info:
            verify_token(access_token, token_type="refresh")

        assert exc_info.value.status_code == 401
        assert "Invalid token type" in exc_info.value.detail

    def test_invalid_token_raises_error(self):
        """Test verifying invalid token raises error"""
        from fastapi import HTTPException

        invalid_token = "invalid.token.string"

        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token, token_type="access")

        assert exc_info.value.status_code == 401

    def test_jwt_token_performance(self):
        """Test JWT generation completes within performance target (<50ms)"""
        import time

        user_id = uuid4()
        email = "test@example.com"

        start = time.perf_counter()
        create_access_token(user_id=user_id, email=email)
        duration = (time.perf_counter() - start) * 1000  # ms

        # Should complete in under 50ms (SC-012 requirement)
        assert duration < 50, f"JWT generation took {duration:.2f}ms (expected <50ms)"

    def test_jwt_validation_performance(self):
        """Test JWT validation completes within performance target (<50ms)"""
        import time

        user_id = uuid4()
        email = "test@example.com"
        token = create_access_token(user_id=user_id, email=email)

        start = time.perf_counter()
        verify_token(token, token_type="access")
        duration = (time.perf_counter() - start) * 1000  # ms

        # Should complete in under 50ms (SC-012 requirement)
        assert duration < 50, f"JWT validation took {duration:.2f}ms (expected <50ms)"
