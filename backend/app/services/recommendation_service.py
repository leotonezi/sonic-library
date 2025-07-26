from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.schemas.review import ReviewResponse
import os
import requests
import time
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.review import Review
from app.models.user_book import UserBook
import re

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

def create_book_recommendation_graph(db: Session, user_id: int) -> Dict[str, Any]:
    """Create a recommendation graph with direct book-to-book edges."""
    print(f"🔍 Creating graph for user_id: {user_id}")
    
    # Get user's reviews and books
    user_reviews = db.query(Review).filter(Review.user_id == user_id).all()
    user_books = db.query(UserBook).filter(UserBook.user_id == user_id).all()
    
    print(f"📚 Found {len(user_reviews)} reviews and {len(user_books)} user books")
    
    if not user_reviews:
        print("❌ No reviews found")
        return {"nodes": [], "edges": [], "message": "No reviews found for recommendation graph."}
    
    # Build similarity graph with direct edges
    nodes = []
    edges = []
    
    # Get books from user reviews and reading list
    book_ids = set()
    for review in user_reviews:
        if review.book_id:
            book_ids.add(review.book_id)
    for user_book in user_books:
        if user_book.book_id:
            book_ids.add(user_book.book_id)
    
    books = db.query(Book).filter(Book.id.in_(book_ids)).all() if book_ids else []
    
    print(f"📖 Found {len(books)} books:")
    for book in books:
        print(f"  - {book.title} by {book.author} (ID: {book.id})")
    
    # Create nodes for user's books
    for book in books:
        user_review = next((r for r in user_reviews if r.book_id == book.id), None)
        user_book_status = next((ub for ub in user_books if ub.book_id == book.id), None)
        
        rating = user_review.rate if user_review else None
        status = user_book_status.status.value if user_book_status else None
        
        # Generate position (simple grid layout)
        position_x = 100 + (len(nodes) % 3) * 200
        position_y = 100 + (len(nodes) // 3) * 150
        
        # Ensure unique node ID
        node_id = f"book-{book.id}-{user_id}"
        
        node = {
            "id": node_id,
            "position": {"x": position_x, "y": position_y},
            "data": {
                "label": book.title,
                "author": book.author,
                "rating": rating,
                "genre": ", ".join([g.name for g in book.genres]) if book.genres else "General"
            },
            "style": {
                "background": "#001f3f",
                "border": "2px solid #00aaff",
                "borderRadius": "8px",
                "padding": "12px",
                "minWidth": "160px",
                "color": "#e0f0ff"
            }
        }
        nodes.append(node)
    
    # Create direct book-to-book edges for similarities
    edges.extend(_create_direct_similarity_edges(books, user_reviews, user_id))
    
    # Get additional recommendations from AI
    print("🤖 Getting AI recommendations...")
    ai_recommendations = _get_ai_book_recommendations(user_reviews, db)
    print(f"🤖 Found {len(ai_recommendations)} AI recommendations")
    
    # Add AI recommendation nodes
    for i, rec in enumerate(ai_recommendations[:3]):  # Limit to 3 AI recommendations
        # Generate position (simple grid layout)
        position_x = 100 + (len(nodes) % 3) * 200
        position_y = 100 + (len(nodes) // 3) * 150
        
        node = {
            "id": f"ai-rec-{i}",
            "position": {"x": position_x, "y": position_y},
            "data": {
                "label": rec.get("title", "Unknown Title"),
                "author": rec.get("author", "Unknown Author"),
                "rating": rec.get("rating"),
                "genre": rec.get("genre", "General"),
                "description": rec.get("description", ""),
                "reasoning": rec.get("reasoning", "AI recommended based on your reading preferences"),
                "is_recommendation": True
            },
            "style": {
                "background": "#4a0e4e",
                "border": "2px solid #e879f9",
                "borderRadius": "8px",
                "padding": "12px",
                "minWidth": "160px",
                "color": "#f8bbff"
            }
        }
        nodes.append(node)
        
        # Create edges from high-rated books to AI recommendations
        for book in books:
            user_review = next((r for r in user_reviews if r.book_id == book.id), None)
            if user_review and user_review.rate >= 4:
                edge = {
                    "id": f"edge-{book.id}-ai-{i}-{user_id}",
                    "source": f"book-{book.id}-{user_id}",
                    "target": f"ai-rec-{i}",
                    "label": "AI Recommended",
                    "style": {"stroke": "#e879f9", "strokeWidth": 3},
                    "labelStyle": {
                        "fill": "#ffffff",
                        "fontWeight": 700,
                        "fontSize": "13px",
                        "background": "rgba(232, 121, 249, 0.9)",
                        "padding": "2px 4px",
                        "borderRadius": "4px"
                    },
                    "labelBgStyle": {"fill": "rgba(232, 121, 249, 0.9)", "fillOpacity": 0.9}
                }
                edges.append(edge)
                break  # Only connect one high-rated book per AI recommendation
    
    return {"nodes": nodes, "edges": edges, "message": "Graph generated successfully"}

def _create_direct_similarity_edges(books: List[Book], user_reviews: List[Review], user_id: int) -> List[Dict[str, Any]]:
    """Create direct book-to-book edges based on similarities."""
    edges = []
    
    for i, book1 in enumerate(books):
        for book2 in books[i+1:]:
            similarities = []
            
            # Same author - this is always a strong connection
            if book1.author and book2.author and book1.author.lower() == book2.author.lower():
                similarities.append(("Same Author", "#00aaff", 3))
            
            # Genre similarity - much more restrictive and intelligent
            book1_genres = set([g.name.lower() for g in book1.genres]) if book1.genres else set()
            book2_genres = set([g.name.lower() for g in book2.genres]) if book2.genres else set()
            
            # Remove generic/broad genres that don't provide meaningful similarity
            generic_genres = {
                'fiction / general', 'fiction', 'general', 'literature', 'books', 'novel',
                'contemporary fiction', 'modern fiction', 'adult fiction'
            }
            
            # Get specific genres only (remove generic ones)
            book1_specific = book1_genres - generic_genres
            book2_specific = book2_genres - generic_genres
            
            print(f"   Book1 specific genres: {book1_specific}")
            print(f"   Book2 specific genres: {book2_specific}")
            
            # Define incompatible specific genre pairs
            incompatible_pairs = [
                ('fiction / fantasy / general', 'fiction / romance / general'),
                ('fiction / fantasy / general', 'fiction / contemporary'),
                ('fiction / romance / general', 'fiction / fantasy / general'),
                ('fiction / romance / general', 'science fiction'),
                ('fiction / romance / general', 'mystery'),
                ('fiction / romance / general', 'horror'),
                ('science fiction', 'fiction / romance / general'),
                ('fantasy', 'romance'),
                ('horror', 'romance'),
                ('thriller', 'romance')
            ]
            
            # Check for incompatible combinations (only block very obvious conflicts)
            is_incompatible = False
            for genre1 in book1_specific:
                for genre2 in book2_specific:
                    if (genre1, genre2) in incompatible_pairs or (genre2, genre1) in incompatible_pairs:
                        print(f"❌ Incompatible genres detected: {genre1} vs {genre2}")
                        is_incompatible = True
                        break
                if is_incompatible:
                    break
            
            # Create genre connections if not incompatible
            if not is_incompatible and book1_genres and book2_genres:
                # First try specific genres
                common_specific = book1_specific.intersection(book2_specific)
                if common_specific:
                    print(f"✅ Compatible specific genres found: {common_specific}")
                    if len(common_specific) >= 2:
                        similarities.append(("Same Genres", "#fc9957", 3))
                    else:
                        similarities.append(("Similar Genre", "#60a5fa", 2))
                # If no specific match but not incompatible, allow broad similarity
                elif book1_genres.intersection(book2_genres):
                    print(f"✅ Broad genre compatibility found")
                    similarities.append(("Similar Category", "#60a5fa", 1))
            
            # Same universe - only for same author or very obvious series
            if _check_same_universe(book1.title, book2.title):
                # Additional check: only connect if same author or very clear series
                if (book1.author and book2.author and book1.author.lower() == book2.author.lower()) or \
                   _is_obvious_series(book1.title, book2.title):
                    similarities.append(("Same Universe", "#fa8537", 3))
            
            # Similar style - only if genres are compatible and descriptions are very similar
            if (book1.description and book2.description and 
                _check_similar_style(book1.description, book2.description) and
                book1_genres and book2_genres):
                # Additional genre compatibility check for style connections
                is_style_compatible = True
                for genre1 in book1_genres:
                    for genre2 in book2_genres:
                        if genre1 in incompatible_genres and genre2 in incompatible_genres[genre1]:
                            is_style_compatible = False
                            break
                if is_style_compatible:
                    similarities.append(("Similar Style", "#3F8EF3", 2))
            
            # Create edge for strongest similarity
            if similarities:
                # Sort by strength (third element in tuple)
                similarities.sort(key=lambda x: x[2], reverse=True)
                strongest = similarities[0]
                
                # Debug logging to understand connections
                print(f"📚 Connecting '{book1.title}' <-> '{book2.title}': {strongest[0]}")
                print(f"   Book1 genres: {[g.name for g in book1.genres] if book1.genres else 'None'}")
                print(f"   Book2 genres: {[g.name for g in book2.genres] if book2.genres else 'None'}")
                print(f"   All similarities found: {[s[0] for s in similarities]}")
                
                # Convert hex color to rgba format like the working mock data
                color_rgba = f"rgba({int(strongest[1][1:3], 16)}, {int(strongest[1][3:5], 16)}, {int(strongest[1][5:7], 16)}, 0.8)"
                
                # Use consistent node ID format with user_id
                edge = {
                    "id": f"edge-{book1.id}-{book2.id}-{user_id}",
                    "source": f"book-{book1.id}-{user_id}",
                    "target": f"book-{book2.id}-{user_id}",
                    "label": strongest[0],
                    "style": {"stroke": strongest[1], "strokeWidth": strongest[2]},
                    "labelStyle": {
                        "fill": "#ffffff",
                        "fontWeight": 700,
                        "fontSize": "13px",
                        "background": color_rgba,
                        "padding": "2px 4px",
                        "borderRadius": "4px"
                    },
                    "labelBgStyle": {"fill": color_rgba, "fillOpacity": 0.9}
                }
                edges.append(edge)
    
    return edges

def _create_connection_nodes_and_edges(books: List[Book], user_reviews: List[Review], connection_node_id: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int]:
    """Create connection nodes and edges based on book similarities."""
    connection_nodes = []
    edges = []
    
    # Group books by similarity criteria
    similarity_groups = _analyze_book_similarities(books, user_reviews)
    
    for similarity_type, group_data in similarity_groups.items():
        for group_key, book_list in group_data.items():
            if len(book_list) >= 2:  # Only create connection nodes for groups with 2+ books
                # Create connection node
                connection_id = f"connection-{connection_node_id}"
                connection_node = {
                    "id": connection_id,
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "label": _get_connection_label(similarity_type, group_key),
                        "connection_type": similarity_type,
                        "description": _get_connection_description(similarity_type, group_key),
                        "book_count": len(book_list)
                    },
                    "type": "connectionNode"
                }
                connection_nodes.append(connection_node)
                
                # Create edges from each book to the connection node
                for book in book_list:
                    edge = {
                        "id": f"edge-book-{book.id}-conn-{connection_node_id}",
                        "source": f"book-{book.id}",
                        "target": connection_id,
                        "type": "to_connection"
                    }
                    edges.append(edge)
                
                connection_node_id += 1
    
    return connection_nodes, edges, connection_node_id

def _analyze_book_similarities(books: List[Book], user_reviews: List[Review]) -> Dict[str, Dict[str, List[Book]]]:
    """Analyze books and group them by similarity criteria."""
    similarity_groups = {
        "same_author": {},
        "same_universe": {},
        "same_genres": {},
        "high_rating": {},
        "similar_style": {}
    }
    
    # Group by author
    for book in books:
        if book.author:
            author_key = book.author.lower()
            if author_key not in similarity_groups["same_author"]:
                similarity_groups["same_author"][author_key] = []
            similarity_groups["same_author"][author_key].append(book)
    
    # Group by genres
    for book in books:
        if book.genres:
            for genre in book.genres:
                genre_key = genre.name.lower()
                if genre_key not in similarity_groups["same_genres"]:
                    similarity_groups["same_genres"][genre_key] = []
                similarity_groups["same_genres"][genre_key].append(book)
    
    # Group by high ratings (4+ stars)
    high_rated_books = []
    for book in books:
        user_review = next((r for r in user_reviews if r.book_id == book.id), None)
        if user_review and user_review.rate >= 4:
            high_rated_books.append(book)
    
    if len(high_rated_books) >= 2:
        similarity_groups["high_rating"]["highly_rated"] = high_rated_books
    
    # Group by universe (series detection)
    universe_groups = {}
    for i, book1 in enumerate(books):
        for book2 in books[i+1:]:
            if _check_same_universe(book1.title, book2.title):
                # Create a universe key based on common words
                universe_key = _extract_universe_key(book1.title, book2.title)
                if universe_key not in universe_groups:
                    universe_groups[universe_key] = set()
                universe_groups[universe_key].add(book1)
                universe_groups[universe_key].add(book2)
    
    for universe_key, book_set in universe_groups.items():
        if len(book_set) >= 2:
            similarity_groups["same_universe"][universe_key] = list(book_set)
    
    # Group by similar style
    style_groups = {}
    for i, book1 in enumerate(books):
        for book2 in books[i+1:]:
            if _check_similar_style(book1.description, book2.description):
                style_key = "similar_writing_style"
                if style_key not in style_groups:
                    style_groups[style_key] = set()
                style_groups[style_key].add(book1)
                style_groups[style_key].add(book2)
    
    for style_key, book_set in style_groups.items():
        if len(book_set) >= 2:
            similarity_groups["similar_style"][style_key] = list(book_set)
    
    return similarity_groups

def _get_connection_label(similarity_type: str, group_key: str) -> str:
    """Get human-readable label for connection node."""
    labels = {
        "same_author": f"By {group_key.title()}",
        "same_universe": f"{group_key.title()} Universe",
        "same_genres": f"{group_key.title()} Genre",
        "high_rating": "Highly Rated Books",
        "similar_style": "Similar Writing Style"
    }
    return labels.get(similarity_type, group_key.title())

def _get_connection_description(similarity_type: str, group_key: str) -> str:
    """Get description for connection node."""
    descriptions = {
        "same_author": f"Books written by the same author: {group_key.title()}",
        "same_universe": f"Books from the same fictional universe or series",
        "same_genres": f"Books sharing the {group_key.title()} genre",
        "high_rating": "Books you rated 4 stars or higher",
        "similar_style": "Books with similar writing style and themes"
    }
    return descriptions.get(similarity_type, f"Books connected by {group_key}")

def _extract_universe_key(title1: str, title2: str) -> str:
    """Extract a key representing the shared universe/series."""
    # Remove common words and numbers
    clean_title1 = re.sub(r'\b(the|a|an|book|volume|vol|part|\d+)\b', '', title1.lower()).strip()
    clean_title2 = re.sub(r'\b(the|a|an|book|volume|vol|part|\d+)\b', '', title2.lower()).strip()
    
    words1 = set(clean_title1.split())
    words2 = set(clean_title2.split())
    common_words = words1.intersection(words2)
    
    if common_words:
        return " ".join(sorted(common_words))
    
    # Fallback: use shorter title as base
    return clean_title1 if len(clean_title1) <= len(clean_title2) else clean_title2

def _check_same_universe(title1: str, title2: str) -> bool:
    """Basic check if books might be from the same universe/series."""
    if not title1 or not title2:
        return False
    
    # Remove common words and numbers
    clean_title1 = re.sub(r'\b(the|a|an|book|volume|vol|part|\d+)\b', '', title1.lower()).strip()
    clean_title2 = re.sub(r'\b(the|a|an|book|volume|vol|part|\d+)\b', '', title2.lower()).strip()
    
    # Check if one title contains significant words from the other
    words1 = set(clean_title1.split())
    words2 = set(clean_title2.split())
    
    if len(words1) > 0 and len(words2) > 0:
        common_words = words1.intersection(words2)
        return len(common_words) >= 2 or (len(common_words) >= 1 and (len(words1) <= 3 or len(words2) <= 3))
    
    return False

def _is_obvious_series(title1: str, title2: str) -> bool:
    """Check if titles are obviously from the same series (very strict)."""
    if not title1 or not title2:
        return False
    
    # Look for very obvious series patterns
    series_patterns = [
        r'harry potter',
        r'lord of the rings',
        r'hobbit',
        r'game of thrones',
        r'song of ice and fire',
        r'hunger games',
        r'twilight',
        r'fifty shades',
        r'chronicles of narnia'
    ]
    
    title1_lower = title1.lower()
    title2_lower = title2.lower()
    
    for pattern in series_patterns:
        if re.search(pattern, title1_lower) and re.search(pattern, title2_lower):
            return True
    
    return False

def _check_similar_style(desc1: Optional[str], desc2: Optional[str]) -> bool:
    """Check if books have similar style based on description keywords - very restrictive."""
    if not desc1 or not desc2:
        return False
    
    # Define very specific style keywords that are meaningful for connections
    style_keywords = [
        "epic fantasy", "urban fantasy", "high fantasy", "dark fantasy",
        "space opera", "hard sci-fi", "cyberpunk", "steampunk",
        "historical fiction", "contemporary fiction", "literary fiction",
        "psychological thriller", "cozy mystery", "epic adventure",
        "coming of age", "dystopian future", "post-apocalyptic",
        "magical realism", "gothic horror", "romantic comedy"
    ]
    
    desc1_lower = desc1.lower()
    desc2_lower = desc2.lower()
    
    # Look for exact phrase matches rather than individual words
    keywords1 = set([kw for kw in style_keywords if kw in desc1_lower])
    keywords2 = set([kw for kw in style_keywords if kw in desc2_lower])
    
    common_keywords = keywords1.intersection(keywords2)
    
    # Also check for very specific thematic similarities
    thematic_pairs = [
        ("vampire", "werewolf"), ("dragon", "magic"), ("wizard", "witch"),
        ("spaceship", "alien"), ("robot", "artificial intelligence"),
        ("detective", "murder"), ("spy", "espionage"),
        ("medieval", "kingdom"), ("pirate", "treasure")
    ]
    
    thematic_matches = 0
    for theme1, theme2 in thematic_pairs:
        if ((theme1 in desc1_lower and theme1 in desc2_lower) or
            (theme2 in desc1_lower and theme2 in desc2_lower) or
            (theme1 in desc1_lower and theme2 in desc2_lower) or
            (theme2 in desc1_lower and theme1 in desc2_lower)):
            thematic_matches += 1
    
    # Require either 2+ exact style phrase matches OR 2+ thematic matches
    return len(common_keywords) >= 2 or thematic_matches >= 2

def _get_ai_book_recommendations(user_reviews: List[Review], db: Session) -> List[Dict[str, Any]]:
    """Get AI-powered book recommendations based on user reviews."""
    if not user_reviews:
        return []
    
    # Convert to ReviewResponse format for existing function
    review_responses = []
    for review in user_reviews:
        review_responses.append(ReviewResponse(
            id=review.id,
            book_id=review.book_id,
            external_book_id=review.external_book_id,
            user_id=review.user_id,
            content=review.content,
            rate=review.rate,
            created_at=review.created_at,
            updated_at=review.updated_at
        ))
    
    # Get AI recommendations using existing function
    ai_result = generate_book_recommendations(review_responses)
    
    # Parse AI recommendations to extract book data
    recommendations = _parse_ai_recommendations(ai_result)
    
    return recommendations

def _parse_ai_recommendations(ai_result: str) -> List[Dict[str, Any]]:
    """Parse AI recommendation text to extract book data."""
    recommendations = []
    
    # Split by ID: pattern to separate books
    book_sections = re.split(r'ID:\s*', ai_result)
    
    for section in book_sections[1:]:  # Skip first empty section
        try:
            lines = section.strip().split('\n')
            if len(lines) < 4:
                continue
                
            external_id = lines[0].strip()
            title = lines[1].replace('Title:', '').strip() if lines[1].startswith('Title:') else lines[1].strip()
            authors = lines[2].replace('Authors:', '').strip() if lines[2].startswith('Authors:') else lines[2].strip()
            
            # Find description and reason
            description_line = next((line for line in lines if line.startswith('Description:')), '')
            description = description_line.replace('Description:', '').strip() if description_line else ''
            
            # Find the "Why recommended" reasoning
            reason_line = next((line for line in lines if line.startswith('Why recommended:')), '')
            reasoning = reason_line.replace('Why recommended:', '').strip() if reason_line else ''
            
            # If no explicit reasoning found, look for it in surrounding text
            if not reasoning:
                for line in lines:
                    if 'recommend' in line.lower() and not line.startswith(('ID:', 'Title:', 'Authors:', 'Description:')):
                        reasoning = line.strip()
                        break
            
            recommendation = {
                "external_id": external_id,
                "title": title,
                "author": authors,
                "description": description,
                "reasoning": reasoning,
                "genre": "AI Recommended",
                "rating": None
            }
            recommendations.append(recommendation)
            
        except Exception:
            continue
    
    return recommendations

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
        ("system", """You are an expert book recommendation engine. Analyze the user's 
         reading preferences based on their positive reviews and recommend books from the provided collection.

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
