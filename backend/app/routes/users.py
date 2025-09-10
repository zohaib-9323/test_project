"""
User Management Routes Module

This module handles all user-related API endpoints including:
- Get current user information
- Get all users (with authentication)
- Get user by ID
- Update user information
- Delete user account

All routes are protected with JWT authentication middleware.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.user import UserResponse, UserUpdate
from app.services.user_service import user_service
from app.middleware.auth import (
    get_current_active_user,
    get_current_user,
    get_current_admin_user,
    get_current_verified_user,
)
from app.models.user import UserInDB

# Create router for user management endpoints
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Get current authenticated user's information.

    Args:
        current_user: Current authenticated user from JWT token

    Returns:
        UserResponse: User information without password

    Raises:
        HTTPException: 401 if not authenticated, 400 if user is inactive
    """
    # Remove password from response for security
    user_data = current_user.dict()
    user_data.pop("hashed_password", None)
    return UserResponse(**user_data)


@router.get("/", response_model=List[UserResponse])
async def get_all_users(current_user: UserInDB = Depends(get_current_admin_user)):
    """Get all users (admin only)."""
    try:
        users = await user_service.get_all_users()
        return users
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching users: {str(e)}",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int, current_user: UserInDB = Depends(get_current_active_user)
):
    """Get user by ID."""
    try:
        # Users can only access their own data unless they're admin
        if current_user.id != user_id and current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this user's data",
            )

        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching user: {str(e)}",
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Update user information."""
    try:
        # Users can only update their own data unless they're admin
        if current_user.id != user_id and current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this user",
            )

        updated_user = await user_service.update_user(user_id, user_update)
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating user: {str(e)}",
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int, current_user: UserInDB = Depends(get_current_active_user)
):
    """Delete user."""
    try:
        # Users can only delete their own account unless they're admin
        if current_user.id != user_id and current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete this user",
            )

        success = await user_service.delete_user(user_id)
        if success:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting user: {str(e)}",
        )
