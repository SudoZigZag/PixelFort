"""
Authentication endpoint tests.

Tests user registration, login, and token validation.
"""

import pytest


def test_register_user(client):
    """Test user registration with valid data."""
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "securepass123"
    })
    
    assert response.status_code == 201
    data = response.json()
    
    # Should return token
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Should return user info
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["username"] == "newuser"
    assert "hashed_password" not in data["user"]  # Password not exposed


def test_register_duplicate_email(client, test_user):
    """Test registration fails with duplicate email."""
    response = client.post("/auth/register", json={
        "email": "test@example.com",  # Already exists
        "username": "different",
        "password": "password123"
    })
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_register_duplicate_username(client, test_user):
    """Test registration fails with duplicate username."""
    response = client.post("/auth/register", json={
        "email": "different@example.com",
        "username": "testuser",  # Already exists
        "password": "password123"
    })
    
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]


def test_register_invalid_email(client):
    """Test registration fails with invalid email."""
    response = client.post("/auth/register", json={
        "email": "not-an-email",
        "username": "user",
        "password": "password123"
    })
    
    assert response.status_code == 422  # Validation error


def test_register_short_password(client):
    """Test registration fails with short password."""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "user",
        "password": "short"  # < 8 characters
    })
    
    assert response.status_code == 422  # Validation error


def test_login_success(client, test_user):
    """Test login with correct credentials."""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"


def test_login_wrong_password(client, test_user):
    """Test login fails with wrong password."""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """Test login fails for non-existent user."""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user(client, auth_headers):
    """Test getting current user info with valid token."""
    response = client.get("/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "hashed_password" not in data


def test_get_current_user_no_token(client):
    """Test getting current user fails without token."""
    response = client.get("/auth/me")
    
    assert response.status_code == 403  # Forbidden (no token)


def test_get_current_user_invalid_token(client):
    """Test getting current user fails with invalid token."""
    response = client.get("/auth/me", headers={
        "Authorization": "Bearer invalid-token-xyz"
    })
    
    assert response.status_code == 401