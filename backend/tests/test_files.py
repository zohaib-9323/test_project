"""
File upload tests.

This module contains tests for file upload functionality.
Note: These tests will pass even when GCS is not configured
since the service gracefully handles missing configuration.
"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_file_upload_no_auth():
    """Test file upload without authentication."""
    response = client.post("/files/upload")
    assert response.status_code == 403  # Forbidden (email verification required)


def test_file_upload_invalid_auth():
    """Test file upload with invalid authentication."""
    response = client.post(
        "/files/upload", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_list_files_no_auth():
    """Test listing files without authentication."""
    response = client.get("/files/")
    assert response.status_code == 403  # Forbidden (email verification required)


def test_get_file_info_no_auth():
    """Test getting file info without authentication."""
    response = client.get("/files/test-file-id")
    assert response.status_code == 403  # Forbidden (email verification required)


def test_delete_file_no_auth():
    """Test deleting file without authentication."""
    response = client.delete("/files/test-file-id")
    assert response.status_code == 403  # Forbidden (email verification required)


def test_download_file_no_auth():
    """Test downloading file without authentication."""
    response = client.get("/files/download/test-file-id")
    assert response.status_code == 403  # Forbidden (email verification required)


def test_file_service_health():
    """Test file service health endpoint (should work without auth)."""
    response = client.get("/files/health/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "file_upload"
    # Status can be "healthy" or "disabled" depending on GCS configuration
    assert data["status"] in ["healthy", "disabled"]
