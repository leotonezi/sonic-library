from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.review_service import ReviewService
from app.schemas.base_schema import ApiResponse
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from app.core.logging_decorator import log_exceptions

router = APIRouter()

def get_review_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔥 User must be authenticated
) -> ReviewService:
    """Inject ReviewService, requiring authenticated user."""
    return ReviewService(db)

@router.post("/", response_model=ApiResponse[ReviewResponse], status_code=201)
@log_exceptions("POST /reviews")
def create(
    review: ReviewCreate,
    review_service: ReviewService = Depends(get_review_service)
):
    obj = review_service.create(review.model_dump())
    return ApiResponse(data=ReviewResponse.model_validate(obj))

@router.get("/", response_model=ApiResponse[list[ReviewResponse]])
@log_exceptions("GET /reviews")
def index(review_service: ReviewService = Depends(get_review_service)):
    reviews = review_service.get_all()
    return ApiResponse(data=[ReviewResponse.model_validate(r) for r in reviews])

@router.get("/{review_id}", response_model=ApiResponse[ReviewResponse])
@log_exceptions("GET /reviews/{review_id}")
def get(review_id: int, review_service: ReviewService = Depends(get_review_service)):
    review = review_service.get_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ApiResponse(data=ReviewResponse.model_validate(review))

@router.get("/book/{book_id}", response_model=ApiResponse[list[ReviewResponse]])
@log_exceptions("GET /reviews/book/{book_id}")
def get_by_book(book_id: int, review_service: ReviewService = Depends(get_review_service)):
    reviews = review_service.get_by_book(book_id)
    return ApiResponse(data=[ReviewResponse.model_validate(r) for r in reviews])

@router.put("/{review_id}", response_model=ApiResponse[ReviewResponse])
@log_exceptions("PUT /reviews/{review_id}")
def update(
    review_id: int,
    review_in: ReviewUpdate,
    review_service: ReviewService = Depends(get_review_service)
):
    review = review_service.get_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    updated_review = review_service.update(review_id, review_in.model_dump(exclude_unset=True))
    return ApiResponse(data=ReviewResponse.model_validate(updated_review))

@router.delete("/{review_id}", status_code=204)
@log_exceptions("DELETE /reviews/{review_id}")
def delete(review_id: int, review_service: ReviewService = Depends(get_review_service)):
    deleted = review_service.delete_by_id(review_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")
    return None