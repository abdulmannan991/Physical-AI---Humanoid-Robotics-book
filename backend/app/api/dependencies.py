"""
API Dependencies

Shared dependencies for FastAPI endpoints.

Constitution: backend/.specify/memory/constitution.md (Section 5)
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import validate_admin_api_key
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
