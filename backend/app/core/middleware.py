"""
Middleware Module

Provides CORS configuration, rate limiting, and request logging.

Constitution: backend/.specify/memory/constitution.md (Section 5)
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)


# Rate limiter instance
# Session-based rate limiting (10 requests per minute per session)
def get_session_id(request: Request) -> str:
    """
    Extract session ID from request for rate limiting.

    Falls back to remote address if session_id not provided.

    Args:
        request: FastAPI request object

    Returns:
        Session identifier for rate limiting
    """
    # Try to get session_id from request body (for POST requests)
    if hasattr(request.state, "session_id") and request.state.session_id:
        return str(request.state.session_id)

    # Fall back to IP-based limiting
    return get_remote_address(request)


limiter = Limiter(
    key_func=get_session_id,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
)


def configure_cors(app) -> None:
    """
    Configure CORS middleware for the application.

    Constitution Reference: Section 5.2 (CORS whitelisting)

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins_list(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-API-Key", "Authorization"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )
    logger.info(f"CORS configured with origins: {settings.CORS_ORIGINS}")


def configure_rate_limiting(app) -> None:
    """
    Configure rate limiting for the application.

    Constitution Reference: Section 5.2 (Rate limiting - 10 req/min)

    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info(f"Rate limiting configured: {settings.RATE_LIMIT_PER_MINUTE}/minute")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and responses.

    Constitution Reference: Section 5.3 (Request logging - NO PII)
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and log details.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response from downstream handler
        """
        # Start timer
        start_time = time.time()

        # Extract request details (NO PII - Constitution Section 5.3)
        request_details = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            # DO NOT LOG: IP address, user agent, cookies (PII protection)
        }

        # Log request
        logger.info(f"Request started: {request_details}")

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"Request completed: "
                f"status={response.status_code} "
                f"duration={duration:.3f}s "
                f"path={request.url.path}"
            )

            # Add custom headers
            response.headers["X-Process-Time"] = str(duration)
            response.headers["X-Version"] = settings.VERSION

            return response

        except Exception as exc:
            # Log error
            duration = time.time() - start_time
            logger.error(
                f"Request failed: "
                f"path={request.url.path} "
                f"duration={duration:.3f}s "
                f"error={str(exc)}"
            )
            raise


class SessionExtractionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract session_id from request body for rate limiting.

    This middleware runs before rate limiting to enable session-based limits.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Extract session_id from request body if present.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response from downstream handler
        """
        # For POST requests with JSON body
        if request.method == "POST" and request.headers.get("content-type") == "application/json":
            try:
                # Read body (will be cached by FastAPI for route handler)
                body = await request.json()
                if "session_id" in body:
                    request.state.session_id = body["session_id"]
            except Exception:
                # Ignore errors - body will be validated by route handler
                pass

        return await call_next(request)


def configure_middleware(app) -> None:
    """
    Configure all middleware for the application.

    Order matters - middlewares are executed in reverse order of addition.

    Args:
        app: FastAPI application instance
    """
    # 1. CORS (runs last - added first)
    configure_cors(app)

    # 2. Request logging
    app.add_middleware(RequestLoggingMiddleware)

    # 3. Session extraction (for rate limiting)
    app.add_middleware(SessionExtractionMiddleware)

    # 4. Rate limiting configuration
    configure_rate_limiting(app)

    logger.info("All middleware configured successfully")
