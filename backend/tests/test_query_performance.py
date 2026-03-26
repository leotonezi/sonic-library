"""
Query performance regression tests.

These tests verify that key endpoints and services don't regress on query count,
preventing N+1 issues from silently returning. Each test seeds data, attaches a
SQLAlchemy event listener to count queries, and asserts that the count stays
below a fixed threshold regardless of row count.
"""

import pytest
from contextlib import contextmanager
from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker
from app.models.book import Book, Genre, book_genres
from app.models.user import User
from app.models.user_book import UserBook, StatusEnum
from app.models.review import Review
from app.core.database import SessionLocal
from tests.conftest import test_engine


# ---------------------------------------------------------------------------
# Query counter helper
# ---------------------------------------------------------------------------

class QueryCounter:
    """Counts SQL statements executed on a given engine."""

    def __init__(self):
        self.count = 0
        self.queries: list[str] = []

    def callback(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1
        self.queries.append(statement)


@contextmanager
def count_queries(engine=test_engine):
    """Context manager that counts queries executed within its block."""
    counter = QueryCounter()
    event.listen(engine, "before_cursor_execute", counter.callback)
    try:
        yield counter
    finally:
        event.remove(engine, "before_cursor_execute", counter.callback)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def seed_user(client):
    """Create and activate a test user, return access token and user data."""
    user_data = {
        "name": "Perf Test User",
        "email": "perfuser@example.com",
        "password": "testpassword",
    }
    client.post("/users", json=user_data)

    # Activate user directly in DB
    db = SessionLocal()
    user = db.query(User).filter_by(email=user_data["email"]).first()
    if user is not None:
        setattr(user, "is_active", True)
        db.commit()
    db.close()

    # Login
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200

    from app.core.security import create_access_token
    from datetime import timedelta
    from app.core.config import settings

    access_token = create_access_token(
        data={"sub": user_data["email"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "user_data": user_data}


@pytest.fixture
def seed_books_with_genres(db_session: Session):
    """Create 12 books, each with 2 genres (from a pool of 5)."""
    genre_names = ["Fiction", "Science", "History", "Fantasy", "Tech"]
    genres = []
    for name in genre_names:
        g = Genre(name=name)
        db_session.add(g)
        genres.append(g)
    db_session.flush()

    books = []
    for i in range(12):
        book = Book(
            title=f"Perf Book {i + 1}",
            author=f"Author {i + 1}",
            description=f"Description for perf book {i + 1}",
            page_count=100 + i,
        )
        db_session.add(book)
        db_session.flush()
        # Assign 2 genres per book (rotating through pool)
        book.genres.append(genres[i % len(genres)])
        book.genres.append(genres[(i + 1) % len(genres)])
        books.append(book)

    db_session.commit()
    for book in books:
        db_session.refresh(book)
    return books


@pytest.fixture
def seed_user_books(db_session: Session, seed_books_with_genres, seed_user):
    """Create UserBook entries for all seeded books."""
    user = db_session.query(User).filter_by(email="perfuser@example.com").first()
    assert user is not None

    statuses = [StatusEnum.TO_READ, StatusEnum.READING, StatusEnum.READ]
    user_books = []
    for i, book in enumerate(seed_books_with_genres):
        ub = UserBook(
            user_id=user.id,
            book_id=book.id,
            status=statuses[i % len(statuses)],
        )
        db_session.add(ub)
        user_books.append(ub)
    db_session.commit()
    for ub in user_books:
        db_session.refresh(ub)
    return user_books


@pytest.fixture
def seed_reviews(db_session: Session, seed_books_with_genres, seed_user):
    """Create reviews for a subset of seeded books."""
    user = db_session.query(User).filter_by(email="perfuser@example.com").first()
    assert user is not None

    reviews = []
    # Create reviews for the first 10 books
    for i, book in enumerate(seed_books_with_genres[:10]):
        review = Review(
            book_id=book.id,
            user_id=user.id,
            content=f"Review content for book {i + 1}",
            rate=(i % 5) + 1,
        )
        db_session.add(review)
        reviews.append(review)
    db_session.commit()
    for r in reviews:
        db_session.refresh(r)
    return reviews


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBooksQueryPerformance:
    """Verify /books endpoint doesn't N+1 on genres."""

    def test_list_books_bounded_queries(self, client, seed_books_with_genres):
        """Listing 12 books with genres should use a bounded number of queries,
        not 1 + N (one per book for genres)."""
        with count_queries() as counter:
            response = client.get("/books/?page=1&page_size=20")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 12

        # With eager loading: expect a small, bounded query count.
        # Without eager loading we'd see 12+ queries (1 per book for genres).
        # Allow up to 10 for the main query + count + eager load + session overhead.
        assert counter.count <= 10, (
            f"Expected bounded queries for /books, got {counter.count}. "
            f"Possible N+1 regression on Book.genres.\n"
            f"Queries: {counter.queries}"
        )


class TestUserBooksQueryPerformance:
    """Verify /user-books/my-books doesn't N+1 on book details."""

    def test_my_books_bounded_queries(self, client, seed_user, seed_user_books):
        """Fetching user's 12 books should use bounded queries,
        not 1 + N (one per user_book for book details)."""
        client.cookies.set("access_token", seed_user["access_token"])

        with count_queries() as counter:
            response = client.get("/user-books/my-books")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 10

        # With eager loading: bounded queries.
        # Without: 12+ queries (one per user_book for book).
        assert counter.count <= 10, (
            f"Expected bounded queries for /user-books/my-books, got {counter.count}. "
            f"Possible N+1 regression on UserBook.book.\n"
            f"Queries: {counter.queries}"
        )


class TestReviewsQueryPerformance:
    """Verify /reviews/book/{id} doesn't N+1 on book/user data."""

    def test_reviews_for_book_bounded_queries(
        self, client, seed_books_with_genres, seed_user, seed_reviews
    ):
        """Fetching reviews for a book should use bounded queries."""
        client.cookies.set("access_token", seed_user["access_token"])
        book = seed_books_with_genres[0]

        with count_queries() as counter:
            response = client.get(f"/reviews/book/{book.id}")

        assert response.status_code == 200

        # With eager loading: bounded queries.
        assert counter.count <= 10, (
            f"Expected bounded queries for /reviews/book/{{id}}, got {counter.count}. "
            f"Possible N+1 regression on Review.book.\n"
            f"Queries: {counter.queries}"
        )


class TestRecommendationGraphQueryPerformance:
    """Verify recommendation graph generation uses bounded query count."""

    def test_graph_generation_bounded_queries(
        self, db_session: Session, seed_books_with_genres, seed_user, seed_reviews, seed_user_books
    ):
        """Building the recommendation graph should use bounded queries
        regardless of how many books/reviews exist."""
        from app.services.recommendation_service import create_book_recommendation_graph

        user = db_session.query(User).filter_by(email="perfuser@example.com").first()
        assert user is not None

        with count_queries() as counter:
            result = create_book_recommendation_graph(db_session, user.id)

        assert len(result["nodes"]) > 0

        # The graph function should:
        #  - query reviews (1)
        #  - query user_books (1)
        #  - query books with genres eager loaded (1-2)
        #  - possibly a few more for AI recommendations (may fail gracefully)
        # Without eager loading: would be 1 + N (genres per book).
        # Allow generous threshold to account for AI recommendation queries.
        assert counter.count <= 15, (
            f"Expected bounded queries for recommendation graph, got {counter.count}. "
            f"Possible N+1 regression on Book.genres.\n"
            f"Queries: {counter.queries}"
        )
