"""
File Upload Models

This module defines Pydantic models for file upload operations including:
- File metadata
- Upload responses
- File information
- File deletion requests

These models handle file operations with Google Cloud Storage integration.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, validator


class FileType(str, Enum):
    """Supported file types for upload."""

    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    OTHER = "other"


class FileUploadResponse(BaseModel):
    """Response model for successful file upload."""

    message: str
    success: bool
    file_id: str
    file_name: str
    file_url: str
    file_size: int
    file_type: str
    uploaded_at: datetime


class FileInfo(BaseModel):
    """Model for file information."""

    file_id: str
    file_name: str
    file_url: str
    file_size: int
    file_type: str
    content_type: str
    uploaded_by: int  # User ID
    uploaded_at: datetime
    is_public: bool = False


class FileListResponse(BaseModel):
    """Response model for file listing."""

    files: List[FileInfo]
    total: int
    page: int
    per_page: int


class FileDeleteResponse(BaseModel):
    """Response model for file deletion."""

    message: str
    success: bool
    file_id: str


class FileUpdateRequest(BaseModel):
    """Request model for updating file metadata."""

    file_name: Optional[str] = None
    is_public: Optional[bool] = None

    @validator("file_name")
    def validate_file_name(cls, v):
        if v is not None and len(v.strip()) < 1:
            raise ValueError("File name cannot be empty")
        return v.strip() if v else v


class FileSearchRequest(BaseModel):
    """Request model for searching files."""

    query: Optional[str] = None
    file_type: Optional[FileType] = None
    uploaded_by: Optional[int] = None
    page: int = 1
    per_page: int = 20

    @validator("page")
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Page must be at least 1")
        return v

    @validator("per_page")
    def validate_per_page(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Per page must be between 1 and 100")
        return v
