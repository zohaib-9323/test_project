"""
Basic tests for the main FastAPI application.

This module contains basic tests to ensure the application starts correctly
and basic endpoints are working.
"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Welcome" in response.json()["message"]


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_file_service_health():
    """Test the file service health endpoint."""
    response = client.get("/files/health/status")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "status" in data
    assert "gcs_configured" in data


def test_auth_endpoints_exist():
    """Test that auth endpoints are properly configured."""
    # Test that auth endpoints exist (should return 422 for missing data, not 404)
    response = client.post("/auth/login")
    assert response.status_code == 422  # Validation error, not 404


def test_user_endpoints_exist():
    """Test that user endpoints are properly configured."""
    # Test that user endpoints exist (should return 403 for missing auth, not 404)
    response = client.get("/users/")
    assert (
        response.status_code == 403
    )  # Forbidden (email verification required), not 404


def test_email_endpoints_exist():
    """Test that email verification endpoints are properly configured."""
    # Test that email endpoints exist (should return 422 for missing data, not 404)
    response = client.post("/email/send-otp")
    assert response.status_code == 422  # Validation error, not 404
