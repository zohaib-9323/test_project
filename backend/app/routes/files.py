"""
File Upload API Routes

This module provides REST API endpoints for file upload and management:
- POST /files/upload - Upload a new file
- GET /files/ - List user's files
- GET /files/{file_id} - Get file information
- DELETE /files/{file_id} - Delete a file
- PUT /files/{file_id} - Update file metadata

All endpoints require authentication and use Google Cloud Storage for file storage.
"""

import logging
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from app.middleware.auth import get_current_verified_user
from app.models.file import (
    FileDeleteResponse,
    FileInfo,
    FileListResponse,
    FileUploadResponse,
)
from app.models.user import UserResponse
from app.services.gcs_service import gcs_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    is_public: bool = Form(False),
    current_user: UserResponse = Depends(get_current_verified_user),
):
    """
    Upload a file to Google Cloud Storage.

    Args:
        file: The file to upload
        is_public: Whether the file should be publicly accessible
        current_user: Current authenticated user

    Returns:
        FileUploadResponse: Information about the uploaded file
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
            )

        # Check file size (limit to 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10MB limit",
            )

        # Reset file pointer
        await file.seek(0)

        # Upload file using GCS service
        file_info = await gcs_service.upload_file(file, current_user.id, is_public)

        logger.info(
            f"✅ File uploaded successfully by user {current_user.id}: {file.filename}"
        )

        return FileUploadResponse(
            message="File uploaded successfully",
            success=True,
            file_id=file_info.file_id,
            file_name=file_info.file_name,
            file_url=file_info.file_url,
            file_size=file_info.file_size,
            file_type=file_info.file_type,
            uploaded_at=file_info.uploaded_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during file upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during file upload",
        )


@router.get("/", response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Files per page"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    current_user: UserResponse = Depends(get_current_verified_user),
):
    """
    List files uploaded by the current user.

    Args:
        page: Page number (1-based)
        per_page: Number of files per page
        file_type: Filter by file type (optional)
        current_user: Current authenticated user

    Returns:
        FileListResponse: List of user's files with pagination
    """
    try:
        # Get user's files
        files = await gcs_service.list_user_files(current_user.id, page, per_page)

        # Filter by file type if specified
        if file_type:
            files = [f for f in files if f.file_type == file_type]

        # Calculate total count (simplified - in production, you might want to store this in a database)
        total = len(files)

        logger.info(f"✅ Listed {len(files)} files for user {current_user.id}")

        return FileListResponse(files=files, total=total, page=page, per_page=per_page)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during file listing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing files",
        )


@router.get("/{file_id}", response_model=FileInfo)
async def get_file_info(
    file_id: str, current_user: UserResponse = Depends(get_current_verified_user)
):
    """
    Get information about a specific file.

    Args:
        file_id: ID of the file
        current_user: Current authenticated user

    Returns:
        FileInfo: Information about the file
    """
    try:
        file_info = await gcs_service.get_file_info(file_id, current_user.id)

        logger.info(f"✅ Retrieved file info for {file_id} by user {current_user.id}")

        return file_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during file info retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while getting file info",
        )


@router.delete("/{file_id}", response_model=FileDeleteResponse)
async def delete_file(
    file_id: str, current_user: UserResponse = Depends(get_current_verified_user)
):
    """
    Delete a file.

    Args:
        file_id: ID of the file to delete
        current_user: Current authenticated user

    Returns:
        FileDeleteResponse: Confirmation of file deletion
    """
    try:
        success = await gcs_service.delete_file(file_id, current_user.id)

        if success:
            logger.info(f"✅ File {file_id} deleted by user {current_user.id}")

            return FileDeleteResponse(
                message="File deleted successfully", success=True, file_id=file_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during file deletion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during file deletion",
        )


@router.get("/download/{file_id}")
async def download_file(
    file_id: str, current_user: UserResponse = Depends(get_current_verified_user)
):
    """
    Download a file (redirects to signed URL).

    Args:
        file_id: ID of the file to download
        current_user: Current authenticated user

    Returns:
        Redirect to file URL
    """
    try:
        file_info = await gcs_service.get_file_info(file_id, current_user.id)

        logger.info(
            f"✅ File download initiated for {file_id} by user {current_user.id}"
        )

        # Return the file URL for download
        from fastapi.responses import RedirectResponse

        return RedirectResponse(url=file_info.file_url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during file download: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during file download",
        )


@router.get("/health/status")
async def file_service_health():
    """
    Check the health status of the file service.

    Returns:
        dict: Service status information
    """
    return {
        "service": "file_upload",
        "status": "healthy" if gcs_service.enabled else "disabled",
        "gcs_configured": gcs_service.enabled,
        "bucket_name": gcs_service.bucket_name if gcs_service.enabled else None,
        "project_id": gcs_service.project_id if gcs_service.enabled else None,
    }
