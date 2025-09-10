"""
Job Service

This module handles business logic for the job system including:
- Company management (CRUD operations)
- Job management (CRUD operations)
- Job application management
- Search and filtering functionality
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import text

from app.config.database import get_database
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


class JobService:
    """Service class for job system operations"""

    def __init__(self):
        self.db = get_database()

    async def create_company(
        self, company_data: CompanyCreate, user_id: int
    ) -> Company:
        """Create a new company"""
        try:
            query = text(
                """
                INSERT INTO companies (name, description, website, industry, size, location, created_by)
                VALUES (:name, :description, :website, :industry, :size, :location, :created_by)
                RETURNING id, name, description, website, industry, size, location, created_by, created_at, updated_at
            """
            )

            result = self.db.execute(
                query,
                {
                    "name": company_data.name,
                    "description": company_data.description,
                    "website": company_data.website,
                    "industry": company_data.industry,
                    "size": company_data.size,
                    "location": company_data.location,
                    "created_by": user_id,
                },
            )

            company_data = result.fetchone()
            if not company_data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create company",
                )

            return Company(
                id=company_data.id,
                name=company_data.name,
                description=company_data.description,
                website=company_data.website,
                industry=company_data.industry,
                size=company_data.size,
                location=company_data.location,
                created_by=company_data.created_by,
                created_at=company_data.created_at,
                updated_at=company_data.updated_at,
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_company(self, company_id: int) -> Optional[Company]:
        """Get a company by ID"""
        try:
            query = text(
                """
                SELECT id, name, description, website, industry, size, location, created_by, created_at, updated_at
                FROM companies WHERE id = :company_id
            """
            )

            result = self.db.execute(query, {"company_id": company_id})
            company_data = result.fetchone()

            if not company_data:
                return None

            return Company(
                id=company_data.id,
                name=company_data.name,
                description=company_data.description,
                website=company_data.website,
                industry=company_data.industry,
                size=company_data.size,
                location=company_data.location,
                created_by=company_data.created_by,
                created_at=company_data.created_at,
                updated_at=company_data.updated_at,
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_companies(
        self, page: int = 1, per_page: int = 20
    ) -> CompanyListResponse:
        """Get list of companies with pagination"""
        try:
            offset = (page - 1) * per_page

            # Get total count
            count_query = text("SELECT COUNT(*) as total FROM companies")
            count_result = self.db.execute(count_query)
            total = count_result.fetchone().total

            # Get companies
            query = text(
                """
                SELECT id, name, description, website, industry, size, location, created_by, created_at, updated_at
                FROM companies
                ORDER BY created_at DESC
                LIMIT :per_page OFFSET :offset
            """
            )

            result = self.db.execute(query, {"per_page": per_page, "offset": offset})
            companies_data = result.fetchall()

            companies = [
                Company(
                    id=company.id,
                    name=company.name,
                    description=company.description,
                    website=company.website,
                    industry=company.industry,
                    size=company.size,
                    location=company.location,
                    created_by=company.created_by,
                    created_at=company.created_at,
                    updated_at=company.updated_at,
                )
                for company in companies_data
            ]

            total_pages = (total + per_page - 1) // per_page

            return CompanyListResponse(
                companies=companies,
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def create_job(self, job_data: JobCreate, user_id: int) -> Job:
        """Create a new job posting"""
        try:
            # Verify company exists and user has permission
            company = await self.get_company(job_data.company_id)
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
                )

            query = text(
                """
                INSERT INTO jobs (title, description, requirements, location, salary_min, salary_max,
                                employment_type, experience_level, remote_work, company_id, posted_by,
                                application_deadline)
                VALUES (:title, :description, :requirements, :location, :salary_min, :salary_max,
                       :employment_type, :experience_level, :remote_work, :company_id, :posted_by,
                       :application_deadline)
                RETURNING id, title, description, requirements, location, salary_min, salary_max,
                         employment_type, experience_level, remote_work, company_id, posted_by,
                         is_active, application_deadline, created_at, updated_at
            """
            )

            result = self.db.execute(
                query,
                {
                    "title": job_data.title,
                    "description": job_data.description,
                    "requirements": job_data.requirements,
                    "location": job_data.location,
                    "salary_min": job_data.salary_min,
                    "salary_max": job_data.salary_max,
                    "employment_type": job_data.employment_type.value,
                    "experience_level": job_data.experience_level.value,
                    "remote_work": job_data.remote_work,
                    "company_id": job_data.company_id,
                    "posted_by": user_id,
                    "application_deadline": job_data.application_deadline,
                },
            )

            job_data = result.fetchone()
            if not job_data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create job",
                )

            return Job(
                id=job_data.id,
                title=job_data.title,
                description=job_data.description,
                requirements=job_data.requirements,
                location=job_data.location,
                salary_min=job_data.salary_min,
                salary_max=job_data.salary_max,
                employment_type=job_data.employment_type,
                experience_level=job_data.experience_level,
                remote_work=job_data.remote_work,
                company_id=job_data.company_id,
                posted_by=job_data.posted_by,
                is_active=job_data.is_active,
                application_deadline=job_data.application_deadline,
                created_at=job_data.created_at,
                updated_at=job_data.updated_at,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_jobs(self, search_request: JobSearchRequest) -> JobListResponse:
        """Get list of jobs with search and filtering"""
        try:
            offset = (search_request.page - 1) * search_request.per_page

            # Build WHERE clause
            where_conditions = ["j.is_active = true"]
            params = {"per_page": search_request.per_page, "offset": offset}

            if search_request.query:
                where_conditions.append(
                    "(j.title ILIKE :query OR j.description ILIKE :query)"
                )
                params["query"] = f"%{search_request.query}%"

            if search_request.location:
                where_conditions.append("j.location ILIKE :location")
                params["location"] = f"%{search_request.location}%"

            if search_request.employment_type:
                where_conditions.append("j.employment_type = :employment_type")
                params["employment_type"] = search_request.employment_type.value

            if search_request.experience_level:
                where_conditions.append("j.experience_level = :experience_level")
                params["experience_level"] = search_request.experience_level.value

            if search_request.remote_work is not None:
                where_conditions.append("j.remote_work = :remote_work")
                params["remote_work"] = search_request.remote_work

            if search_request.salary_min:
                where_conditions.append("j.salary_max >= :salary_min")
                params["salary_min"] = search_request.salary_min

            if search_request.company_id:
                where_conditions.append("j.company_id = :company_id")
                params["company_id"] = search_request.company_id

            where_clause = " AND ".join(where_conditions)

            # Get total count
            count_query = text(
                f"""
                SELECT COUNT(*) as total
                FROM jobs j
                JOIN companies c ON j.company_id = c.id
                WHERE {where_clause}
            """
            )
            count_result = self.db.execute(count_query, params)
            total = count_result.fetchone().total

            # Get jobs with company info
            query = text(
                f"""
                SELECT j.id, j.title, j.description, j.requirements, j.location, j.salary_min, j.salary_max,
                       j.employment_type, j.experience_level, j.remote_work, j.company_id, j.posted_by,
                       j.is_active, j.application_deadline, j.created_at, j.updated_at,
                       c.id as company_id, c.name as company_name, c.description as company_description,
                       c.website as company_website, c.industry as company_industry, c.size as company_size,
                       c.location as company_location, c.created_by as company_created_by,
                       c.created_at as company_created_at, c.updated_at as company_updated_at
                FROM jobs j
                JOIN companies c ON j.company_id = c.id
                WHERE {where_clause}
                ORDER BY j.created_at DESC
                LIMIT :per_page OFFSET :offset
            """
            )

            result = self.db.execute(query, params)
            jobs_data = result.fetchall()

            jobs = []
            for job_data in jobs_data:
                company = Company(
                    id=job_data.company_id,
                    name=job_data.company_name,
                    description=job_data.company_description,
                    website=job_data.company_website,
                    industry=job_data.company_industry,
                    size=job_data.company_size,
                    location=job_data.company_location,
                    created_by=job_data.company_created_by,
                    created_at=job_data.company_created_at,
                    updated_at=job_data.company_updated_at,
                )

                job = Job(
                    id=job_data.id,
                    title=job_data.title,
                    description=job_data.description,
                    requirements=job_data.requirements,
                    location=job_data.location,
                    salary_min=job_data.salary_min,
                    salary_max=job_data.salary_max,
                    employment_type=job_data.employment_type,
                    experience_level=job_data.experience_level,
                    remote_work=job_data.remote_work,
                    company_id=job_data.company_id,
                    posted_by=job_data.posted_by,
                    is_active=job_data.is_active,
                    application_deadline=job_data.application_deadline,
                    created_at=job_data.created_at,
                    updated_at=job_data.updated_at,
                )

                jobs.append(JobWithCompany(**job.model_dump(), company=company))

            total_pages = (
                total + search_request.per_page - 1
            ) // search_request.per_page

            return JobListResponse(
                jobs=jobs,
                total=total,
                page=search_request.page,
                per_page=search_request.per_page,
                total_pages=total_pages,
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_job(self, job_id: int) -> Optional[JobWithCompany]:
        """Get a job by ID with company information"""
        try:
            query = text(
                """
                SELECT j.id, j.title, j.description, j.requirements, j.location, j.salary_min, j.salary_max,
                       j.employment_type, j.experience_level, j.remote_work, j.company_id, j.posted_by,
                       j.is_active, j.application_deadline, j.created_at, j.updated_at,
                       c.id as company_id, c.name as company_name, c.description as company_description,
                       c.website as company_website, c.industry as company_industry, c.size as company_size,
                       c.location as company_location, c.created_by as company_created_by,
                       c.created_at as company_created_at, c.updated_at as company_updated_at
                FROM jobs j
                JOIN companies c ON j.company_id = c.id
                WHERE j.id = :job_id AND j.is_active = true
            """
            )

            result = self.db.execute(query, {"job_id": job_id})
            job_data = result.fetchone()

            if not job_data:
                return None

            company = Company(
                id=job_data.company_id,
                name=job_data.company_name,
                description=job_data.company_description,
                website=job_data.company_website,
                industry=job_data.company_industry,
                size=job_data.company_size,
                location=job_data.company_location,
                created_by=job_data.company_created_by,
                created_at=job_data.company_created_at,
                updated_at=job_data.company_updated_at,
            )

            job = Job(
                id=job_data.id,
                title=job_data.title,
                description=job_data.description,
                requirements=job_data.requirements,
                location=job_data.location,
                salary_min=job_data.salary_min,
                salary_max=job_data.salary_max,
                employment_type=job_data.employment_type,
                experience_level=job_data.experience_level,
                remote_work=job_data.remote_work,
                company_id=job_data.company_id,
                posted_by=job_data.posted_by,
                is_active=job_data.is_active,
                application_deadline=job_data.application_deadline,
                created_at=job_data.created_at,
                updated_at=job_data.updated_at,
            )

            return JobWithCompany(**job.model_dump(), company=company)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def apply_to_job(
        self, application_data: JobApplicationCreate, user_id: int
    ) -> JobApplication:
        """Apply to a job"""
        try:
            # Check if job exists and is active
            job = await self.get_job(application_data.job_id)
            if not job:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job not found or not active",
                )

            # Check if user already applied
            existing_query = text(
                """
                SELECT id FROM job_applications
                WHERE job_id = :job_id AND applicant_id = :applicant_id
            """
            )
            existing_result = self.db.execute(
                existing_query,
                {"job_id": application_data.job_id, "applicant_id": user_id},
            )

            if existing_result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already applied to this job",
                )

            # Create application
            query = text(
                """
                INSERT INTO job_applications (job_id, applicant_id, cover_letter, resume_url)
                VALUES (:job_id, :applicant_id, :cover_letter, :resume_url)
                RETURNING id, job_id, applicant_id, cover_letter, resume_url, status, applied_at, reviewed_at, notes
            """
            )

            result = self.db.execute(
                query,
                {
                    "job_id": application_data.job_id,
                    "applicant_id": user_id,
                    "cover_letter": application_data.cover_letter,
                    "resume_url": application_data.resume_url,
                },
            )

            app_data = result.fetchone()
            if not app_data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create application",
                )

            return JobApplication(
                id=app_data.id,
                job_id=app_data.job_id,
                applicant_id=app_data.applicant_id,
                cover_letter=app_data.cover_letter,
                resume_url=app_data.resume_url,
                status=app_data.status,
                applied_at=app_data.applied_at,
                reviewed_at=app_data.reviewed_at,
                notes=app_data.notes,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )


# Create service instance
job_service = JobService()
