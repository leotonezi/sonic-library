import pytest
from fastapi.testclient import TestClient
from app.main import app
from faker import Faker
from email_validator import validate_email, EmailNotValidError
from app.core.database import SessionLocal
from app.models.user import User
from typing import Optional, Dict, Any

fake = Faker()


class MultiUserTestHelper:
    """Helper class for managing multiple users in tests."""
    
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.books: Dict[int, Dict[str, Any]] = {}
        self.reviews: Dict[str, Dict[str, Any]] = {}
        self.user_books: Dict[str, Dict[str, Any]] = {}
    
    def create_user(self, name: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
        """Create a user and return their credentials and cookies."""
        password = fake.password(length=10)
        user_data = {
            "name": name or fake.name(),
            "email": email or fake.unique.email(domain="gmail.com"),
            "password": password
        }

        try:
            validated = validate_email(user_data["email"])
            user_data["email"] = validated.normalized
        except EmailNotValidError as e:
            raise AssertionError(f"Generated invalid email: {user_data['email']}") from e

        # Each user gets their own TestClient
        user_client = TestClient(app)

        # Create user
        response = user_client.post("/users", json=user_data)
        assert response.status_code == 200, f"User creation failed: {response.text}"

        # Activate user
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(email=user_data["email"]).first()
            if user:
                user.is_active = True  # type: ignore
                db.commit()
            else:
                raise Exception("User not found in database after creation!")
        finally:
            db.close()

        # Login to get cookies
        login_data = {
            "username": user_data["email"],
            "password": password
        }
        response = user_client.post("/auth/token", data=login_data)
        assert response.status_code == 200, f"Authentication failed: {response.text}"
        for name, value in response.cookies.items():
            user_client.cookies.set(name, value)

        user_info = {
            "data": user_data,
            "cookies": response.cookies,
            "user_id": None,  # Will be filled when needed
            "client": user_client
        }
        self.users[user_data["email"]] = user_info
        return user_info
    
    def get_user_id(self, user_info: Dict[str, Any]) -> int:
        """Get user ID from the database."""
        if user_info["user_id"] is None:
            db = SessionLocal()
            try:
                user = db.query(User).filter_by(email=user_info["data"]["email"]).first()
                if user is None:
                    raise Exception("User not found in database")
                user_info["user_id"] = int(user.id)  # type: ignore
            finally:
                db.close()
        return user_info["user_id"]
    
    def create_book(self, user_info: Dict[str, Any], book_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a book and return book info."""
        if book_data is None:
            book_data = {
                "title": fake.sentence(nb_words=4),
                "author": fake.name(),
                "description": fake.text(max_nb_chars=200),
                "genres": ["Mystery", "Thriller"]
            }
        
        response = user_info["client"].post("/books", json=book_data)
        assert response.status_code == 201, f"Book creation failed: {response.text}"
        
        book_info = response.json()["data"]
        self.books[book_info["id"]] = book_info
        return book_info
    
    def add_book_to_library(self, user_info: Dict[str, Any], book_id: int, status: str = "TO_READ") -> Dict[str, Any]:
        """Add a book to user's library."""
        user_book_data = {
            "book_id": book_id,
            "status": status
        }
        response = user_info["client"].post("/user-books", json=user_book_data)
        assert response.status_code == 201, f"Adding book to library failed: {response.text}"
        user_book_info = response.json()["data"]
        key = f"{user_info['data']['email']}_{book_id}"
        self.user_books[key] = user_book_info
        return user_book_info
    
    def add_review(self, user_info: Dict[str, Any], book_id: int, review_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add a review to a book."""
        if review_data is None:
            review_data = {
                "book_id": book_id,
                "content": fake.text(max_nb_chars=300),
                "rate": fake.random_int(min=1, max=5)
            }
        
        response = user_info["client"].post("/reviews", json=review_data)
        assert response.status_code == 201, f"Review creation failed: {response.text}"
        
        review_info = response.json()["data"]
        key = f"{user_info['data']['email']}_{book_id}"
        self.reviews[key] = review_info
        return review_info


@pytest.fixture
def multi_user_helper():
    """Fixture to provide MultiUserTestHelper."""
    return MultiUserTestHelper()


def test_multiple_users_can_add_reviews_to_same_book(multi_user_helper):
    """Test that multiple users can add reviews to the same book."""
    print("\n=== Testing multiple users adding reviews to same book ===")
    
    # Create 3 users
    user1 = multi_user_helper.create_user("Alice Johnson", "alice@test.com")
    user2 = multi_user_helper.create_user("Bob Smith", "bob@test.com")
    user3 = multi_user_helper.create_user("Carol Davis", "carol@test.com")
    
    # User1 creates a book
    book = multi_user_helper.create_book(user1, {
        "title": "The Great Mystery",
        "author": "John Doe",
        "description": "A thrilling mystery novel",
        "genres": ["Mystery", "Thriller"]
    })
    
    # All users add the book to their libraries
    print(f"[TEST DEBUG] user1: {user1['data']['email']} id={multi_user_helper.get_user_id(user1)}, book_id={book['id']}")
    multi_user_helper.add_book_to_library(user1, book["id"], "READ")
    print(f"[TEST DEBUG] user2: {user2['data']['email']} id={multi_user_helper.get_user_id(user2)}, book_id={book['id']}")
    multi_user_helper.add_book_to_library(user2, book["id"], "READ")
    print(f"[TEST DEBUG] user3: {user3['data']['email']} id={multi_user_helper.get_user_id(user3)}, book_id={book['id']}")
    multi_user_helper.add_book_to_library(user3, book["id"], "READ")
    
    # Each user adds a review
    review1 = multi_user_helper.add_review(user1, book["id"], {
        "book_id": book["id"],
        "content": "Amazing book! Couldn't put it down.",
        "rate": 5
    })
    
    review2 = multi_user_helper.add_review(user2, book["id"], {
        "book_id": book["id"],
        "content": "Good plot but predictable ending.",
        "rate": 3
    })
    
    review3 = multi_user_helper.add_review(user3, book["id"], {
        "book_id": book["id"],
        "content": "Well-written characters and engaging story.",
        "rate": 4
    })
    
    # Verify all reviews are created
    assert review1["content"] == "Amazing book! Couldn't put it down."
    assert review2["content"] == "Good plot but predictable ending."
    assert review3["content"] == "Well-written characters and engaging story."
    
    # Verify all users can see all reviews
    for user in [user1, user2, user3]:
        response = user["client"].get(f"/reviews/book/{book['id']}")
        assert response.status_code == 200
        reviews = response.json()["data"]
        assert len(reviews) == 3
        
        # Check that all reviews are present
        review_contents = [r["content"] for r in reviews]
        assert "Amazing book! Couldn't put it down." in review_contents
        assert "Good plot but predictable ending." in review_contents
        assert "Well-written characters and engaging story." in review_contents
    
    print("✅ All users successfully added reviews and can see all reviews")


def test_users_can_see_their_own_libraries(multi_user_helper):
    """Test that users can see their own libraries and they are isolated."""
    print("\n=== Testing users can see their own libraries ===")
    
    # Create 2 users
    user1 = multi_user_helper.create_user("David Wilson", "david@test.com")
    user2 = multi_user_helper.create_user("Emma Brown", "emma@test.com")
    
    # Create books
    book1 = multi_user_helper.create_book(user1, {
        "title": "Science Fiction Adventure",
        "author": "Jane Smith",
        "description": "A journey through space",
        "genres": ["Science Fiction"]
    })
    
    book2 = multi_user_helper.create_book(user2, {
        "title": "Romance Novel",
        "author": "Mike Johnson",
        "description": "A love story",
        "genres": ["Romance"]
    })
    
    book3 = multi_user_helper.create_book(user1, {
        "title": "Thriller Book",
        "author": "Sarah Davis",
        "description": "A suspenseful thriller",
        "genres": ["Thriller"]
    })
    
    # User1 adds book1 and book3 to their library
    multi_user_helper.add_book_to_library(user1, book1["id"], "READ")
    multi_user_helper.add_book_to_library(user1, book3["id"], "TO_READ")
    
    # User2 adds book2 to their library
    multi_user_helper.add_book_to_library(user2, book2["id"], "READ")
    
    # Check User1's library
    response = user1["client"].get("/user-books/my-books")
    assert response.status_code == 200
    user1_books = response.json()["data"]
    assert len(user1_books) == 2
    
    user1_book_titles = [book["book"]["title"] for book in user1_books]
    assert "Science Fiction Adventure" in user1_book_titles
    assert "Thriller Book" in user1_book_titles
    assert "Romance Novel" not in user1_book_titles
    
    # Check User2's library
    response = user2["client"].get("/user-books/my-books")
    assert response.status_code == 200
    user2_books = response.json()["data"]
    assert len(user2_books) == 1
    
    user2_book_titles = [book["book"]["title"] for book in user2_books]
    assert "Romance Novel" in user2_book_titles
    assert "Science Fiction Adventure" not in user2_book_titles
    assert "Thriller Book" not in user2_book_titles
    
    print("✅ Users can see their own isolated libraries")


def test_users_can_see_other_users_reviews(multi_user_helper):
    """Test that users can see reviews from other users."""
    print("\n=== Testing users can see other users' reviews ===")
    
    # Create 2 users
    user1 = multi_user_helper.create_user("Frank Miller", "frank@test.com")
    user2 = multi_user_helper.create_user("Grace Lee", "grace@test.com")
    
    # User1 creates a book
    book = multi_user_helper.create_book(user1, {
        "title": "The Shared Book",
        "author": "Author Name",
        "description": "A book that both users will review",
        "genres": ["Fiction"]
    })
    
    # User1 adds a review
    review1 = multi_user_helper.add_review(user1, book["id"], {
        "book_id": book["id"],
        "content": "This is my review as the first user",
        "rate": 4
    })
    
    # User2 adds a review
    review2 = multi_user_helper.add_review(user2, book["id"], {
        "book_id": book["id"],
        "content": "This is my review as the second user",
        "rate": 5
    })
    
    # User1 should see both reviews
    response = user1["client"].get(f"/reviews/book/{book['id']}")
    assert response.status_code == 200
    reviews = response.json()["data"]
    assert len(reviews) == 2
    
    # Check that both reviews are visible
    review_contents = [r["content"] for r in reviews]
    assert "This is my review as the first user" in review_contents
    assert "This is my review as the second user" in review_contents
    
    # User2 should also see both reviews
    response = user2["client"].get(f"/reviews/book/{book['id']}")
    assert response.status_code == 200
    reviews = response.json()["data"]
    assert len(reviews) == 2
    
    review_contents = [r["content"] for r in reviews]
    assert "This is my review as the first user" in review_contents
    assert "This is my review as the second user" in review_contents
    
    print("✅ Users can see reviews from other users")


def test_user_cannot_modify_other_users_reviews(multi_user_helper):
    """Test that users cannot modify reviews from other users."""
    print("\n=== Testing users cannot modify other users' reviews ===")
    
    # Create 2 users
    user1 = multi_user_helper.create_user("Henry Adams", "henry@test.com")
    user2 = multi_user_helper.create_user("Ivy Chen", "ivy@test.com")
    
    # User1 creates a book and adds a review
    book = multi_user_helper.create_book(user1, {
        "title": "The Protected Book",
        "author": "Author Name",
        "description": "A book with protected reviews",
        "genres": ["Fiction"]
    })
    
    review = multi_user_helper.add_review(user1, book["id"], {
        "book_id": book["id"],
        "content": "Original review content",
        "rate": 3
    })
    
    # User2 tries to update User1's review (should fail)
    update_data = {
        "content": "Malicious content",
        "rate": 1
    }
    
    response = user2["client"].put(f"/reviews/{review['id']}", json=update_data)
    # This should fail - users can only modify their own reviews
    assert response.status_code in [403, 404], f"Expected 403 or 404, got {response.status_code}"
    
    # Verify the review content hasn't changed
    response = user1["client"].get(f"/reviews/{review['id']}")
    assert response.status_code == 200
    review_data = response.json()["data"]
    assert review_data["content"] == "Original review content"
    assert review_data["rate"] == 3
    
    print("✅ Users cannot modify other users' reviews")


def test_user_cannot_remove_other_users_books_from_library(multi_user_helper):
    """Test that users cannot remove books from other users' libraries."""
    print("\n=== Testing users cannot remove other users' books ===")
    
    # Create 2 users
    user1 = multi_user_helper.create_user("Jack Wilson", "jack@test.com")
    user2 = multi_user_helper.create_user("Kate Davis", "kate@test.com")
    
    # User1 creates a book and adds it to their library
    book = multi_user_helper.create_book(user1, {
        "title": "The Protected Library Book",
        "author": "Author Name",
        "description": "A book in user1's library",
        "genres": ["Fiction"]
    })
    
    user_book = multi_user_helper.add_book_to_library(user1, book["id"], "READ")
    
    # User2 tries to remove the book from User1's library (should fail)
    response = user2["client"].delete(f"/user-books/{user_book['id']}")
    assert response.status_code in [403, 404], f"Expected 403 or 404, got {response.status_code}"
    
    # Verify the book is still in User1's library
    response = user1["client"].get("/user-books/my-books")
    assert response.status_code == 200
    user1_books = response.json()["data"]
    user1_book_titles = [book["book"]["title"] for book in user1_books]
    assert "The Protected Library Book" in user1_book_titles
    
    print("✅ Users cannot remove books from other users' libraries")


def test_comprehensive_multi_user_scenario(multi_user_helper):
    """Test a comprehensive scenario with multiple users interacting with the platform."""
    print("\n=== Testing comprehensive multi-user scenario ===")
    
    # Create 3 users
    user1 = multi_user_helper.create_user("Liam O'Connor", "liam@test.com")
    user2 = multi_user_helper.create_user("Mia Rodriguez", "mia@test.com")
    user3 = multi_user_helper.create_user("Noah Thompson", "noah@test.com")
    
    # User1 creates multiple books
    book1 = multi_user_helper.create_book(user1, {
        "title": "The First Book",
        "author": "Author One",
        "description": "The first book in the series",
        "genres": ["Fantasy"]
    })
    
    book2 = multi_user_helper.create_book(user1, {
        "title": "The Second Book",
        "author": "Author Two",
        "description": "The second book in the series",
        "genres": ["Science Fiction"]
    })
    
    # All users add books to their libraries with different statuses
    multi_user_helper.add_book_to_library(user1, book1["id"], "READ")
    multi_user_helper.add_book_to_library(user1, book2["id"], "TO_READ")
    
    multi_user_helper.add_book_to_library(user2, book1["id"], "READ")
    multi_user_helper.add_book_to_library(user2, book2["id"], "READING")
    
    multi_user_helper.add_book_to_library(user3, book1["id"], "TO_READ")
    
    # Users add reviews
    multi_user_helper.add_review(user1, book1["id"], {
        "book_id": book1["id"],
        "content": "Great fantasy book!",
        "rate": 5
    })
    
    multi_user_helper.add_review(user2, book1["id"], {
        "book_id": book1["id"],
        "content": "Enjoyed the world-building",
        "rate": 4
    })
    
    multi_user_helper.add_review(user2, book2["id"], {
        "book_id": book2["id"],
        "content": "Interesting sci-fi concepts",
        "rate": 4
    })
    
    # Test that each user can see their own library correctly
    for user, expected_books in [
        (user1, [("The First Book", "READ"), ("The Second Book", "TO_READ")]),
        (user2, [("The First Book", "READ"), ("The Second Book", "READING")]),
        (user3, [("The First Book", "TO_READ")])
    ]:
        response = user["client"].get("/user-books/my-books")
        assert response.status_code == 200
        user_books = response.json()["data"]
        
        assert len(user_books) == len(expected_books)
        
        for expected_title, expected_status in expected_books:
            found = False
            for user_book in user_books:
                if (user_book["book"]["title"] == expected_title and 
                    user_book["status"] == expected_status):
                    found = True
                    break
            assert found, f"Expected book {expected_title} with status {expected_status} not found"
    
    # Test that all users can see all reviews for book1
    for user in [user1, user2, user3]:
        response = user["client"].get(f"/reviews/book/{book1['id']}")
        assert response.status_code == 200
        reviews = response.json()["data"]
        assert len(reviews) == 2
        
        review_contents = [r["content"] for r in reviews]
        assert "Great fantasy book!" in review_contents
        assert "Enjoyed the world-building" in review_contents
    
    # Test that users can see reviews for book2
    for user in [user1, user2, user3]:
        response = user["client"].get(f"/reviews/book/{book2['id']}")
        assert response.status_code == 200
        reviews = response.json()["data"]
        assert len(reviews) == 1
        
        review_contents = [r["content"] for r in reviews]
        assert "Interesting sci-fi concepts" in review_contents
    
    print("✅ Comprehensive multi-user scenario passed")


def test_user_isolation_and_data_integrity(multi_user_helper):
    """Test that user data is properly isolated and data integrity is maintained."""
    print("\n=== Testing user isolation and data integrity ===")
    
    # Create 2 users
    user1 = multi_user_helper.create_user("Oliver Garcia", "oliver@test.com")
    user2 = multi_user_helper.create_user("Penelope Martinez", "penelope@test.com")
    
    # User1 creates a book and adds it to their library
    book = multi_user_helper.create_book(user1, {
        "title": "The Isolated Book",
        "author": "Author Name",
        "description": "A book for testing isolation",
        "genres": ["Mystery"]
    })
    
    user_book1 = multi_user_helper.add_book_to_library(user1, book["id"], "READ")
    
    # User2 adds the same book to their library
    user_book2 = multi_user_helper.add_book_to_library(user2, book["id"], "TO_READ")
    
    # Verify that each user has their own user_book entry
    assert user_book1["id"] != user_book2["id"]
    assert user_book1["status"] == "READ"
    assert user_book2["status"] == "TO_READ"
    
    # User1 adds a review
    review = multi_user_helper.add_review(user1, book["id"], {
        "book_id": book["id"],
        "content": "My personal review",
        "rate": 4
    })
    
    # Verify that the review is associated with User1
    response = user1["client"].get(f"/reviews/{review['id']}")
    assert response.status_code == 200
    review_data = response.json()["data"]
    assert review_data["user_id"] == multi_user_helper.get_user_id(user1)
    
    # Verify that User2 can see the review but it's not theirs
    response = user2["client"].get(f"/reviews/{review['id']}")
    assert response.status_code == 200
    review_data = response.json()["data"]
    assert review_data["user_id"] == multi_user_helper.get_user_id(user1)
    assert review_data["user_id"] != multi_user_helper.get_user_id(user2)
    
    print("✅ User isolation and data integrity verified")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])