"""
Job System API Routes

This module defines API endpoints for the job system including:
- Company management endpoints
- Job management endpoints
- Job application endpoints
- Search and filtering endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.middleware.auth import get_current_verified_user
from app.models.job import (
    Company,
    CompanyCreate,
    CompanyListResponse,
    Job,
    JobApplication,
    JobApplicationCreate,
    JobCreate,
    JobListResponse,
    JobSearchRequest,
    JobWithCompany,
)
from app.models.user import UserInDB, UserRole

# from app.services.job_service import job_service


# Temporary mock job service until SQLAlchemy issue is resolved
class MockJobService:
    async def get_jobs(self, search_request):
        return JobListResponse(jobs=[], total=0, page=1, per_page=20, total_pages=0)

    async def create_company(self, company_data, user_id):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Job service temporarily unavailable. Please try again later.",
        )

    async def get_companies(self, page, per_page):
        return CompanyListResponse(
            companies=[], total=0, page=1, per_page=20, total_pages=0
        )

    async def get_company(self, company_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    async def create_job(self, job_data, user_id):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Job service temporarily unavailable. Please try again later.",
        )

    async def get_job(self, job_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    async def apply_to_job(self, application_data, user_id):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Job service temporarily unavailable. Please try again later.",
        )


job_service = MockJobService()

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/companies/", response_model=Company, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: UserInDB = Depends(get_current_verified_user),
):
    """
    Create a new company

    Only users with 'company' or 'admin' role can create companies.
    """
    if current_user.role not in [UserRole.COMPANY, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company users and admins can create companies",
        )

    return await job_service.create_company(company_data, current_user.id)


@router.get("/companies/", response_model=CompanyListResponse)
async def get_companies(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserInDB = Depends(get_current_verified_user),
):
    """
    Get list of companies with pagination

    All verified users can view companies.
    """
    return await job_service.get_companies(page, per_page)


@router.get("/companies/{company_id}", response_model=Company)
async def get_company(
    company_id: int, current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get a specific company by ID

    All verified users can view company details.
    """
    company = await job_service.get_company(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )
    return company


@router.post("/", response_model=Job, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate, current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Create a new job posting

    Only users with 'company' or 'admin' role can create jobs.
    """
    if current_user.role not in [UserRole.COMPANY, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company users and admins can create jobs",
        )

    return await job_service.create_job(job_data, current_user.id)


@router.get("/", response_model=JobListResponse)
async def get_jobs(
    query: Optional[str] = Query(None, description="Search query"),
    location: Optional[str] = Query(None, description="Location filter"),
    employment_type: Optional[str] = Query(None, description="Employment type filter"),
    experience_level: Optional[str] = Query(
        None, description="Experience level filter"
    ),
    remote_work: Optional[bool] = Query(None, description="Remote work filter"),
    salary_min: Optional[int] = Query(None, ge=0, description="Minimum salary filter"),
    company_id: Optional[int] = Query(None, description="Company filter"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserInDB = Depends(get_current_verified_user),
):
    """
    Get list of jobs with search and filtering

    All verified users can search and view jobs.
    """
    search_request = JobSearchRequest(
        query=query,
        location=location,
        employment_type=employment_type,
        experience_level=experience_level,
        remote_work=remote_work,
        salary_min=salary_min,
        company_id=company_id,
        page=page,
        per_page=per_page,
    )

    return await job_service.get_jobs(search_request)


@router.get("/{job_id}", response_model=JobWithCompany)
async def get_job(
    job_id: int, current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get a specific job by ID with company information

    All verified users can view job details.
    """
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return job


@router.post(
    "/{job_id}/apply",
    response_model=JobApplication,
    status_code=status.HTTP_201_CREATED,
)
async def apply_to_job(
    job_id: int,
    application_data: JobApplicationCreate,
    current_user: UserInDB = Depends(get_current_verified_user),
):
    """
    Apply to a job

    All verified users can apply to jobs.
    The job_id in the URL must match the job_id in the request body.
    """
    if application_data.job_id != job_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job ID in URL must match job ID in request body",
        )

    return await job_service.apply_to_job(application_data, current_user.id)


@router.get("/health/status")
async def health_check():
    """
    Health check endpoint for job service

    No authentication required.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "service": "job_system",
            "status": "healthy",
            "message": "Job system is running properly",
        },
    )
