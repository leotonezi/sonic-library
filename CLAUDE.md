# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend API | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |
| Database | PostgreSQL | 5432 |
| Test Frontend | http://localhost:3001 | 3001 |
| Test Backend | http://localhost:8001 | 8001 |`

---

## Development Commands

### Full Application (Recommended)
```bash
# Start all services with Docker
docker-compose up --build

# Start test environment (isolated database)
docker-compose -f docker-compose.test.yml up --build
```

### Backend (FastAPI)
```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_books.py

# Run with verbose output
pytest -v

# Run single test
pytest tests/test_books.py::test_create_book -v
```

### Frontend (Next.js)
```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build

# Linting
npm run lint

# E2E tests (interactive)
npm run cypress:open

# E2E tests (headless)
npm run cypress:run
```

---

## Architecture Overview

### Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Backend Framework | FastAPI | 0.115.11 |
| Backend ORM | SQLAlchemy | 2.0.39 |
| Database | PostgreSQL | 14 |
| Frontend Framework | Next.js | 15.2.5 |
| UI Library | React | 19.0.0 |
| State Management | Zustand | 5.0.3 |
| Styling | Tailwind CSS | 4.1.3 |
| AI/LLM | LangChain + OpenAI | GPT-3.5-turbo |
| E2E Testing | Cypress | 15.4.0 |
| Containerization | Docker Compose | - |

### Project Structure

```
sonic-library/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/v1/endpoints/   # Route handlers
│   │   │   ├── auth.py         # Login, signup, logout, activation
│   │   │   ├── books.py        # Book CRUD, search, popular
│   │   │   ├── user_books.py   # User library management
│   │   │   ├── reviews.py      # Review system
│   │   │   ├── recommendations.py  # AI recommendations
│   │   │   └── users.py        # User profile
│   │   ├── core/               # Configuration & utilities
│   │   │   ├── config.py       # Environment settings
│   │   │   ├── database.py     # DB connection & pooling
│   │   │   ├── security.py     # JWT & password handling
│   │   │   └── mail.py         # Email service
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── book.py
│   │   │   ├── user_book.py
│   │   │   └── review.py
│   │   ├── schemas/            # Pydantic validation schemas
│   │   │   └── base_schema.py  # ApiResponse, PaginationResponse
│   │   └── services/           # Business logic layer
│   │       ├── base_service.py # Generic CRUD operations
│   │       └── recommendation_service.py  # LangChain integration
│   ├── alembic/                # Database migrations
│   └── tests/                  # Pytest test files
│
├── frontend/                   # Next.js application
│   └── src/
│       ├── app/                # App Router pages
│       │   ├── (public)/       # Login, signup (no auth required)
│       │   └── (protected)/    # Books, library, recommendations
│       │       └── layout.tsx  # Auth wrapper
│       ├── components/         # React components
│       │   ├── navbar.tsx      # Global navigation with search
│       │   ├── pagination.tsx  # Search pagination
│       │   └── features/       # Feature-specific components
│       │       └── BookRecommendationGraph.tsx
│       ├── store/              # Zustand state management
│       │   ├── useAuthStore.ts
│       │   └── useSearchBookStore.ts
│       ├── services/           # API communication layer
│       │   └── bookService.ts
│       ├── lib/                # Utilities & helpers
│       │   └── api-client.ts   # HTTP client with auth
│       ├── types/              # TypeScript interfaces
│       ├── hooks/              # Custom React hooks
│       └── config.ts           # App configuration
│   └── cypress/                # E2E tests
│       ├── e2e/                # Test specs
│       ├── fixtures/           # Test data
│       └── support/            # Custom commands
│
├── docker-compose.yml          # Development environment
└── docker-compose.test.yml     # Isolated test environment
```

---

## Database Models & Relationships

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │       │   UserBook  │       │    Book     │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │──┐    │ id (PK)     │    ┌──│ id (PK)     │
│ name        │  │    │ user_id (FK)│────┘  │ external_id │
│ email       │  └───>│ book_id (FK)│       │ title       │
│ password    │       │ external_id │       │ author      │
│ is_active   │       │ status      │       │ genres (M2M)│
│ profile_pic │       │ created_at  │       └─────────────┘
└─────────────┘       └─────────────┘              │
       │                                           │
       │              ┌─────────────┐              │
       │              │   Review    │              │
       │              ├─────────────┤              │
       └─────────────>│ id (PK)     │<─────────────┘
                      │ user_id (FK)│
                      │ book_id (FK)│
                      │ external_id │
                      │ content     │
                      │ rate (1-5)  │
                      └─────────────┘
