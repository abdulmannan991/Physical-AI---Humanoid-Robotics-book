"""
Security Module

Provides input sanitization, API key validation, and XSS prevention.

Constitution: backend/.specify/memory/constitution.md (Section 5.3 - Security)
"""

import re
import html
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

# API Key header for admin endpoints
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def sanitize_text(text: str) -> str:
    """
    Sanitize user input to prevent XSS attacks.

    Args:
        text: Raw user input text

    Returns:
        Sanitized text with HTML entities escaped

    Constitution Reference: Section 5.3 (Input validation)
    """
    # Escape HTML entities
    sanitized = html.escape(text)

    # Remove null bytes
    sanitized = sanitized.replace("\x00", "")

    # Normalize whitespace
    sanitized = re.sub(r"\s+", " ", sanitized)

    return sanitized.strip()


def validate_query_length(query: str, max_length: int = 2000) -> None:
    """
    Validate query length.

    Args:
        query: User query text
        max_length: Maximum allowed length

    Raises:
        HTTPException: If query is too long or empty

    Constitution Reference: Section 4.3 (Request validation)
    """
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )

    if len(query) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query exceeds maximum length of {max_length} characters"
        )


def validate_selected_text(
    selected_text: Optional[str],
    max_length: int = 500
) -> None:
    """
    Validate selected text length.

    Args:
        selected_text: User-selected text from page
        max_length: Maximum allowed length

    Raises:
        HTTPException: If selected text is too long

    Constitution Reference: FR-014 (selected text truncation)
    """
    if selected_text and len(selected_text) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Selected text exceeds maximum length of {max_length} characters"
        )


async def validate_admin_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> str:
    """
    Validate admin API key for protected endpoints.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is missing or invalid

    Constitution Reference: Section 5.3 (API key authentication)
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    if api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

    return api_key


def validate_session_id_format(session_id: str) -> None:
    """
    Validate session ID format (must be valid UUID).

    Args:
        session_id: Session identifier

    Raises:
        HTTPException: If session_id is not a valid UUID

    Constitution Reference: Section 4.2 (Session management)
    """
    # UUID v4 regex pattern
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        re.IGNORECASE
    )

    if not uuid_pattern.match(session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session_id format. Must be a valid UUID v4."
        )


def check_for_injection_attempts(text: str) -> None:
    """
    Check for common injection attack patterns.

    Args:
        text: User input text

    Raises:
        HTTPException: If potential injection attack detected

    Constitution Reference: Section 5.3 (Security - prevent injection)
    """
    # Common SQL injection patterns
    sql_patterns = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(--)",
        r"(;.*\bDROP\b)",
    ]

    # Common XSS patterns (in addition to HTML escaping)
    xss_patterns = [
        r"(<script[^>]*>.*?</script>)",
        r"(javascript:)",
        r"(onerror\s*=)",
        r"(onload\s*=)",
    ]

    all_patterns = sql_patterns + xss_patterns

    for pattern in all_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input detected"
            )
