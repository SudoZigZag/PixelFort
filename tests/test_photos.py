"""
Photo endpoint tests.

Tests photo upload, viewing, and deletion.
"""

import pytest
import io


def test_upload_photo_authenticated(client, auth_headers, test_photo_bytes):
    """Test photo upload with authentication."""
    files = {"file": ("test.jpg", io.BytesIO(test_photo_bytes), "image/jpeg")}
    
    response = client.post("/photos/upload", headers=auth_headers, files=files)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["original_filename"] == "test.jpg"
    assert data["user_id"] == 1
    assert "file_hash" in data
    assert "thumbnail_path" in data


def test_upload_photo_no_auth(client, test_photo_bytes):
    """Test photo upload fails without authentication."""
    files = {"file": ("test.jpg", io.BytesIO(test_photo_bytes), "image/jpeg")}
    
    response = client.post("/photos/upload", files=files)
    
    assert response.status_code == 403  # Not authenticated


def test_upload_duplicate_photo(client, auth_headers, test_photo_bytes):
    """Test uploading same photo twice is rejected (deduplication)."""
    files = {"file": ("test.jpg", io.BytesIO(test_photo_bytes), "image/jpeg")}
    
    # First upload - should succeed
    response1 = client.post("/photos/upload", headers=auth_headers, files=files)
    assert response1.status_code == 201
    
    # Second upload - should fail (duplicate)
    files = {"file": ("test.jpg", io.BytesIO(test_photo_bytes), "image/jpeg")}
    response2 = client.post("/photos/upload", headers=auth_headers, files=files)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


def test_list_photos(client, auth_headers, test_photo_bytes):
    """Test listing all photos."""
    # Upload a photo first
    files = {"file": ("test.jpg", io.BytesIO(test_photo_bytes), "image/jpeg")}
    client.post("/photos/upload", headers=auth_headers, files=files)
    
    # List photos
    response = client.get("/photos")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["original_filename"] == "test.jpg"


def test_get_photo_by_id(client, auth_headers, test_photo_bytes):
    """Test getting a specific photo by ID."""
    # Upload a photo
    files = {"file": ("test.jpg", io.BytesIO(test_photo_bytes), "image/jpeg")}
    upload_response = client.post("/photos/upload", headers=auth_headers, files=files)
    photo_id = upload_response.json()["id"]
    
    # Get photo by ID
    response = client.get(f"/photos/{photo_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == photo_id
    assert data["original_filename"] == "test.jpg"


def test_get_nonexistent_photo(client):
    """Test getting non-existent photo returns 404."""
    response = client.get("/photos/999")
    
    assert response.status_code == 404


def test_delete_own_photo(client, auth_headers, test_photo_bytes):
    """Test deleting your own photo."""
    # Upload a photo
    files = {"file": ("test.jpg", io.BytesIO(test_photo_bytes), "image/jpeg")}
    upload_response = client.post("/photos/upload", headers=auth_headers, files=files)
    photo_id = upload_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/photos/{photo_id}", headers=auth_headers)
    
    assert response.status_code == 204  # No content
    
    # Verify it's gone
    get_response = client.get(f"/photos/{photo_id}")
    assert get_response.status_code == 404


def test_delete_photo_no_auth(client, auth_headers, test_photo_bytes):
    """Test deleting photo fails without authentication."""
    # Upload a photo
    files = {"file": ("test.jpg", io.BytesIO(test_photo_bytes), "image/jpeg")}
    upload_response = client.post("/photos/upload", headers=auth_headers, files=files)
    photo_id = upload_response.json()["id"]
    
    # Try to delete without auth
    response = client.delete(f"/photos/{photo_id}")
    
    assert response.status_code == 403  # Not authenticated


def test_delete_others_photo(client, auth_headers, auth_headers_user2, test_photo_bytes):
    """Test users cannot delete others' photos."""
    # User 1 uploads a photo
    files = {"file": ("test.jpg", io.BytesIO(test_photo_bytes), "image/jpeg")}
    upload_response = client.post("/photos/upload", headers=auth_headers, files=files)
    photo_id = upload_response.json()["id"]
    
    # User 2 tries to delete it
    response = client.delete(f"/photos/{photo_id}", headers=auth_headers_user2)
    
    assert response.status_code == 403  # Forbidden
    assert "only delete your own" in response.json()["detail"]


def test_get_user_photos(client, auth_headers, test_user, test_photo_bytes):
    """Test getting all photos for a specific user."""
    # Upload a photo
    files = {"file": ("test.jpg", io.BytesIO(test_photo_bytes), "image/jpeg")}
    client.post("/photos/upload", headers=auth_headers, files=files)
    
    # Get user's photos
    response = client.get(f"/users/{test_user.id}/photos")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["user_id"] == test_user.id