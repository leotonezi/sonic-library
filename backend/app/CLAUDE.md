# Backend App Layer

## Structure

```
app/
├── api/v1/endpoints/   # Route handlers
├── core/               # Config, DB, security, mail
├── models/             # SQLAlchemy ORM models
├── schemas/            # Pydantic validation schemas
├── services/           # Business logic layer
└── main.py             # FastAPI app entry point
```

## Patterns

### Service Layer
All services extend `BaseService` for generic CRUD:
```python
class BookService(BaseService[Book]):
    def __init__(self, db: Session):
        super().__init__(db, Book)
```

### Authentication
Use dependency injection for protected endpoints:
```python
@router.get("/my-books")
def get_my_books(current_user: User = Depends(get_current_user)):
    ...
```

### Error Handling
Use `HTTPException` with early returns (guard clauses):
```python
if not book:
    raise HTTPException(status_code=404, detail="Book not found")
```

## Key Modules

### `core/`
- `config.py` — Environment settings via Pydantic `BaseSettings`
- `database.py` — DB connection, session factory, pooling
- `security.py` — JWT creation/verification, password hashing (HS256)
- `mail.py` — Email service for account activation

### `models/`
- `user.py` — User (name, email, password, is_active, profile_pic)
- `book.py` — Book (external_id, title, author, genres M2M)
- `user_book.py` — UserBook (user_id, book_id, external_id, status)
- `review.py` — Review (user_id, book_id, external_id, content, rate 1-5)

### `schemas/`
- `base_schema.py` — `ApiResponse`, `PaginationResponse` wrappers

### `services/`
- `base_service.py` — Generic CRUD (get, get_all, create, update, delete)
- `recommendation_service.py` — LangChain + OpenAI integration

## AI Recommendations

1. Analyzes user's review history via LangChain
2. GPT-3.5-turbo generates personalized recommendations
3. Results searched against Google Books API
4. Cached 1hr (MD5 hash of reviews as key)
