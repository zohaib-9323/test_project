"""
Google Cloud Storage Service

This module provides file upload and management functionality using Google Cloud Storage.
It handles:
- File uploads to GCS buckets
- File metadata management
- File URL generation
- File deletion
- File listing and search

The service uses service account authentication for secure access to GCS.
"""

import os
import uuid
import mimetypes
from datetime import datetime, timezone
from typing import Optional, List, BinaryIO
from google.cloud import storage
from google.cloud.exceptions import NotFound, GoogleCloudError
from fastapi import HTTPException, status, UploadFile
from app.models.file import FileInfo, FileType
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GCSService:
    def __init__(self):
        """Initialize Google Cloud Storage service."""
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        self.project_id = os.getenv("GCS_PROJECT_ID")

        if not self.bucket_name or not self.project_id:
            logger.warning(
                "GCS credentials not configured. File upload will be disabled."
            )
            self.enabled = False
            return

        try:
            # Initialize GCS client
            self.client = storage.Client(project=self.project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            self.enabled = True
            logger.info(
                f"✅ GCS service initialized successfully. Bucket: {self.bucket_name}"
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize GCS service: {str(e)}")
            self.enabled = False

    def _generate_file_id(self) -> str:
        """Generate a unique file ID."""
        return str(uuid.uuid4())

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        return os.path.splitext(filename)[1].lower()

    def _determine_file_type(self, content_type: str, extension: str) -> FileType:
        """Determine file type based on content type and extension."""
        if content_type.startswith("image/"):
            return FileType.IMAGE
        elif content_type.startswith("video/"):
            return FileType.VIDEO
        elif content_type.startswith("audio/"):
            return FileType.AUDIO
        elif content_type in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "application/rtf",
        ]:
            return FileType.DOCUMENT
        else:
            return FileType.OTHER

    def _generate_file_path(self, file_id: str, filename: str) -> str:
        """Generate file path in GCS bucket."""
        # Create organized folder structure: files/YYYY/MM/DD/file_id_original_name
        now = datetime.now(timezone.utc)
        date_path = now.strftime("%Y/%m/%d")
        return f"files/{date_path}/{file_id}_{filename}"

    async def upload_file(
        self, file: UploadFile, user_id: int, is_public: bool = False
    ) -> FileInfo:
        """
        Upload a file to Google Cloud Storage.

        Args:
            file: FastAPI UploadFile object
            user_id: ID of the user uploading the file
            is_public: Whether the file should be publicly accessible

        Returns:
            FileInfo: Information about the uploaded file
        """
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File upload service is not configured",
            )

        try:
            # Generate unique file ID and path
            file_id = self._generate_file_id()
            file_path = self._generate_file_path(file_id, file.filename)

            # Determine content type
            content_type = (
                file.content_type
                or mimetypes.guess_type(file.filename)[0]
                or "application/octet-stream"
            )

            # Determine file type
            extension = self._get_file_extension(file.filename)
            file_type = self._determine_file_type(content_type, extension)

            # Create blob in GCS
            blob = self.bucket.blob(file_path)

            # Set metadata
            blob.metadata = {
                "file_id": file_id,
                "uploaded_by": str(user_id),
                "original_filename": file.filename,
                "file_type": file_type.value,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            }

            # Upload file content
            file_content = await file.read()
            blob.upload_from_string(file_content, content_type=content_type)

            # Set public access if requested
            if is_public:
                blob.make_public()

            # Generate file URL
            if is_public:
                file_url = blob.public_url
            else:
                # Generate signed URL for private files (valid for 1 hour)
                file_url = blob.generate_signed_url(
                    expiration=datetime.now(timezone.utc).timestamp() + 3600,
                    method="GET",
                )

            # Create file info
            file_info = FileInfo(
                file_id=file_id,
                file_name=file.filename,
                file_url=file_url,
                file_size=len(file_content),
                file_type=file_type.value,
                content_type=content_type,
                uploaded_by=user_id,
                uploaded_at=datetime.now(timezone.utc),
                is_public=is_public,
            )

            logger.info(
                f"✅ File uploaded successfully: {file.filename} (ID: {file_id})"
            )
            return file_info

        except GoogleCloudError as e:
            logger.error(f"❌ GCS error during file upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}",
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error during file upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during file upload",
            )

    async def delete_file(self, file_id: str, user_id: int) -> bool:
        """
        Delete a file from Google Cloud Storage.

        Args:
            file_id: ID of the file to delete
            user_id: ID of the user requesting deletion

        Returns:
            bool: True if file was deleted successfully
        """
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File service is not configured",
            )

        try:
            # Find the blob by searching for the file_id in metadata
            blobs = self.bucket.list_blobs(prefix="files/")

            for blob in blobs:
                if blob.metadata and blob.metadata.get("file_id") == file_id:
                    # Check if user has permission to delete (uploaded by same user)
                    if blob.metadata.get("uploaded_by") != str(user_id):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to delete this file",
                        )

                    # Delete the blob
                    blob.delete()
                    logger.info(f"✅ File deleted successfully: {file_id}")
                    return True

            # File not found
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        except HTTPException:
            raise
        except GoogleCloudError as e:
            logger.error(f"❌ GCS error during file deletion: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}",
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error during file deletion: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during file deletion",
            )

    async def get_file_info(self, file_id: str, user_id: int) -> FileInfo:
        """
        Get information about a specific file.

        Args:
            file_id: ID of the file
            user_id: ID of the user requesting the info

        Returns:
            FileInfo: Information about the file
        """
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File service is not configured",
            )

        try:
            # Find the blob by searching for the file_id in metadata
            blobs = self.bucket.list_blobs(prefix="files/")

            for blob in blobs:
                if blob.metadata and blob.metadata.get("file_id") == file_id:
                    # Check if user has permission to access (uploaded by same user)
                    if blob.metadata.get("uploaded_by") != str(user_id):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to access this file",
                        )

                    # Generate file URL
                    if blob.metadata.get("is_public", "false").lower() == "true":
                        file_url = blob.public_url
                        is_public = True
                    else:
                        file_url = blob.generate_signed_url(
                            expiration=datetime.now(timezone.utc).timestamp() + 3600,
                            method="GET",
                        )
                        is_public = False

                    # Create file info
                    file_info = FileInfo(
                        file_id=file_id,
                        file_name=blob.metadata.get("original_filename", "Unknown"),
                        file_url=file_url,
                        file_size=blob.size,
                        file_type=blob.metadata.get("file_type", "other"),
                        content_type=blob.content_type or "application/octet-stream",
                        uploaded_by=user_id,
                        uploaded_at=datetime.fromisoformat(
                            blob.metadata.get(
                                "uploaded_at", datetime.now(timezone.utc).isoformat()
                            )
                        ),
                        is_public=is_public,
                    )

                    return file_info

            # File not found
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        except HTTPException:
            raise
        except GoogleCloudError as e:
            logger.error(f"❌ GCS error during file info retrieval: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get file info: {str(e)}",
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error during file info retrieval: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while getting file info",
            )

    async def list_user_files(
        self, user_id: int, page: int = 1, per_page: int = 20
    ) -> List[FileInfo]:
        """
        List files uploaded by a specific user.

        Args:
            user_id: ID of the user
            page: Page number (1-based)
            per_page: Number of files per page

        Returns:
            List[FileInfo]: List of file information
        """
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File service is not configured",
            )

        try:
            # List all blobs with files/ prefix
            blobs = self.bucket.list_blobs(prefix="files/")

            user_files = []
            for blob in blobs:
                if blob.metadata and blob.metadata.get("uploaded_by") == str(user_id):
                    # Generate file URL
                    if blob.metadata.get("is_public", "false").lower() == "true":
                        file_url = blob.public_url
                        is_public = True
                    else:
                        file_url = blob.generate_signed_url(
                            expiration=datetime.now(timezone.utc).timestamp() + 3600,
                            method="GET",
                        )
                        is_public = False

                    # Create file info
                    file_info = FileInfo(
                        file_id=blob.metadata.get("file_id", ""),
                        file_name=blob.metadata.get("original_filename", "Unknown"),
                        file_url=file_url,
                        file_size=blob.size,
                        file_type=blob.metadata.get("file_type", "other"),
                        content_type=blob.content_type or "application/octet-stream",
                        uploaded_by=user_id,
                        uploaded_at=datetime.fromisoformat(
                            blob.metadata.get(
                                "uploaded_at", datetime.now(timezone.utc).isoformat()
                            )
                        ),
                        is_public=is_public,
                    )

                    user_files.append(file_info)

            # Sort by upload date (newest first)
            user_files.sort(key=lambda x: x.uploaded_at, reverse=True)

            # Apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page

            return user_files[start_idx:end_idx]

        except GoogleCloudError as e:
            logger.error(f"❌ GCS error during file listing: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list files: {str(e)}",
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error during file listing: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while listing files",
            )


# Global GCS service instance
gcs_service = GCSService()
