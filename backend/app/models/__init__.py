# app/models/__init__.py
from app.models.user import User
from app.models.book import Book
from app.models.review import Review
from app.models.book import GenreEnum
from app.models.user_book import UserBook, StatusEnum

# This ensures all models are imported and available
__all__ = ["User", "Book", "GenreEnum", "Review", "UserBook", "StatusEnum"]