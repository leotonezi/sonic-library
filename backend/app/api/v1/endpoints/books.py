from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.book_service import BookService
from app.services.user_book_service import UserBookService
from app.services.review_service import ReviewService
from app.schemas.base_schema import ApiResponse, PaginationResponse
from app.schemas.book import BookCreate, BookResponse
from app.schemas.user_book import serialize_user_book
from app.schemas.review import ReviewResponse
from app.core.security import get_current_user
from app.models.user import User
from app.core.logging_decorator import log_exceptions
from app.core.config import settings

import re, html, requests, os
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

router = APIRouter()

# Simple in-memory cache for popular books
_popular_books_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = settings.POPULAR_BOOKS_CACHE_TTL  # Configurable TTL from settings

def get_cached_popular_books(max_results: int) -> Optional[list]:
    """Get popular books from cache if available and not expired."""
    cache_key = f"popular_books_{max_results}"
    cached_data = _popular_books_cache.get(cache_key)
    
    if cached_data:
        current_time = time.time()
        if current_time - cached_data["timestamp"] < CACHE_TTL:
            logger.info(f"Cache hit for popular books with max_results={max_results}")
            return cached_data["data"]
        else:
            # Remove expired cache entry
            logger.info(f"Cache expired for popular books with max_results={max_results}")
            del _popular_books_cache[cache_key]
    else:
        logger.info(f"Cache miss for popular books with max_results={max_results}")
    
    return None

def set_cached_popular_books(max_results: int, data: list):
    """Cache popular books data with timestamp."""
    cache_key = f"popular_books_{max_results}"
    _popular_books_cache[cache_key] = {
        "data": data,
        "timestamp": time.time()
    }
    logger.info(f"Cached popular books with max_results={max_results}, data_count={len(data)}")

def get_book_service(
    db: Session = Depends(get_db),
) -> BookService:
    return BookService(db)

