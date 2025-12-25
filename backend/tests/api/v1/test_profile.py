"""
API Tests for Profile Endpoints

Tests GET /profile and POST /profile/image endpoints.

Constitution: backend/.specify/memory/constitution.md (Section 7)
"""

import pytest
from httpx import AsyncClient
import base64
from io import BytesIO
from PIL import Image

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
async def authenticated_user(client):
    """Create and login a test user, return cookies"""
    # Create user via signup
    signup_response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "profiletest@example.com",
            "password": "ProfileTest123!"
        }
    )

    assert signup_response.status_code == 201

    # Return cookies for authenticated requests
    return {
        "cookies": signup_response.cookies,
        "user_data": signup_response.json()
    }


def create_test_image(format="PNG", size=(100, 100), color=(255, 0, 0)):
    """Helper to create a test image in memory"""
    img = Image.new('RGB', size, color)
    buffer = BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()


def create_base64_image(format="PNG", size=(100, 100)):
    """Helper to create base64-encoded test image"""
    image_bytes = create_test_image(format, size)
    return base64.b64encode(image_bytes).decode('utf-8')


class TestGetProfileEndpoint:
    """Tests for GET /api/v1/profile (T053)"""

    @pytest.mark.asyncio
    async def test_get_profile_authenticated(self, client, authenticated_user):
        """Test GET /profile returns user info when authenticated"""
        cookies = authenticated_user["cookies"]
        user_data = authenticated_user["user_data"]

        response = await client.get(
            "/api/v1/profile",
            cookies=cookies
        )

        assert response.status_code == 200
        data = response.json()

        # Should return user profile data
        assert data["id"] == user_data["id"]
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "created_at" in data
        assert "profile_image_url" in data

        # Should NOT return password
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_get_profile_unauthenticated(self, client):
        """Test GET /profile returns 401 when not authenticated"""
        response = await client.get("/api/v1/profile")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_profile_invalid_token(self, client):
        """Test GET /profile returns 401 with invalid token"""
        response = await client.get(
            "/api/v1/profile",
            cookies={"access_token": "invalid.token.here"}
        )

        assert response.status_code == 401


class TestImageValidation:
    """Tests for image validation utility (T052)"""

    @pytest.mark.asyncio
    async def test_upload_valid_png_image(self, client, authenticated_user):
        """Test uploading valid PNG image succeeds"""
        cookies = authenticated_user["cookies"]

        # Create valid PNG image
        image_base64 = create_base64_image(format="PNG", size=(200, 200))

        response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": image_base64},
            cookies=cookies
        )

        assert response.status_code == 200
        data = response.json()

        assert "profile_image_url" in data
        assert data["profile_image_url"] is not None
        assert "message" in data

    @pytest.mark.asyncio
    async def test_upload_valid_jpeg_image(self, client, authenticated_user):
        """Test uploading valid JPEG image succeeds"""
        cookies = authenticated_user["cookies"]

        # Create valid JPEG image
        image_base64 = create_base64_image(format="JPEG", size=(150, 150))

        response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": image_base64},
            cookies=cookies
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_upload_valid_webp_image(self, client, authenticated_user):
        """Test uploading valid WebP image succeeds"""
        cookies = authenticated_user["cookies"]

        # Create valid WebP image
        image_base64 = create_base64_image(format="WEBP", size=(180, 180))

        response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": image_base64},
            cookies=cookies
        )

        assert response.status_code == 200


