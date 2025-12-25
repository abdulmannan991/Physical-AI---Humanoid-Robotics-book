"""
Authentication Service

Handles user creation, authentication, and username collision resolution.

Constitution: backend/.specify/memory/constitution.md (Section 5.3 - Security)
"""

import re
import base64
import io
import logging
from typing import Optional
from uuid import UUID
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password
from app.models.database import User

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for user authentication operations.

    Handles:
    - User creation with username collision resolution
    - Password authentication
    - Username derivation from email
    - Profile image validation and processing
    """

    # Maximum image size: 5MB
    MAX_IMAGE_SIZE_MB = 5
    MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

    # Allowed image formats
    ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP'}

    # Magic bytes for format validation
    MAGIC_BYTES = {
        'JPEG': [b'\xFF\xD8\xFF'],
        'PNG': [b'\x89PNG\r\n\x1a\n'],
        'WEBP': [b'RIFF']
    }

    @staticmethod
    def validate_profile_image(base64_data: str) -> str:
        """
        Validate and process profile image upload.

        Security checks:
        1. Size validation (≤5MB)
        2. Format validation (JPG/PNG/WebP only)
        3. Magic bytes verification (prevent format spoofing)
        4. Re-encoding to strip EXIF metadata

        Args:
            base64_data: Base64-encoded image string (may include data URI prefix)

        Returns:
            str: Clean base64-encoded image with data URI prefix

        Raises:
            HTTPException: 400 if validation fails

        Constitution Reference: FR-019, FR-020, FR-021
        """
        try:
            # Strip data URI prefix if present
            if ',' in base64_data:
                base64_data = base64_data.split(',', 1)[1]

            # Decode base64
            try:
                image_bytes = base64.b64decode(base64_data)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid base64 encoding"
                )

            # Check size (≤5MB)
            if len(image_bytes) > AuthService.MAX_IMAGE_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image size exceeds {AuthService.MAX_IMAGE_SIZE_MB}MB limit"
                )

            # Verify magic bytes
            valid_magic = False
            for format_type, magic_list in AuthService.MAGIC_BYTES.items():
                for magic in magic_list:
                    if image_bytes.startswith(magic):
                        valid_magic = True
                        break
                if valid_magic:
                    break

            if not valid_magic:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image format (JPG/PNG/WebP only)"
                )

            # Open and validate with Pillow
            try:
                image = Image.open(io.BytesIO(image_bytes))
                image.verify()  # Verify integrity
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Corrupted or invalid image file"
                )

            # Re-open for processing (verify() consumes the file)
            image = Image.open(io.BytesIO(image_bytes))

            # Check format
            if image.format not in AuthService.ALLOWED_FORMATS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported format: {image.format}. Allowed: JPG, PNG, WebP"
                )

            # Re-encode to strip EXIF metadata and ensure clean output
            output_buffer = io.BytesIO()

            # Convert JPEG to ensure compatibility
            if image.format == 'JPEG':
                image.save(output_buffer, format='JPEG', quality=85, optimize=True)
                mime_type = 'image/jpeg'
            elif image.format == 'PNG':
                image.save(output_buffer, format='PNG', optimize=True)
                mime_type = 'image/png'
            else:  # WEBP
                image.save(output_buffer, format='WEBP', quality=85)
                mime_type = 'image/webp'

            # Encode to base64 with data URI prefix
            output_buffer.seek(0)
            clean_base64 = base64.b64encode(output_buffer.read()).decode('utf-8')
            return f"data:{mime_type};base64,{clean_base64}"

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Catch-all for unexpected errors
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image processing failed: {str(e)}"
            )

    @staticmethod
    def derive_username(email: str) -> str:
        """
        Derive username from email address.

        Extracts the part before @ symbol and sanitizes it.

        Args:
            email: User email address

        Returns:
            Sanitized username (alphanumeric + underscores only)

        Example:
            "hamza@gmail.com" -> "hamza"
            "john.doe@example.com" -> "johndoe"
        """
        # Extract part before @
        local_part = email.split('@')[0]

        # Remove non-alphanumeric characters (keep underscores)
        username = re.sub(r'[^a-zA-Z0-9_]', '', local_part)

        # Ensure it's not empty (fallback to 'user' if sanitization removed everything)
        if not username:
            username = 'user'

        # Lowercase for consistency
        return username.lower()

    @staticmethod
    async def resolve_username_collision(
        db: AsyncSession,
        base_username: str
    ) -> str:
        """
        Resolve username collisions by appending sequential numbers.

        If 'hamza' exists, tries 'hamza2', 'hamza3', etc.

        Args:
            db: Database session
            base_username: Base username to check

        Returns:
            Available username (may have number suffix)

        Example:
            If 'hamza' and 'hamza2' exist -> returns 'hamza3'
        """
        # Check if base username is available
        result = await db.execute(
            select(User).where(User.username == base_username)
        )
        existing_user = result.scalar_one_or_none()

        if not existing_user:
            # Base username is available
            return base_username

        # Try appending numbers until we find an available username
        counter = 2
        while counter < 10000:  # Safety limit to prevent infinite loop
            candidate = f"{base_username}{counter}"

            result = await db.execute(
                select(User).where(User.username == candidate)
            )
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                return candidate

            counter += 1

        # If we somehow hit the limit, raise error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate unique username"
        )

    @staticmethod
    async def create_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> User:
        """
        Create a new user account.

        Steps:
        1. Check if email already exists
        2. Derive username from email
        3. Resolve username collisions (append numbers if needed)
        4. Hash password with Argon2id
        5. Create user in database

        Args:
            db: Database session
            email: User email address
            password: Plain text password (will be hashed)

        Returns:
            Created User object

        Raises:
            HTTPException: 400 if email already exists

        Constitution Reference: FR-001 (User signup), FR-002 (Username derivation)
        """
        logger.info(f"[AUTH SERVICE] Creating user for email: {email}")

        # Check if email already exists
        logger.debug(f"[AUTH SERVICE] Checking if email exists: {email}")
        result = await db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.warning(f"[AUTH SERVICE] Email already registered: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Derive username from email
        base_username = AuthService.derive_username(email)
        logger.debug(f"[AUTH SERVICE] Derived base username: {base_username}")

        # Resolve username collisions
        final_username = await AuthService.resolve_username_collision(
            db, base_username
        )
        logger.debug(f"[AUTH SERVICE] Final username: {final_username}")

        # Hash password
        logger.debug(f"[AUTH SERVICE] Hashing password for {email}")
        password_hash = hash_password(password)

        # Create user
        logger.debug(f"[AUTH SERVICE] Creating User object for {email}")
        user = User(
            email=email,
            username=final_username,
            password_hash=password_hash,
            profile_image_url=None
        )

        logger.debug(f"[AUTH SERVICE] Adding user to database session")
        db.add(user)

        logger.debug(f"[AUTH SERVICE] Committing transaction for {email}")
        await db.commit()

        logger.debug(f"[AUTH SERVICE] Refreshing user object")
        await db.refresh(user)

        logger.info(f"[AUTH SERVICE] User created successfully: {user.id} ({user.email})")

        return user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            db: Database session
            email: User email address
            password: Plain text password to verify

        Returns:
            User object if authentication successful, None otherwise

        Constitution Reference: FR-005 (User login)
        """
        logger.info(f"[AUTH SERVICE] Authenticating user: {email}")

        # Find user by email
        logger.debug(f"[AUTH SERVICE] Querying database for user: {email}")
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            # User not found
            logger.warning(f"[AUTH SERVICE] User not found: {email}")
            return None

        logger.debug(f"[AUTH SERVICE] User found: {user.id}, verifying password")

        # Verify password
        if not verify_password(user.password_hash, password):
            # Invalid password
            logger.warning(f"[AUTH SERVICE] Invalid password for user: {email}")
            return None

        logger.info(f"[AUTH SERVICE] Authentication successful for user: {user.id} ({email})")
        return user

    @staticmethod
    async def update_profile_image(
        db: AsyncSession,
        user_id: UUID,
        profile_image_url: str
    ) -> User:
        """
        Update user's profile image.

        Args:
            db: Database session
            user_id: User UUID
            profile_image_url: Base64-encoded image with data URI prefix

        Returns:
            Updated User object

        Raises:
            HTTPException: 404 if user not found

        Constitution Reference: FR-022 (Profile image update)
        """
        # Find user by ID
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update profile image
        user.profile_image_url = profile_image_url
        await db.commit()
        await db.refresh(user)

        return user


# Global instance
auth_service = AuthService()
