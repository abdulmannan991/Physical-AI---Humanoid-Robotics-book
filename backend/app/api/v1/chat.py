"""
Chat Endpoint

Handles user queries and returns RAG-powered responses.

Constitution: backend/.specify/memory/constitution.md (Section 5.1)
"""

import logging
from fastapi import APIRouter, HTTPException, status, Request
from uuid import uuid4

from app.models.request import ChatRequest
from app.models.response import ChatResponse
from app.services.rag import rag_service
from app.services.database import db_service
from app.core.security import (
    sanitize_text,
    validate_query_length,
    validate_selected_text,
    check_for_injection_attempts
)
from app.core.middleware import limiter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a query and receive RAG-powered answer",
    description="Submit a question and receive an intelligent answer with source citations",
    responses={
        200: {
            "description": "Successful response with answer and citations",
            "model": ChatResponse
        },
        400: {
            "description": "Invalid request (empty query, query too long, etc.)"
        },
        429: {
            "description": "Rate limit exceeded (10 requests per minute)"
        },
        500: {
            "description": "Internal server error (LLM/Qdrant unavailable)"
        }
    }
)
@limiter.limit(f"{10}/minute")  # 10 requests per minute (FR-017)
async def chat(request: Request, chat_request: ChatRequest) -> ChatResponse:
    """
    Process user query and return RAG-powered response.

    This endpoint:
    1. Validates and sanitizes input
    2. Creates or retrieves session
    3. Handles text selection feature (User Story 2)
    4. Retrieves relevant content from Qdrant
    5. Generates answer using LLM
    6. Logs query to database
    7. Returns answer with citations

    Constitution Reference: FR-001 through FR-034 (User Story 1 + 2 + 3)
    """
    try:
        # Step 1: Input validation and sanitization
        query = sanitize_text(chat_request.query)
        validate_query_length(query)
        check_for_injection_attempts(query)

        # Handle selected text (User Story 2 - FR-011 through FR-014)
        if chat_request.selected_text:
            validate_selected_text(chat_request.selected_text)
            selected = sanitize_text(chat_request.selected_text)

            # Truncate if > 1000 chars (FR-014)
            if len(selected) > 1000:
                selected = selected[:500]

            # Prepend "Explain: " to query
            query = f"Explain: {selected}"
            logger.info(f"Text selection query: {query[:100]}")

        # Step 2: Session management (FR-034)
        session_id = chat_request.session_id

        if session_id:
            # Validate existing session
            existing_session = await db_service.get_session_by_id(session_id)
            if not existing_session:
                logger.warning(f"Session {session_id} not found, creating new one")
                session_id = await db_service.create_session()
        else:
            # Create new session
            session_id = await db_service.create_session()
            logger.info(f"Created new session: {session_id}")

        # If database unavailable, use temporary session ID
        if not session_id:
            session_id = uuid4()
            logger.warning(f"Database unavailable, using temporary session: {session_id}")

        # Step 3: RAG pipeline - Retrieval (FR-006, FR-007)
        chunks, retrieval_latency = await rag_service.retrieve(
            query=query,
            top_k=chat_request.top_k
        )

        if not chunks:
            logger.warning("No chunks retrieved from Qdrant")
            # Return fallback message if retrieval failed
            from app.services.rag import OUT_OF_SCOPE_MESSAGE
            return ChatResponse(
                answer=OUT_OF_SCOPE_MESSAGE,
                citations=[],
                confidence=0.0,
                session_id=session_id
            )

        # Step 4: RAG pipeline - Generation (FR-005, FR-008, FR-009)
        response, llm_latency = await rag_service.generate_answer(
            query=query,
            chunks=chunks,
            session_id=session_id
        )

        # Step 5: Log query to database (FR-035 - NO PII)
        if session_id:
            await db_service.update_session_activity(session_id)
            await db_service.log_query(
                session_id=session_id,
                query_text=query,
                response_text=response.answer,
                confidence_score=response.confidence,
                retrieval_latency_ms=retrieval_latency,
                llm_latency_ms=llm_latency
            )

        logger.info(
            f"Query processed: session={session_id}, "
            f"confidence={response.confidence:.3f}, "
            f"retrieval={retrieval_latency}ms, "
            f"llm={llm_latency}ms"
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions (from validation)
        raise

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing query"
        )
