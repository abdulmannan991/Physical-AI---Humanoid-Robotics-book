"""
Admin Ingestion Endpoint

Allows administrators to trigger content re-ingestion via protected API endpoint.

Constitution: backend/.specify/memory/constitution.md (Section 6 - Admin endpoints)
"""

import logging
import time
import asyncio
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.services.ingestion import ingestion_service
from app.utils.chunking import chunk_markdown

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["admin"])


class IngestResponse(BaseModel):
    """Response model for ingestion endpoint."""

    status: str
    chunks_ingested: int
    duration_seconds: float
    message: str


async def validate_admin_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """
    Validate admin API key from header.

    Args:
        x_api_key: API key from X-API-Key header

    Raises:
        HTTPException: If API key is invalid

    Constitution Reference: Section 6 (Admin authentication)
    """
    if not x_api_key or x_api_key != settings.ADMIN_API_KEY:
        logger.warning("Invalid admin API key attempted")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "X-API-Key"},
        )


@router.post(
    "",
    response_model=IngestResponse,
    summary="Trigger content re-ingestion (Admin only)",
    description="Re-parse and re-ingest all course content from /docs folder. Requires admin API key.",
    status_code=status.HTTP_200_OK,
)
async def trigger_ingestion(
    x_api_key: str = Header(..., alias="X-API-Key")
) -> IngestResponse:
    """
    Trigger content re-ingestion (Admin only).

    Requires X-API-Key header with valid admin key.

    Process:
    1. Validate admin API key
    2. Parse all Markdown files from /docs
    3. Chunk content intelligently
    4. Generate embeddings
    5. Upload to Qdrant

    Returns:
        IngestResponse with status, count, and duration

    Raises:
        HTTPException 401: Invalid API key
        HTTPException 500: Ingestion failed
    """
    # Validate admin authentication
    await validate_admin_key(x_api_key)

    logger.info("Admin ingestion triggered")
    start_time = time.time()

    try:
        # Get docs path (parent directory of backend)
        backend_dir = Path(__file__).parent.parent.parent.parent
        docs_path = backend_dir.parent / "docs"

        if not docs_path.exists():
            logger.error(f"Docs path not found: {docs_path}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Docs folder not found at {docs_path}",
            )

        # Parse docs folder
        logger.info(f"Parsing docs from: {docs_path}")
        chunks = ingestion_service.parse_docs_folder(str(docs_path))

        if not chunks:
            logger.warning("No chunks parsed from docs folder")
            return IngestResponse(
                status="warning",
                chunks_ingested=0,
                duration_seconds=time.time() - start_time,
                message="No content found to ingest",
            )

        # Embed and store chunks
        logger.info(f"Embedding and storing {len(chunks)} chunks...")
        await ingestion_service.embed_and_store(chunks)

        duration = time.time() - start_time
        logger.info(
            f"Ingestion complete: {len(chunks)} chunks in {duration:.2f}s"
        )

        return IngestResponse(
            status="success",
            chunks_ingested=len(chunks),
            duration_seconds=round(duration, 2),
            message=f"Successfully ingested {len(chunks)} chunks from {docs_path}",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}",
        )
