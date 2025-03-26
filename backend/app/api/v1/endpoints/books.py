from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.book_service import BookService
from app.schemas.book import BookCreate, BookResponse

router = APIRouter()

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    """Dependency function to inject BookService."""
    return BookService(db)

@router.post("/", response_model=BookResponse)
def create(book: BookCreate, book_service: BookService = Depends(get_book_service)):
    """Create a new book"""
    return book_service.create(book.model_dump())

@router.get("/", response_model=list[BookResponse])
def index(book_service: BookService = Depends(get_book_service)):
    """Get all books"""
    return book_service.get_all()

@router.get("/{book_id}", response_model=BookResponse)
def get(book_id: int, book_service: BookService = Depends(get_book_service)):
    """Retrieve a book by ID"""
    book = book_service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book