def get_book_service_auth(
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
@log_exceptions("POST /books", log_response=False)
def create(book: BookCreate, book_service: BookService = Depends(get_book_service_auth)):
    try:
        obj = book_service.create(book.model_dump())
        response = BookResponse.from_orm_with_genres(obj)
        return ApiResponse(data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating book: {e}")

@router.get("/", response_model=PaginationResponse[BookResponse])
@log_exceptions("GET /books", log_response=False)
def index(
    search: str = Query(default=None, description="Search books by title or author"),
    genre: str = Query(default=None, description="Filter by genre"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    book_service: BookService = Depends(get_book_service)
):
    try:
        books, total_count, total_pages, current_page = book_service.filter_books_paginated(
            page=page, page_size=page_size, search=search, genre=genre
        )
        pagination_info = {
            "current_page": current_page,
            "total_pages": total_pages,
            "total_count": total_count,
            "page_size": page_size,
            "has_next": current_page < total_pages,
            "has_previous": current_page > 1,
            "start_index": (current_page - 1) * page_size,
            "end_index": min(current_page * page_size, total_count)
        }
        return PaginationResponse(
            data=[BookResponse.from_orm_with_genres(b) for b in books],
            pagination=pagination_info,
            message="Books fetched successfully",
            status="ok"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error listing books: " + str(e))

@router.get("/search-external", response_model=PaginationResponse)
@log_exceptions("GET /books/search-external", log_response=False)
def search_external_books(
    q: str = Query(..., description="Search books by title, author, or ISBN"),
    max_results: int = Query(10, ge=1, le=40),
    page: int = Query(1, ge=1, description="Page number (Google Books API limitation: max 40 results per page)"),
):
    """
    Search for books using the Google Books API and return normalized results.
    Note: Google Books API has a limitation of 40 results per page.
    """
    GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
    GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

    # Google Books API has a limit of 40 results per page
    max_results_per_page = min(max_results, 40)
    start_index = (page - 1) * max_results_per_page

    params = {
        "q": q,
        "maxResults": max_results_per_page,
        "startIndex": start_index,
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

        # Calculate pagination info
        total_items = data.get("totalItems", 0)
        total_pages = (total_items + max_results_per_page - 1) // max_results_per_page if total_items > 0 else 0
        
        pagination_info = {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_items,
            "page_size": max_results_per_page,
            "has_next": page < total_pages,
            "has_previous": page > 1,
            "start_index": start_index,
            "end_index": start_index + len(books)
        }

        return PaginationResponse(
            data=books,
            pagination=pagination_info,
            message="Books fetched successfully",
            status="ok"
        )

    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Google Books API error: {str(e)}")

@router.get("/external/{external_id}", response_model=ApiResponse)
@log_exceptions("GET /books/external/{external_id}", log_response=False)
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

        # Get reviews using the external book ID
        reviews_data = review_service.get_by_external_book_with_user(external_id) if external_id else []
        reviews = [
            ReviewResponse.model_validate(
                {**review.__dict__, "user_name": user_name, "user_profile_picture": user_profile_picture}
            )
            for review, user_name, user_profile_picture in reviews_data
        ]

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

@router.get("/popular", response_model=PaginationResponse)
@log_exceptions("GET /books/popular", log_response=False)
def get_popular_books(
    max_results: int = Query(12, ge=1, le=40),
    page: int = Query(1, ge=1, description="Page number"),
):
    """
    Fetch popular books using the Google Books API with curated search terms.
    Cached for 1 hour to improve performance.
    """
    # Check cache first
    cached_books = get_cached_popular_books(max_results)
    if cached_books:
        # Apply pagination to cached results
        start_index = (page - 1) * max_results
        end_index = start_index + max_results
        paginated_books = cached_books[start_index:end_index]
        
        total_items = len(cached_books)
        total_pages = (total_items + max_results - 1) // max_results
        
        pagination_info = {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_items,
            "page_size": max_results,
            "has_next": page < total_pages,
            "has_previous": page > 1,
            "start_index": start_index,
            "end_index": min(end_index, total_items)
        }
        
        return PaginationResponse(
            data=paginated_books,
            pagination=pagination_info,
            message="Popular books fetched from cache",
            status="ok"
        )

    GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
    GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

    # Popular search terms to get diverse popular books
    popular_queries = [
        "bestseller fiction",
        "popular books",
        "award winning novels",
        "classic literature",
        "modern romance",
        "thriller mystery"
    ]

    all_books = []
    books_per_query = max(2, max_results // len(popular_queries))

    for query in popular_queries:
        params = {
            "q": query,
            "maxResults": books_per_query,
            "orderBy": "relevance"
        }
        if GOOGLE_BOOKS_API_KEY:
            params["key"] = GOOGLE_BOOKS_API_KEY

        try:
            resp = requests.get(GOOGLE_BOOKS_API_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("items", []):
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
                
                # Only add if not already in the list (avoid duplicates)
                if not any(b["external_id"] == book["external_id"] for b in all_books):
                    all_books.append(book)
                    
                    # Stop if we have enough books
                    if len(all_books) >= max_results:
                        break

        except requests.RequestException as e:
            print(f"Error fetching books for query '{query}': {str(e)}")
            continue

    final_books = all_books[:max_results]
    
    # Cache the results
    set_cached_popular_books(max_results, final_books)

    # Apply pagination
    start_index = (page - 1) * max_results
    end_index = start_index + max_results
    paginated_books = final_books[start_index:end_index]
    
    total_items = len(final_books)
    total_pages = (total_items + max_results - 1) // max_results
    
    pagination_info = {
        "current_page": page,
        "total_pages": total_pages,
        "total_count": total_items,
        "page_size": max_results,
        "has_next": page < total_pages,
        "has_previous": page > 1,
        "start_index": start_index,
        "end_index": min(end_index, total_items)
    }

    return PaginationResponse(
        data=paginated_books,
        pagination=pagination_info,
        message="Popular books fetched successfully",
        status="ok"
    )

@router.get("/popular/cache/status", response_model=ApiResponse)
@log_exceptions("GET /books/popular/cache/status", log_response=False)
def get_popular_books_cache_status():
    """
    Get the status of the popular books cache including size and TTL information.
    """
    current_time = time.time()
    cache_info = []
    
    for cache_key, cache_data in _popular_books_cache.items():
        age = current_time - cache_data["timestamp"]
        remaining_ttl = max(0, CACHE_TTL - age)
        cache_info.append({
            "key": cache_key,
            "age_seconds": round(age, 2),
            "remaining_ttl_seconds": round(remaining_ttl, 2),
            "data_count": len(cache_data["data"])
        })
    
    return {
        "data": {
            "total_entries": len(_popular_books_cache),
            "cache_ttl_seconds": CACHE_TTL,
            "entries": cache_info
        },
        "message": "Cache status retrieved successfully",
        "status": "ok"
    }

@router.delete("/popular/cache", response_model=ApiResponse)
@log_exceptions("DELETE /books/popular/cache", log_response=False)
def clear_popular_books_cache():
    """
    Clear the popular books cache. Useful for admin purposes or when cache needs to be refreshed.
    """
    global _popular_books_cache
    cache_size = len(_popular_books_cache)
    _popular_books_cache.clear()
    
    return {
        "data": {"cleared_entries": cache_size},
        "message": f"Popular books cache cleared. Removed {cache_size} cached entries.",
        "status": "ok"
    }

@router.get("/{book_id}", response_model=ApiResponse[BookResponse])
@log_exceptions("GET /books/{book_id}", log_response=False)
def get(book_id: int, book_service: BookService = Depends(get_book_service_auth)):
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
