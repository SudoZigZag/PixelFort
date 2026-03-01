"""
User endpoint tests.

Tests user CRUD operations.
"""

import pytest


def test_list_users(client, test_user):
    """Test listing all users."""
    response = client.get("/users")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check if response has count and users
    if isinstance(data, dict) and "users" in data:
        # Format: {"count": N, "users": [...]}
        assert data["count"] >= 1
        assert isinstance(data["users"], list)
        assert any(u["email"] == "test@example.com" for u in data["users"])
    else:
        # Format: [...]
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(u["email"] == "test@example.com" for u in data)


def test_get_user_by_id(client, test_user):
    """Test getting a specific user by ID."""
    response = client.get(f"/users/{test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == test_user.id
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "hashed_password" not in data  # Password not exposed


def test_get_nonexistent_user(client):
    """Test getting non-existent user returns 404."""
    response = client.get("/users/999")
    
    assert response.status_code == 404


def test_update_own_user(client, auth_headers, test_user):
    """Test updating your own user account."""
    response = client.patch(f"/users/{test_user.id}", headers=auth_headers, json={
        "username": "updated_username"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["username"] == "updated_username"
    assert data["email"] == "test@example.com"  # Unchanged


def test_update_others_user(client, auth_headers, test_user_2):
    """Test updating another user's account is forbidden."""
    response = client.patch(f"/users/{test_user_2.id}", headers=auth_headers, json={
        "username": "hacked"
    })
    
    assert response.status_code == 403
    assert "only update your own" in response.json()["detail"]


def test_update_user_no_auth(client, test_user):
    """Test updating user fails without authentication."""
    response = client.patch(f"/users/{test_user.id}", json={
        "username": "newname"
    })
    
    assert response.status_code == 403


def test_delete_own_user(client, auth_headers, test_user):
    """Test deleting your own user account."""
    response = client.delete(f"/users/{test_user.id}", headers=auth_headers)
    
    assert response.status_code == 204
    
    # Verify user is gone
    get_response = client.get(f"/users/{test_user.id}")
    assert get_response.status_code == 404


def test_delete_others_user(client, auth_headers, test_user_2):
    """Test deleting another user's account is forbidden."""
    response = client.delete(f"/users/{test_user_2.id}", headers=auth_headers)
    
    assert response.status_code == 403
    assert "only delete your own" in response.json()["detail"]