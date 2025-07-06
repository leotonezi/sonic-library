import pytest
from fastapi.testclient import TestClient
from app.models.user import User
from app.core.security import hash_password
from sqlalchemy.orm import Session
import io
from PIL import Image

def create_test_image():
    """Create a simple test image."""
    img = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io

def test_upload_profile_picture(client: TestClient, db_session: Session):
    """Test uploading a profile picture."""
    # Create a test user
    user = User(
        name="Test User",
        email="test@example.com",
        password=hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Login to get cookies
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    cookies = response.cookies
    
    # Create test image
    img_io = create_test_image()
    
    # Upload profile picture
    response = client.post(
        "/users/me/profile-picture",
        files={"file": ("test.jpg", img_io, "image/jpeg")},
        cookies=cookies
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["profile_picture"] is not None
    
    # Verify user was updated in database
    db_session.refresh(user)
    assert user.profile_picture is not None

def test_update_profile_name(client: TestClient, db_session: Session):
    """Test updating profile name."""
    # Create a test user
    user = User(
        name="Test User",
        email="test@example.com",
        password=hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Login to get cookies
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    cookies = response.cookies
    
    new_name = "Updated Name"
    
    response = client.put(
        "/users/me/profile",
        json={"name": new_name},
        cookies=cookies
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == new_name
    
    # Verify user was updated in database
    db_session.refresh(user)
    assert user.name == new_name

def test_get_user_with_profile_picture(client: TestClient, db_session: Session):
    """Test getting user data includes profile picture."""
    # Create a test user
    user = User(
        name="Test User",
        email="test@example.com",
        password=hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Login to get cookies
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    cookies = response.cookies
    
    # First upload a profile picture
    img_io = create_test_image()
    response = client.post(
        "/users/me/profile-picture",
        files={"file": ("test.jpg", img_io, "image/jpeg")},
        cookies=cookies
    )
    assert response.status_code == 200
    
    # Get user data
    response = client.get("/users/me", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["profile_picture"] is not None

def test_reviews_include_user_profile_picture(client: TestClient, db_session: Session):
    """Test that reviews include user profile picture information."""
    # Create a test user
    user = User(
        name="Test User",
        email="test@example.com",
        password=hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create a test book
    from app.models.book import Book
    book = Book(
        title="Test Book",
        author="Test Author",
        description="A test book.",
        page_count=123,
        language="en"
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)

    # Login to get cookies
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    cookies = response.cookies

    # Upload profile picture
    img_io = create_test_image()
    response = client.post(
        "/users/me/profile-picture",
        files={"file": ("test.jpg", img_io, "image/jpeg")},
        cookies=cookies
    )
    assert response.status_code == 200

    # Create a review for the created book
    review_data = {
        "book_id": book.id,
        "content": "Great book!",
        "rate": 5
    }

    response = client.post("/reviews/", json=review_data, cookies=cookies)
    assert response.status_code == 201

    # Get reviews for the book
    response = client.get(f"/reviews/book/{book.id}", cookies=cookies)
    assert response.status_code == 200
    data = response.json()

    if data["data"]:  # If there are reviews
        review = data["data"][0]
        assert "user_profile_picture" in review
        assert review["user_name"] == user.name 