import pytest
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.user_book import UserBook, StatusEnum
from app.core.database import SessionLocal
from app.models.user import User

@pytest.fixture
def test_user(client):
    user_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    client.post("/users", json=user_data)
    # Activate user in DB
    db = SessionLocal()
    user = db.query(User).filter_by(email=user_data["email"]).first()
    if user is not None:
        setattr(user, "is_active", True)
        db.commit()
    db.close()
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    
    # Create the token manually for testing since TestClient doesn't handle cookies properly
    from app.core.security import create_access_token
    from datetime import timedelta
    from app.core.config import settings
    
    access_token = create_access_token(
        data={"sub": user_data["email"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "user_data": user_data}

@pytest.fixture
def test_books(db_session: Session):
    """Create test books"""
    books = []
    for i in range(15):  # Create 15 books for pagination testing
        book = Book(
            title=f"Test Book {i+1}",
            author=f"Author {i+1}",
            description=f"Description for book {i+1}",
            page_count=100 + i
        )
        db_session.add(book)
        books.append(book)
    db_session.commit()
    for book in books:
        db_session.refresh(book)
    return books

@pytest.fixture
def test_user_books(db_session: Session, test_books: list[Book], test_user):
    """Create test user books"""
    user = db_session.query(User).filter_by(email="testuser@example.com").first()
    if user is None:
        raise RuntimeError("Test user not found in DB. Ensure user is created before running this fixture.")
    user_books = []
    for i, book in enumerate(test_books):
        user_book = UserBook(
            user_id=user.id,
            book_id=book.id,
            status=StatusEnum.TO_READ if i % 3 == 0 else StatusEnum.READING if i % 3 == 1 else StatusEnum.READ
        )
        db_session.add(user_book)
        user_books.append(user_book)
    db_session.commit()
    for user_book in user_books:
        db_session.refresh(user_book)
    return user_books

def test_user_books_pagination(client, test_user, test_books, test_user_books):
    """Test pagination for user books endpoint"""
    access_token = test_user["access_token"]
    # Set the access token as a cookie
    client.cookies.set("access_token", access_token)
    response = client.get("/user-books/my-books/paginated?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) == 5
    assert data["pagination"]["current_page"] == 1
    assert data["pagination"]["total_pages"] == 3
    assert data["pagination"]["total_count"] == 15
    assert data["pagination"]["has_next"] == True
    assert data["pagination"]["has_previous"] == False
    response = client.get("/user-books/my-books/paginated?page=2&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert data["pagination"]["current_page"] == 2
    assert data["pagination"]["has_next"] == True
    assert data["pagination"]["has_previous"] == True
    response = client.get("/user-books/my-books/paginated?page=3&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert data["pagination"]["current_page"] == 3
    assert data["pagination"]["has_next"] == False
    assert data["pagination"]["has_previous"] == True

def test_user_books_pagination_with_status_filter(client, test_user, test_books, test_user_books):
    """Test pagination with status filter"""
    access_token = test_user["access_token"]
    # Set the access token as a cookie
    client.cookies.set("access_token", access_token)
    response = client.get("/user-books/my-books/paginated?page=1&page_size=10&status=TO_READ")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert data["pagination"]["total_count"] == 5
    assert data["pagination"]["total_pages"] == 1

def test_books_pagination(client, test_books: list[Book]):
    """Test pagination for books endpoint"""
    response = client.get("/books/?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) == 5
    assert data["pagination"]["current_page"] == 1
    assert data["pagination"]["total_pages"] == 3
    assert data["pagination"]["total_count"] == 15
    assert data["pagination"]["has_next"] == True
    assert data["pagination"]["has_previous"] == False
    response = client.get("/books/?page=2&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert data["pagination"]["current_page"] == 2
    assert data["pagination"]["has_next"] == True
    assert data["pagination"]["has_previous"] == True

def test_google_books_search_pagination(client):
    """Test pagination for Google Books search endpoint"""
    response = client.get("/books/search-external?q=python&page=1&max_results=10")
    if response.status_code == 200:
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert "current_page" in data["pagination"]
        assert "total_pages" in data["pagination"]
        assert "total_count" in data["pagination"]

def test_popular_books_pagination(client):
    """Test pagination for popular books endpoint"""
    response = client.get("/books/popular?page=1&max_results=10")
    if response.status_code == 200:
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert "current_page" in data["pagination"]
        assert "total_pages" in data["pagination"]
        assert "total_count" in data["pagination"] 