"""
File Service for Database Operations

This module handles file-related database operations including:
- Storing file metadata in database
- Retrieving file information
- Managing file access permissions
- File listing and search
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from app.config.database import db_config
from app.models.file import (
    FileAccess,
    FileListResponse,
    FileMetadata,
    FileType,
    FileUpdateRequest,
    FileUploadResponse,
)
from app.services.storage_service import storage_service


class FileService:
    def __init__(self):
        self.db = db_config.get_client()
        self.table = "files"

    async def create_file_record(self, file_data: dict) -> FileUploadResponse:
        """Create a new file record in the database"""
        try:
            # Prepare file data for database insertion
            db_data = {
                "id": file_data["file_id"],
                "filename": file_data["filename"],
                "original_filename": file_data["original_filename"],
                "file_type": file_data["file_type"],
                "file_size": file_data["file_size"],
                "mime_type": file_data["mime_type"],
                "access_level": file_data["access_level"],
                "gcs_bucket": file_data.get("gcs_bucket", ""),
                "gcs_path": file_data.get("gcs_path", ""),
                "upload_url": file_data["upload_url"],
                "download_url": file_data["download_url"],
                "thumbnail_url": file_data.get("thumbnail_url"),
                "description": file_data.get("description"),
                "tags": file_data.get("tags", []),
                "uploaded_by": file_data["uploaded_by"],
                "uploaded_at": file_data["uploaded_at"].isoformat(),
                "expires_at": (
                    file_data.get("expires_at").isoformat()
                    if file_data.get("expires_at")
                    else None
                ),
                "is_active": True,
            }

            # Insert into database
            result = self.db.table(self.table).insert(db_data).execute()

            if result.data:
                return FileUploadResponse(**file_data)
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create file record",
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating file record: {str(e)}",
            )

    async def get_file_by_id(self, file_id: str) -> Optional[FileUploadResponse]:
        """Get file information by ID"""
        try:
            result = (
                self.db.table(self.table)
                .select("*")
                .eq("id", file_id)
                .eq("is_active", True)
                .execute()
            )

            if result.data:
                file_data = result.data[0]
                return FileUploadResponse(
                    file_id=file_data["id"],
                    filename=file_data["filename"],
                    original_filename=file_data["original_filename"],
                    file_type=file_data["file_type"],
                    file_size=file_data["file_size"],
                    mime_type=file_data["mime_type"],
                    access_level=file_data["access_level"],
                    upload_url=file_data["upload_url"],
                    download_url=file_data["download_url"],
                    thumbnail_url=file_data.get("thumbnail_url"),
                    description=file_data.get("description"),
                    tags=file_data.get("tags", []),
                    uploaded_by=file_data["uploaded_by"],
                    uploaded_at=datetime.fromisoformat(file_data["uploaded_at"]),
                    expires_at=(
                        datetime.fromisoformat(file_data["expires_at"])
                        if file_data.get("expires_at")
                        else None
                    ),
                )
            return None

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving file: {str(e)}",
            )

    async def get_user_files(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        file_type: Optional[FileType] = None,
        access_level: Optional[FileAccess] = None,
    ) -> FileListResponse:
        """Get files uploaded by a specific user"""
        try:
            # Build query
            query = (
                self.db.table(self.table)
                .select("*")
                .eq("uploaded_by", user_id)
                .eq("is_active", True)
            )

            # Apply filters
            if file_type:
                query = query.eq("file_type", file_type.value)
            if access_level:
                query = query.eq("access_level", access_level.value)

            # Get total count
            count_result = query.execute()
            total = len(count_result.data) if count_result.data else 0

            # Apply pagination
            offset = (page - 1) * per_page
            query = query.order("uploaded_at", desc=True).range(
                offset, offset + per_page - 1
            )

            result = query.execute()

            files = []
            if result.data:
                for file_data in result.data:
                    files.append(
                        FileUploadResponse(
                            file_id=file_data["id"],
                            filename=file_data["filename"],
                            original_filename=file_data["original_filename"],
                            file_type=file_data["file_type"],
                            file_size=file_data["file_size"],
                            mime_type=file_data["mime_type"],
                            access_level=file_data["access_level"],
                            upload_url=file_data["upload_url"],
                            download_url=file_data["download_url"],
                            thumbnail_url=file_data.get("thumbnail_url"),
                            description=file_data.get("description"),
                            tags=file_data.get("tags", []),
                            uploaded_by=file_data["uploaded_by"],
                            uploaded_at=datetime.fromisoformat(
                                file_data["uploaded_at"]
                            ),
                            expires_at=(
                                datetime.fromisoformat(file_data["expires_at"])
                                if file_data.get("expires_at")
                                else None
                            ),
                        )
                    )

            return FileListResponse(
                files=files,
                total=total,
                page=page,
                per_page=per_page,
                has_next=offset + per_page < total,
                has_prev=page > 1,
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving user files: {str(e)}",
            )

    async def get_public_files(
        self, page: int = 1, per_page: int = 20, file_type: Optional[FileType] = None
    ) -> FileListResponse:
        """Get public files"""
        try:
            # Build query for public files
            query = (
                self.db.table(self.table)
                .select("*")
                .eq("access_level", "public")
                .eq("is_active", True)
            )

            # Apply file type filter
            if file_type:
                query = query.eq("file_type", file_type.value)

            # Get total count
            count_result = query.execute()
            total = len(count_result.data) if count_result.data else 0

            # Apply pagination
            offset = (page - 1) * per_page
            query = query.order("uploaded_at", desc=True).range(
                offset, offset + per_page - 1
            )

            result = query.execute()

            files = []
            if result.data:
                for file_data in result.data:
                    files.append(
                        FileUploadResponse(
                            file_id=file_data["id"],
                            filename=file_data["filename"],
                            original_filename=file_data["original_filename"],
                            file_type=file_data["file_type"],
                            file_size=file_data["file_size"],
                            mime_type=file_data["mime_type"],
                            access_level=file_data["access_level"],
                            upload_url=file_data["upload_url"],
                            download_url=file_data["download_url"],
                            thumbnail_url=file_data.get("thumbnail_url"),
                            description=file_data.get("description"),
                            tags=file_data.get("tags", []),
                            uploaded_by=file_data["uploaded_by"],
                            uploaded_at=datetime.fromisoformat(
                                file_data["uploaded_at"]
                            ),
                            expires_at=(
                                datetime.fromisoformat(file_data["expires_at"])
                                if file_data.get("expires_at")
                                else None
                            ),
                        )
                    )

            return FileListResponse(
                files=files,
                total=total,
                page=page,
                per_page=per_page,
                has_next=offset + per_page < total,
                has_prev=page > 1,
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving public files: {str(e)}",
            )

    async def update_file_metadata(
        self, file_id: str, user_id: int, update_data: FileUpdateRequest
    ) -> FileUploadResponse:
        """Update file metadata"""
        try:
            # Check if file exists and user has permission
            file_result = (
                self.db.table(self.table)
                .select("*")
                .eq("id", file_id)
                .eq("uploaded_by", user_id)
                .eq("is_active", True)
                .execute()
            )

            if not file_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found or access denied",
                )

            file_data = file_result.data[0]

            # Prepare update data
            update_dict = {}
            if update_data.description is not None:
                update_dict["description"] = update_data.description
            if update_data.access_level is not None:
                update_dict["access_level"] = update_data.access_level.value
            if update_data.tags is not None:
                update_dict["tags"] = update_data.tags

            if not update_dict:
                # No changes to make
                return await self.get_file_by_id(file_id)

            # Update in database
            result = (
                self.db.table(self.table)
                .update(update_dict)
                .eq("id", file_id)
                .execute()
            )

            if result.data:
                # Update GCS metadata if needed
                if file_data.get("gcs_path"):
                    gcs_metadata = {
                        "original_filename": file_data["original_filename"],
                        "uploaded_by": str(user_id),
                        "file_type": file_data["file_type"],
                        "description": update_dict.get(
                            "description", file_data.get("description", "")
                        ),
                        "tags": ",".join(
                            update_dict.get("tags", file_data.get("tags", []))
                        ),
                    }
                    await storage_service.update_file_metadata(
                        file_data["gcs_path"], gcs_metadata
                    )

                return await self.get_file_by_id(file_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update file metadata",
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating file metadata: {str(e)}",
            )

    async def delete_file(self, file_id: str, user_id: int) -> bool:
        """Delete a file (soft delete)"""
        try:
            # Check if file exists and user has permission
            file_result = (
                self.db.table(self.table)
                .select("*")
                .eq("id", file_id)
                .eq("uploaded_by", user_id)
                .eq("is_active", True)
                .execute()
            )

            if not file_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found or access denied",
                )

            file_data = file_result.data[0]

            # Soft delete in database
            result = (
                self.db.table(self.table)
                .update({"is_active": False})
                .eq("id", file_id)
                .execute()
            )

            if result.data:
                # Delete from GCS if enabled
                if file_data.get("gcs_path"):
                    await storage_service.delete_file(file_data["gcs_path"])
                return True
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete file",
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting file: {str(e)}",
            )

    async def search_files(
        self,
        user_id: int,
        query: str,
        file_type: Optional[FileType] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> FileListResponse:
        """Search files by name, description, or tags"""
        try:
            # Build search query
            search_query = (
                self.db.table(self.table)
                .select("*")
                .eq("uploaded_by", user_id)
                .eq("is_active", True)
            )

            # Apply file type filter
            if file_type:
                search_query = search_query.eq("file_type", file_type.value)

            # Note: Supabase doesn't have full-text search by default
            # This is a basic implementation - you might want to use a search service
            result = search_query.execute()

            # Filter results by search term (basic implementation)
            filtered_files = []
            if result.data:
                for file_data in result.data:
                    searchable_text = f"{file_data['original_filename']} {file_data.get('description', '')} {' '.join(file_data.get('tags', []))}".lower()
                    if query.lower() in searchable_text:
                        filtered_files.append(file_data)

            total = len(filtered_files)

            # Apply pagination
            offset = (page - 1) * per_page
            paginated_files = filtered_files[offset : offset + per_page]

            files = []
            for file_data in paginated_files:
                files.append(
                    FileUploadResponse(
                        file_id=file_data["id"],
                        filename=file_data["filename"],
                        original_filename=file_data["original_filename"],
                        file_type=file_data["file_type"],
                        file_size=file_data["file_size"],
                        mime_type=file_data["mime_type"],
                        access_level=file_data["access_level"],
                        upload_url=file_data["upload_url"],
                        download_url=file_data["download_url"],
                        thumbnail_url=file_data.get("thumbnail_url"),
                        description=file_data.get("description"),
                        tags=file_data.get("tags", []),
                        uploaded_by=file_data["uploaded_by"],
                        uploaded_at=datetime.fromisoformat(file_data["uploaded_at"]),
                        expires_at=(
                            datetime.fromisoformat(file_data["expires_at"])
                            if file_data.get("expires_at")
                            else None
                        ),
                    )
                )

            return FileListResponse(
                files=files,
                total=total,
                page=page,
                per_page=per_page,
                has_next=offset + per_page < total,
                has_prev=page > 1,
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching files: {str(e)}",
            )


# Global file service instance
file_service = FileService()
