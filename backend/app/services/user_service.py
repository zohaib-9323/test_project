from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status

from app.config.database import db_config
from app.models.user import UserCreate, UserInDB, UserResponse, UserRole, UserUpdate
from app.utils.auth import get_password_hash, verify_password


class UserService:
    def __init__(self):
        self.db = db_config.get_client()
        self.table = "users"

    async def create_user(self, user: UserCreate) -> UserResponse:
        """Create a new user."""
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(user.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            # Hash password
            hashed_password = get_password_hash(user.password)

            # Prepare user data
            user_data = {
                "name": user.name,
                "email": user.email,
                "hashed_password": hashed_password,
                "role": user.role.value if user.role else UserRole.USER.value,
                "is_active": True,
                "is_email_verified": False,  # New users need to verify email
            }

            # Insert user using real Supabase client
            result = self.db.table(self.table).insert(user_data).execute()

            if result.data:
                user_response = result.data[0]
                # Remove password from response
                user_response.pop("hashed_password", None)
                return UserResponse(**user_response)
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user",
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        try:
            result = self.db.table(self.table).select("*").eq("email", email).execute()

            if result.data:
                return UserInDB(**result.data[0])
            return None

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID."""
        try:
            result = self.db.table(self.table).select("*").eq("id", user_id).execute()

            if result.data:
                user_data = result.data[0].copy()
                # Remove password from response
                user_data.pop("hashed_password", None)
                return UserResponse(**user_data)
            return None

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_all_users(self) -> List[UserResponse]:
        """Get all users."""
        try:
            result = self.db.table(self.table).select("*").execute()

            users = []
            for user_data in result.data:
                # Remove password from response
                user_data_copy = user_data.copy()
                user_data_copy.pop("hashed_password", None)
                users.append(UserResponse(**user_data_copy))

            return users

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def update_user(self, user_id: int, user_update: UserUpdate) -> UserResponse:
        """Update user information."""
        try:
            # Check if user exists
            existing_user = await self.get_user_by_id(user_id)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            # Prepare update data
            update_data = {}
            if user_update.name is not None:
                update_data["name"] = user_update.name
            if user_update.email is not None:
                # Check if new email is already taken
                existing_email_user = await self.get_user_by_email(user_update.email)
                if existing_email_user and existing_email_user.id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered",
                    )
                update_data["email"] = user_update.email
                update_data["is_email_verified"] = (
                    False  # Reset verification when email changes
                )

            if user_update.role is not None:
                update_data["role"] = user_update.role.value

            if not update_data:
                return existing_user

            # Update user using real Supabase client
            result = (
                self.db.table(self.table)
                .update(update_data)
                .eq("id", user_id)
                .execute()
            )

            if result.data:
                user_data = result.data[0].copy()
                # Remove password from response
                user_data.pop("hashed_password", None)
                return UserResponse(**user_data)
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update user",
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        try:
            # Check if user exists
            existing_user = await self.get_user_by_id(user_id)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            # Delete user
            result = self.db.table(self.table).delete().eq("id", user_id).execute()

            return len(result.data) > 0

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


# Global user service instance
user_service = UserService()