```

**Key Points:**
- `UserBook` supports both local books (`book_id`) and external Google Books (`external_book_id`)
- `Review` can reference local or external books
- Status options: `TO_READ`, `READING`, `READ`
- Rating constraint: 1-5 stars

---

## API Endpoints Reference

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/token` | No | Login (returns JWT in cookie) |
| POST | `/signup` | No | Register (sends activation email) |
| GET | `/activate` | No | Activate account via email link |
| POST | `/logout` | No | Clear auth cookies |

### Books (`/api/v1/books`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | List local books (paginated, filterable) |
| POST | `/` | Yes | Create local book |
| GET | `/{id}` | No | Get book details |
| GET | `/search-external` | No | Search Google Books API |
| GET | `/popular` | No | Get popular books (cached 1hr) |

### User Library (`/api/v1/user-books`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/` | Yes | Add book to library |
| GET | `/my-books` | Yes | Get user's books |
| GET | `/my-books/paginated` | Yes | Get books with pagination & status filter |
| PUT | `/{id}` | Yes | Update book status |
| DELETE | `/{id}` | Yes | Remove from library |

### Reviews (`/api/v1/reviews`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/` | Yes | Create review |
| GET | `/book/{id}` | Yes | Get reviews for local book |
| GET | `/book/external/{id}` | Yes | Get reviews for external book |

### Recommendations (`/api/v1/recommendations`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | Yes | Generate AI recommendations |
| GET | `/graph` | Yes | Get graph visualization data |

### API Response Format

**Standard Response:**
```json
{
  "data": { ... },
  "message": "Success",
  "status": "ok"
}
```

**Paginated Response:**
```json
{
  "data": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 50,
    "page_size": 10,
    "has_next": true,
    "has_previous": false,
    "start_index": 0,
    "end_index": 10
  },
  "message": "Success",
  "status": "ok"
}
```

---

## Key Patterns & Conventions

### Backend Patterns

**Service Layer Pattern:**
```python
# All services extend BaseService for CRUD operations
class BookService(BaseService[Book]):
    def __init__(self, db: Session):
        super().__init__(db, Book)

    # Custom business logic methods
    def filter_books_paginated(self, search: str, genre: str, page: int):
        ...
```

**Authentication:**
```python
# Dependency injection for protected endpoints
@router.get("/my-books")
def get_my_books(current_user: User = Depends(get_current_user)):
    ...
```

**Error Handling:**
```python
# Use HTTPException with early returns
if not book:
    raise HTTPException(status_code=404, detail="Book not found")
```

### Frontend Patterns

**Import Aliases:**
```typescript
// Use path mappings configured in tsconfig.json
import { apiClient } from '@/lib/api-client'
import { Book, UserBook } from '@/types'
import { useAuthStore } from '@/store/useAuthStore'
```

**State Management (Zustand):**
```typescript
// Simple store pattern
const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoading: false,

  checkAuth: async () => {
    const response = await apiClient.get('/users/me')
    set({ user: response.data })
  },

  logout: async () => {
    await apiClient.post('/auth/logout')
    set({ user: null })
  }
}))
```

**Protected Routes:**
```typescript
// (protected)/layout.tsx wraps all authenticated pages
// Checks auth status and redirects to /login if unauthorized
```

**API Client Usage:**
```typescript
// Use the centralized apiClient
const books = await apiClient.get<Book[]>('/books')
await apiClient.post('/user-books', { book_id: 123 })
```

### Naming Conventions

| Context | Convention | Example |
|---------|------------|---------|
| Backend Models | PascalCase | `User`, `UserBook` |
| Backend Endpoints | kebab-case | `/user-books`, `/search-external` |
| Backend Services | PascalCase + Service | `BookService` |
| Frontend Components | PascalCase | `NavBar`, `BookCard` |
| Frontend Files | kebab-case | `book-card.tsx` |
| Zustand Stores | camelCase + use prefix | `useAuthStore` |
| TypeScript Types | PascalCase | `Book`, `PaginatedResponse` |

---

## Authentication Flow

