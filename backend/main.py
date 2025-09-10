"""
FastAPI Application Entry Point

This is the main application file that:
- Creates and configures the FastAPI application
- Sets up CORS middleware for frontend communication
- Includes authentication and user management routes
- Provides health check and welcome endpoints

The application serves as a RESTful API for user management with JWT authentication.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routes import auth, email_verification, files, users

# Create FastAPI application instance
app = FastAPI(
    title="User Management API",
    description="A secure user management API with authentication",
    version="1.0.0",
)

# Configure CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API route modules
app.include_router(auth.router)  # Authentication routes (/auth/*)
app.include_router(users.router)  # User management routes (/users/*)
app.include_router(email_verification.router)  # Email verification routes (/email/*)
app.include_router(files.router)  # File upload routes (/files/*)


@app.get("/")
async def root():
    """
    Welcome endpoint for the API.

    Returns:
        dict: Welcome message
    """
    return {"message": "Welcome to User Management API"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring API status.

    Returns:
        dict: Health status
    """
    return {"status": "healthy"}
