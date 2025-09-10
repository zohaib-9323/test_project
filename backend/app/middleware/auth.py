"""
Authentication Middleware Module

This module provides authentication middleware for protecting API endpoints:
- JWT token verification
- User authentication and authorization
- Current user dependency injection

The middleware validates JWT tokens and extracts user information for protected routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.user import UserInDB, UserRole
from app.services.user_service import user_service
from app.utils.auth import verify_token

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserInDB:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        UserInDB: Authenticated user information

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials

    # Verify and decode JWT token
    payload = verify_token(token)
    email = payload.get("sub")

    # Check if email is present in token
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database using email from token
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    """
    Get current authenticated and active user.

    Args:
        current_user: Current authenticated user from get_current_user dependency

    Returns:
        UserInDB: Active user information

    Raises:
        HTTPException: 400 if user account is inactive
    """
    # Check if user account is active
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: UserInDB = Depends(get_current_active_user),
) -> UserInDB:
    """
    Get current authenticated user with admin role.

    Args:
        current_user: Current authenticated user from get_current_active_user dependency

    Returns:
        UserInDB: Admin user information

    Raises:
        HTTPException: 403 if user is not an admin
    """
    # Check if user has admin role
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


async def get_current_verified_user(
    current_user: UserInDB = Depends(get_current_active_user),
) -> UserInDB:
    """
    Get current authenticated user with verified email.

    Args:
        current_user: Current authenticated user from get_current_active_user dependency

    Returns:
        UserInDB: Verified user information

    Raises:
        HTTPException: 400 if user email is not verified
    """
    # Check if user email is verified
    if not current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification required",
        )
    return current_user
