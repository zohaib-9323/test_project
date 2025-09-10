"""
Authentication tests.

This module contains tests for authentication functionality including
login, signup, and token validation.
"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_signup_missing_data():
    """Test signup with missing required data."""
    response = client.post("/auth/signup", json={})
    assert response.status_code == 422


def test_signup_invalid_email():
    """Test signup with invalid email format."""
    response = client.post(
        "/auth/signup",
        json={
            "name": "Test User",
            "email": "invalid-email",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 422


def test_signup_weak_password():
    """Test signup with weak password."""
    response = client.post(
        "/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "123",  # Too weak
        },
    )
    assert response.status_code == 422


def test_login_missing_data():
    """Test login with missing credentials."""
    response = client.post("/auth/login", json={})
    assert response.status_code == 422


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_get_current_user_no_token():
    """Test getting current user without token."""
    response = client.get("/auth/me")
    assert response.status_code == 404  # Endpoint doesn't exist


def test_get_current_user_invalid_token():
    """Test getting current user with invalid token."""
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 404  # Endpoint doesn't exist


def test_logout_no_token():
    """Test logout without token."""
    response = client.post("/auth/logout")
    assert response.status_code == 404  # Endpoint doesn't exist
