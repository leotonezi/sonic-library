import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.core.database import get_db
from app.core.security import get_admin_user
from app.core.logging_decorator import log_exceptions
from app.models.user import User
from app.models.review import Review
from app.models.user_book import UserBook
from app.models.book import Book
from app.schemas.admin import (
    AdminUserResponse,
    AdminUserDetailResponse,
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
    query = db.query(User)

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
    users = query.offset(offset).limit(page_size).all()

    items = []
    for user in users:
        books_count = db.query(func.count(UserBook.id)).filter(UserBook.user_id == user.id).scalar() or 0
        reviews_count = db.query(func.count(Review.id)).filter(Review.user_id == user.id).scalar() or 0
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

    # Get user's books with book titles
    user_books = (
        db.query(UserBook)
        .filter(UserBook.user_id == user_id)
        .outerjoin(Book, UserBook.book_id == Book.id)
        .all()
    )
    books_list = []
    for ub in user_books:
        book_title = None
        if ub.book_id:
            book = db.query(Book).filter(Book.id == ub.book_id).first()
            if book:
                book_title = book.title
        books_list.append({
            "id": ub.id,
            "book_id": ub.book_id,
            "external_book_id": ub.external_book_id,
            "book_title": book_title,
            "status": ub.status.value if hasattr(ub.status, "value") else str(ub.status),
            "created_at": str(ub.created_at) if ub.created_at else None,
        })

    # Get user's reviews with book titles
    reviews = db.query(Review).filter(Review.user_id == user_id).all()
    reviews_list = []
    for r in reviews:
        book_title = None
        if r.book_id:
            book = db.query(Book).filter(Book.id == r.book_id).first()
            if book:
                book_title = book.title
        reviews_list.append({
            "id": r.id,
            "book_id": r.book_id,
            "external_book_id": r.external_book_id,
            "book_title": book_title,
            "content": r.content,
            "rate": r.rate,
            "created_at": str(r.created_at) if r.created_at else None,
        })

    books_count = len(user_books)
    reviews_count = len(reviews)

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
