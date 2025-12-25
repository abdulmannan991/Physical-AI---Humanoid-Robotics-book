"""
Profile Endpoint

Handles user profile management (view profile, upload image, chat history).

Constitution: backend/.specify/memory/constitution.md (Section 5.3)
"""

import logging
from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request import ImageUpload
from app.models.response import UserResponse, ChatSessionSummary, ChatMessageDetail
from app.models.database import User
from app.services.auth import auth_service
from app.services.database import db_service
from app.api.dependencies import get_db_session, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["profile"])


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get current user's profile",
    description="Returns authenticated user's profile information",
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "model": UserResponse
        },
        401: {
            "description": "Unauthorized - missing or invalid token"
        }
    }
)
async def get_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user's profile.

    Requires authentication (JWT token).

    Returns:
        UserResponse: User profile with id, email, username, profile_image_url, created_at

    Constitution Reference: FR-016 (View profile)
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        profile_image_url=current_user.profile_image_url,
        created_at=current_user.created_at
    )


@router.post(
    "/profile/image",
    response_model=UserResponse,
    summary="Upload profile image",
    description="Upload or update profile image (base64-encoded, max 5MB)",
    responses={
        200: {
            "description": "Profile image uploaded successfully",
            "model": UserResponse
        },
        400: {
            "description": "Invalid image (wrong format, too large, corrupted)"
        },
        401: {
            "description": "Unauthorized - missing or invalid token"
        }
    }
)
async def upload_profile_image(
    image_upload: ImageUpload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """
    Upload or update profile image.

    Validates:
    - Size ≤5MB
    - Format: JPG, PNG, or WebP
    - Magic bytes verification
    - Strips EXIF metadata

    Args:
        image_upload: Base64-encoded image data
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        UserResponse: Updated user profile

    Raises:
        HTTPException: 400 if image validation fails

    Constitution Reference: FR-019, FR-020, FR-021, FR-022
    """
    try:
        # Validate and process image
        clean_image_data = auth_service.validate_profile_image(
            image_upload.image_data
        )

        # Update user profile in database
        updated_user = await auth_service.update_profile_image(
            db=db,
            user_id=current_user.id,
            profile_image_url=clean_image_data
        )

        logger.info(f"Profile image updated for user {current_user.id}")

        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            profile_image_url=updated_user.profile_image_url,
            created_at=updated_user.created_at
        )

    except HTTPException:
        # Re-raise validation errors
        raise

    except Exception as e:
        logger.error(f"Profile image upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload profile image"
        )


@router.get(
    "/profile/chat-history",
    response_model=List[ChatSessionSummary],
    summary="Get user's chat history",
    description="Returns paginated list of user's chat sessions ordered by recent activity",
    responses={
        200: {
            "description": "Chat history retrieved successfully",
            "model": List[ChatSessionSummary]
        },
        401: {
            "description": "Unauthorized - missing or invalid token"
        }
    }
)
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of sessions to return"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip")
) -> List[ChatSessionSummary]:
    """
    Get authenticated user's chat history.

    Returns paginated list of chat sessions ordered by last_activity_at DESC (most recent first).

    Pagination:
    - limit: Maximum sessions per page (1-100, default 50)
    - offset: Number of sessions to skip (default 0)

    Example:
        GET /api/v1/profile/chat-history?limit=20&offset=0  # First 20 sessions
        GET /api/v1/profile/chat-history?limit=20&offset=20 # Next 20 sessions

    Constitution Reference: FR-028, FR-029 (Chat history with pagination)
    """
    try:
        # Get user's chat sessions from database
        sessions = await db_service.get_user_sessions(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )

        # Convert to response model
        return [
            ChatSessionSummary(
                session_id=session.session_id,
                started_at=session.started_at,
                last_activity_at=session.last_activity_at,
                message_count=session.message_count
            )
            for session in sessions
        ]

    except Exception as e:
        logger.error(f"Chat history retrieval error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )


@router.get(
    "/profile/sessions/{session_id}",
    response_model=List[ChatMessageDetail],
    summary="Get session conversation details",
    description="Returns full conversation history for a specific chat session (user's session only)",
    responses={
        200: {
            "description": "Session messages retrieved successfully",
            "model": List[ChatMessageDetail]
        },
        401: {
            "description": "Unauthorized - missing or invalid token"
        },
        404: {
            "description": "Session not found or does not belong to user"
        }
    }
)
async def get_session_details(
    session_id: UUID,
    current_user: User = Depends(get_current_user)
) -> List[ChatMessageDetail]:
    """
    Get full conversation details for a specific session.

    Verifies that the session belongs to the authenticated user.

    Args:
        session_id: Session UUID from path parameter
        current_user: Authenticated user (from JWT)

    Returns:
        List of messages (queries and responses) ordered chronologically

    Constitution Reference: FR-028, FR-029 (View session details)
    """
    try:
        # Get session messages from database (includes authorization check)
        messages = await db_service.get_session_messages(
            session_id=session_id,
            user_id=current_user.id
        )

        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or does not belong to user"
            )

        # Convert to response model
        return [
            ChatMessageDetail(
                id=msg.log_id,
                query_text=msg.query_text,
                response_text=msg.response_text_truncated or "",
                timestamp=msg.created_at,
                confidence_score=msg.confidence_score or 0.0
            )
            for msg in messages
        ]

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Session details retrieval error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session details"
        )
