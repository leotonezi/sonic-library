from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.book_service import BookService
from app.schemas.base_schema import ApiResponse
from app.schemas.book import BookCreate, BookResponse

router = APIRouter()

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    """Dependency function to inject BookService."""
    return BookService(db)

@router.post("/", response_model=ApiResponse[BookResponse], status_code=201)
def create(book: BookCreate, book_service: BookService = Depends(get_book_service)):
    """Create a new book"""
    obj = book_service.create(book.model_dump())
    return ApiResponse(data=BookResponse.model_validate(obj))

@router.get("/", response_model=ApiResponse[list[BookResponse]])
def index(
    search: str = Query(default=None, description="Search books by title or author"),
    genre: str = Query(default=None, description="Filter by genre"),
    book_service: BookService = Depends(get_book_service)
):
    """Get all books or filter by title or author and/or genre"""
    books = book_service.filter_books(search=search, genre=genre)
    return ApiResponse(data=[BookResponse.model_validate(b) for b in books])

@router.get("/{book_id}", response_model=ApiResponse[BookResponse])
def get(book_id: int, book_service: BookService = Depends(get_book_service)):
    """Retrieve a book by ID"""
    book = book_service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return ApiResponse(data=BookResponse.model_validate(book))