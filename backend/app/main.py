"""
FastAPI Main Application

Entry point for the RAG Chatbot Backend API.

Constitution: backend/.specify/memory/constitution.md (v2.0.0)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.middleware import configure_middleware
from app.api.v1 import api_router
from app.services.database import db_service
from app.services.qdrant import qdrant_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown tasks.

    Startup:
    - Initialize database tables
    - Create Qdrant collection if needed

    Shutdown:
    - Close database connections
    """
    # Startup
    logger.info(f"Starting RAG Chatbot Backend v{settings.VERSION}")

    try:
        # Initialize database tables
        await db_service.create_tables()
        logger.info("Database tables initialized")

        # Create Qdrant collection
        qdrant_service.create_collection()
        logger.info("Qdrant collection ready")

    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Continue startup even if some services fail (graceful degradation)

    yield

    # Shutdown
    logger.info("Shutting down RAG Chatbot Backend")
    try:
        await db_service.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot Backend",
    description="Intelligent Q&A system for Physical AI & Humanoid Robotics course",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure middleware (CORS, rate limiting, logging)
configure_middleware(app)

# Include API routes
app.include_router(api_router)


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint - redirect to docs.

    Returns:
        JSON response with API information
    """
    return {
        "name": "RAG Chatbot Backend",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint not found",
            "error_code": "NOT_FOUND"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
