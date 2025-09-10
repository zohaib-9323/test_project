"""
Authentication Routes Module

This module handles all authentication-related API endpoints including:
- User registration (signup)
- User login with JWT token generation
- Token-based authentication flow

The routes are protected with proper error handling and validation.
"""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from app.config.settings import settings
from app.models.user import Token, UserCreate, UserLogin, UserResponse
from app.services.user_service import user_service
from app.utils.auth import create_access_token

# Create router for authentication endpoints
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(user: UserCreate):
    """
    Register a new user account.

    Args:
        user: UserCreate model containing name, email, and password

    Returns:
        UserResponse: Created user information (without password)

    Raises:
        HTTPException: 400 if email already exists, 500 for server errors
    """
    try:
        # Create new user through service layer
        new_user = await user_service.create_user(user)
        return new_user
    except HTTPException:
        # Re-raise HTTP exceptions (like email already exists)
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signup: {str(e)}",
        )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Authenticate user and return JWT access token.

    Args:
        user_credentials: UserLogin model containing email and password

    Returns:
        Token: JWT access token with expiration

    Raises:
        HTTPException: 401 for invalid credentials, 400 for inactive user, 500 for server errors
    """
    try:
        # Authenticate user credentials
        user = await user_service.authenticate_user(
            user_credentials.email, user_credentials.password
        )

        # Check if user exists and credentials are valid
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        # Create JWT access token with expiration
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        # Return token information
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        # Re-raise HTTP exceptions (like invalid credentials)
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}",
        )
