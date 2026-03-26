# Backend — FastAPI

## Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_books.py

# Run single test
pytest tests/test_books.py::test_create_book -v

# Run with coverage
pytest --cov=app
```

## Database Migrations (Alembic)

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1
```

## Database Models

```
User         → UserBook (FK: user_id) → Book (FK: book_id)
User/Book    → Review (FK: user_id, book_id)
```

- `UserBook` supports local books (`book_id`) and external Google Books (`external_book_id`)
- `Review` can reference local or external books
- Status options: `TO_READ`, `READING`, `READ`
- Rating constraint: 1-5 stars

## API Response Format

```json
{ "data": {...}, "message": "Success", "status": "ok" }
```

Paginated responses include a `pagination` object with `current_page`, `total_pages`, `total_count`, `page_size`, `has_next`, `has_previous`.

## API Endpoints

### Auth (`/api/v1/auth`)
- `POST /token` — Login (returns JWT in cookie)
- `POST /signup` — Register (sends activation email)
- `GET /activate` — Activate account via email link
- `POST /logout` — Clear auth cookies

### Books (`/api/v1/books`)
- `GET /` — List books (paginated, filterable)
- `POST /` — Create book (auth required)
- `GET /{id}` — Get book details
- `GET /search-external` — Search Google Books API
- `GET /popular` — Popular books (cached 1hr)

### User Library (`/api/v1/user-books`)
- `POST /` — Add book to library
- `GET /my-books` — Get user's books
- `GET /my-books/paginated` — Paginated with status filter
- `PUT /{id}` — Update book status
- `DELETE /{id}` — Remove from library

### Reviews (`/api/v1/reviews`)
- `POST /` — Create review
- `GET /book/{id}` — Reviews for local book
- `GET /book/external/{id}` — Reviews for external book

### Recommendations (`/api/v1/recommendations`)
- `GET /` — Generate AI recommendations
- `GET /graph` — Graph visualization data

## Auth Flow

1. Signup → create user (is_active=false) → activation email → activate → login
2. Login → validate → JWT in HTTP-only cookie (30min access, 7day refresh, HS256)
3. Auth check → `GET /users/me` → 401 means redirect to login
4. Logout → clear cookies

## Environment Variables

```
DATABASE_URL=postgresql+psycopg2://postgres:password@db:5432/fastlibrary
SECRET_KEY, OPENAI_API_KEY, FRONTEND_URL, BACKEND_URL
MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_SERVER, MAIL_PORT
TESTING=false, POPULAR_BOOKS_CACHE_TTL=3600
```

## Adding a New Endpoint

1. Create/update model in `app/models/`
2. Create Pydantic schema in `app/schemas/`
3. Add service method in `app/services/`
4. Create endpoint in `app/api/v1/endpoints/`
5. Register router in `app/api/v1/__init__.py`
6. Add tests in `tests/`

## Troubleshooting

- **DB connection errors**: `docker-compose down && docker-compose up --build`
- **Auth not working**: Check cookies, verify `FRONTEND_URL`, check `is_active`
- **AI recommendations failing**: Verify `OPENAI_API_KEY`, user needs >= 1 review
