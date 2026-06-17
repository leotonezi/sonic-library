import pytest
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.review import Review
from app.models.user_book import UserBook, StatusEnum
from app.core.database import SessionLocal
from app.models.user import User
from app.core.config import settings

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


# ---------------------------------------------------------------------------
# New: /user-books/my-books (now paginated)
# ---------------------------------------------------------------------------

def test_my_books_is_now_paginated(client, test_user, test_books, test_user_books):
    """GET /user-books/my-books must return PaginationResponse."""
    access_token = test_user["access_token"]
    client.cookies.set("access_token", access_token)
    response = client.get("/user-books/my-books?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) == 5
    assert data["pagination"]["total_count"] == 15
    assert data["pagination"]["has_next"] is True


def test_my_books_page_size_clamped(client, test_user, test_books, test_user_books):
    """page_size > MAX_PAGE_SIZE is clamped silently."""
    access_token = test_user["access_token"]
    client.cookies.set("access_token", access_token)
    huge = settings.MAX_PAGE_SIZE + 500
    response = client.get(f"/user-books/my-books?page=1&page_size={huge}")
    assert response.status_code == 200
    data = response.json()
    # Clamped: at most MAX_PAGE_SIZE items returned, all 15 fit within 100
    assert len(data["data"]) == 15
    assert data["pagination"]["page_size"] == settings.MAX_PAGE_SIZE


# ---------------------------------------------------------------------------
# New: /user-books/status/{status} (now paginated)
# ---------------------------------------------------------------------------

def test_status_endpoint_is_paginated(client, test_user, test_books, test_user_books):
    """GET /user-books/status/{status} must return PaginationResponse."""
    access_token = test_user["access_token"]
    client.cookies.set("access_token", access_token)
    response = client.get("/user-books/status/TO_READ?page=1&page_size=3")
    assert response.status_code == 200
    data = response.json()
    assert "pagination" in data
    assert data["pagination"]["total_count"] == 5  # 15 books, every 3rd is TO_READ (indices 0,3,6,9,12)
    assert data["pagination"]["total_pages"] == 2
    assert len(data["data"]) == 3


# ---------------------------------------------------------------------------
# New: review endpoints
# ---------------------------------------------------------------------------

@pytest.fixture
def test_reviews(db_session: Session, test_books: list, test_user) -> list:
    """Create reviews for the first test book (12 reviews for pagination testing)."""
    user = db_session.query(User).filter_by(email="testuser@example.com").first()
    if user is None:
        raise RuntimeError("Test user not found.")

    book = test_books[0]
    reviews = []
    for i in range(12):
        review = Review(
            book_id=book.id,
            user_id=user.id,
            content=f"Review content {i+1}",
            rate=(i % 5) + 1,
        )
        db_session.add(review)
        reviews.append(review)
    db_session.commit()
    for r in reviews:
        db_session.refresh(r)
    return reviews


def test_reviews_list_is_paginated(client, test_user, test_books, test_reviews):
    """GET /reviews returns PaginationResponse with correct structure."""
    access_token = test_user["access_token"]
    client.cookies.set("access_token", access_token)
    response = client.get("/reviews?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) == 5
    assert data["pagination"]["current_page"] == 1
    assert data["pagination"]["total_count"] == 12
    assert data["pagination"]["total_pages"] == 3
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["has_previous"] is False


def test_reviews_list_page_size_clamped(client, test_user, test_books, test_reviews):
    """page_size > MAX_PAGE_SIZE is silently clamped on GET /reviews."""
    access_token = test_user["access_token"]
    client.cookies.set("access_token", access_token)
    huge = settings.MAX_PAGE_SIZE + 999
    response = client.get(f"/reviews?page=1&page_size={huge}")
    assert response.status_code == 200
    data = response.json()
    # All 12 reviews fit within the clamped MAX_PAGE_SIZE
    assert len(data["data"]) == 12
    assert data["pagination"]["page_size"] == settings.MAX_PAGE_SIZE


def test_reviews_by_book_is_paginated(client, test_user, test_books, test_reviews):
    """GET /reviews/book/{book_id} returns PaginationResponse."""
    access_token = test_user["access_token"]
    client.cookies.set("access_token", access_token)
    book_id = test_books[0].id
    response = client.get(f"/reviews/book/{book_id}?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) == 5
    assert data["pagination"]["total_count"] == 12
    assert data["pagination"]["total_pages"] == 3
    assert data["pagination"]["has_next"] is True


def test_reviews_by_book_second_page(client, test_user, test_books, test_reviews):
    """Page 2 of /reviews/book/{book_id} has correct state."""
    access_token = test_user["access_token"]
    client.cookies.set("access_token", access_token)
    book_id = test_books[0].id
    response = client.get(f"/reviews/book/{book_id}?page=2&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert data["pagination"]["current_page"] == 2
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["has_previous"] is True


def test_reviews_by_book_page_size_clamped(client, test_user, test_books, test_reviews):
    """page_size > MAX_PAGE_SIZE is clamped on GET /reviews/book/{book_id}."""
    access_token = test_user["access_token"]
    client.cookies.set("access_token", access_token)
    book_id = test_books[0].id
    huge = settings.MAX_PAGE_SIZE + 999
    response = client.get(f"/reviews/book/{book_id}?page=1&page_size={huge}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 12
    assert data["pagination"]["page_size"] == settings.MAX_PAGE_SIZE


# ---------------------------------------------------------------------------
# New: /reviews/book/external/{id} pagination
# ---------------------------------------------------------------------------

@pytest.fixture
def test_external_reviews(db_session: Session, test_user) -> list:
    """Create reviews for an external book id (8 reviews for pagination testing)."""
    user = db_session.query(User).filter_by(email="testuser@example.com").first()
    if user is None:
        raise RuntimeError("Test user not found.")

    external_id = "external-test-book-001"
    reviews = []
    for i in range(8):
        review = Review(
            external_book_id=external_id,
            user_id=user.id,
            content=f"External review content {i + 1}",
            rate=(i % 5) + 1,
        )
        db_session.add(review)
        reviews.append(review)
    db_session.commit()
    for r in reviews:
        db_session.refresh(r)
    return reviews


def test_reviews_by_external_book_is_paginated(client, test_user, test_external_reviews):
    """GET /reviews/book/external/{id} returns PaginationResponse with correct structure."""
    access_token = test_user["access_token"]
    client.cookies.set("access_token", access_token)
    response = client.get("/reviews/book/external/external-test-book-001?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) == 5
    assert data["pagination"]["current_page"] == 1
    assert data["pagination"]["total_count"] == 8
    assert data["pagination"]["total_pages"] == 2
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["has_previous"] is False


def test_reviews_by_external_book_second_page(client, test_user, test_external_reviews):
    """Page 2 of /reviews/book/external/{id} returns the remaining items."""
    access_token = test_user["access_token"]
    client.cookies.set("access_token", access_token)
    response = client.get("/reviews/book/external/external-test-book-001?page=2&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3
    assert data["pagination"]["current_page"] == 2
    assert data["pagination"]["has_next"] is False
    assert data["pagination"]["has_previous"] is True