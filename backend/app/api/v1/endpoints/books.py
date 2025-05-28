from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.book_service import BookService
from app.services.user_book_service import UserBookService
from app.services.review_service import ReviewService
from app.schemas.base_schema import ApiResponse
from app.schemas.book import BookCreate, BookResponse
from app.schemas.user_book import serialize_user_book
from app.schemas.review import ReviewResponse
from app.core.security import get_current_user
from app.models.user import User
from app.core.logging_decorator import log_exceptions

import re, html, requests, os

router = APIRouter()

def get_book_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookService:
    return BookService(db)

def get_review_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewService:
    return ReviewService(db)

def get_user_book_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserBookService:
    return UserBookService(db)

@router.post("/", response_model=ApiResponse[BookResponse], status_code=201)
@log_exceptions("POST /books")
def create(book: BookCreate, book_service: BookService = Depends(get_book_service)):
    try:
        obj = book_service.create(book.model_dump())
        response = BookResponse.from_orm_with_genres(obj)
        return ApiResponse(data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating book: {e}")

@router.get("/", response_model=ApiResponse[list[BookResponse]])
@log_exceptions("GET /books")
def index(
    search: str = Query(default=None, description="Search books by title or author"),
    genre: str = Query(default=None, description="Filter by genre"),
    book_service: BookService = Depends(get_book_service)
):
    try:
        books = book_service.filter_books(search=search, genre=genre)
        return ApiResponse(data=[BookResponse.from_orm_with_genres(b) for b in books])
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error listing books: " + str(e))

@router.get("/search-external", response_model=ApiResponse)
@log_exceptions("GET /books/search-external")
def search_external_books(
    q: str = Query(..., description="Search books by title, author, or ISBN"),
    max_results: int = Query(10, ge=1, le=40),
):
    """
    Search for books using the Google Books API and return normalized results.
    """
    GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
    GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

    params = {
        "q": q,
        "maxResults": max_results,
    }
    if GOOGLE_BOOKS_API_KEY:
        params["key"] = GOOGLE_BOOKS_API_KEY

    try:
        resp = requests.get(GOOGLE_BOOKS_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        books = []
        for item in data.get("items", []):
            info = item.get("volumeInfo", {})
            books.append({
                "external_id": item.get("id"),
                "title": info.get("title"),
                "authors": info.get("authors", []),
                "publishedDate": info.get("publishedDate"),
                "description": info.get("description"),
                "thumbnail": info.get("imageLinks", {}).get("thumbnail"),
                "pageCount": info.get("pageCount"),
                "categories": info.get("categories", []),
                "language": info.get("language"),
            })

        return {
            "data": books,
            "message": "Books fetched successfully",
            "status": "ok"
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Google Books API error: {str(e)}")

@router.get("/external/{external_id}", response_model=ApiResponse)
@log_exceptions("GET /books/external/{external_id}")
def get_book_by_external_id(
    external_id: str = Path(..., description="Google Books volume ID"),
    user_book_service: UserBookService = Depends(get_user_book_service),
    review_service: ReviewService = Depends(get_review_service)
):
    """
    Fetch a single book from Google Books API by its external (Google) ID.
    """
    GOOGLE_BOOKS_API_URL = f"https://www.googleapis.com/books/v1/volumes/{external_id}"
    GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

    params = {}
    if GOOGLE_BOOKS_API_KEY:
        params["key"] = GOOGLE_BOOKS_API_KEY

    try:
        resp = requests.get(GOOGLE_BOOKS_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        item = resp.json()

        user_book = user_book_service.get_by_external_book(external_id)

        info = item.get("volumeInfo", {})
        book = {
            "external_id": item.get("id"),
            "title": info.get("title"),
            "authors": info.get("authors", []),
            "publishedDate": info.get("publishedDate"),
            "description": clean_html(info.get("description")),
            "thumbnail": info.get("imageLinks", {}).get("thumbnail"),
            "pageCount": info.get("pageCount"),
            "categories": info.get("categories", []),
            "language": info.get("language"),
        }

        user_book_response = serialize_user_book(user_book) if user_book else None

        reviews_data = review_service.get_by_book(user_book.book_id) if user_book else []
        reviews = [ReviewResponse.model_validate(r) for r in reviews_data]

        return {
            "data": {
                "book": book,
                "userBook": user_book_response,
                "reviews": reviews
            },
            "message": "Book fetched successfully",
            "status": "ok"
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Google Books API error: {str(e)}")

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


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = html.unescape(raw_html)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<.*?>', '', text)
    return text.strip()
