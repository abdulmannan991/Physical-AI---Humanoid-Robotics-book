"""
Security Module

Provides input sanitization, API key validation, XSS prevention, JWT authentication, and password hashing.

Constitution: backend/.specify/memory/constitution.md (Section 5.3 - Security)
"""

import re
import html
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

# API Key header for admin endpoints
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Initialize Argon2 password hasher with security-optimized parameters
# Parameters: memory=65536 (64MB), time_cost=3, parallelism=4
# Targets ~150ms hashing time per research.md specifications
password_hasher = PasswordHasher(
    time_cost=3,         # 3 iterations
    memory_cost=65536,   # 64 MB
    parallelism=4,       # 4 threads
    hash_len=32,         # 32-byte hash
    salt_len=16          # 16-byte salt
)


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


# ==================== JWT Authentication Functions ====================


def create_access_token(user_id: UUID, email: str) -> str:
    """
    Create a JWT access token for authenticated user.

    Args:
        user_id: User's unique identifier
        email: User's email address

    Returns:
        JWT access token string

    Security: Tokens expire after JWT_ACCESS_TOKEN_EXPIRE_MINUTES (default: 1 day)
    """
    expiration = datetime.utcnow() + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload: Dict[str, Any] = {
        "sub": str(user_id),  # Subject (user ID)
        "email": email,
        "exp": expiration,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at
        "type": "access"
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token


def create_refresh_token(user_id: UUID) -> str:
    """
    Create a JWT refresh token for token renewal.

    Args:
        user_id: User's unique identifier

    Returns:
        JWT refresh token string

    Security: Tokens expire after JWT_REFRESH_TOKEN_EXPIRE_MINUTES (default: 7 days)
    """
    expiration = datetime.utcnow() + timedelta(
        minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
    )

    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "exp": expiration,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or wrong type
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Verify token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}."
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token without verification (for inspection).

    Args:
        token: JWT token string

    Returns:
        Decoded payload or None if invalid

    Note: This does NOT verify the token signature. Use verify_token() for authentication.
    """
    try:
        payload = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        return payload
    except jwt.InvalidTokenError:
        return None


# ==================== Password Hashing Functions ====================


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2id.

    Args:
        password: Plain text password

    Returns:
        Argon2id hashed password string

    Security: Uses Argon2id with 64MB memory, 3 iterations, 4 threads
    Performance: ~150ms hashing time (meets <200ms requirement)
    """
    return password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """
    Verify a password against an Argon2id hash.

    Args:
        password_hash: Stored Argon2id hash
        password: Plain text password to verify

    Returns:
        True if password matches, False otherwise

    Performance: ~150ms verification time
    """
    try:
        password_hasher.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        # Password does not match
        return False
    except (VerificationError, InvalidHash) as e:
        # Hash is corrupted or invalid
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )


def validate_password_strength(password: str) -> None:
    """
    Validate password meets strength requirements.

    Requirements (per spec.md FR-003):
    - Minimum 8 characters
    - At least one number
    - At least one special character

    Args:
        password: Plain text password

    Raises:
        HTTPException: If password does not meet requirements
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    if not re.search(r'\d', password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one number"
        )

    if not re.search(r'[!@#$%^&*(),.?":{}|<>_+\-=\[\]\\;/]', password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one special character"
        )
