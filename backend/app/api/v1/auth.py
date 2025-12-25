"""
Authentication API Endpoints

Handles user signup, login, logout, and profile retrieval.

Constitution: backend/.specify/memory/constitution.md (Section 5)
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, get_current_user
from app.core.security import create_access_token, create_refresh_token
from app.models.request import UserCreate, UserLogin
from app.models.response import UserResponse
from app.models.database import User
from app.services.auth import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user account",
    description="Register a new user with email and password. Username is auto-derived from email with collision resolution."
)
async def signup(
    user_data: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """
    Create a new user account.

    Process:
    1. Validate email and password (Pydantic validation)
    2. Check email doesn't already exist
    3. Derive username from email (e.g., hamza@gmail.com -> hamza)
    4. Resolve username collisions (hamza -> hamza2 if needed)
    5. Hash password with Argon2id
    6. Create user in database
    7. Generate JWT tokens
    8. Set httpOnly cookies
    9. Return user info

    Constitution Reference: FR-001 (User signup), FR-003 (Password requirements)
    """
    logger.info(f"[AUTH API] Signup attempt for email: {user_data.email}")

    try:
        # Create user (handles email uniqueness, username derivation, password hashing)
        user = await auth_service.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password
        )

        logger.info(f"[AUTH API] Signup success - User created: {user.id} ({user.email})")

        # DO NOT auto-login user after signup (security best practice)
        # User must manually log in after creating account

        # Return user info (no password hash, no JWT tokens)
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            profile_image_url=user.profile_image_url,
            created_at=user.created_at
        )
    except Exception as e:
        logger.error(f"[AUTH API] Signup failed for {user_data.email}: {str(e)}")
        raise


@router.post(
    "/login",
    response_model=UserResponse,
    summary="Login with email and password",
    description="Authenticate user and set JWT tokens in httpOnly cookies."
)
async def login(
    credentials: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """
    Authenticate user with email and password.

    Process:
    1. Find user by email
    2. Verify password with Argon2id
    3. Generate JWT tokens
    4. Set httpOnly cookies (1 day or 7 days based on remember_me)
    5. Return user info

    Constitution Reference: FR-005 (User login), FR-006 (Remember me)
    """
    logger.info(f"[AUTH API] Login attempt for email: {credentials.email}, remember_me: {credentials.remember_me}")

    try:
        # Authenticate user
        user = await auth_service.authenticate_user(
            db=db,
            email=credentials.email,
            password=credentials.password
        )

        if not user:
            logger.warning(f"[AUTH API] Login failed - Invalid credentials for {credentials.email}")
            # Invalid credentials (don't reveal whether email or password is wrong)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        logger.info(f"[AUTH API] Authentication successful for user: {user.id} ({user.email})")

        # Generate JWT tokens
        access_token = create_access_token(user_id=user.id, email=user.email)
        refresh_token = create_refresh_token(user_id=user.id)

        logger.info(f"[AUTH API] JWT tokens generated for user: {user.id}")

        # Set token expiry based on remember_me
        if credentials.remember_me:
            # 7 days for both tokens
            access_max_age = 7 * 24 * 60 * 60
            refresh_max_age = 7 * 24 * 60 * 60
        else:
            # 1 day access, 7 days refresh
            access_max_age = 24 * 60 * 60
            refresh_max_age = 7 * 24 * 60 * 60

        # Set httpOnly cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=access_max_age
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=refresh_max_age
        )

        logger.info(f"[AUTH API] Cookies set for user: {user.id}, access_max_age: {access_max_age}s")

        # Return user info
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            profile_image_url=user.profile_image_url,
            created_at=user.created_at
        )

        logger.info(f"[AUTH API] Login success - Returning user data for: {user.id}")

        return user_response

    except HTTPException:
        # Re-raise HTTP exceptions (already logged above)
        raise
    except Exception as e:
        logger.error(f"[AUTH API] Login error for {credentials.email}: {str(e)}", exc_info=True)
        raise


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
    description="Clear JWT tokens from cookies."
)
async def logout(response: Response) -> None:
    """
    Logout user by clearing authentication cookies.

    Constitution Reference: FR-008 (User logout)
    """
    # Clear access token cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )

    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )

    # 204 No Content (no response body)
    return


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get authenticated user's information from JWT token."
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information.

    Requires valid JWT token in cookies.

    Constitution Reference: FR-011 (Get current user)
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        profile_image_url=current_user.profile_image_url,
        created_at=current_user.created_at
    )