```
1. SIGNUP
   User submits form → POST /auth/signup → Create user (is_active=false)
   → Send activation email → User clicks link → GET /auth/activate
   → Set is_active=true → Redirect to login

2. LOGIN
   User submits credentials → POST /auth/token → Validate credentials
   → Generate JWT → Set HTTP-only cookie → Return user data
   → Frontend: useAuthStore.setUser() → Redirect to /books

3. AUTH CHECK (on page load)
   Frontend calls checkAuth() → GET /users/me → Valid? Set user state
   → Invalid (401)? Clear state, redirect to /login

4. LOGOUT
   POST /auth/logout → Clear cookies → useAuthStore.logout()
   → Redirect to /login
```

**JWT Configuration:**
- Access token: 30 minutes expiry
- Refresh token: 7 days expiry
- Storage: HTTP-only cookies (secure)
- Algorithm: HS256

---

## AI Recommendations System

**Flow:**
1. User reviews books with ratings
2. GET `/recommendations/` triggers LangChain
3. System analyzes user's review history
4. GPT-3.5-turbo generates personalized recommendations
5. Results searched against Google Books API
6. Cached for 1 hour (MD5 hash of reviews as key)

**Graph Visualization:**
- Uses `@xyflow/react` library
- Nodes: User's books + recommended books
- Edges: Similarity relationships
- Interactive pan/zoom

---

## Testing Strategy

### Backend (pytest)
```bash
# Run all tests
cd backend && pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_auth.py::test_login -v
```

### Frontend (Cypress E2E)
```bash
# Development mode (interactive)
npm run cypress:open

# CI mode (headless)
npm run cypress:run

# Against test environment
npm run cypress:open:test
```

**Test Environment:**
- Uses `docker-compose.test.yml`
- Isolated database (port 5433)
- Frontend on port 3001
- Backend on port 8001

### Test Data
- Fixtures in `frontend/cypress/fixtures/`
- Custom commands in `frontend/cypress/support/commands.ts`

---

## Development Guidelines

### Code Style
- **Type Safety**: Always use TypeScript types, Python type hints
- **Async/Await**: Use for all I/O operations
- **Early Returns**: Prefer guard clauses over nested conditions
- **Functional Style**: Prefer pure functions, avoid mutations
- **Descriptive Names**: Variables/functions should be self-documenting

### What to Avoid
- Don't store JWTs in localStorage (use HTTP-only cookies)
- Don't skip type annotations in new code
- Don't create new files when editing existing ones works
- Don't add unused imports or dead code
- Don't commit `.env` files or secrets

### Pull Request Checklist
- [ ] Tests pass (`pytest` and `npm run lint`)
- [ ] Types are correct (no `any` unless necessary)
- [ ] API changes documented
- [ ] Database migrations created if schema changed
- [ ] No console.log or print statements left in code

---

## Common Tasks

### Adding a New API Endpoint
1. Create/update model in `backend/app/models/`
2. Create Pydantic schema in `backend/app/schemas/`
3. Add service method in `backend/app/services/`
4. Create endpoint in `backend/app/api/v1/endpoints/`
5. Register router in `backend/app/api/v1/__init__.py`
6. Add tests in `backend/tests/`

### Adding a New Frontend Page
1. Create page file in `frontend/src/app/(protected)/` or `(public)/`
2. Add types in `frontend/src/types/`
3. Create API service function in `frontend/src/services/`
4. Add Zustand store if needed in `frontend/src/store/`
5. Create components in `frontend/src/components/`

### Database Migrations
```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Environment Variables

### Backend (`.env`)
```env
DATABASE_URL=postgresql+psycopg2://postgres:password@db:5432/fastlibrary
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-...
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
MAIL_USERNAME=email@example.com
MAIL_PASSWORD=password
MAIL_FROM=noreply@example.com
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
TESTING=false
POPULAR_BOOKS_CACHE_TTL=3600
```

### Frontend (`.env.local`)
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Restart containers
docker-compose down && docker-compose up --build
```

**Frontend build errors:**
```bash
# Clear cache and reinstall
cd frontend && rm -rf node_modules .next && npm install
```

**Auth not working:**
- Check cookies are being set (HTTP-only, same-site)
- Verify `FRONTEND_URL` matches actual frontend URL
- Check `is_active` is `true` for user

**AI recommendations failing:**
- Verify `OPENAI_API_KEY` is set
- Check user has reviewed at least 1 book
- Review LangChain logs for errors