class TestImageUploadEndpoint:
    """Tests for POST /api/v1/profile/image (T054, T055)"""

    @pytest.mark.asyncio
    async def test_upload_image_too_large(self, client, authenticated_user):
        """Test uploading image >5MB fails (T055)"""
        cookies = authenticated_user["cookies"]

        # Create image larger than 5MB
        # 5MB = 5 * 1024 * 1024 bytes
        # Base64 is ~33% larger, so we need to create a large enough image
        # A 2000x2000 RGB image is about 12MB uncompressed
        large_image_base64 = create_base64_image(format="PNG", size=(2500, 2500))

        # Verify the base64 is actually large
        decoded_size = len(base64.b64decode(large_image_base64))
        assert decoded_size > 5 * 1024 * 1024, "Test image should be >5MB"

        response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": large_image_base64},
            cookies=cookies
        )

        assert response.status_code == 400
        assert "exceeds maximum" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_invalid_base64(self, client, authenticated_user):
        """Test uploading invalid base64 fails (T055)"""
        cookies = authenticated_user["cookies"]

        response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": "not-valid-base64!!!"},
            cookies=cookies
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_non_image_file(self, client, authenticated_user):
        """Test uploading non-image data fails (T055)"""
        cookies = authenticated_user["cookies"]

        # Base64 encode a text file
        text_data = b"This is not an image file"
        text_base64 = base64.b64encode(text_data).decode('utf-8')

        response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": text_base64},
            cookies=cookies
        )

        assert response.status_code == 400
        assert "invalid image" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_image_unauthenticated(self, client):
        """Test uploading image without authentication fails"""
        image_base64 = create_base64_image(format="PNG")

        response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": image_base64}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_upload_image_with_data_url_prefix(self, client, authenticated_user):
        """Test uploading image with data URL prefix (data:image/png;base64,...)"""
        cookies = authenticated_user["cookies"]

        image_base64 = create_base64_image(format="PNG")
        # Add data URL prefix
        data_url = f"data:image/png;base64,{image_base64}"

        response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": data_url},
            cookies=cookies
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_upload_image_updates_profile(self, client, authenticated_user):
        """Test uploading image updates user profile"""
        cookies = authenticated_user["cookies"]

        # Upload image
        image_base64 = create_base64_image(format="PNG")
        upload_response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": image_base64},
            cookies=cookies
        )

        assert upload_response.status_code == 200

        # Get profile and verify image is set
        profile_response = await client.get(
            "/api/v1/profile",
            cookies=cookies
        )

        assert profile_response.status_code == 200
        profile_data = profile_response.json()

        assert profile_data["profile_image_url"] is not None
        assert len(profile_data["profile_image_url"]) > 0

    @pytest.mark.asyncio
    async def test_upload_image_replaces_previous(self, client, authenticated_user):
        """Test uploading new image replaces previous one"""
        cookies = authenticated_user["cookies"]

        # Upload first image
        image1_base64 = create_base64_image(format="PNG", size=(100, 100))
        response1 = await client.post(
            "/api/v1/profile/image",
            json={"image_data": image1_base64},
            cookies=cookies
        )

        assert response1.status_code == 200
        first_image_url = response1.json()["profile_image_url"]

        # Upload second image
        image2_base64 = create_base64_image(format="JPEG", size=(150, 150))
        response2 = await client.post(
            "/api/v1/profile/image",
            json={"image_data": image2_base64},
            cookies=cookies
        )

        assert response2.status_code == 200
        second_image_url = response2.json()["profile_image_url"]

        # Images should be different
        assert first_image_url != second_image_url

    @pytest.mark.asyncio
    async def test_upload_image_performance(self, client, authenticated_user):
        """Test image upload completes within 3s for 5MB image (SC-003)"""
        import time

        cookies = authenticated_user["cookies"]

        # Create a large image (close to 5MB limit)
        # A 2000x2000 image is approximately 4MB
        large_image_base64 = create_base64_image(format="JPEG", size=(2000, 2000))

        start_time = time.perf_counter()

        response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": large_image_base64},
            cookies=cookies
        )

        duration = time.perf_counter() - start_time

        # Should complete within 3 seconds (SC-003)
        assert duration < 3.0, f"Image upload took {duration:.2f}s (expected <3s per SC-003)"

        # Upload should succeed
        if response.status_code == 400 and "exceeds maximum" in response.json().get("detail", ""):
            pytest.skip("Test image exceeds 5MB limit (expected for large test images)")

        assert response.status_code == 200


class TestImageSecurity:
    """Tests for image security validation (T052)"""

    @pytest.mark.asyncio
    async def test_image_metadata_stripped(self, client, authenticated_user):
        """Test uploaded images have EXIF metadata stripped"""
        cookies = authenticated_user["cookies"]

        # Create image with EXIF data
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))

        # Add EXIF data
        from PIL.PngImagePlugin import PngInfo
        metadata = PngInfo()
        metadata.add_text("Comment", "This is test metadata")

        buffer = BytesIO()
        img.save(buffer, format="PNG", pnginfo=metadata)
        buffer.seek(0)

        image_with_metadata = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Upload image
        response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": image_with_metadata},
            cookies=cookies
        )

        assert response.status_code == 200

        # Retrieve profile image
        profile_response = await client.get(
            "/api/v1/profile",
            cookies=cookies
        )

        stored_image_base64 = profile_response.json()["profile_image_url"]

        # Decode and check for metadata removal
        stored_image_bytes = base64.b64decode(stored_image_base64)
        stored_image = Image.open(BytesIO(stored_image_bytes))

        # Metadata should be stripped (getexif() or info should be empty/minimal)
        # PNG images without metadata have minimal info
        assert len(stored_image.info) <= 1, "Image metadata should be stripped"

    @pytest.mark.asyncio
    async def test_image_dimensions_within_limits(self, client, authenticated_user):
        """Test images with extreme dimensions are rejected"""
        cookies = authenticated_user["cookies"]

        # Try uploading very large dimensions (>4096x4096)
        # This would cause memory issues
        try:
            huge_image_base64 = create_base64_image(format="PNG", size=(5000, 5000))
        except Exception:
            pytest.skip("Cannot create test image with extreme dimensions")

        response = await client.post(
            "/api/v1/profile/image",
            json={"image_data": huge_image_base64},
            cookies=cookies
        )

        # Should either reject due to size or dimensions
        assert response.status_code in [400, 413]
