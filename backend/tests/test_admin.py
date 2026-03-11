"""Tests for admin auth and read endpoints (US-007) and write endpoints (US-008)."""

import pytest
from app.models.user import User
from app.models.book import Book
from app.models.review import Review
from app.models.user_book import UserBook, StatusEnum
from app.core.security import hash_password


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ADMIN_EMAIL = "admin@sonic.com"
REGULAR_EMAIL = "regular@example.com"
PASSWORD = "testpass123"


def _create_admin_user(db_session):
    """Create an active admin user in the DB."""
    user = User(
        name="Admin User",
        email=ADMIN_EMAIL,
        password=hash_password(PASSWORD),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_regular_user(db_session, email=REGULAR_EMAIL, name="Regular User"):
    """Create an active non-admin user in the DB."""
    user = User(
        name=name,
        email=email,
        password=hash_password(PASSWORD),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _login(client, email, password=PASSWORD):
    """Login and return cookies."""
    resp = client.post("/auth/token", data={"username": email, "password": password})
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    return resp.cookies


def _create_book(db_session, title="Test Book", external_id=None):
    """Create a book record."""
    book = Book(
        title=title,
        author="Test Author",
        external_id=external_id,
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    return book


def _create_review(db_session, user_id, book_id=None, external_book_id=None, content="Good book", rate=4):
    """Create a review record."""
    review = Review(
        user_id=user_id,
        book_id=book_id,
        external_book_id=external_book_id,
        content=content,
        rate=rate,
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)
    return review


def _create_user_book(db_session, user_id, book_id=None, external_book_id=None, status=StatusEnum.TO_READ):
    """Create a user-book record."""
    ub = UserBook(
        user_id=user_id,
        book_id=book_id,
        external_book_id=external_book_id,
        status=status,
    )
    db_session.add(ub)
    db_session.commit()
    db_session.refresh(ub)
    return ub


# ===========================================================================
# US-007: Auth tests
# ===========================================================================


class TestAdminAuth:
    """Test that admin endpoints enforce authentication and authorization."""

    ADMIN_ENDPOINTS = [
        ("GET", "/api/v1/admin/users"),
        ("GET", "/api/v1/admin/users/1"),
        ("GET", "/api/v1/admin/reviews"),
        ("GET", "/api/v1/admin/user-books"),
        ("GET", "/api/v1/admin/stats"),
    ]

    @pytest.mark.parametrize("method,url", ADMIN_ENDPOINTS)
    def test_unauthenticated_returns_401(self, client, method, url):
        """Non-authenticated requests should return 401."""
        resp = getattr(client, method.lower())(url)
        assert resp.status_code == 401

    @pytest.mark.parametrize("method,url", ADMIN_ENDPOINTS)
    def test_non_admin_returns_403(self, client, db_session, method, url):
        """Authenticated non-admin users should return 403."""
        _create_regular_user(db_session)
        cookies = _login(client, REGULAR_EMAIL)
        resp = getattr(client, method.lower())(url, cookies=cookies)
        assert resp.status_code == 403


# ===========================================================================
# US-007: Read endpoint tests
# ===========================================================================


class TestListUsers:
    """GET /api/v1/admin/users"""

    def test_returns_paginated_users(self, client, db_session):
        admin = _create_admin_user(db_session)
        user2 = _create_regular_user(db_session)
        cookies = _login(client, ADMIN_EMAIL)

        resp = client.get("/api/v1/admin/users", cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert data["total"] == 2

    def test_returns_books_and_reviews_count(self, client, db_session):
        admin = _create_admin_user(db_session)
        user = _create_regular_user(db_session)
        book = _create_book(db_session, title="Counted Book", external_id="ext-cnt-1")
        _create_review(db_session, user_id=user.id, book_id=book.id, rate=5)
        _create_review(db_session, user_id=user.id, external_book_id="ext-other", rate=3)
        _create_user_book(db_session, user_id=user.id, book_id=book.id)
        cookies = _login(client, ADMIN_EMAIL)

        resp = client.get("/api/v1/admin/users", cookies=cookies)
        items = resp.json()["items"]
        # Find the regular user item
        user_item = next(i for i in items if i["email"] == REGULAR_EMAIL)
        assert user_item["books_count"] == 1
        assert user_item["reviews_count"] == 2

    def test_search_by_name(self, client, db_session):
        admin = _create_admin_user(db_session)
        _create_regular_user(db_session, email="alice@example.com", name="Alice Wonderland")
        _create_regular_user(db_session, email="bob@example.com", name="Bob Builder")
        cookies = _login(client, ADMIN_EMAIL)

        resp = client.get("/api/v1/admin/users", params={"search": "alice"}, cookies=cookies)
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["name"] == "Alice Wonderland"

    def test_search_by_email(self, client, db_session):
        admin = _create_admin_user(db_session)
        _create_regular_user(db_session, email="findme@special.com", name="Find Me")
        cookies = _login(client, ADMIN_EMAIL)

        resp = client.get("/api/v1/admin/users", params={"search": "findme@special"}, cookies=cookies)
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["email"] == "findme@special.com"


class TestGetUserDetail:
    """GET /api/v1/admin/users/{id}"""

    def test_returns_user_with_books_and_reviews(self, client, db_session):
        admin = _create_admin_user(db_session)
        user = _create_regular_user(db_session)
        book = _create_book(db_session, title="Detail Book", external_id="ext-detail-1")
        _create_review(db_session, user_id=user.id, book_id=book.id, content="Nice", rate=4)
        _create_user_book(db_session, user_id=user.id, book_id=book.id, status=StatusEnum.READING)
        cookies = _login(client, ADMIN_EMAIL)

        resp = client.get(f"/api/v1/admin/users/{user.id}", cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == user.id
        assert data["name"] == "Regular User"
        assert len(data["books"]) == 1
        assert len(data["reviews"]) == 1
        assert data["books_count"] == 1
        assert data["reviews_count"] == 1

    def test_404_for_nonexistent_user(self, client, db_session):
        _create_admin_user(db_session)
        cookies = _login(client, ADMIN_EMAIL)
        resp = client.get("/api/v1/admin/users/99999", cookies=cookies)
        assert resp.status_code == 404


class TestListReviews:
    """GET /api/v1/admin/reviews"""

    def test_returns_paginated_reviews(self, client, db_session):
        admin = _create_admin_user(db_session)
        user = _create_regular_user(db_session)
        book = _create_book(db_session, title="Review Book", external_id="ext-rev-1")
        _create_review(db_session, user_id=user.id, book_id=book.id, content="Great", rate=5)
        _create_review(db_session, user_id=user.id, book_id=book.id, content="OK", rate=3)
        cookies = _login(client, ADMIN_EMAIL)

        resp = client.get("/api/v1/admin/reviews", cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        item = data["items"][0]
        assert "user_name" in item
        assert "book_title" in item
        assert item["user_name"] == "Regular User"
        assert item["book_title"] == "Review Book"


class TestListUserBooks:
    """GET /api/v1/admin/user-books"""

    def test_returns_paginated_user_books(self, client, db_session):
        admin = _create_admin_user(db_session)
        user = _create_regular_user(db_session)
        book = _create_book(db_session, title="UB Book", external_id="ext-ub-1")
        _create_user_book(db_session, user_id=user.id, book_id=book.id, status=StatusEnum.READ)
        cookies = _login(client, ADMIN_EMAIL)

        resp = client.get("/api/v1/admin/user-books", cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        item = data["items"][0]
        assert item["user_name"] == "Regular User"
        assert item["book_title"] == "UB Book"
        assert item["status"] == "READ"


class TestGetStats:
    """GET /api/v1/admin/stats"""

    def test_returns_correct_aggregate_counts(self, client, db_session):
        admin = _create_admin_user(db_session)
        user = _create_regular_user(db_session)
        book = _create_book(db_session, title="Stats Book", external_id="ext-stats-1")
        _create_review(db_session, user_id=user.id, book_id=book.id, rate=4)
        _create_review(db_session, user_id=admin.id, book_id=book.id, rate=2)
        _create_user_book(db_session, user_id=user.id, book_id=book.id)
        cookies = _login(client, ADMIN_EMAIL)

        resp = client.get("/api/v1/admin/stats", cookies=cookies)
        assert resp.status_code == 200
        stats = resp.json()["data"]
        assert stats["total_users"] == 2
        assert stats["total_active_users"] == 2
        assert stats["total_books"] == 1
        assert stats["total_reviews"] == 2
        assert stats["total_user_books"] == 1
        assert stats["avg_rating"] == 3.0
