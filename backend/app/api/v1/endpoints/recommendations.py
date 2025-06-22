from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.review import Review
from app.models.book import Book
from app.services.recommendation_service import generate_book_recommendations
from app.schemas.base_schema import ApiResponse
from app.core.security import get_current_user
from app.core.logging_decorator import log_exceptions

router = APIRouter()

@router.get("/{user_id}")
@log_exceptions("GET /recommendations/{user_id}")
def get_recommendations(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
    user_reviews = db.query(Review).filter(Review.user_id == current_user.id).all()
    if not user_reviews:
        raise HTTPException(status_code=404, detail="User has no reviews")

    books = db.query(Book).all()

    from app.schemas.review import ReviewResponse
    from app.schemas.book import BookResponse
    user_reviews_pydantic = [ReviewResponse.model_validate(r) for r in user_reviews]
    books_pydantic = [BookResponse.from_orm_with_genres(b) for b in books]

    recommendations = generate_book_recommendations(user_reviews_pydantic, books_pydantic)
    return ApiResponse(data=recommendations)
