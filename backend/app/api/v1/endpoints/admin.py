import math
import secrets
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.core.database import get_db
from app.core.security import get_admin_user, hash_password
from app.core.logging_decorator import log_exceptions
from app.models.user import User
from app.models.review import Review
from app.models.user_book import UserBook
from app.models.book import Book
from app.schemas.admin import (
    AdminUserResponse,
    AdminUserDetailResponse,
    AdminReviewResponse,
    AdminUserBookResponse,
    AdminStatsResponse,
    AdminUserUpdate,
    AdminReviewUpdate,
    PaginationResponse,
)
from app.schemas.base_schema import ApiResponse

router = APIRouter()


@router.get("/users", response_model=PaginationResponse[AdminUserResponse])
@log_exceptions("GET /admin/users")
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """List all users with pagination and search."""
    books_count_subq = (
        db.query(UserBook.user_id, func.count(UserBook.id).label("books_count"))
        .group_by(UserBook.user_id)
        .subquery()
    )
    reviews_count_subq = (
        db.query(Review.user_id, func.count(Review.id).label("reviews_count"))
        .group_by(Review.user_id)
        .subquery()
    )

    query = (
        db.query(
            User,
            func.coalesce(books_count_subq.c.books_count, 0).label("books_count"),
            func.coalesce(reviews_count_subq.c.reviews_count, 0).label("reviews_count"),
        )
        .outerjoin(books_count_subq, User.id == books_count_subq.c.user_id)
        .outerjoin(reviews_count_subq, User.id == reviews_count_subq.c.user_id)
    )

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_filter),
                User.email.ilike(search_filter),
            )
        )

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    results = query.offset(offset).limit(page_size).all()

    items = []
    for user, books_count, reviews_count in results:
        items.append(
            AdminUserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                is_active=user.is_active,
                profile_picture=user.profile_picture,
                books_count=books_count,
                reviews_count=reviews_count,
            )
        )

    return PaginationResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/users/{user_id}", response_model=ApiResponse[AdminUserDetailResponse])
@log_exceptions("GET /admin/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get a single user with their books and reviews."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user's books with book titles via JOIN (no per-row queries)
    user_books_rows = (
        db.query(UserBook, Book.title.label("book_title"))
        .outerjoin(Book, UserBook.book_id == Book.id)
        .filter(UserBook.user_id == user_id)
        .all()
    )
    books_list = []
    for ub, book_title in user_books_rows:
        books_list.append({
            "id": ub.id,
            "book_id": ub.book_id,
            "external_book_id": ub.external_book_id,
            "book_title": book_title,
            "status": ub.status.value if hasattr(ub.status, "value") else str(ub.status),
            "created_at": str(ub.created_at) if ub.created_at else None,
        })

    # Get user's reviews with book titles via JOIN (no per-row queries)
    reviews_rows = (
        db.query(Review, Book.title.label("book_title"))
        .outerjoin(Book, Review.book_id == Book.id)
        .filter(Review.user_id == user_id)
        .all()
    )
    reviews_list = []
    for r, book_title in reviews_rows:
        reviews_list.append({
            "id": r.id,
            "book_id": r.book_id,
            "external_book_id": r.external_book_id,
            "book_title": book_title,
            "content": r.content,
            "rate": r.rate,
            "created_at": str(r.created_at) if r.created_at else None,
        })

    books_count = len(user_books_rows)
    reviews_count = len(reviews_rows)

    detail = AdminUserDetailResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        is_active=user.is_active,
        profile_picture=user.profile_picture,
        books_count=books_count,
        reviews_count=reviews_count,
        books=books_list,
        reviews=reviews_list,
    )

    return ApiResponse(data=detail)


@router.get("/reviews", response_model=PaginationResponse[AdminReviewResponse])
@log_exceptions("GET /admin/reviews")
def list_reviews(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """List all reviews with pagination and search."""
    query = (
        db.query(Review, User.name.label("user_name"), Book.title.label("book_title"))
        .join(User, Review.user_id == User.id)
        .outerjoin(Book, Review.book_id == Book.id)
    )

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_filter),
                Book.title.ilike(search_filter),
            )
        )

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    results = query.offset(offset).limit(page_size).all()

    items = []
    for review, user_name, book_title in results:
        items.append(
            AdminReviewResponse(
                id=review.id,
                user_id=review.user_id,
                user_name=user_name,
                book_id=review.book_id,
                external_book_id=review.external_book_id,
                book_title=book_title,
                content=review.content,
                rate=review.rate,
                created_at=review.created_at,
            )
        )

    return PaginationResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/user-books", response_model=PaginationResponse[AdminUserBookResponse])
