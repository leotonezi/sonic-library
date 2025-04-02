from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.review_service import ReviewService
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter()

def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    """Dependency function to inject ReviewService."""
    return ReviewService(db)

@router.post("/", response_model=ReviewResponse)
def create(review: ReviewCreate, review_service: ReviewService = Depends(get_review_service)):
    """Create a new review"""
    return review_service.create(review.model_dump())

@router.get("/", response_model=list[ReviewResponse])
def index(review_service: ReviewService = Depends(get_review_service)):
    """Get all reviews"""
    return review_service.get_all()

@router.get("/{review_id}", response_model=ReviewResponse)
def get(review_id: int, review_service: ReviewService = Depends(get_review_service)):
    """Retrieve a review by ID"""
    review = review_service.get_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.get("/book/{book_id}", response_model=list[ReviewResponse])
def get_by_book(book_id: int, review_service: ReviewService = Depends(get_review_service)):
    """Get reviews by book ID"""
    return review_service.get_by_book(book_id)
