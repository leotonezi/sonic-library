from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_book_service import UserBookService
from app.services.book_service import BookService
from app.schemas.base_schema import ApiResponse, PaginationResponse
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user_book import UserBookCreate, UserBookResponse, UserBookUpdate, serialize_user_book
from app.core.logging_decorator import log_exceptions
from app.models.user_book import StatusEnum

router = APIRouter()

def get_user_book_service(db: Session = Depends(get_db)) -> UserBookService:
    return UserBookService(db)

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    return BookService(db)

@router.post("/", response_model=ApiResponse[UserBookResponse], status_code=201)
@log_exceptions("POST /user-books")
def create(
    user_book: UserBookCreate,
    current_user: User = Depends(get_current_user),
    user_book_service: UserBookService = Depends(get_user_book_service),
    book_service: BookService = Depends(get_book_service)
):
    # Validate that either book_id or external_book_id is provided, not both
    if bool(getattr(user_book, "book_id", None)) == bool(user_book.external_book_id):
        raise HTTPException(
            status_code=400,
            detail="Exactly one of book_id or external_book_id must be provided"
        )

    # --- Check if book exists, or create it ---
    book_id = getattr(user_book, "book_id", None)
    external_book_id = user_book.external_book_id

    if book_id:
        book = book_service.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book with this ID does not exist.")
    elif external_book_id:
        book = book_service.get_by_external_id(external_book_id)
        if not book:
            if not user_book.book:
                raise HTTPException(status_code=400, detail="Book data required to create new book.")
            try:
                book_data = user_book.book.dict()
                book_data["external_id"] = external_book_id
                book = book_service.create(book_data)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error creating book: {str(e)}"
                )
        book_id = book.id

    # Check for duplicate user_book
    existing = user_book_service.get_by_user_and_book(current_user.id, book_id)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This book is already in the user's library."
        )

    data = user_book.model_dump(exclude_unset=True)
    data["user_id"] = current_user.id

    data.pop("book", None)
    data["book_id"] = book_id

    obj = user_book_service.create(data)
    return ApiResponse(data=serialize_user_book(obj))

@router.get("/my-books", response_model=ApiResponse[list[UserBookResponse]])
@log_exceptions("GET /user-books/my-books")
def get_my_books(
    current_user: User = Depends(get_current_user),
    user_book_service: UserBookService = Depends(get_user_book_service),
    status: str | None = Query(None, description="Filter by reading status: TO READ, READ, READING")
):
    """Get all books in the user's library, optionally filtered by status."""
    books = user_book_service.get_books_by_user(current_user.id, status=status)
    return ApiResponse(data=[serialize_user_book(b) for b in books])

@router.get("/my-books/paginated", response_model=PaginationResponse[UserBookResponse])
@log_exceptions("GET /user-books/my-books/paginated")
def get_my_books_paginated(
    current_user: User = Depends(get_current_user),
    user_book_service: UserBookService = Depends(get_user_book_service),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    status: str | None = Query(None, description="Filter by reading status: TO READ, READ, READING")
):
    """Get paginated books in the user's library, optionally filtered by status."""
    books, total_count, total_pages, current_page = user_book_service.get_books_by_user_paginated(
        current_user.id, page=page, page_size=page_size, status=status
    )
    
    pagination_info = {
        "current_page": current_page,
        "total_pages": total_pages,
        "total_count": total_count,
        "page_size": page_size,
        "has_next": current_page < total_pages,
        "has_previous": current_page > 1
    }
    
    return PaginationResponse(
        data=[serialize_user_book(b) for b in books],
        pagination=pagination_info
    )

@router.get("/book/{book_id}", response_model=ApiResponse[UserBookResponse])
@log_exceptions("GET /user-books/book/{book_id}")
def get_by_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    user_book_service: UserBookService = Depends(get_user_book_service)
):
    """Get user's relationship with a specific local book."""
    book = user_book_service.get_by_user_and_book(current_user.id, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found in user's library")
    return ApiResponse(data=UserBookResponse.model_validate(book))

@router.get("/book/external/{external_id}", response_model=ApiResponse[UserBookResponse])
@log_exceptions("GET /user-books/book/external/{external_id}")
def get_by_external_book(
    external_id: str,
    current_user: User = Depends(get_current_user),
    user_book_service: UserBookService = Depends(get_user_book_service)
):
    """Get user's relationship with a specific external book."""
    book = user_book_service.get_by_user_and_external_book(current_user.id, external_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found in user's library")
    return ApiResponse(data=UserBookResponse.model_validate(book))

@router.put("/{user_book_id}", response_model=ApiResponse[UserBookResponse])
@log_exceptions("PUT /user-books/{user_book_id}")
def update(
    user_book_id: int,
    user_book_in: UserBookUpdate,
    current_user: User = Depends(get_current_user),
    user_book_service: UserBookService = Depends(get_user_book_service)
):
    """Update a book's status in user's library."""
    # Get existing user_book
    user_book = user_book_service.get_by_id(user_book_id)
    if not user_book:
        raise HTTPException(status_code=404, detail="Book not found in library")

    # Verify ownership
    if user_book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this book")

    updated = user_book_service.update(
        user_book_id,
        user_book_in.model_dump(exclude_unset=True)
    )
    return ApiResponse(data=serialize_user_book(updated))

@router.delete("/{user_book_id}", status_code=204)
@log_exceptions("DELETE /user-books/{user_book_id}")
def delete(
    user_book_id: int,
    current_user: User = Depends(get_current_user),
    user_book_service: UserBookService = Depends(get_user_book_service)
):
    """Remove a book from user's library."""
    # Get existing user_book
    user_book = user_book_service.get_by_id(user_book_id)
    if not user_book:
        raise HTTPException(status_code=404, detail="Book not found in library")

    # Verify ownership
    if user_book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to remove this book")

    user_book_service.delete_by_id(user_book_id)
    return None

@router.get("/status/{status}", response_model=ApiResponse[list[UserBookResponse]])
@log_exceptions("GET /user-books/status/{status}")
def get_by_status(
    status: StatusEnum,
    current_user: User = Depends(get_current_user),
    user_book_service: UserBookService = Depends(get_user_book_service)
):
    """Get all books with a specific status from user's library."""
    books = user_book_service.get_by_user_and_status(current_user.id, status)
    return ApiResponse(data=[UserBookResponse.model_validate(b) for b in books])