@log_exceptions("GET /admin/user-books")
def list_user_books(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """List all user-book records with pagination and search."""
    query = (
        db.query(UserBook, User.name.label("user_name"), Book.title.label("book_title"))
        .join(User, UserBook.user_id == User.id)
        .outerjoin(Book, UserBook.book_id == Book.id)
    )

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_filter),
                Book.title.ilike(search_filter),
            )
        )

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    results = query.offset(offset).limit(page_size).all()

    items = []
    for ub, user_name, book_title in results:
        items.append(
            AdminUserBookResponse(
                id=ub.id,
                user_id=ub.user_id,
                user_name=user_name,
                book_id=ub.book_id,
                external_book_id=ub.external_book_id,
                book_title=book_title,
                status=ub.status.value if hasattr(ub.status, "value") else str(ub.status),
                created_at=ub.created_at,
            )
        )

    return PaginationResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=ApiResponse[AdminStatsResponse])
@log_exceptions("GET /admin/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get aggregate admin statistics."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    total_books = db.query(func.count(Book.id)).scalar() or 0
    total_reviews = db.query(func.count(Review.id)).scalar() or 0
    total_user_books = db.query(func.count(UserBook.id)).scalar() or 0
    avg_rating = db.query(func.avg(Review.rate)).scalar() or 0.0

    stats = AdminStatsResponse(
        total_users=total_users,
        total_active_users=total_active_users,
        total_books=total_books,
        total_reviews=total_reviews,
        total_user_books=total_user_books,
        avg_rating=round(float(avg_rating), 2),
    )

    return ApiResponse(data=stats)


@router.put("/users/{user_id}", response_model=ApiResponse[AdminUserResponse])
@log_exceptions("PUT /admin/users/{user_id}")
def update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Update user fields (name, email, is_active)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.name is not None:
        user.name = user_update.name
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    db.commit()
    db.refresh(user)

    books_count_subq = (
        db.query(func.count(UserBook.id))
        .filter(UserBook.user_id == user.id)
        .correlate(User)
        .scalar_subquery()
    )
    reviews_count_subq = (
        db.query(func.count(Review.id))
        .filter(Review.user_id == user.id)
        .correlate(User)
        .scalar_subquery()
    )
    counts = db.query(books_count_subq, reviews_count_subq).one()
    books_count = counts[0] or 0
    reviews_count = counts[1] or 0

    return ApiResponse(
        data=AdminUserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            profile_picture=user.profile_picture,
            books_count=books_count,
            reviews_count=reviews_count,
        )
    )


@router.delete("/users/{user_id}")
@log_exceptions("DELETE /admin/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Soft delete a user by setting is_active=False."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return {"message": f"User {user_id} has been deactivated"}


@router.post("/users/{user_id}/reset-password")
@log_exceptions("POST /admin/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Reset a user's password to a random generated password."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_password = secrets.token_urlsafe(12)
    user.password = hash_password(new_password)
    db.commit()

    return {"message": "Password has been reset", "new_password": new_password}


@router.put("/reviews/{review_id}", response_model=ApiResponse[AdminReviewResponse])
@log_exceptions("PUT /admin/reviews/{review_id}")
def update_review(
    review_id: int,
    review_update: AdminReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Update review fields (content, rate)."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review_update.content is not None:
        review.content = review_update.content
    if review_update.rate is not None:
        review.rate = review_update.rate

    db.commit()
    db.refresh(review)

    # Get user_name and book_title in a single query
    result = (
        db.query(User.name, Book.title)
        .outerjoin(Book, Book.id == review.book_id)
        .filter(User.id == review.user_id)
        .first()
    )
    user_name = result[0] if result else ""
    book_title = result[1] if result else None

    return ApiResponse(
        data=AdminReviewResponse(
            id=review.id,
            user_id=review.user_id,
            user_name=user_name,
            book_id=review.book_id,
            external_book_id=review.external_book_id,
            book_title=book_title,
            content=review.content,
            rate=review.rate,
            created_at=review.created_at,
        )
    )


@router.delete("/reviews/{review_id}")
@log_exceptions("DELETE /admin/reviews/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Hard delete a review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()

    return {"message": f"Review {review_id} has been deleted"}


@router.delete("/user-books/{user_book_id}")
@log_exceptions("DELETE /admin/user-books/{user_book_id}")
def delete_user_book(
    user_book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Hard delete a user-book record."""
    user_book = db.query(UserBook).filter(UserBook.id == user_book_id).first()
    if not user_book:
        raise HTTPException(status_code=404, detail="User-book record not found")

    db.delete(user_book)
    db.commit()

    return {"message": f"User-book record {user_book_id} has been deleted"}
