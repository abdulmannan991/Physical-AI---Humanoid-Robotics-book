"""
Health Check Endpoint

Provides system health status for all services.

Constitution: backend/.specify/memory/constitution.md (Section 5.1)
"""

import logging
from fastapi import APIRouter

from app.models.response import HealthResponse
from app.services.database import db_service
from app.services.qdrant import qdrant_service
from app.services.embeddings import embeddings_service
from app.services.llm import llm_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Check the health status of all system components"
)
async def health_check() -> HealthResponse:
    """
    Check health status of all services.

    Returns:
        HealthResponse with status of each component

    Constitution Reference: Section 5.1 (Health monitoring)
    """
    # Check each service
    qdrant_healthy = await qdrant_service.health_check()
    db_healthy = await db_service.health_check()
    embeddings_healthy = embeddings_service.health_check()
    llm_healthy = llm_service.health_check()

    # Determine overall status
    all_services = [qdrant_healthy, db_healthy, embeddings_healthy, llm_healthy]

    if all(all_services):
        overall_status = "healthy"
    elif any(all_services):
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    # Build response
    response = HealthResponse(
        status=overall_status,
        version=settings.VERSION,
        qdrant_status="available" if qdrant_healthy else "unavailable",
        llm_status="available" if llm_healthy else "unavailable",
        database_status="available" if db_healthy else "unavailable",
        embeddings_status="available" if embeddings_healthy else "unavailable"
    )

    logger.info(f"Health check: {overall_status}")
    return response
