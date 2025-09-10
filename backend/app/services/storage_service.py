"""
Google Cloud Storage Service

This module handles file operations with Google Cloud Storage including:
- File upload to GCS
- File download from GCS
- File deletion from GCS
- Signed URL generation for secure access
- File metadata management
"""

import mimetypes
import os
import uuid
from datetime import datetime, timedelta
from typing import BinaryIO, Optional, Tuple

import magic  # For better MIME type detection
from fastapi import HTTPException, status
from google.cloud import storage
from google.cloud.exceptions import NotFound


class StorageService:
    def __init__(self):
        # Initialize Google Cloud Storage client
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        self.project_id = os.getenv("GCS_PROJECT_ID")

        if not self.bucket_name or not self.project_id:
            print("⚠️  Google Cloud Storage not configured. Using mock storage service.")
            self.enabled = False
            return

        try:
            # Initialize the client (will use service account from environment)
            self.client = storage.Client(project=self.project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            self.enabled = True
            print(f"✅ Connected to Google Cloud Storage bucket: {self.bucket_name}")
        except Exception as e:
            print(f"❌ Failed to connect to Google Cloud Storage: {str(e)}")
            self.enabled = False

    def _generate_file_id(self) -> str:
        """Generate a unique file ID"""
        return str(uuid.uuid4())

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        return os.path.splitext(filename)[1].lower()

    def _detect_mime_type(self, file_content: bytes, filename: str) -> str:
        """Detect MIME type of file content"""
        try:
            # Try to use python-magic for better detection
            mime_type = magic.from_buffer(file_content, mime=True)
            if mime_type and mime_type != "application/octet-stream":
                return mime_type
        except:
            pass

        # Fallback to mimetypes module
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"

    def _determine_file_type(self, mime_type: str) -> str:
        """Determine file type category from MIME type"""
        if mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("video/"):
            return "video"
        elif mime_type.startswith("audio/"):
            return "audio"
        elif mime_type in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
            "text/csv",
        ]:
            return "document"
        else:
            return "other"

    def _generate_gcs_path(self, file_id: str, filename: str) -> str:
        """Generate GCS path for file storage"""
        # Organize files by date and type
        date_folder = datetime.now().strftime("%Y/%m/%d")
        return f"uploads/{date_folder}/{file_id}{self._get_file_extension(filename)}"

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        user_id: int,
        description: Optional[str] = None,
        access_level: str = "private",
        tags: Optional[list] = None,
    ) -> dict:
        """
        Upload file to Google Cloud Storage

        Args:
            file_content: File content as bytes
            filename: Original filename
            user_id: ID of user uploading the file
            description: Optional file description
            access_level: File access level (private, public, restricted)
            tags: Optional tags for the file

        Returns:
            dict: File metadata and URLs
        """
        if not self.enabled:
            # Mock response for testing
            file_id = self._generate_file_id()
            return {
                "file_id": file_id,
                "filename": filename,
                "original_filename": filename,
                "file_type": "other",
                "file_size": len(file_content),
                "mime_type": "application/octet-stream",
                "access_level": access_level,
                "upload_url": f"mock://upload/{file_id}",
                "download_url": f"mock://download/{file_id}",
                "thumbnail_url": None,
                "description": description,
                "tags": tags or [],
                "uploaded_by": user_id,
                "uploaded_at": datetime.now(),
                "expires_at": None,
            }

        try:
            # Generate unique file ID and GCS path
            file_id = self._generate_file_id()
            gcs_path = self._generate_gcs_path(file_id, filename)

            # Detect MIME type and file type
            mime_type = self._detect_mime_type(file_content, filename)
            file_type = self._determine_file_type(mime_type)

            # Create blob and upload file
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_string(file_content, content_type=mime_type)

            # Set metadata
            blob.metadata = {
                "original_filename": filename,
                "uploaded_by": str(user_id),
                "file_type": file_type,
                "description": description or "",
                "tags": ",".join(tags) if tags else "",
            }
            blob.patch()

            # Generate URLs
            upload_url = f"gs://{self.bucket_name}/{gcs_path}"
            download_url = self._generate_signed_url(gcs_path, access_level)
            thumbnail_url = (
                self._generate_thumbnail_url(gcs_path, file_type)
                if file_type == "image"
                else None
            )

            return {
                "file_id": file_id,
                "filename": f"{file_id}{self._get_file_extension(filename)}",
                "original_filename": filename,
                "file_type": file_type,
                "file_size": len(file_content),
                "mime_type": mime_type,
                "access_level": access_level,
                "gcs_bucket": self.bucket_name,
                "gcs_path": gcs_path,
                "upload_url": upload_url,
                "download_url": download_url,
                "thumbnail_url": thumbnail_url,
                "description": description,
                "tags": tags or [],
                "uploaded_by": user_id,
                "uploaded_at": datetime.now(),
                "expires_at": None,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}",
            )

    def _generate_signed_url(
        self, gcs_path: str, access_level: str, expiration_hours: int = 24
    ) -> str:
        """Generate signed URL for file access"""
        try:
            blob = self.bucket.blob(gcs_path)

            if access_level == "public":
                # For public files, return public URL
                return blob.public_url
            else:
                # For private/restricted files, generate signed URL
                expiration = datetime.now() + timedelta(hours=expiration_hours)
                return blob.generate_signed_url(expiration=expiration)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate download URL: {str(e)}",
            )

    def _generate_thumbnail_url(self, gcs_path: str, file_type: str) -> Optional[str]:
        """Generate thumbnail URL for images"""
        if file_type != "image":
            return None

        try:
            # For images, you might want to generate thumbnails
            # This is a placeholder - you'd implement actual thumbnail generation
            return None
        except:
            return None

    async def delete_file(self, gcs_path: str) -> bool:
        """Delete file from Google Cloud Storage"""
        if not self.enabled:
            return True  # Mock success

        try:
            blob = self.bucket.blob(gcs_path)
            blob.delete()
            return True
        except NotFound:
            return False  # File doesn't exist
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}",
            )

    async def get_file_info(self, gcs_path: str) -> Optional[dict]:
        """Get file information from GCS"""
        if not self.enabled:
            return None

        try:
            blob = self.bucket.blob(gcs_path)
            if not blob.exists():
                return None

            return {
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created,
                "updated": blob.updated,
                "metadata": blob.metadata or {},
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get file info: {str(e)}",
            )

    async def update_file_metadata(self, gcs_path: str, metadata: dict) -> bool:
        """Update file metadata in GCS"""
        if not self.enabled:
            return True  # Mock success

        try:
            blob = self.bucket.blob(gcs_path)
            blob.metadata = metadata
            blob.patch()
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update file metadata: {str(e)}",
            )


# Global storage service instance
storage_service = StorageService()
