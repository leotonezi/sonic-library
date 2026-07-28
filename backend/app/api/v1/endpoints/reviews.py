from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.review_service import ReviewService
from app.schemas.base_schema import ApiResponse, PaginationResponse
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from app.core.logging_decorator import log_exceptions
from app.core.config import settings

import logging
import math

logger = logging.getLogger(__name__)

router = APIRouter(redirect_slashes=False)


def get_review_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewService:
    """Inject ReviewService, requiring authenticated user."""
    return ReviewService(db)


def _build_pagination(
    page: int, page_size: int, total_count: int
) -> dict:
    total_pages = max(1, math.ceil(total_count / page_size)) if total_count > 0 else 1
    return {
        "current_page": page,
        "total_pages": total_pages,
        "total_count": total_count,
        "page_size": page_size,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def _rows_to_review_responses(rows: list) -> list[ReviewResponse]:
    result = []
    for review_data, user_name, user_profile_picture in rows:
        review_dict = {
            "id": review_data.id,
            "book_id": review_data.book_id,
            "external_book_id": review_data.external_book_id,
            "content": review_data.content,
            "rate": review_data.rate,
            "user_id": review_data.user_id,
            "user_name": user_name,
            "user_profile_picture": user_profile_picture,
        }
        result.append(ReviewResponse.model_validate(review_dict))
    return result


@router.post("", response_model=ApiResponse[ReviewResponse], status_code=201)
@log_exceptions("POST /reviews")
def create(
    review: ReviewCreate,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    review_data = review.model_dump()
    review_data["user_id"] = current_user.id
    obj = review_service.create(review_data)
    return ApiResponse(data=ReviewResponse.model_validate(obj))


@router.get("", response_model=PaginationResponse[ReviewResponse])
@log_exceptions("GET /reviews")
def index(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        description="Number of items per page (clamped to MAX_PAGE_SIZE)",
    ),
    review_service: ReviewService = Depends(get_review_service),
):
    """List all reviews with pagination."""
    page_size = min(page_size, settings.MAX_PAGE_SIZE)
    reviews_raw, total_count = review_service.get_all_paginated(page=page, page_size=page_size)
    return PaginationResponse(
        data=[ReviewResponse.model_validate(r) for r in reviews_raw],
        pagination=_build_pagination(page, page_size, total_count),
        message="Reviews fetched successfully",
        status="ok",
    )


@router.get("/{review_id}", response_model=ApiResponse[ReviewResponse])
@log_exceptions("GET /reviews/{review_id}")
def get(review_id: int, review_service: ReviewService = Depends(get_review_service)):
    review = review_service.get_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ApiResponse(data=ReviewResponse.model_validate(review))


@router.get("/book/{book_id}", response_model=PaginationResponse[ReviewResponse])
@log_exceptions("GET /reviews/book/{book_id}")
def get_by_book(
    book_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        description="Number of items per page (clamped to MAX_PAGE_SIZE)",
    ),
    review_service: ReviewService = Depends(get_review_service),
):
    """Paginated reviews for a local book."""
    page_size = min(page_size, settings.MAX_PAGE_SIZE)
    rows, total_count = review_service.get_by_book_with_user_paginated(
        book_id, page=page, page_size=page_size
    )
    return PaginationResponse(
        data=_rows_to_review_responses(rows),
        pagination=_build_pagination(page, page_size, total_count),
        message="Reviews fetched successfully",
        status="ok",
    )


@router.get("/book/external/{book_id}", response_model=PaginationResponse[ReviewResponse])
@log_exceptions("GET /reviews/book/external/{book_id}")
def get_by_external_book(
    book_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        description="Number of items per page (clamped to MAX_PAGE_SIZE)",
    ),
    review_service: ReviewService = Depends(get_review_service),
):
    """Paginated reviews for an external (Google Books) book."""
    page_size = min(page_size, settings.MAX_PAGE_SIZE)
    rows, total_count = review_service.get_by_external_book_with_user_paginated(
        book_id, page=page, page_size=page_size
    )
    return PaginationResponse(
        data=_rows_to_review_responses(rows),
        pagination=_build_pagination(page, page_size, total_count),
        message="Reviews fetched successfully",
        status="ok",
    )

@router.put("/{review_id}", response_model=ApiResponse[ReviewResponse])
@log_exceptions("PUT /reviews/{review_id}")
def update(
    review_id: int,
    review_in: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service)
):
    review = review_service.get_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if the current user owns this review
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this review")
    
    updated_review = review_service.update(review_id, review_in.model_dump(exclude_unset=True))
    return ApiResponse(data=ReviewResponse.model_validate(updated_review))

@router.delete("/{review_id}", status_code=204)
@log_exceptions("DELETE /reviews/{review_id}")
def delete(
    review_id: int,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service)
):
    review = review_service.get_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if the current user owns this review
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")
    
    deleted = review_service.delete_by_id(review_id)
    return None