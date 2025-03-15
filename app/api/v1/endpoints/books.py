from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.book_service import create_book, get_books
from app.schemas.book import BookCreate, BookResponse

router = APIRouter()

@router.post("/", response_model=BookResponse)
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    return create_book(db, book)

@router.get("/", response_model=list[BookResponse])
def list_books(db: Session = Depends(get_db)):
    return get_books(db)