from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.book_service import BookService
from app.schemas.base_schema import ApiResponse
from app.schemas.book import BookCreate, BookResponse
from app.core.security import get_current_user
from app.models.user import User
from app.core.logging_decorator import log_exceptions

router = APIRouter()

def get_book_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookService:
    return BookService(db)

@router.post("/", response_model=ApiResponse[BookResponse], status_code=201)
@log_exceptions("POST /books")
def create(book: BookCreate, book_service: BookService = Depends(get_book_service)):
    try:
        obj = book_service.create(book.model_dump())
        return ApiResponse(data=BookResponse.model_validate(obj))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error creating book")

@router.get("/", response_model=ApiResponse[list[BookResponse]])
@log_exceptions("GET /books")
def index(
    search: str = Query(default=None, description="Search books by title or author"),
    genre: str = Query(default=None, description="Filter by genre"),
    book_service: BookService = Depends(get_book_service)
):
    try:
        books = book_service.filter_books(search=search, genre=genre)
        return ApiResponse(data=[BookResponse.model_validate(b) for b in books])
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error listing books")

@router.get("/{book_id}", response_model=ApiResponse[BookResponse])
@log_exceptions("GET /books/{book_id}")
def get(book_id: int, book_service: BookService = Depends(get_book_service)):
    try:
        book = book_service.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return ApiResponse(data=BookResponse.model_validate(book))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving book")