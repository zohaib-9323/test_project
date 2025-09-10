"""
Job System Models

This module defines Pydantic models for the job system including:
- Company model for company information
- Job model for job postings
- Job application model for user applications
- Various request/response models for API endpoints
"""

from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class EmploymentType(str, Enum):
    """Employment type enumeration"""
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class ExperienceLevel(str, Enum):
    """Experience level enumeration"""
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"


class ApplicationStatus(str, Enum):
    """Job application status enumeration"""
    PENDING = "pending"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class UserRole(str, Enum):
    """User role enumeration (updated to include company)"""
    ADMIN = "admin"
    USER = "user"
    COMPANY = "company"


class CompanyBase(BaseModel):
    """Base company model with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Company name")
    description: Optional[str] = Field(None, description="Company description")
    website: Optional[str] = Field(None, max_length=255, description="Company website URL")
    industry: Optional[str] = Field(None, max_length=100, description="Company industry")
    size: Optional[str] = Field(None, max_length=50, description="Company size")
    location: Optional[str] = Field(None, max_length=255, description="Company location")


class CompanyCreate(CompanyBase):
    """Model for creating a new company"""
    pass


class CompanyUpdate(BaseModel):
    """Model for updating company information"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)


class Company(CompanyBase):
    """Complete company model with database fields"""
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobBase(BaseModel):
    """Base job model with common fields"""
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    description: str = Field(..., min_length=1, description="Job description")
    requirements: Optional[str] = Field(None, description="Job requirements")
    location: Optional[str] = Field(None, max_length=255, description="Job location")
    salary_min: Optional[int] = Field(None, ge=0, description="Minimum salary")
    salary_max: Optional[int] = Field(None, ge=0, description="Maximum salary")
    employment_type: EmploymentType = Field(..., description="Type of employment")
    experience_level: ExperienceLevel = Field(..., description="Required experience level")
    remote_work: bool = Field(False, description="Whether remote work is allowed")
    application_deadline: Optional[date] = Field(None, description="Application deadline")


class JobCreate(JobBase):
    """Model for creating a new job"""
    company_id: int = Field(..., description="ID of the company posting the job")


class JobUpdate(BaseModel):
    """Model for updating job information"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    requirements: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    employment_type: Optional[EmploymentType] = None
    experience_level: Optional[ExperienceLevel] = None
    remote_work: Optional[bool] = None
    application_deadline: Optional[date] = None
    is_active: Optional[bool] = None


class Job(JobBase):
    """Complete job model with database fields"""
    id: int
    company_id: int
    posted_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobWithCompany(Job):
    """Job model with company information"""
    company: Company

    class Config:
        from_attributes = True


class JobApplicationBase(BaseModel):
    """Base job application model"""
    cover_letter: Optional[str] = Field(None, description="Cover letter")
    resume_url: Optional[str] = Field(None, max_length=500, description="Resume URL")


class JobApplicationCreate(JobApplicationBase):
    """Model for creating a job application"""
    job_id: int = Field(..., description="ID of the job being applied to")


class JobApplicationUpdate(BaseModel):
    """Model for updating job application status"""
    status: ApplicationStatus = Field(..., description="Application status")
    notes: Optional[str] = Field(None, description="Review notes")


class JobApplication(JobApplicationBase):
    """Complete job application model with database fields"""
    id: int
    job_id: int
    applicant_id: int
    status: ApplicationStatus
    applied_at: datetime
    reviewed_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


class JobApplicationWithDetails(JobApplication):
    """Job application model with job and applicant details"""
    job: Job
    applicant: dict  # Basic user info

    class Config:
        from_attributes = True


class JobSearchRequest(BaseModel):
    """Model for job search parameters"""
    query: Optional[str] = Field(None, description="Search query")
    location: Optional[str] = Field(None, description="Location filter")
    employment_type: Optional[EmploymentType] = Field(None, description="Employment type filter")
    experience_level: Optional[ExperienceLevel] = Field(None, description="Experience level filter")
    remote_work: Optional[bool] = Field(None, description="Remote work filter")
    salary_min: Optional[int] = Field(None, ge=0, description="Minimum salary filter")
    company_id: Optional[int] = Field(None, description="Company filter")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class JobListResponse(BaseModel):
    """Response model for job listing"""
    jobs: List[JobWithCompany]
    total: int
    page: int
    per_page: int
    total_pages: int


class CompanyListResponse(BaseModel):
    """Response model for company listing"""
    companies: List[Company]
    total: int
    page: int
    per_page: int
    total_pages: int


class JobApplicationListResponse(BaseModel):
    """Response model for job application listing"""
    applications: List[JobApplicationWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int
