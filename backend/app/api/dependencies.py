"""
API Dependencies

Shared dependencies for FastAPI endpoints.

Constitution: backend/.specify/memory/constitution.md (Section 5)
"""

from typing import AsyncGenerator, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import validate_admin_api_key, verify_token
from app.models.database import User
from app.services.database import db_service


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Yields:
        AsyncSession instance

    Example:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db_session)):
            # Use db session
            ...
    """
    async with db_service.get_session() as session:
        yield session


async def get_admin_api_key(
    api_key: str = Depends(validate_admin_api_key)
) -> str:
    """
    Dependency to validate admin API key.

    Args:
        api_key: API key from security.py validation

    Returns:
        Validated API key

    Example:
        @app.post("/admin/endpoint")
        async def admin_endpoint(
            api_key: str = Depends(get_admin_api_key)
        ):
            # Endpoint protected by admin API key
            ...
    """
    return api_key


def get_settings():
    """
    Dependency to inject settings.

    Returns:
        Settings instance

    Example:
        @app.get("/endpoint")
        async def endpoint(settings: Settings = Depends(get_settings)):
            # Use settings
            ...
    """
    return settings


# ==================== Authentication Dependencies ====================


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Dependency to get current authenticated user from JWT token in cookies.

    Args:
        request: FastAPI request object (contains cookies)
        db: Database session

    Returns:
        User object of authenticated user

    Raises:
        HTTPException: 401 if token is missing, invalid, or user not found

    Example:
        @app.get("/api/v1/profile")
        async def get_profile(
            current_user: User = Depends(get_current_user)
        ):
            return {"user": current_user}

    Constitution Reference: FR-007, FR-012 (Authentication required)
    """
    # Extract JWT token from cookies
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify token and extract payload
    try:
        payload = verify_token(access_token, token_type="access")
        user_id_str = payload.get("sub")

        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        user_id = UUID(user_id_str)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

    # Query user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, None otherwise.

    Used for endpoints that work with both authenticated and guest users.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        User object if authenticated, None if not authenticated

    Example:
        @app.post("/api/v1/chat")
        async def chat(
            current_user: Optional[User] = Depends(get_current_user_optional)
        ):
            # Link session to user if authenticated, NULL if guest
            user_id = current_user.id if current_user else None
            ...

    Constitution Reference: FR-024, FR-025 (Guest support), FR-026, FR-027 (Session linking)
    """
    # Extract JWT token from cookies
    access_token = request.cookies.get("access_token")

    if not access_token:
        # No token = guest user
        return None

    try:
        # Verify token and extract payload
        payload = verify_token(access_token, token_type="access")
        user_id_str = payload.get("sub")

        if not user_id_str:
            return None

        user_id = UUID(user_id_str)

        # Query user from database
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        return user

    except (HTTPException, ValueError):
        # Invalid or expired token = treat as guest
        return None
