from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.schemas.review import ReviewResponse
import os
import requests
import time
import hashlib
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
else:
    raise ValueError("OPENAI_API_KEY not set in environment")

llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")

# Simple in-memory cache for recommendations
_recommendations_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 3600  # 1 hour cache

def get_google_books_by_genre(genres: List[str], max_results: int = 20) -> List[Dict]:
    """Fetch books from Google Books API based on genres."""
    GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
    GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
    
    # Create search query from genres
    genre_query = " OR ".join([f"subject:{genre}" for genre in genres])
    
    params = {
        "q": genre_query,
        "maxResults": min(max_results, 40),
        "orderBy": "relevance"
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
                "categories": info.get("categories", []),
                "averageRating": info.get("averageRating"),
                "ratingsCount": info.get("ratingsCount"),
                "pageCount": info.get("pageCount"),
                "language": info.get("language")
            })
        return books
    except:
        return []

def create_cache_key(user_reviews: List[ReviewResponse]) -> str:
    """Create a cache key based on user reviews."""
    reviews_data = [{"book_id": r.book_id, "rate": r.rate, "content": r.content} for r in user_reviews]
    reviews_json = json.dumps(reviews_data, sort_keys=True)
    return hashlib.md5(reviews_json.encode()).hexdigest()

def get_cached_recommendations(cache_key: str) -> Optional[str]:
    """Get recommendations from cache if available and not expired."""
    cached_data = _recommendations_cache.get(cache_key)
    
    if cached_data:
        current_time = time.time()
        if current_time - cached_data["timestamp"] < CACHE_TTL:
            return cached_data["data"]
        else:
            del _recommendations_cache[cache_key]
    
    return None

def set_cached_recommendations(cache_key: str, data: str):
    """Cache recommendations with timestamp."""
    _recommendations_cache[cache_key] = {
        "data": data,
        "timestamp": time.time()
    }

def generate_book_recommendations(user_reviews: List[ReviewResponse]) -> str:
    # Check cache first
    cache_key = create_cache_key(user_reviews)
    cached_result = get_cached_recommendations(cache_key)
    if cached_result:
        return cached_result
    
    # Filter for positive ratings only (3+ stars)
    positive_reviews = [r for r in user_reviews if r.rate >= 3]
    
    if not positive_reviews:
        return "No positive reviews found. Please rate some books you enjoyed to get better recommendations."
    
    # Extract genres from positive reviews to search Google Books
    # This is a simple approach - in a real implementation you'd want to store book metadata
    all_genres = []
    for review in positive_reviews:
        # You could enhance this by storing book genres in your review or book model
        # For now, we'll use some common genres as fallback
        all_genres.extend(["fiction", "literature", "bestseller"])
    
    # Get books from Google Books API
    google_books = get_google_books_by_genre(list(set(all_genres)), max_results=30)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert book recommendation engine. Analyze the user's reading preferences based on their positive reviews and recommend books from the provided collection.

Guidelines:
- Only recommend books the user hasn't already reviewed
- Focus on books with good ratings and reviews when available
- Consider genre preferences, writing style, and themes
- Provide 5 specific recommendations with detailed explanations
- Be concise but insightful in your reasoning"""),
        ("user", """User's Positive Reviews (3+ stars):
{positive_reviews}

Available Books from Google Books:
{google_books}

Based on their positive reviews, recommend 5 books from the available collection and explain why each book matches their preferences. 

IMPORTANT: For each recommendation, you MUST use this exact format:
ID: [use the exact external_id from the book list above, like "7-BTAgAAQBAJ"]
Title: [book title]
Authors: [authors]
Description: [brief description]
Why recommended: [your reasoning]

Make sure to use the exact external_id value (the alphanumeric string with hyphens) from the Google Books data provided above.""")
    ])

    # Format positive reviews with more context
    reviews_text = "\n".join([
        f"Book ID {r.book_id}: \"{r.content}\" (Rating: {r.rate}/5 stars)"
        for r in positive_reviews
    ])
    
    # Format Google Books data
    books_text = "\n".join([
        f"ID: {book['external_id']}\nTitle: {book['title']}\nAuthors: {', '.join(book.get('authors', []))}\nCategories: {', '.join(book.get('categories', []))}\nDescription: {book.get('description', 'No description available')[:200]}...\nAverage Rating: {book.get('averageRating', 'N/A')}\nPage Count: {book.get('pageCount', 'N/A')}\n---"
        for book in google_books[:15]  # Limit to avoid token limits
    ])

    chain = prompt | llm
    result = chain.invoke({
        "positive_reviews": reviews_text,
        "google_books": books_text
    }).content
    
    # Cache the result
    set_cached_recommendations(cache_key, result)
    
    return result
